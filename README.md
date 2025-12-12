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
```

## Running the Application

```bash
python src/main.py
```

## Input commands

- Type 'exit', 'quit', or 'q' to quit the application.
- Type 'voice' or 'v' to use voice input. You can also type your commands directly using text.

## Disable Text-to-Speech
- Set the environment variable `TTS_ENABLED` to `false`.

## Input Examples
- How much is my account balance?
- Deposit 50 dollars
- Withdraw 50 dollars
- What are my investment options?
- What are my bank policies?
- What is the frequently asked question about my account?

Supports multi-query input. For example:
- Deposit 20 dollars in my bank account and show me my account balance.
- Tell me about my investment options and show me my account balance.

## Technologies used
- OpenAI Whisper for voice input
- OpenAI TTS for text-to-speech
- LangChain/LangGraph for multi-agent orchestration
- FAISS for vector store and semantic search. Needed for RAG to enable users to ask questions related to investment options and policies.
- LangFuse for observability and performance monitoring
- SQLite for database storage of bank account details, transactions, and account management.
- Pydantic for data validation. Ensures data consistency and type safety.

## Observability and Performance Monitoring
Project needs to be sustainable and maintainable.
Management needs insights on costs and performance.
To achieve this, we will use Langfuse to monitor the application.

## Running Tests

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

## Features

- **Bank Operations**: Deposit, withdraw, check balance, view account details
- **Investment Information**: Query investment products and services
- **FAQ Support**: Get answers to frequently asked questions
- **Policy Information**: Access bank policies and procedures
- **Multi-Agent Queries**: Ask multiple questions in a single query
- **Natural Language**: Express intent naturally instead of navigating menus
- **Accessibility**: Designed for visually impaired users (text and voice support)
- **Voice Input**: Use voice to input queries with OpenAI Whisper
- **Text-to-Speech**: Use text-to-speech to output responses with OpenAI TTS

## Architecture

- **Orchestrator Agent**: Routes queries to appropriate specialized agents
- **Bank Agent**: Handles transactions and account operations
- **Investment Agent**: Provides investment information using RAG
- **FAQ Agent**: Answers questions using knowledge base
- **Policy Agent**: Explains bank policies
- **Aggregator Agent**: Combines responses from multiple agents

## Technologies

- **LangChain/LangGraph**: Multi-agent orchestration
- **FAISS**: Vector store for semantic search
- **Pydantic**: Data validation
- **LangFuse**: Observability and monitoring
- **SQLite**: Banking database

Agents and Agent Role/Description
Discuss how each agent works and how they interact.
- Orchestrator (Tell how it works)
- Bank Agent (Explain how it handles transactions and account operations)
- Investment Agent (Explain how it provides investment information using RAG)
- FAQ Agent (Explain how it answers questions using knowledge base)
- Policy Agent (Explain bank policies)
- Aggregator Agent (Expalain how it combines responses from multiple agents)
## Documentation

- [Proposal](docs/proposal.md) - Project proposal and design