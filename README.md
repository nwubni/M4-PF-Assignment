# M4-PF-Assignment
Andela GenAI Fourth Assignment

## Overview

An accessible banking assistant that enables visually impaired users to perform banking operations through natural language conversations (text or voice). The system uses a multi-agent architecture with specialized agents for different banking functions.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python src/database/init_db.py
```

### 3. Build Vector Indices

```bash
python -m src.build.index src/data/faq.txt
python -m src.build.index src/data/investment.txt
python -m src.build.index src/data/policy.txt
```

### 4. Configure Environment Variables

Create a `.env` file with:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LangFuse (Optional)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Text-to-Speech (Optional)
TTS_ENABLED=true
TTS_SPEED=1.4
```

## Running the Application

```bash
python src/main.py
```

### Input Commands

- Type `exit`, `quit`, or `q` to quit the application.
- Type `voice` or `v` to use voice input. You can also type your commands directly using text.

### Disable Text-to-Speech

Set the environment variable `TTS_ENABLED` to `false` in your `.env` file or export it before running:

```bash
export TTS_ENABLED=false
python src/main.py
```

## Input Examples

**Single Query Examples:**
- How much is my account balance?
- Deposit 50 dollars
- Withdraw 50 dollars
- What are my investment options?
- What are my bank policies?

**Multi-Query Examples:**
- Deposit 20 dollars in my bank account and show me my account balance.
- What investment options do you have, and can I have multiple accounts?

## Key Assumptions
- **Moderation**: Has been fully implemented for user input and system responses
- **Caching**: Is available to reduce latency for repeated queries

## Features

- **Bank Operations**: Deposit, withdraw, check balance, view account details
- **Investment Information**: Query investment products and services using RAG
- **FAQ Support**: Get answers to frequently asked questions from knowledge base
- **Policy Information**: Access bank policies and procedures
- **Multi-Agent Queries**: Ask multiple questions in a single query
- **Multi-Turn Conversations**: Handle follow-up questions (e.g., asking for deposit amount)
- **Natural Language**: Express intent naturally instead of navigating menus
- **Accessibility**: Designed for visually impaired users with text and voice support
- **Voice Input**: Use voice to input queries with OpenAI Whisper
- **Text-to-Speech**: Output responses using Google TTS (gTTS) for accessibility

## Architecture

The system uses a **multi-agent orchestration pattern** where specialized agents collaborate to handle different aspects of banking operations:

```
User Query
    ↓
Orchestrator Agent (classifies intent, detects multi-query)
    ↓
    ├─→ Bank Agent (transactions, balance, account details)
    ├─→ Investment Agent (RAG-based investment information)
    ├─→ FAQ Agent (RAG-based FAQ answers)
    ├─→ Policy Agent (RAG-based policy information)
    └─→ Aggregator Agent (combines multi-agent responses)
    ↓
Response to User
```

### Agent Roles and Descriptions

#### Orchestrator Agent
The orchestrator is the entry point and routing hub of the system. It:
- Classifies user queries into categories (deposit, withdrawal, balance, investment, FAQ, policy)
- Detects multi-part queries (e.g., "What are my investments and what is my balance?")
- Decomposes multi-queries into sub-queries for different agents
- Routes queries to appropriate specialized agents
- Manages the workflow state and coordinates agent responses
- Uses Pydantic models (`UserQueryModel`, `MultiQueryModel`) for structured classification

#### Bank Agent
Handles all banking transaction operations:
- **Deposits**: Processes deposit requests and updates account balance in SQLite database
- **Withdrawals**: Processes withdrawal requests with balance validation
- **Balance Checks**: Retrieves and returns current account balance
- **Account Details**: Provides comprehensive account information
- Supports both single queries and multi-query scenarios
- Returns structured responses that can be aggregated with other agent responses

#### Investment Agent
Provides investment information using Retrieval-Augmented Generation (RAG):
- Uses FAISS vector store to search investment-related documents
- Retrieves relevant context from `investment.txt` knowledge base
- Generates contextually relevant responses about investment products and services
- Preserves state for multi-query scenarios to enable response aggregation

#### FAQ Agent
Answers frequently asked questions using RAG:
- Uses FAISS vector store to search FAQ documents
- Retrieves relevant context from `faq.txt` knowledge base
- Provides accurate answers based on the bank's FAQ knowledge base
- Preserves state for multi-query scenarios

#### Policy Agent
Explains bank policies and procedures using RAG:
- Uses FAISS vector store to search policy documents
- Retrieves relevant context from `policy.txt` knowledge base
- Provides detailed policy information and procedures
- Preserves state for multi-query scenarios

#### Aggregator Agent
Combines responses from multiple agents for multi-part queries:
- Collects responses from specialized agents processed sequentially
- Joins multiple agent responses into a single coherent answer
- Returns the aggregated response to the user
- Ensures seamless user experience for complex queries spanning multiple domains

## Why Multi-Agent Architecture?

The system uses a multi-agent architecture for several key reasons:

