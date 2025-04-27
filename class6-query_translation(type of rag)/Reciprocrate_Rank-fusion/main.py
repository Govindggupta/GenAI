from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from colorama import Fore, Style
import json

embedder = GoogleGenerativeAIEmbeddings(
    google_api_key="gemini_api_key",
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
    You are a helpful ai assistant that answers the user query from the pdf content provided to you.
    You use the Reciprocate Rank fusion test technique (i.e., rrf) to answer the user query.

    Things to follow:
    - All queries and actions must be relevant to the user query.
    - Output format should be in JSON only.
    - You create 3 for the user query entered. 
    - You analyze the chunks and then answer the question using the chunks and descriptive if required.
    
    Available functions:
    - get_relevant_chunks

    Output JSON format:
    {{
        "step" : "plan" | "query" | "action" | "observe" | "output",
        "content" : "string",
        "function" : "Name of the function if the step is action",
        "input" : "Input parameter for the function if the step is action"
    }}

    Example:

    user_query: what is nodejs?
    output:
    {{"step" : "plan" , "content": "User is asking about the nodejs"}}
    {{"step" : "query" , "content": ["What is Node.js?", "How does Node.js work?", "What are the benefits of using Node.js?"]}}
    {{"step" : "action" , "function": "get_relevant_chunks", "input": ["query1", "query2", "query3"]}}
    {{"step" : "observe", "output": [...]}}
    {{"step" : "output", "content": "..."}}
"""

while True:
    message = []
    multiple_query = []

    message.append({"role": "system", "content": system_prompt})
    user_query = input(f"{Fore.BLUE} > {Style.RESET_ALL}")
    if (user_query == "exit") or (user_query == "quit"):
        break
    message.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            messages=message
        )

        parsed_output = json.loads(response.choices[0].message.content)
        message.append({"role": "assistant", "content": json.dumps(parsed_output)})

        step = parsed_output.get("step")

        if step == "plan":
            continue

        if step == "query":
            multiple_query = parsed_output.get("content")
            print(f"{Fore.GREEN}Query Variations: {multiple_query}{Style.RESET_ALL}")
            continue

        if step == "action":
            tool_name = parsed_output.get("function")
            print(f"{Fore.YELLOW}Tool Invoked: {tool_name}{Style.RESET_ALL}")

            if tool_name in available_tools:
                all_results = []  
                
                for query in multiple_query:
                    result = available_tools[tool_name]["fn"](query)
                    all_results.append(result)  
                
                # ---- RRF Fusion Start ----
                k = 60  
                scores = {}
                doc_objects = {} 
                
                for result_list in all_results:
                    for rank, doc in enumerate(result_list):
                        key = doc.page_content.strip()
                        if key not in doc_objects:
                            doc_objects[key] = doc
                        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
                
                # Sort by scores
                sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                for i in range(len(sorted_docs)):
                    print(f"{Fore.MAGENTA} {sorted_docs[i]} {Style.RESET_ALL}")
                    print('......')
                
                
                chunk_summaries = []
                for content, _ in sorted_docs:
                    doc = doc_objects[content]
                    chunk_summaries.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    })
                # ---- RRF Fusion End ----
                
                message.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "step": "observe",
                        "output": chunk_summaries
                    })
                })

                print(f"{Fore.GREEN} {Style.DIM}Observed Chunks: {json.dumps(chunk_summaries, indent=2)}{Style.RESET_ALL}")
                continue

            
        if step == "output":
            print(f"{Fore.BLUE}Final Output: {parsed_output.get('content')}{Style.RESET_ALL}")
            break
        
