from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


load_dotenv()

llm=init_chat_model("claude-haiku-4-5-20251001", temperature=0)

# define the State type, used for runtime state management in LangGraph
# add context-specific metadata to a type. Annotated Type allows you to attach metadata to a type.
# to accept TypeDict data, we only can use squre bracket or using .get method to access the value, .get() method also accepts an optional second argument to provide a default value if the key is not found.
class State(TypedDict):
    messages: Annotated[list, add_messages] #add_message is a reducer that helps manage chat messages
    message_type: str| None

# used to classify user messages output by the LLM, ... means required field without default value, Literal limits the field to specific string values
# we always use pydantic BaseModel to define LLM output structure/schema, and the model will use the description to better understand the field purpose and generate more accurate output
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ..., description="Classifiy if the message requires an emotional (therapist-like) response or a logical (fact-based) response"
    )

def classify_message(state: State) :
    last_message=state["messages"][-1]
    classifier_output=llm.with_structured_output(MessageClassifier)
    result=classifier_output.invoke([{
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {"role": "user", "content": last_message.content}])
    
    # whatever we return here will be merged into the State that matches the State type
    return {'message_type': result.message_type}

# we are still able to get the 'next_node' field even it's not defined in the State type, it's ok to not define all the fields in the State type.
def router(state: State):
    message_type=state.get("message_type")
    if message_type=="emotional":
        return {'next_node': 'therapist'}
    return {'next_node': 'logical'}

def therapist_agent(state: State):
    message_history=state["messages"][-5:] if len(state["messages"]) > 5 else state["messages"] 
    message=[{
        "role": "system",
        "content":"""You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
    }] + message_history
    reply=llm.invoke(message)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    message_history=state["messages"][-5:] if len(state["messages"]) > 5 else state["messages"]  
    message=[{
        "role": "system",
        "content":  """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""
    }] + message_history
    
    reply=llm.invoke(message)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# Allow LangGraph to build a graph based on the State type
graph_builder = StateGraph(State)

graph_builder.add_node('classify', classify_message)
graph_builder.add_node('router', router)
graph_builder.add_node('therapist', therapist_agent)
graph_builder.add_node('logical', logical_agent)

graph_builder.add_edge(START, 'classify')
graph_builder.add_edge('classify', 'router')
#the lamda function's code is equal to (state) => state.next_node in javascript
graph_builder.add_conditional_edges('router', lambda state: state['next_node'], {'therapist': 'therapist', 'logical': 'logical'})
graph_builder.add_edge('therapist', END)
graph_builder.add_edge('logical', END)

graph=graph_builder.compile()


def run_chatbot():
    state={"messages":[],"message_type":None}

    while True:
        userInput=input('Please let me what I can help you with:')

        if userInput.lower()=='quit':
            print("Goodbye!")
            break

        state["messages"] = state.get("messages", []) + [{"role": "user", "content": userInput}]

        state = graph.invoke(state)
        # print("Assistant:", state["messages"][-1].content)
        
        # Display conversation history
        print("\n--- Conversation History ---")
        for msg in state["messages"]:
            # Handle both dict messages and LangChain message objects
            if isinstance(msg, dict):
                role = msg["role"].capitalize()
                content = msg["content"]
            else:
                # LangChain message object is a class instance
                role = msg.type.capitalize() # type(msg).__name__.replace("Message", "") or msg.__class__.__name__.removesuffix("Message")
                content = msg.content
            print(f"{role}: {content}")
        print("----------------------------\n")


if __name__ == "__main__":
    run_chatbot()