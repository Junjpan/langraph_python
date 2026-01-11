from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


load_dotenv()

llm=init_chat_model("claude-haiku-4-5-20251001", temperature=0)

# define the State type
class State(TypedDict):
    messages: Annotated[list, add_messages] #add_message is a reducer that helps manage chat messages
    # message_type: str| None

# Allow LangGraph to build a graph based on the State type
graph_builder = StateGraph(State)

# define the node function
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# register the node function with the graph builder
graph_builder.add_node('chatbot', chatbot)

graph_builder.add_edge(START, 'chatbot')
graph_builder.add_edge('chatbot', END)

graph=graph_builder.compile()

state = {"messages": []}  # Initialize persistent state outside the loop

while True:
    user_input=input("Enter your message (or 'quit' to exit): ")
    if user_input.lower() == 'quit':
        print("Goodbye!")
        break

    #get a new state after the invoke
    state=graph.invoke({"messages": state["messages"] + [("user", user_input)]}) # in python, put a two list togehter we can use + operator or [*list1, *list2]
    
    # Extract and display the assistant's response in readable format
    messages = state["messages"]
    if messages:
        last_message = messages[-1]
        print("Debug - Last message object:", last_message)  # Debugging line
        if hasattr(last_message, 'content'):
            assistant_response = last_message.content
        else:
            assistant_response = str(last_message)
        
        print("\n" + "="*60)
        print("Assistant:", assistant_response)
        print("="*60 + "\n")
    
    # Display last 10 chat history
    print("\n--- Last 10 Messages ---")
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    for msg in recent_messages:
        if hasattr(msg, 'content'):
            content = msg.content
            role = msg.type if hasattr(msg, 'type') else 'unknown'
        else:
            content = str(msg)
            role = 'unknown'
        print(f"{role}: {content}")
    print("------------------------\n")
