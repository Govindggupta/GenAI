import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedder():
    return GoogleGenerativeAIEmbeddings(
        google_api_key="AIzaSyBfbdVV0YNmWCK2p5q_qnWzKHwdMlu0T5s",
        model="models/text-embedding-004",
    )

def get_retriever(qdrant_url: str, collection_name: str):
    embedder = get_embedder()
    return QdrantVectorStore.from_existing_collection(
        url=qdrant_url,
        collection_name=collection_name,
        embedding=embedder,
    )

def ask_nodejs_doc(query: str) -> str:
    retriever = get_retriever("http://localhost:6333", "basic_rag")
    results = retriever.similarity_search(query=query)

    if not results:
        return (
            "Sorry, I couldn't find anything related to your query in the Node.js docs."
        )

    response = "Here's what I found in the Node.js documentation:\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. {result.page_content.strip()}\n\n"

    return response.strip()



client = OpenAI(
    api_key="gemini_api_key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

available_tools = {
    "ask_nodejs_doc": {
        "fn": ask_nodejs_doc,
        "description": "Takes a question about Node.js and returns relevant documentation info",
    },
}

system_prompt = f"""
You are a helpful AI Assistant specialized in resolving queries using available tools.

You work step-by-step: plan → action → observe → output.

Available Tools:
- ask_nodejs_doc: Takes a question about Node.js and returns related answers from docs.

Output JSON Format:
{{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
}}

Example:
User Query: What is the FS module?
Output: {{ "step": "plan", "content": "The user is asking about Node.js FS module" }}
Output: {{ "step": "plan", "content": "I should use ask_nodejs_doc" }}
Output: {{ "step": "action", "function": "ask_nodejs_doc", "input": "What is FS module?" }}
Output: {{ "step": "observe", "output": "..." }}
Output: {{ "step": "output", "content": "The FS module allows working with the file system..." }}
"""
messages = [{"role": "system", "content": system_prompt}]

while True:
    user_query = input("> ")
    if user_query.strip().lower() == "clear":
        break
    messages.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            n=1,
            messages=messages,
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get('content')}")
            continue

        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if tool := available_tools.get(tool_name):
                result = tool["fn"](tool_input)
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"step": "observe", "output": result}),
                    }
                )
                continue

        if parsed_output.get("step") == "output":
            print(f"\n🤖 Final Answer:\n{parsed_output.get('content')}\n")
            break