# Accessible Banking Assistant: Voice-Enabled Multi-Agent System

## Problem Statement

A Fintech company identified a critical accessibility barrier in financial services. Traditional banking systems require visual navigation through complex menus and buttons, forcing customers with visual impairments to make stressful trips to physical branches for basic transactions and inquiries. This creates significant barriers that prevent visually impaired users from independently managing their banking needs, forcing them to rely on assistance from others or avoid digital banking altogether.

Additionally, even for sighted users, navigating through multiple menus and searching for specific functions can be cumbersome and time-consuming. The traditional button-and-menu paradigm requires users to know where to look and how to navigate, rather than simply expressing their intent naturally.

## Solution Overview

This solution is a conversational AI banking assistant that services customers through both voice and text input, with support for multi-queries. The architecture includes five intelligent specialized agents with an orchestrator that understands customer needs and routes queries to specialized agents for bank transactions, investment advice, policy information, and general inquiries. Each response is automatically evaluated for quality through comprehensive monitoring and observability.

This doesn't just serve customers with visual impairments; it creates truly inclusive banking for everyone by eliminating complex navigation and physical branch visits.

## Target Users

**Primary Users:**
- **Visually impaired individuals** who need an accessible way to perform daily banking transactions without visual interface dependencies
- Users who prefer **natural language interaction** over navigating complex menu structures

**Secondary Users:**
- General banking customers seeking **convenience** in expressing their banking intent through conversation rather than searching for buttons and menus
- Users who want to perform banking operations using **text or voice** input

## Key Features

1. **Natural Language Banking Operations**
   - Perform deposits, withdrawals, balance checks, and account inquiries through conversational interactions
   - Express intent naturally instead of navigating complex menu structures
   - Multi-turn conversations that handle follow-up questions and clarifications
   - Support for multi-query input (e.g., "What are my investments and what is my balance?")

2. **Accessibility-First Design**
   - **Text input**: Type banking requests naturally
   - **Voice input**: Speak banking requests using OpenAI Whisper for speech-to-text
   - **Text-to-speech output**: Responses are read aloud using Google TTS (gTTS) for visually impaired users
   - No reliance on visual buttons or menus

3. **Specialized Multi-Agent Architecture**
   - **Orchestrator Agent**: Intelligently classifies user intent and routes queries to appropriate specialized agents
   - **Bank Agent**: Handles transactions (deposits, withdrawals, balance checks, account details)
   - **Investment Agent**: Provides investment information using RAG with vector search
   - **FAQ Agent**: Answers frequently asked questions using knowledge base with RAG
   - **Policy Agent**: Explains bank policies and procedures using RAG
   - **Aggregator Agent**: Combines responses from multiple agents for multi-part queries

4. **Quality Assurance and Monitoring**
   - Automatic quality evaluation through LangFuse observability
   - LLM call tracking and performance analytics
   - Comprehensive monitoring of agent behavior and response quality

## Value Proposition

### For Visually Impaired Users
- **Independence**: Perform banking transactions without visual assistance or stressful branch visits
- **Accessibility**: Voice-enabled interface eliminates barriers to digital banking
- **Natural Interaction**: Use natural language instead of memorizing menu structures
- **Comprehensive Support**: Access to all banking services (transactions, investments, FAQs, policies)

### For All Users
- **Convenience**: Express intent naturally rather than searching for buttons
- **Efficiency**: Faster transaction processing through conversation
- **User-Friendly**: No need to learn complex application navigation
- **Multi-Modal**: Support for both text and voice input
- **Inclusive Banking**: Eliminates the need for physical branch visits for routine inquiries

## Success Criteria

1. **Functional Requirements**
   - Successfully route user queries to appropriate specialized agents
   - Complete banking transactions (deposits, withdrawals) through conversation
   - Provide accurate information about investments, FAQs, and policies
   - Handle multi-turn conversations with follow-up questions
   - Support multi-query input spanning multiple agents

2. **Accessibility Requirements**
   - Support text input for banking operations
   - Support voice input for banking operations using OpenAI Whisper
   - Provide text-to-speech output for responses using Google TTS
   - No dependency on visual interface elements

