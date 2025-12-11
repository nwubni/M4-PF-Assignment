# Multi-Query Aggregator Guide

## Overview
The multi-agent system now supports handling multiple queries in a single user request. For example:
- "What investment options do you have, and what is my account balance?"
- "I want to deposit 100 dollars and also check my investment portfolio"
- "How many days can I take off in a year, and what is my account balance?"

## How It Works

### 1. Query Detection (Orchestrator)
The orchestrator first checks if the user query contains multiple sub-queries:
- Uses `orchestrator_multi.txt` prompt to analyze the query
- Returns a `MultiQueryModel` with `is_multi_query` flag and list of `sub_queries`
- Each sub-query has: `query`, `category`, and `agent`

### 2. Sequential Processing
If multi-query detected:
1. Orchestrator routes to the first agent with the first sub-query
2. Agent processes the query and returns response with `result` state preserved
3. Agent routes back to orchestrator (not END)
4. Orchestrator checks if more sub-queries remain
5. If yes, routes to next agent with next sub-query
6. Repeats until all sub-queries processed
7. Finally routes to aggregator

### 3. Aggregation
The aggregator agent:
- Collects all agent responses from the message history
- Filters out orchestrator JSON messages
- Uses an LLM to combine responses into a coherent answer
- Returns the final combined response

## Key Implementation Details

### Agent Changes
All agents (bank, investment, policy, FAQ) now:
```python
# Check if this is part of a multi-query
result = state.get("result", {})
if result.get("is_multi_query"):
    # Preserve all messages and route back to orchestrator
    return {
        "messages": messages + [AIMessage(content=response_text)],
        "next": AgentsEnum.ORCHESTRATOR.value,
        "result": result,
    }
else:
    # Single query, end here
    return {
        "messages": [AIMessage(content=response_text)],
        "next": "END",
    }
```

### State Management
The `result` field in state tracks:
- `is_multi_query`: Boolean flag
- `sub_queries`: List of sub-queries to process
- `current_sub_query_index`: Which sub-query is being processed
- `original_query`: The original user query for aggregation

### Routing Logic
In `main.py`, the `route_from_agent` function:
```python
def route_from_agent(state: AgentState):
    result = state.get("result", {})
    next_value = state.get("next", "END")
    # If it's a multi-query, always route back to orchestrator
    if result.get("is_multi_query"):
        return AgentsEnum.ORCHESTRATOR.value
    # Otherwise use the next value from state
    return next_value if next_value else "END"
```

## Testing

Run the test script:
```bash
python test_simple_multi.py
```

Or test in the main application:
```bash
python src/main.py
```

Then enter a multi-part query like:
```
What investment options do you have, and what is my account balance?
```

## Example Flow

**User Query:** "What investment options do you have, and what is my account balance?"

**Flow:**
1. Orchestrator detects 2 sub-queries:
   - "What investment options do you have?" → investment agent
   - "What is my account balance?" → bank agent

2. Routes to investment agent → gets response about investment options

3. Routes back to orchestrator → detects more sub-queries

4. Routes to bank agent → gets response about account balance

5. Routes back to orchestrator → all sub-queries done

6. Routes to aggregator → combines both responses

7. Returns final combined response to user

## Prompts

### orchestrator_multi.txt
Analyzes if query needs multiple agents and decomposes it into sub-queries.

### orchestrator.txt
Handles single-query classification (used when `is_multi_query=false`).

## Models

### MultiQueryModel
```python
class MultiQueryModel(BaseModel):
    is_multi_query: bool
    sub_queries: List[SubQuery] = []
    original_query: str

class SubQuery(BaseModel):
    query: str
    category: str
    agent: str
```

## Troubleshooting

**Issue:** Agents not routing back to orchestrator
- **Fix:** Ensure agents check `result.get("is_multi_query")` and return orchestrator as next

**Issue:** Messages not preserved
- **Fix:** Agents must append to messages: `messages + [AIMessage(...)]`

**Issue:** Aggregator not receiving all responses
- **Fix:** Check that all agents preserve messages in multi-query mode

**Issue:** Infinite loop
- **Fix:** Ensure orchestrator increments `current_sub_query_index` and routes to aggregator when done
