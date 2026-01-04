# LangGraph Chatbot Architecture

## Overview
This document explains how the chatbot system works, focusing on the relationship between `graph.invoke()` and the `chatbot` node function.

## Key Components

### 1. State Management
```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```
- **State** defines the data structure passed through the graph
- **`add_messages`** is a reducer that automatically appends new messages to the list
- This maintains conversation history across iterations

### 2. Graph Builder
```python
graph_builder = StateGraph(State)
```
- Creates a directed graph that orchestrates the data flow
- Manages state transformations as data moves through nodes

### 3. The Chatbot Node Function
```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

**What it does:**
- Takes the current `state` as input
- Accesses all accumulated messages: `state["messages"]`
- Sends **all messages** (entire conversation history) to the LLM
- Returns the LLM response wrapped in the state structure

**Why it matters:**
- This is where the actual AI interaction happens
- The LLM receives full context of the conversation
- It's a separate function so it can be reused, tested, and extended

## Execution Flow

### Step-by-Step Process

1. **User Input**
   ```python
   state=graph.invoke({"messages": state["messages"] + [("user", user_input)]})
   ```
   - Creates a fresh message list with accumulated history + new user message
   - Passes it to `graph.invoke()`

2. **Graph Execution** (happens inside `graph.invoke()`)
   ```
   START → 'chatbot' node → END
   ```
   - Graph routes execution to the 'chatbot' node
   - Passes the state containing all messages

3. **Chatbot Node Processes**
   ```python
   def chatbot(state: State):
       return {"messages": [llm.invoke(state["messages"])]}
   ```
   - Receives state with full conversation history
   - LLM processes all messages to generate context-aware response
   - Returns new message added to state

4. **Reducer Applies Update**
   - The `add_messages` reducer automatically appends the LLM response
   - State is updated with the new message
   - Updated state returned to the main loop

5. **Display & Continue**
   - Extract and display the assistant response
   - Show last 10 messages for user reference
   - Loop continues with updated state

## Why They Work Together

### `graph.invoke()` is the **Orchestrator**
- Manages control flow (START → END)
- Handles state transitions
- Applies reducers to state updates
- Provides a framework for composable, reusable nodes

### `chatbot()` is the **Worker**
- Contains the actual business logic (LLM call)
- Receives prepared state from the graph
- Returns transformed state back to graph
- Can be tested independently
- Can be replaced/extended without changing graph structure

## Conversation History Persistence

```python
state = {"messages": []}  # Initialize outside loop

while True:
    # Each iteration:
    # 1. Takes current state.messages (accumulated history)
    # 2. Appends new user message
    # 3. Passes to graph
    # 4. Chatbot node adds LLM response
    # 5. State is updated with both messages
    state=graph.invoke({"messages": state["messages"] + [("user", user_input)]})
```

**Result:** All previous messages remain in state, so the LLM always has full context.

## Example Execution

**Iteration 1:**
```
Input: "Hello"
State messages: []
Passed to graph: [("user", "Hello")]
Chatbot sends to LLM: [("user", "Hello")]
LLM returns: "Hi, how can I help?"
State updated: [("user", "Hello"), ("assistant", "Hi, how can I help?")]
```

**Iteration 2:**
```
Input: "What's your name?"
State messages: [("user", "Hello"), ("assistant", "Hi, how can I help?")]
Passed to graph: [...previous messages..., ("user", "What's your name?")]
Chatbot sends to LLM: [All 3 messages - full context]
LLM returns: "I'm Claude..."
State updated: [All 4 messages]
```

## Summary

| Component | Role | Function |
|-----------|------|----------|
| `graph.invoke()` | Control Flow | Routes execution, manages state, applies reducers |
| `chatbot()` | Business Logic | Calls LLM with full conversation context |
| `state` | Memory | Persists across loop iterations, grows with each exchange |
| `add_messages` | Reducer | Automatically merges new messages into state |

The architecture separates **orchestration** (graph) from **execution** (chatbot node), making the system modular, testable, and extensible.
