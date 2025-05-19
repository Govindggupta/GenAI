# from mem0 import Memory
from openai import OpenAI

# GEMINI_API_KEY = "AIzaSyBfbdVV0YNmWCK2p5q_qnWzKHwdMlu0T5s"

# QUADRANT_HOST = "localhost"

# NEO4J_URL = "bolt://localhost:7687"
# NEO4J_USERNAME = "neo4j"
# NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"

# config = {
#     "version": "v1.1",
#     "embedder": {
#         "provider": "google",
#         "config": {
#             "api_key": GEMINI_API_KEY,
#             "model": "models/text-embedding-004"  # Gemini embedding model
#         },
#     },
#     "llm": {
#         "provider": "google",
#         "config": {
#             "api_key": GEMINI_API_KEY,
#             "model": "gemini-2.0-flash"  # Gemini LLM
#         },
#     },
#     "vector_store": {
#         "provider": "qdrant",
#         "config": {
#             "host": QUADRANT_HOST,
#             "port": 6333,
#         },
#     },
#     "graph_store": {
#         "provider": "neo4j",
#         "config": {
#             "url": NEO4J_URL,
#             "username": NEO4J_USERNAME,
#             "password": NEO4J_PASSWORD,
#         },
#     },
# }

# mem_client = Memory.from_config(config)

OpenAI_client = OpenAI(
    api_key="AIzaSyD1MkJaYvnWoh5EG2dzb8pvkcmNQwtMcIw",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def chat(message):
    messages = [{"role": "user", "content": message}]

    response = OpenAI_client.chat.completions.create(
        model="gemini-2.0-flash",
        response_format={"type": "json_object"},
        messages=messages
    )

    messages.append({"role": "assistant", "content": response.choices[0].message.content})

    return response.choices[0].message.content


while True:
    user_input = input(">> ")
    response = chat(user_input)
    print("Bot:", response)
