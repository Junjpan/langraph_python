# Agentic AI Chatbot - main.py Overview

## What Does the Agentic AI Do?

This program implements an **adaptive agentic AI chatbot** using LangGraph that intelligently routes conversations to specialized agents based on message type. The AI system dynamically responds to user input by:

1. **Classifying messages** - Determines if the user needs emotional support or logical analysis
2. **Managing conversation history** - Summarizes old messages when conversations get too long (exceeds 6 messages)
3. **Routing to specialized agents** - Directs conversations to either a Therapist Agent or Logical Agent
4. **Generating contextual responses** - Each agent uses appropriate personalities and incorporates conversation summaries

---

## System Architecture Diagram

```
                              ┌─────────────────────────┐
                              │   User Input            │
                              │ (User Message)          │
                              └────────────┬────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────────────┐
                        │  1. CLASSIFY MESSAGE                 │
                        │  ├─ Analyze message type             │
                        │  └─ Output: "emotional" or "logical" │
                        └────────────┬─────────────────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │ Check Message Count      │
                        │ (> 6 messages?)          │
                        └─────────────┬────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼ YES                               ▼ NO
        ┌──────────────────────┐            ┌──────────────────────────┐
        │  2A. SUMMARY GENERATOR│            │ 2B. ROUTE MESSAGE (Direct)
        │  ├─ Summarizes old   │            │  ├─ Check message_type   │
        │  │  messages         │            │  └─ Route to appropriate │
        │  └─ Returns updated  │            │     agent node           │
        │     state with new   │            │                          │
        │     messages + summary            └─────────────┬────────────┘
        └────────────┬─────────┘                          │
                     │                                    │
                     └────────────┬─────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  3. ROUTE MESSAGE           │
                    │  ├─ Check message_type      │
                    │  └─ Route to appropriate    │
                    │     agent node              │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
                    ▼                            ▼
        ┌──────────────────────────┐  ┌──────────────────────────┐
        │ 4A. THERAPIST AGENT      │  │ 4B. LOGICAL AGENT        │
        │                          │  │                          │
        │ ├─ Empathetic response   │  │ ├─ Fact-based response   │
        │ ├─ Emotional validation  │  │ ├─ Clear & concise       │
        │ ├─ Thoughtful questions  │  │ ├─ Evidence-driven       │
        │ ├─ Uses conversation     │  │ ├─ Direct & structured   │
        │ │  summary               │  │ ├─ Uses conversation     │
        │ └─ Output: compassionate │  │ │  summary               │
        │   assistant reply        │  │ └─ Output: logical       │
        │                          │  │   assistant reply        │
        └────────────┬─────────────┘  └──────────────┬───────────┘
                     │                                │
                     └────────────┬─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  5. RETURN RESPONSE         │
                    │  ├─ Add assistant message   │
                    │  │  to state                │
                    │  └─ End conversation turn   │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                        ┌──────────────────────────┐
                        │  Display Output          │
                        │  ├─ Show conversation    │
                        │  │  history              │
                        │  └─ Prompt for next input│
                        └──────────────────────────┘
```

---

## Key Components

### 1. **State Management**
- Maintains `messages` (chat history), `message_type` (classification), and `summary` (conversation summary)
- Uses LangGraph's `StateGraph` for robust state handling

### 2. **Message Classification Node**
- Uses Claude Haiku LLM with structured output
- Classifies messages as "emotional" or "logical"
- Determines the routing path for the conversation

### 3. **Summary Generator Node**
- Triggered when conversation exceeds 6 messages
- Summarizes old messages using the LLM
- Preserves recent messages (last 6) for context
- Prevents token overflow in long conversations

### 4. **Router Node**
- Conditional routing based on `message_type`
- Routes to either Therapist or Logical agent

### 5. **Specialized Agent Nodes**
- **Therapist Agent**: Provides emotional support, empathy, and validates feelings
- **Logical Agent**: Provides fact-based, evidence-driven responses

### 6. **Graph Execution**
- LangGraph compiles the workflow into an executable graph
- Each user input triggers one complete cycle through the workflow
- Supports multi-turn conversations with continuous state updates

---

## Workflow Summary

1. User inputs a message
2. System classifies the message type (emotional vs. logical)
3. If conversation is too long (>6 messages), summarize old messages
4. Route to appropriate specialized agent (Therapist or Logical)
5. Agent generates contextual response using conversation history & summary
6. Response is added to state and displayed to user
7. Repeat for next user input
