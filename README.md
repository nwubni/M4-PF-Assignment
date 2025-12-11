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

To quit the application, type 'exit', 'quit', or 'q'.

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

## Documentation

- [Proposal](docs/proposal.md) - Project proposal and design
- [LangFuse Setup](docs/LANGFUSE_SETUP.md) - Monitoring setup guide
- [Test Documentation](src/test_data/README.md) - Test suite documentation