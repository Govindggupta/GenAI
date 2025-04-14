import os
import re
import json
from colorama import Fore, Style
from dotenv import load_dotenv
from google import genai

#success = green 
#error = red 
#warning = yellow
#output = blute

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

#to run the command in the terminal
def run_command(command):
    os.system(command=command)
    return True

#takes any directoy name , i.e, hello or hello/world/test/wow
def create_directory(directory_name):
    try: 
        os.makedirs(directory_name, exist_ok=True)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating directory: {e}{Style.RESET_ALL}")
        return False    
    
def write_to_file(filename, content, mode="w"):
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, mode) as file:
            file.write(content)
        return True
    except Exception as e:    
        print(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")
        return False        
    

available_tools = {
    "run_command": {
        "fn": run_command, 
        "description" : "Runs a terminal command in the current working directory, without sudo. Input: {'command': 'string'}"
    },
    "create_directory": {
        "fn": create_directory, 
        "description" : "Creates a directory in the current working directory. Input: {'directory_name': 'string'}"
    },
    "write_to_file": {
        "fn": write_to_file, 
        "description" : "Writes content to a file in the current working directory. Input: {'filename': 'string', 'content': 'string', 'mode': 'w|a'}"
    }
}

system_prompt = f"""
    You are an expert fullstack developer assistant capable of generating complete project structures.
    you have access to tools that can create directories, write files, and run commands.
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
    - run_command
    - create_directory
    - write_to_file
    
    Example: 
    User_query : create me a react application with a signup and login page 
    Output : {{'step' : 'plan', 'content' : 'user want me to creat a react application with a signup and login page'}}
    Output : {{'step' : 'action', 'function': 'create_directory', 'input': 'react-app'}}
    output : {{'step' : 'observe', 'output': 'Directory created successfully'}}
    output : {{'step' : 'action', 'function': 'run_command', 'input': 'cd react-app && npm create vite@latest'}}
    
    output : {{'step': 'action', 'function': 'run_command', 'input': 'npm install react-router-dom'}}
    output : {{'step': 'observe', 'output': 'Installed react-router-dom'}}
    output : {{ 'step': 'action', 'function': 'run_command', 'input': 'npm install tailwindcss @tailwindcss/vite'}}
    output : {{'step': 'observe', 'output': 'Installed tailwindcss'}}
    output : {{'step': 'action', 'function': 'write_to_file', 'input' : ' content: '@tailwind base;\n@tailwind components;\n@tailwind utilities;'}}
    output : {{'step': 'observe', 'output': 'Tailwind CSS configured'}}
    output : {{'step': 'action', 'function': 'write_to_file', 'input' : 'contned}}
    

"""
while True:
        
    messages = []
    user_query = input(F"{Fore.LIGHTMAGENTA_EX} > {Style.RESET_ALL}")
    messages.append(json.dumps({"role": "user", "content": user_query}))

    while True: 
        response = client.models.generate_content(
            # system prompt
            config=genai.types.GenerateContentConfig(system_instruction=system_prompt),
            model="gemini-2.0-flash",
            contents=messages,
        )

        #this is used to convert the response into the perfect json format. 
        cleaned_text = re.sub(r"^```json|```$", "",response.text.strip(), flags=re.MULTILINE).strip()
        try:
            parsed_output = json.loads(cleaned_text)
        except json.JSONDecodeError:
            print(f"\033[91m❌ Failed to parse response as JSON: {response.text}\033[0m")


        if parsed_output.get("step") == "plan":
            messages.append(json.dumps(parsed_output))
            print(f"{Fore.BLUE}{parsed_output}{Style.RESET_ALL}")
            continue
        
        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            
            if tool_name in available_tools:
                print(f"{Fore.BLUE}{parsed_output}{Style.RESET_ALL}")
                output = available_tools[tool_name]["fn"](tool_input)
                messages.append(json.dumps({"step": "observe", "output": output}))
                continue
            
        if parsed_output.get("step") == "observe":
            print(f"{Fore.GREEN}{parsed_output}{Style.RESET_ALL}")
            continue
        
        if parsed_output.get("step") == "output":
            print(f"{Fore.GREEN}{parsed_output}{Style.RESET_ALL}")
            break
        
        