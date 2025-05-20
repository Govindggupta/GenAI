from mem0 import Memory
from openai import OpenAI
from colorama import Fore, Style

OPENAI_API_KEY = "sk-proj-oLTALbCqFOkKiehWtHIwZIcdjE7McASdZmJQghvh4OHHeMmH4hnGlE0JGRahUdcdvelWR0tkA"

QUADRANT_HOST = "localhost"

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"},
    },
    "llm": {"provider": "openai", "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": NEO4J_URL, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    },
}


mem_client = Memory.from_config(config)

OpenAI_client = OpenAI(api_key=OPENAI_API_KEY)


def chat(message):

    mem_result = mem_client.search(query=message, user_id="1234")
    print(f'{Fore.MAGENTA}{Style.DIM} mem : {mem_result} {Style.RESET_ALL}')

    memories = "\n".join([m["memory"] for m in mem_result.get("results")])

    print(f'{Fore.BLUE}{Style.DIM} memories : {memories} {Style.RESET_ALL}')

    SYSTEM_PROMPT = f"""You are a helpful assistant that answers questions based on the provided context.
    Memory and it's score : {memories}
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]
    response = OpenAI_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )

    messages.append(
        {"role": "assistant", "content": response.choices[0].message.content})

    mem_client.add(messages, user_id="1234")

    return response.choices[0].message.content


while True:
    user_input = input(">> ")
    if (user_input.lower() == "exit"):
        break
    response = chat(user_input)
    print("Bot:", response)
