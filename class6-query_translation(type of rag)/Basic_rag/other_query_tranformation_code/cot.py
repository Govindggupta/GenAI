from openai import OpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

embedder = GoogleGenerativeAIEmbeddings(
    google_api_key=GEMINI_API_KEY,
    model="models/text-embedding-004"
)

def get_relevant_chunks(query):
    retriver = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="learning_langchain",
        embedding=embedder,
    )
    return retriver.similarity_search(query=query)

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

available_tools = {
    "get_relevant_chunks": {
        "fn": get_relevant_chunks,
        "description": "Get relevant chunks from the vector store"
    }
}


system_prompt = f"""
    you are a helpful ai assistant that answers the user query from the pdf content provided to you.
    You use the Query Decomposition technique (i.e., Chain of thought) to answer the user query.
    
    Things to follow:
    - All queries and actions must be relevant to the user query.
    - Output format should be in JSON only.
    - You create 3-5 queries according to the user query.
    
    Available functions:
    - get_relevant_chunks
    
    Output JSON format:
    {{
        "step" : "plan" | "query" | "action" | "observe" | "output",
        "content" : "string",
        "function" : "Name of the function if the step is action",
        "input" : "Input parameter for the function if the step is action"
    }}


"""

message = []
message.append({"role": "system", "content": system_prompt})
user_query = input(f"{Fore.BLUE} > {Style.RESET_ALL}")
# if (user_query == "exit") or (user_query == "quit"):
# break
message.append({"role": "user", "content": user_query})



response = client.chat.completions.create(
    model="gemini-2.0-flash",
    response_format={"type": "json_object"},
    messages=message
)

print(response.choices[0].message.content)

