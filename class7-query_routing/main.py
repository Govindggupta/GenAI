print("hello world")

from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

def llm_router(query):
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )

    system_prompt = f"""
        you are a helpfull ai assistant which tells the type of the user query which is entered by the user. 
        you check the user query and tell weather the query is about . 
        
        Type of the query : 
        1. coding 
        2. research 
        3. talking
        4. roasting 

        Things to be considered : 
        - output format should be in json 
        
        Output Format : 
        {{ "type" : "<type of the query>"}}
    """

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            { "role": "user", "content": query },
        ]
    )

    parsed_output = json.loads(response.choices[0].message.content)

    if parsed_output["type"] == "coding":
        return {"type" : "coding", "llm" : "gpt-4.5-turbo"}
    elif parsed_output["type"] == "research":
        return {"type" : "research", "llm" : "deepseek"}
    elif parsed_output["type"] == "talking":
        return {"type" : "talking", "llm" : "gpt-4o-mini"}
    elif parsed_output["type"] == "roasting":
        return {"type" : "roasting", "llm" : "grok"}
    else:
        return {"type" : "unknown", "llm" : "gpt-4o-mini"}    
        
        
def main():
    while True: 
        query = input("Enter your query : ")
        if query == "exit":
            break
        print(llm_router(query))
        print("\n")
        
        
if __name__ == "__main__":
    main()
    
# This is the basic application the logical routing in which you return the llm to be used according to the user query and then do the further steps according to the output of the llm.