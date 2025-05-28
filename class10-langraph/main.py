from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
import time
from langsmith.wrappers import wrap_openai
from pydantic import BaseModel

load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")    

client = wrap_openai(OpenAI())

class DetectCallResponse(BaseModel):
    is_question_ai: bool
    
class AiResponse(BaseModel):
    ai_message: str
    

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

def detect_query(state: State):
    
    user_message = state.get("user_message")
    
    
    SYSTEM_PROMPT = """
    Your task is to determine whether the user's query is a coding-related question.
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=DetectCallResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    
    
    
    state["is_coding_question"] = result.choices[0].message.parsed.is_question_ai
    return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

def solve_coding_question(state: State): 
    user_message = state.get("user_message")
    
    #openai call
    SYSTEM_PROMPT = """
    your task is to solve the simple question of the user. 
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=AiResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    
    
    #openai call
    state["ai_message"] = result.choices[0].message.parsed.ai_message
    return state

def solve_simple_question(state: State):
    user_message = state.get("user_message")
    
    SYSTEM_PROMPT = """
    your task is to solve the simple question of the user. 
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=AiResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    
    
    #openai call
    state["ai_message"] = result.choices[0].message.parsed.ai_message
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)


graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

#user the graph 

def call_graph():
    state = {
        "user_message": "explain me about pydantic in python",
        "ai_message": "",
        "is_coding_question": False
    }
    print(state["is_coding_question"])
    result = graph.invoke(state)
    print(result)

    
call_graph()
time.sleep(5)