3. **Quality Requirements**
   - Accurate transaction processing
   - Relevant and contextually appropriate responses
   - Robust error handling and validation
   - Production-ready code quality
   - Comprehensive monitoring and observability

## Technical Approach

### Multi-Agent Architecture

The system uses a **multi-agent orchestration pattern** where specialized agents collaborate to handle different aspects of banking operations:

1. **Orchestrator Agent**: 
   - Classifies user intent using LLM with Pydantic validation
   - Detects and decomposes multi-part queries
   - Routes queries to appropriate specialized agents
   - Manages conversation flow and state

2. **Specialized Agents**:
   - Each agent handles a specific domain (banking, investments, FAQs, policies)
   - Investment, FAQ, and Policy agents use RAG (Retrieval-Augmented Generation) with FAISS vector stores for knowledge-based responses
   - Bank Agent handles transaction logic and database operations
   - Aggregator Agent combines responses from multiple agents for multi-part queries
   - Agents can request follow-up information when needed

### Technologies Integrated

1. **LangChain & LangGraph**
   - Multi-agent orchestration and workflow management
   - Agent state management and routing
   - Message passing between agents
   - Conditional workflows based on agent responses

2. **Vector Store (FAISS)**
   - Semantic search for investment information
   - FAQ knowledge base retrieval
   - Policy document search
   - Enables contextually relevant responses through RAG

3. **Pydantic**
   - Data validation for user queries
   - Structured data models for agent communication (`UserQueryModel`, `MultiQueryModel`)
   - Type safety and error handling

4. **LangFuse**
   - Observability and monitoring
   - LLM call tracking and performance analytics
   - Automatic quality evaluation through trace analysis
   - Cost and performance insights

5. **Audio Processing**
   - **OpenAI Whisper**: Speech-to-Text for voice input
   - **Google TTS (gTTS)**: Text-to-Speech for voice output
   - Multi-modal input handling

6. **SQLite**
   - Database for bank account details, transactions, and account management
   - Transaction history tracking

### Design Decisions

**Why Multi-Agent vs Single Agent?**
- **Specialization**: Each agent can be optimized for its specific domain (banking operations vs investment advice)
- **Scalability**: Easy to add new specialized agents without affecting existing ones
- **Maintainability**: Clear separation of concerns makes the system easier to maintain and debug
- **Performance**: Specialized agents with domain-specific knowledge bases provide more accurate responses
- **Context Management**: Prevents context overload by routing to specialized agents rather than loading all knowledge into a single agent

**Why Vector Store for RAG?**
- Enables semantic search across large knowledge bases (investment products, FAQs, policies)
- Provides contextually relevant information to LLM responses
- Allows for easy updates to knowledge bases without retraining models
- Reduces token usage by retrieving only relevant context

**Why LangGraph for Orchestration?**
- Provides robust state management for multi-turn conversations
- Enables complex routing logic between agents
- Supports conditional workflows based on agent responses
- Manages multi-query decomposition and response aggregation

**Why Automatic Quality Evaluation?**
- Ensures production-ready responses through comprehensive monitoring
- Provides insights into system performance and costs
- Enables continuous improvement through observability
- Supports sustainable and maintainable system operations

## Future Enhancements

1. **Enhanced Audio Support**
   - Voice authentication
   - Transaction confirmation via voice
   - Improved TTS quality and customization

2. **Document Analysis**
   - Image-to-text for check processing
   - Legal document explanation
   - Receipt and statement analysis

3. **Enhanced Security**
   - Secure multi-factor authentication
   - Voice biometric authentication
   - Transaction verification workflows

4. **Advanced Features**
   - Multi-language support
   - Personalized recommendations
   - Transaction history analysis and insights
   - Proactive financial advice

## Conclusion

This project addresses a critical accessibility gap in banking applications while providing enhanced convenience for all users. By combining multi-agent AI architecture with natural language processing and voice capabilities, we create a banking assistant that is both powerful and accessible. The solution doesn't just serve customers with visual impairments; it creates truly inclusive banking for everyone by eliminating complex navigation and physical branch visits, enabling all users to independently manage their banking needs through natural conversation.
