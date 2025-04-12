import json
from google import genai
from google.genai import types
import re
import os
import requests

client = genai.Client(api_key='AIzaSyBgDhIc9WWUuvsJUqcwvrqc5MjN5iUvwZ4')

def get_weather(city): 
    print("tool called get weather")
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"

available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city"
    }
}

system_prompt = f"""
    You are a AI agent who is specialized in solving user queries.
    You work on start, plan, action, observe mode.
    for the given user queries and available tools , plan the step by step execution, based on the planning, select the relavant tool from the available tool . and based on the tool selection you perform an action to call the tool. 

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}  
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""


# response = client.models.generate_content(
#     config=types.GenerateContentConfig(system_instruction=system_prompt),
#     model='gemini-2.0-flash-001', 
#     contents=[
#         'tell me the weather of the city new york',
#         json.dumps({'step': 'plan', 'content': 'The user is asking for the weather in New York City.'}), 
#         json.dumps({'step': 'plan', 'content': 'I should use the get_weather tool to find the weather.'}),
#         json.dumps({'step': 'action', 'function': 'get_weather', 'input': 'new york'}),
#         json.dumps({'step': 'observe', 'output': 'The current weather in New York is 15 degrees Celsius and sunny.'}),
#         json.dumps({'step': 'output', 'content': 'The current weather in New York is 15 degrees Celsius and sunny.'})
#         ],
    

# )
# cleaned_text = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
# try:
#     parsed_output = json.loads(cleaned_text)
#     print(parsed_output)
# except json.JSONDecodeError:
#     print("❌ Failed to parse response as JSON:", response.text)

# rather than writting this again and again , we make it in a loop which keeps on taking the output till final steps is achieved
while True:

        
    messages = []
    query = input('> ')
    if(query == "exit"):
        break
    messages.append(json.dumps({'step' : 'query', 'content' : query}))

    while True: 
        response = client.models.generate_content(
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            model='gemini-2.0-flash-001',
            contents=messages,
        )
        cleaned_text = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
        try: 
            parsed_output = json.loads(cleaned_text)
            messages.append(json.dumps(parsed_output))
        except json.JSONDecodeError:
            print("❌ Failed to parse response as JSON:", response.text)
            
            
        if parsed_output.get("step") == "plan": 
            print(f"🧠: {parsed_output.get('content')}")
            continue
        
        if parsed_output.get("step") == "action": 
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            
            if available_tools.get(tool_name, False) != False: 
                output = available_tools[tool_name].get("fn")(tool_input)
                messages.append(json.dumps({"step": "observe", "output":  output}))
                continue
            
        if parsed_output.get("step") == "output": 
            print(f"🤖: {parsed_output.get('content')}")
            break

            
        
            
            
        
        
    
# while True: 
#     user_query = input('> ')
#     os.system(command=user_query)
#     print(user_query)
    
#     if (user_query == "exit"):
#         break



