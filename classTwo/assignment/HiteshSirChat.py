from google import genai
from google.genai import types

client = genai.Client(api_key='AIzaSyBZOD1sCNjkSpXKpCipMJcDpnU_xl5rUb4')

with open("System.txt" , "r", encoding="utf-8") as file:
    system_prompt = file.read()

response = client.models.generate_content(
    config=types.GenerateContentConfig(system_instruction=system_prompt),
    model='gemini-2.0-flash-001', contents='tamme koi piyush nam ke bande ko jante ho ?'
)
print(response.text)