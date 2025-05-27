from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END

load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")    

client = OpenAI()

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

def detect_query(state: State):
    user_message = state.get("user_messsage")
    
    #openai call
    
    state.is_coding_question = True
    return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

def solve_coding_question(state: State): 
    user_message = state.get("user_messsage")
    
    #openai call
    state.ai_message = "I solved the coding question"
    return state

def solve_simple_question(state: State):
    user_message = state.get("user_messsage")
    
    #openai call
    state.ai_message = "I solved the simple question"
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_edge("detect_query", route_edge)

graph_builder.add_conditional_edges("route_edge", "solve_coding_question")
graph_builder.add_conditional_edges("route_edge", "solve_simple_question")

graph_builder.add_edge("solve_coding_questioni", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()



#user the graph 

def call_graph():
    state = {
        "user_message": "What is the capital of France?",
        "ai_message": "",
        "is_coding_question": False
    }
    result = graph.invoke(state)
    print(result)

    
call_graph()