from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from colorama import Fore, Style
import json

embedder = GoogleGenerativeAIEmbeddings(
    google_api_key="gemini_api_key", model="models/text-embedding-004")


def get_relevant_chunks(query):
    # code to get relevant chunks from the vector store

    retriver = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="learning_langchain",
        embedding=embedder,
    )

    return retriver.similarity_search(
        query=query,
    )

# search_results = get_relevant_chunks("what is nodejs exactly? ")

# print(f"{Fore.GREEN} {search_results} {Style.RESET_ALL}")


client = OpenAI(
    api_key="gemini_api_key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

available_tools = {
    "get_relevant_chunks": {
        "fn": get_relevant_chunks,
        "description": "Get relevant chunks from the vector store"
    }
}

system_prompt = f"""
    You are a helpful AI assistant that answers user query from the pdf provided to you . 
    You are given a context of the document and answer is extracted from the context.
    Answer the user query as best as you can. If you are not sure about the answer, answer with saying "I don't know".
    
    Things to follow : 
    - output format should be in the json format only. 
    - you also tell the page number that where user should look for the answer.
    
    Output json format : 
        {{
            "step" : "plan"|"action"|"observe"|"output",
            "content" : "string",
            "function" : "Name of the function if the step is action",
            "input" : "Input parameter for the function if the step is action"
        }}
        
    available functions : 
    -get_relevant_chunks
    
    Example:
    User Query: What is the FS module?
    Output: {{ "step": "plan", "content": "The user is asking about Node.js FS module" }}
    Output: {{ "step": "plan", "content": "I should function get_relevant_chunks" }}
    Output: {{ "step": "action", "function": "get_related_chunks", "input": "what is the FS module?" }}
    Output: {{ "step": "observe", "output": "..." }}
    Output: {{ "step": "output", "content": "The FS module allows working with the file system..." }}
"""

while True:

    message = []
    message.append({"role": "system", "content": system_prompt})
    user_query = input(f"{Fore.BLUE} > {Style.RESET_ALL}")
    message.append({"role": "user", "content": user_query})

    while True:

        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            messages=message
        )

        parsed_output = json.loads(response.choices[0].message.content)
        message.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"{Fore.GREEN} {parsed_output.get('content')} {Style.RESET_ALL}")
            continue

        if parsed_output.get("step") == "action":

            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if tool_name in available_tools:
                result = available_tools[tool_name]["fn"](tool_input)
                print(f"{Fore.GREEN} {Style.DIM} {result} {Style.RESET_ALL}")

                result_serializable = [
                    {
                        "content": doc.page_content,
                        # includes page, author, source file, etc.
                        "metadata": doc.metadata
                    }
                    for doc in result
                ]

                message.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "step": "observe",
                        "output": result_serializable
                    })
                })
                continue

        if parsed_output.get("step") == "output":
            print(
                f"{Fore.BLUE} Your final Output : {parsed_output.get('content')} {Style.RESET_ALL}")
            break
