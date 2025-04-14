

import os
import subprocess
import json
import time
from pathlib import Path
import datetime
import stat
from google import genai
from google.genai import types
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File and directory management functions (unchanged from original)


def is_safe_path(path):
    """Validates if the path is within current working directory."""
    path = os.path.abspath(path)
    cwd = os.path.abspath(os.getcwd())
    return path.startswith(cwd)


def is_safe_command(command):
    """Checks if a command is safe to execute (no sudo)."""
    if "sudo" in command.lower().split():
        return False
    return True


def read_file(filename):
    """Reads and returns the contents of a file in the current working directory."""
    if not is_safe_path(filename):
        print(
            f"Error: File '{filename}' is not in the current working directory.")
        return None
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def get_file_metadata(filename):
    """Returns metadata for a file in the current working directory."""
    if not is_safe_path(filename):
        print(
            f"Error: File '{filename}' is not in the current working directory.")
        return None
    try:
        file_path = Path(filename)
        if not file_path.exists():
            print(f"Error: File '{filename}' not found.")
            return None

        stat_info = file_path.stat()
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        accessed_time = datetime.datetime.fromtimestamp(stat_info.st_atime)
        perms = stat.filemode(stat_info.st_mode)

        metadata = {
            'name': file_path.name,
            'size': stat_info.st_size,
            'created': created_time.isoformat(),
            'modified': modified_time.isoformat(),
            'accessed': accessed_time.isoformat(),
            'permissions': perms,
            'is_directory': file_path.is_dir(),
            'is_file': file_path.is_file(),
            'absolute_path': str(file_path.absolute()),
        }
        return metadata
    except Exception as e:
        print(f"Error getting file metadata: {e}")
        return None


def list_directory_contents(directory="."):
    """Lists all files and directories in the specified directory."""
    if not is_safe_path(directory):
        print(
            f"Error: Directory '{directory}' is not in the current working directory.")
        return None
    try:
        abs_dir = os.path.abspath(directory)
        if not os.path.exists(abs_dir):
            print(f"Error: Directory '{directory}' not found.")
            return None
        if not os.path.isdir(abs_dir):
            print(f"Error: '{directory}' is not a directory.")
            return None

        files = []
        directories = []
        for item in os.listdir(abs_dir):
            item_path = os.path.join(abs_dir, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                directories.append(item)

        return {
            'files': files,
            'directories': directories,
            'total_files': len(files),
            'total_directories': len(directories)
        }
    except Exception as e:
        print(f"Error listing directory contents: {e}")
        return None


def write_to_file(filename, content, mode="w"):
    """Writes content to a file in the current working directory."""
    if not is_safe_path(filename):
        print(
            f"Error: File '{filename}' is not in the current working directory.")
        return False
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, mode) as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False


