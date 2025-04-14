import os
import subprocess
import json
import time
from pathlib import Path
import datetime
import stat
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# File and directory management functions from the previous example


def is_safe_path(path):
    """
    Validates if the path is within current working directory.

    Args:
        path (str): Path to validate

    Returns:
        bool: True if path is safe, False otherwise
    """
    # Get absolute paths for comparison
    path = os.path.abspath(path)
    cwd = os.path.abspath(os.getcwd())

    # Check if the path is within the current working directory
    return path.startswith(cwd)


def is_safe_command(command):
    """
    Checks if a command is safe to execute (no sudo).

    Args:
        command (str): Command to check

    Returns:
        bool: True if command is safe, False otherwise
    """
    # Check if command contains sudo
    if "sudo" in command.lower().split():
        return False
    return True


def read_file(filename):
    """
    Reads and returns the contents of a file in the current working directory.

    Args:
        filename (str): Name of the file to read

    Returns:
        str: Contents of the file if successful
        None: If file doesn't exist or isn't in the current directory
    """
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
    """
    Returns metadata for a file in the current working directory.

    Args:
        filename (str): Name of the file to get metadata for

    Returns:
        dict: Dictionary containing file metadata if successful
        None: If file doesn't exist or isn't in the current directory
    """
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

        # Convert timestamps to human-readable format
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        accessed_time = datetime.datetime.fromtimestamp(stat_info.st_atime)

        # Get file permissions
        perms = stat.filemode(stat_info.st_mode)

        metadata = {
            'name': file_path.name,
            'size': stat_info.st_size,  # Size in bytes
            'created': created_time,
            'modified': modified_time,
            'accessed': accessed_time,
            'permissions': perms,
            'is_directory': file_path.is_dir(),
            'is_file': file_path.is_file(),
            'absolute_path': file_path.absolute(),
        }

        return metadata
    except Exception as e:
        print(f"Error getting file metadata: {e}")
        return None


