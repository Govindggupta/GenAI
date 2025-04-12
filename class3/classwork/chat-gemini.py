import json
from google import genai
from google.genai import types
import re
import os

client = genai.Client(api_key='AIzaSyBgDhIc9WWUuvsJUqcwvrqc5MjN5iUvwZ4')

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


response = client.models.generate_content(
    config=types.GenerateContentConfig(system_instruction=system_prompt),
    model='gemini-2.0-flash-001', 
    contents='tell me the weather of the city new york',
    

)
cleaned_text = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
try:
    parsed_output = json.loads(cleaned_text)
    print(parsed_output)
except json.JSONDecodeError:
    print("❌ Failed to parse response as JSON:", response.text)
    
    
    
while True: 
    user_query = input('> ')
    os.system(command=user_query)
    print(user_query)
    
    if (user_query == "exit"):
        break