### 1. Specialization
Each agent is optimized for its specific domain:
- **Bank Agent** handles transaction logic and database operations
- **Investment, FAQ, and Policy Agents** use domain-specific RAG knowledge bases
- This specialization ensures more accurate and relevant responses

### 2. Preventing Context Overload
Instead of loading all knowledge (banking operations, investments, FAQs, policies) into a single agent's context:
- Each agent only processes relevant information for its domain
- Reduces token usage and improves response quality
- Prevents the LLM from being overwhelmed with irrelevant context

### 3. Scalability
- Easy to add new specialized agents without affecting existing ones
- Each agent can be independently updated or improved
- New domains (e.g., loans, insurance) can be added as separate agents

### 4. Maintainability
- Clear separation of concerns makes the system easier to maintain and debug
- Each agent has a single, well-defined responsibility
- Changes to one agent don't impact others

### 5. Performance
- Specialized agents with domain-specific knowledge bases provide more accurate responses
- RAG agents can efficiently search large knowledge bases without loading everything into context
- Parallel processing potential for independent queries

## Agent Collaboration

Agents collaborate through a coordinated workflow managed by LangGraph:

### Single Query Flow
1. **User Input** - Orchestrator receives the query
2. **Classification** - Orchestrator classifies the query using LLM and Pydantic validation
3. **Routing** - Orchestrator routes to the appropriate specialized agent
4. **Processing** - Specialized agent processes the query (using RAG if applicable)
5. **Response** - Agent returns response directly to the user

### Multi-Query Flow
1. **User Input** - Orchestrator receives a complex query (e.g., "What are my investments and what is my balance?")
2. **Multi-Query Detection** - Orchestrator detects multiple intents using `MultiQueryModel`
3. **Query Decomposition** - Orchestrator splits the query into sub-queries:
   - Sub-query 1: "What are my investments?" - Investment Agent
   - Sub-query 2: "What is my balance?" - Bank Agent
4. **Sequential Processing** - Orchestrator routes to each agent sequentially, collecting responses
5. **State Management** - Responses are stored in the workflow state
6. **Aggregation** - Orchestrator routes to Aggregator Agent with all collected responses
7. **Combined Response** - Aggregator combines responses into a single coherent answer
8. **Final Response** - User receives the aggregated response

### State Management
- LangGraph's `AgentState` maintains conversation state across agent transitions
- The `result` field stores multi-query metadata (sub-queries, current index, collected responses)
- Each agent preserves the state when routing back to the orchestrator

## Technologies

- **LangChain/LangGraph**: Multi-agent orchestration, workflow management, and state handling
- **OpenAI GPT-4o-mini**: LLM for query classification, intent detection, and natural language understanding
- **OpenAI Whisper**: Speech-to-text for voice input
- **Google TTS (gTTS)**: Text-to-speech for audio output (requires internet)
- **FAISS**: Vector store for semantic search and RAG implementation
- **HuggingFace Embeddings**: Sentence transformers (`all-MiniLM-L6-v2`) for document embeddings
- **Pydantic**: Data validation and structured models for agent communication
- **LangFuse**: Observability, monitoring, and performance tracking for LLM calls
- **SQLite**: Database for bank account details, transactions, and account management
- **Pygame**: Audio playback for TTS output

## Observability and Performance Monitoring

The project integrates **LangFuse** for comprehensive observability and monitoring:

### Purpose
- **Sustainability**: Monitor system performance and identify bottlenecks
- **Maintainability**: Track LLM usage patterns and agent behavior
- **Cost Management**: Monitor API costs and token usage across agents
- **Performance Insights**: Analyze response times, success rates, and error patterns

### Implementation
- LangFuse callbacks are integrated into all LLM calls (orchestrator, RAG agents)
- Traces are created for each conversation with metadata (user query, voice enabled, etc.)
- Spans track individual agent operations (multi-query detection, single-query classification, RAG retrieval)
- Metadata includes agent type, operation type, and query context

### Configuration
LangFuse is optional and gracefully degrades if not configured. To enable:
1. Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` in `.env`
2. The system automatically uses LangFuse callbacks when available
3. View traces and analytics in the LangFuse dashboard

See [LangFuse Setup Guide](docs/LANGFUSE_SETUP.md) for detailed configuration instructions.

## Running Tests

The project includes a comprehensive test suite with golden data to validate system behavior.

### Run All Tests

```bash
python run_tests.py
```

Or:

```bash
python -m src.test_data.test_runner
```

### Run Specific Test Suites

```bash
# Single query tests only
python -m src.test_data.test_single_queries

# Multi-query tests only
python -m src.test_data.test_multi_queries
```

### Test Coverage

The test suite validates:
- Single-agent queries (bank operations, investments, FAQs, policies)
- Multi-agent queries (combining multiple intents)
- Transaction flows (deposits, withdrawals)
- Response accuracy against golden data

## Documentation

- [Proposal](docs/proposal.md) - Project proposal and design
- [LangFuse Setup](docs/LANGFUSE_SETUP.md) - LangFuse integration guide
- [Test Data README](src/test_data/README.md) - Testing documentation