def run_command(command):
    """Runs a terminal command in the current working directory, without sudo."""
    if not is_safe_command(command):
        print("Error: Cannot run commands with 'sudo'.")
        return None
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        stdout, stderr = process.communicate()
        return {
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode
        }
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def create_directory(directory_name):
    """Creates a directory in the current working directory."""
    if not is_safe_path(directory_name):
        print(
            f"Error: Directory '{directory_name}' is not in the current working directory.")
        return False
    try:
        os.makedirs(directory_name, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

# Gemini Project Generator


class GeminiProjectGenerator:
    def __init__(self, api_key):
        """Initializes the project generator with Gemini API key."""
        self.client = genai.Client(api_key=api_key)
        
        # Store both the functions and descriptions
        self.tool_functions = {
            "read_file": read_file,
            "get_file_metadata": get_file_metadata,
            "list_directory_contents": list_directory_contents,
            "write_to_file": write_to_file,
            "run_command": run_command,
            "create_directory": create_directory
        }
        
        # Only descriptions for the system prompt
        self.tool_descriptions = {
            "read_file": "Reads contents of a file in the current working directory. Input: {'filename': 'string'}",
            "get_file_metadata": "Returns metadata for a file in the current working directory. Input: {'filename': 'string'}",
            "list_directory_contents": "Lists all files and directories in the specified directory. Input: {'directory': 'string'}",
            "write_to_file": "Writes content to a file in the current working directory. Input: {'filename': 'string', 'content': 'string', 'mode': 'w|a'}",
            "run_command": "Runs a terminal command in the current working directory, without sudo. Input: {'command': 'string'}",
            "create_directory": "Creates a directory in the current working directory. Input: {'directory_name': 'string'}"
        }
        
        self.messages = []
        self.project_name = None

    def _handle_action(self, action):
        """Handles action steps from Gemini responses."""
        tool_name = action.get("function")
        tool_input = action.get("input")
        
        if tool_name in self.tool_functions:
            try:
                # Convert string input to dict if needed
                if isinstance(tool_input, str):
                    tool_input = json.loads(tool_input)
                
                # Call the tool function
                output = self.tool_functions[tool_name](**tool_input)
                return {
                    "step": "observe",
                    "output": output
                }
            except Exception as e:
                return {
                    "step": "error",
                    "content": f"Error executing {tool_name}: {str(e)}"
                }
        else:
            return {
                "step": "error",
                "content": f"Unknown tool: {tool_name}"
            }

    def generate_project(self, project_type, project_name, project_description):
        """Generates a fullstack project based on the provided specifications."""
        self.project_name = project_name
        start_time = time.time()
        
        system_prompt = f"""
You are an expert fullstack developer assistant capable of generating complete project structures.
You have access to tools that can create directories, write files, and run commands.
Rules:
- Work only within the current directory
- Cannot use sudo commands
- Create well-organized, production-ready project structure
- Include proper files with appropriate content
- Be systematic and thorough
- Follow the Output JSON Format

Output JSON Format:
{{
    "step": "plan|action|observe|output",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function",
}}

Available Tools:
{json.dumps(self.tool_descriptions, indent=2)}

Project Type: {project_type}
Project Name: {project_name}
Project Description: {project_description}
"""

        self.messages = [{
            "role": "user",
            "content": f"Generate a complete {project_type} project named '{project_name}' with description: {project_description}"
        }]

        actions_taken = []
        generated_files = []
        generated_dirs = []
        max_steps = 25
        step = 0

        print(f"Starting project generation for {project_name}...")
        print(f"Type: {project_type}")
        print(f"Description: {project_description}")
        print("=" * 80)

        while step < max_steps:
            step += 1
            print(f"\nStep {step} of project generation process:")

            try:
                response = self.client.models.generate_content(
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt),
                    model='gemini-1.5-pro-latest',
                    contents=[json.dumps(msg) for msg in self.messages]
                )

                parsed_response = self._parse_gemini_response(response)
                if not parsed_response:
                    continue

                self.messages.append(parsed_response)

                if parsed_response.get("step") == "plan":
                    print(f"🧠 Planning: {parsed_response.get('content')}")
                    continue

                elif parsed_response.get("step") == "action":
                    print(f"⚡ Action: {parsed_response.get('function')}")
                    action_result = self._handle_action(parsed_response)
                    self.messages.append(action_result)

                    # Track actions
                    if action_result["step"] == "observe":
                        tool_name = parsed_response.get("function")
                        tool_input = parsed_response.get("input")

                        if tool_name == "create_directory":
                            if isinstance(tool_input, dict):
                                generated_dirs.append(
                                    tool_input.get("directory_name"))
                            else:
                                generated_dirs.append(tool_input)
                            print(f"  Created directory: {tool_input}")

                        elif tool_name == "write_to_file":
                            if isinstance(tool_input, dict):
                                filename = tool_input.get("filename")
                            else:
                                filename = tool_input
                            generated_files.append(filename)
                            print(f"  Created file: {filename}")

                        actions_taken.append({
                            "step": step,
                            "action": tool_name,
                            "args": tool_input,
                            "result": action_result["output"]
                        })

                elif parsed_response.get("step") == "output":
                    print(f"✅ Completion: {parsed_response.get('content')}")
                    break

            except Exception as e:
                print(f"Error during project generation: {e}")
                actions_taken.append({
                    "step": step,
                    "error": str(e)
                })
                break

        # Get final summary
        summary_response = self.client.models.generate_content(
            config=types.GenerateContentConfig(
                system_instruction=system_prompt),
            model='gemini-1.5-pro-latest',
            contents=[json.dumps(msg) for msg in self.messages] +
            [json.dumps(
                {"role": "user", "content": "Provide a summary of what you've created including the project structure, files, and key features."})]
        )

        summary = summary_response.text

        end_time = time.time()
        duration = end_time - start_time

        return {
            "project_name": project_name,
            "project_type": project_type,
            "total_steps": step,
            "total_files": len(generated_files),
            "total_directories": len(generated_dirs),
            "files_created": generated_files,
            "directories_created": generated_dirs,
            "generation_time_seconds": duration,
            "summary": summary,
            "actions": actions_taken
        }


def main():
    """Main function that takes input from the terminal and runs the generator."""
    print("=" * 80)
    print("GEMINI PROJECT GENERATOR")
    print("=" * 80)
    print("This tool will generate a complete project structure based on your specifications.")
    print("Please provide the following information:")
    print()

    project_type = input(
        "Enter project type (e.g., MERN Stack, Django+React): ").strip()
    project_name = input("Enter project name: ").strip()

    print("\nEnter project description (type 'END' on a new line when finished):")
    project_description_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        project_description_lines.append(line)

    project_description = "\n".join(project_description_lines)

    api_key = os.getenv("GEMINI_API_KEY") or input("Enter your Gemini API key: ") 

    generator = GeminiProjectGenerator(api_key)

    print(f"\nStarting project generation for {project_name}...")
    print(f"Type: {project_type}")
    print(f"Description: {project_description}")
    print("=" * 80)

    result = generator.generate_project(
        project_type, project_name, project_description)

    print("\n" + "="*80)
    print("PROJECT GENERATION SUMMARY")
    print("="*80)
    print(f"Project Name: {result['project_name']}")
    print(f"Project Type: {result['project_type']}")
    print(f"Generation Time: {result['generation_time_seconds']:.2f} seconds")
    print(f"Total Steps: {result['total_steps']}")
    print(f"Total Files Created: {result['total_files']}")
    print(f"Total Directories Created: {result['total_directories']}")

    print("\nDIRECTORIES CREATED:")
    for directory in result['directories_created']:
        print(f"- {directory}")

    print("\nFILES CREATED:")
    for file in result['files_created']:
        print(f"- {file}")

    print("\nPROJECT SUMMARY:")
    print(result['summary'])

    with open(f"{project_name}_generation_summary.json", "w") as f:
        json.dump(result, f, indent=2)

    print(
        f"\nDetailed generation summary saved to {project_name}_generation_summary.json")


if __name__ == "__main__":
    main()
