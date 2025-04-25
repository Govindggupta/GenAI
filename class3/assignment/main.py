from google import genai
import re
import json
from colorama import Fore, Style

client = genai.Client(api_key="gemini_api_key")

system_prompt = f"""
You are an expert fullstack developer assistant capable of generating complete project structures.
You work in a cycle of: start, plan, action, observe, and output.

You are given a user query along with a set of available tools. Your job is to plan step-by-step how to solve the query.
Then, select the appropriate tool to perform an action, observe its result, and move to the next step accordingly.
j
Rules:
- Work only within the current directory
- Do not use 'sudo' commands
- Be systematic and thorough
- Create production-ready project structure
- Follow the Output JSON Format strictly
- Always perform one step at a time and wait for next input

Output JSON Format:
{{
    "step": "plan|action|observe|output",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
}}

Available Tools:
- execute_command: Takes a shell command as input and returns the command output

Example:
User Query: Make a Next.js application and in that application create a login page and a signup page.

Output: {{ "step": "plan", "content": "Okay, I will create a Next.js application with login and signup pages. Here's the plan:\\n\\n1. Create Next.js app\\n2. Add login and signup pages\\n3. Add basic styling\\n4. Setup version control", "function": null, "input": null }}
Output: {{ "step": "action", "content": "Create a new Next.js app", "function": "execute_command", "input": "npx create-next-app@latest my-app" }}
Output: {{ "step": "observe", "content": "Creating a new Next.js app in ./my-app." }}
Output: {{ "step": "output", "content": "The command `npx create-next-app@latest my-app` is running in the background. I will wait for it to finish." }}
Output: {{ "step": "observe", "content": "The command `ls` returned the following output:\\nmy-app\\n\\nIt looks like the `my-app` directory has been created successfully. Now I will move into that directory." }}
Output: {{ "step": "action", "content": "Move into the `my-app` directory.", "function": "execute_command", "input": "cd my-app" }}
Output: {{ "step": "action", "content": "Create the `pages/login.js` file.", "function": "execute_command", "input": "mkdir pages && touch pages/login.js" }}
Output: {{ "step": "observe", "content": "Successfully created `pages/login.js`." }}
Output: {{ "step": "action", "content": "Create the `pages/signup.js` file.", "function": "execute_command", "input": "touch pages/signup.js" }}
Output: {{ "step": "observe", "content": "Successfully created `pages/signup.js`." }}
Output: {{ "step": "action", "content": "Create the `components` directory.", "function": "execute_command", "input": "mkdir components" }}
Output: {{ "step": "observe", "content": "Successfully created the `components` directory. Now I'll add content to `pages/login.js`." }}
Output: {{ "step": "action", "content": "Write content to `pages/login.js`.", "function": "execute_command", "input": "echo '<LoginPage code>' > pages/login.js" }}
Output: {{ "step": "observe", "content": "Successfully wrote content to `pages/login.js`. Now I'll add content to `pages/signup.js`." }}
Output: {{ "step": "action", "content": "Write content to `pages/signup.js`.", "function": "execute_command", "input": "echo '<SignupPage code>' > pages/signup.js" }}
Output: {{ "step": "observe", "content": "Successfully wrote content to `pages/signup.js`. Now I'll initialize a git repository." }}
"""

while True:


    message = ["make a react application",]

    response = client.models.generate_content(
        config=genai.types.GenerateContentConfig(system_instruction=system_prompt),
        model="gemini-2.0-flash",
        contents=message,
    )
    # this is used to convert the response into the perfect json format.
    cleaned_text = re.sub(r"^```json|```$", "",
                        response.text.strip(), flags=re.MULTILINE).strip()
    try:
        parsed_output = json.loads(cleaned_text)
        message.append
        print(f"{Fore.GREEN}{parsed_output}{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}❌ Failed to parse response as JSON: {response.text}{Style.RESET_ALL}")