def list_directory_contents(directory="."):
    """
    Lists all files and directories in the specified directory.

    Args:
        directory (str): Directory to list contents from (defaults to current directory)

    Returns:
        dict: Dictionary with 'files' and 'directories' lists if successful
        None: If directory doesn't exist or isn't in the current working directory
    """
    if not is_safe_path(directory):
        print(
            f"Error: Directory '{directory}' is not in the current working directory.")
        return None

    try:
        # Get the absolute path of the directory
        abs_dir = os.path.abspath(directory)

        if not os.path.exists(abs_dir):
            print(f"Error: Directory '{directory}' not found.")
            return None

        if not os.path.isdir(abs_dir):
            print(f"Error: '{directory}' is not a directory.")
            return None

        # Lists to store files and directories
        files = []
        directories = []

        # Iterate through directory contents
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
    """
    Writes content to a file in the current working directory.

    Args:
        filename (str): Name of the file to write to
        content (str): Content to write to the file
        mode (str): Write mode ('w' for overwrite, 'a' for append)

    Returns:
        bool: True if writing was successful, False otherwise
    """
    if not is_safe_path(filename):
        print(
            f"Error: File '{filename}' is not in the current working directory.")
        return False

    try:
        # Create directories if they don't exist
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
    """
    Runs a terminal command in the current working directory, without sudo.

    Args:
        command (str): Command to run

    Returns:
        dict: Dictionary with 'stdout', 'stderr', and 'returncode' if successful
        None: If command contains sudo or other error occurs
    """
    if not is_safe_command(command):
        print("Error: Cannot run commands with 'sudo'.")
        return None

    try:
        # Run the command and capture output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()  # Ensure command runs in current working directory
        )

        # Get output
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
    """
    Creates a directory in the current working directory.

    Args:
        directory_name (str): Name of directory to create

    Returns:
        bool: True if creation was successful, False otherwise
    """
    if not is_safe_path(directory_name):
        print(
            f"Error: Directory '{directory_name}' is not in the current working directory.")
        return False

    try:
        # Create the directory
        os.makedirs(directory_name, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

# GPT-4o Integration for Project Generation


class ProjectGenerator:
    def __init__(self, api_key):
        """
        Initializes the project generator with OpenAI API key.

        Args:
            api_key (str): OpenAI API key
        """
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai"
        )
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads contents of a file in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to read"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_metadata",
                    "description": "Returns metadata for a file in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to get metadata for"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory_contents",
                    "description": "Lists all files and directories in the specified directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to list contents from (defaults to current directory)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_to_file",
                    "description": "Writes content to a file in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to write to"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            },
                            "mode": {
                                "type": "string",
                                "description": "Write mode ('w' for overwrite, 'a' for append)",
                                "enum": ["w", "a"]
                            }
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Runs a terminal command in the current working directory, without sudo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to run"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Creates a directory in the current working directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_name": {
                                "type": "string",
                                "description": "Name of directory to create"
                            }
                        },
                        "required": ["directory_name"]
                    }
                }
            }
        ]
        self.messages = []
        self.project_name = None

    def generate_readme(self, project_type, project_name, project_description, project_structure=None):
        """
        Generates or regenerates a README.md file for a project.

        Args:
            project_type (str): Type of the project (e.g., "MERN", "Django+React", etc.)
            project_name (str): Name of the project
            project_description (str): Detailed description of the project
            project_structure (dict, optional): Existing project structure information

        Returns:
            dict: Result of README generation
        """
        start_time = time.time()

        # Check if README.md already exists
        readme_exists = os.path.exists("README.md")

        # Initial prompt to GPT-4o
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert technical writer specialized in creating comprehensive README.md files "
                    "for software projects. Your task is to generate a professional README.md that follows "
                    "best practices and includes all standard sections such as project description, features, "
                    "installation, usage, API documentation (if applicable), technologies used, and contributing guidelines."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a detailed README.md for a {project_type} project named '{project_name}' "
                    f"with the following description:\n\n{project_description}\n\n"
                    f"Use proper Markdown formatting and follow industry best practices for "
                    f"structuring a README file. Include sections for prerequisites, installation, "
                    f"usage, API endpoints (if applicable), and contributing guidelines."
                )
            }
        ]

        # If we have project structure info, add it to the prompt
        if project_structure:
            dir_list = "\n".join(
                [f"- {d}" for d in project_structure.get("directories_created", [])])
            file_list = "\n".join(
                [f"- {f}" for f in project_structure.get("files_created", [])])

            structure_prompt = (
                f"\n\nThis project has the following structure:\n\nDirectories:\n{dir_list}\n\n"
                f"Files:\n{file_list}\n\nPlease incorporate this structure information into "
                f"the README.md where appropriate, especially in the installation and usage sections."
            )

            messages[1]["content"] += structure_prompt

        try:
            # Get response from GPT-4o
            response = self.client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=messages
            )

            # Get the README content
            readme_content = response.choices[0].message.content

            # Write to README.md
            success = write_to_file("README.md", readme_content)

            end_time = time.time()
            duration = end_time - start_time

            return {
                "success": success,
                "readme_existed": readme_exists,
                "content": readme_content,
                "generation_time_seconds": duration
            }

        except Exception as e:
            print(f"Error generating README: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_tool_calls(self, tool_calls):
        """
        Handles tool calls from GPT-4o responses.

        Args:
            tool_calls (list): List of tool calls from the model

        Returns:
            list: List of tool responses
        """
        tool_responses = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            response_content = None

            if function_name == "read_file":
                response_content = read_file(function_args.get("filename"))

            elif function_name == "get_file_metadata":
                metadata = get_file_metadata(function_args.get("filename"))
                # Convert datetime objects to strings for JSON serialization
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, datetime.datetime):
                            metadata[key] = value.isoformat()
                        elif isinstance(value, Path):
                            metadata[key] = str(value)
                response_content = metadata

            elif function_name == "list_directory_contents":
                response_content = list_directory_contents(
                    function_args.get("directory", "."))

            elif function_name == "write_to_file":
                success = write_to_file(
                    function_args.get("filename"),
                    function_args.get("content"),
                    function_args.get("mode", "w")
                )
                response_content = {"success": success}

            elif function_name == "run_command":
                result = run_command(function_args.get("command"))
                response_content = result

            elif function_name == "create_directory":
                success = create_directory(function_args.get("directory_name"))
                response_content = {"success": success}

            tool_responses.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(response_content)
            })

        return tool_responses

    def generate_project(self, project_type, project_name, project_description):
        """
        Generates a fullstack project based on the provided specifications.

        Args:
            project_type (str): Type of the project (e.g., "MERN", "Django+React", etc.)
            project_name (str): Name of the project
            project_description (str): Detailed description of the project

        Returns:
            dict: Project generation summary
        """
        self.project_name = project_name
        start_time = time.time()

        # Initial prompt to GPT-4o
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert fullstack developer assistant capable of generating complete project structures. "
                    "You have access to tools that can create directories, write files, and run commands "
                    "to set up a complete project structure. "
                    "Focus on creating a well-organized, production-ready project structure with proper files and content. "
                    "You must work only within the current directory and cannot use sudo commands. "
                    "When creating files, include proper content that would be expected in a professional project. "
                    "Be systematic and thorough in your approach."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a complete {project_type} project named '{project_name}' with the following description: {project_description}\n\n"
                    f"Please create the directory structure, all necessary files with appropriate content, "
                    f"and include configuration files, code files, and documentation. "
                    f"Work step by step to build a production-ready project structure."
                )
            }
        ]

        # Track all actions taken
        actions_taken = []
        generated_files = []
        generated_dirs = []

        max_steps = 25  # Limit the number of steps to prevent infinite loops
        step = 0

        print(f"Starting project generation for {project_name}...")
        print(f"Type: {project_type}")
        print(f"Description: {project_description}")
        print("=" * 80)

        while step < max_steps:
            step += 1
            print(f"\nStep {step} of project generation process:")

            try:
                # Get response from GPT-4o
                response = self.client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=self.messages,
                    tools=self.available_tools,
                    tool_choice="auto"
                )

                # Get the response message
                response_message = response.choices[0].message

                # Add the response to messages
                self.messages.append(response_message.model_dump())

                # Check if the response contains tool calls
                if response_message.tool_calls:
                    print(
                        f"- Processing {len(response_message.tool_calls)} tool calls...")

                    # Handle the tool calls
                    tool_responses = self._handle_tool_calls(
                        response_message.tool_calls)

                    # Track actions
                    for tool_call, tool_response in zip(response_message.tool_calls, tool_responses):
                        function_name = tool_call.function.name
                        function_args = json.loads(
                            tool_call.function.arguments)

                        if function_name == "create_directory":
                            generated_dirs.append(
                                function_args.get("directory_name"))
                            print(
                                f"  Created directory: {function_args.get('directory_name')}")

                        elif function_name == "write_to_file":
                            filename = function_args.get("filename")
                            generated_files.append(filename)
                            print(f"  Created file: {filename}")

                        actions_taken.append({
                            "step": step,
                            "action": function_name,
                            "args": function_args,
                            "result": json.loads(tool_response["output"])
                        })

                    # Add individual tool responses to messages
                    for tool_response in tool_responses:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_response["tool_call_id"],
                            "content": tool_response["output"]
                        })
                else:
                    print(
                        f"- Assistant message: {response_message.content[:100]}...")

                    # Check if the project generation is complete
                    if "project generation is complete" in response_message.content.lower() or "project structure is now complete" in response_message.content.lower():
                        print(
                            "\nProject generation marked as complete by the assistant.")
                        break

                    # Ask for the next step
                    self.messages.append({
                        "role": "user",
                        "content": "Please continue with the next steps to complete the project structure."
                    })

            except Exception as e:
                print(f"Error during project generation: {e}")
                actions_taken.append({
                    "step": step,
                    "error": str(e)
                })
                break

        # Get the final summary of the project
        self.messages.append({
            "role": "user",
            "content": "Provide a summary of what you've created including the project structure, files, and key features."
        })

        summary_response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=self.messages
        )

        summary = summary_response.choices[0].message.content

        end_time = time.time()
        duration = end_time - start_time

        # Return the project generation summary
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
    """
    Main function that takes input from the terminal and runs the generator.
    """
    print("=" * 80)
    print("GPT-4o PROJECT GENERATOR")
    print("=" * 80)
    print("This tool will generate a complete project structure based on your specifications.")
    print("Please provide the following information:")
    print()

    # Get project type
    project_type = input(
        "Enter project type (e.g., MERN Stack, Django+React): ").strip()

    # Get project name
    project_name = input("Enter project name: ").strip()

    # Get project description (multiline input)
    print("\nEnter project description (type 'END' on a new line when finished):")
    project_description_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        project_description_lines.append(line)

    project_description = "\n".join(project_description_lines)

    # Get the OpenAI API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set this variable in a .env file or directly in your environment.")
        return

    # Create the project generator
    generator = ProjectGenerator(api_key)

    print(f"\nStarting project generation for {project_name}...")
    print(f"Type: {project_type}")
    print(f"Description: {project_description}")
    print("=" * 80)

    # Generate the complete project
    result = generator.generate_project(
        project_type, project_name, project_description)

    # Print summary
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

    # Save the project summary to a file
    with open(f"{project_name}_generation_summary.json", "w") as f:
        json.dump(result, f, indent=2)

    print(
        f"\nDetailed generation summary saved to {project_name}_generation_summary.json")


if __name__ == "__main__":
    main()
