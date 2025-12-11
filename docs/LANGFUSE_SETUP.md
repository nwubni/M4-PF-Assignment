# LangFuse Monitoring Setup

This document explains how LangFuse monitoring is integrated into the bank application.

## Overview

LangFuse is integrated to provide observability and monitoring for all LLM calls across the multi-agent system. This allows you to:
- Track all LLM interactions
- Monitor token usage and costs
- Debug agent behavior
- Analyze user queries and responses
- Set up alerts for errors or performance issues

## Configuration

### 1. Environment Variables

Add the following to your `.env` file:

```bash
# LangFuse Configuration
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud
```

You can get your keys from [LangFuse Cloud](https://cloud.langfuse.com) or set up a self-hosted instance.

### 2. Installation

LangFuse is already in `requirements.txt`. If you need to install it:

```bash
pip install langfuse
```

## Integration Points

### 1. RAG Agents (FAQ, Investment, Policy)

All RAG agents created via `rag_agent_factory.py` automatically include LangFuse monitoring:

- **Trace Name**: `{vector_store_name}_agent` (e.g., `faq_agent`, `investment_agent`)
- **Metadata**: Includes agent type and vector store name
- **Monitored Operations**: 
  - Vector store retrieval
  - LLM response generation

### 2. Orchestrator Agent

The orchestrator has two monitoring points:

- **Multi-Query Detection**:
  - Trace Name: `orchestrator_multi_query`
  - Monitors query decomposition into sub-queries

- **Single Query Classification**:
  - Trace Name: `orchestrator_single_query`
  - Monitors query classification and routing

### 3. Bank Agent

The bank agent currently doesn't use LLM calls, so no LangFuse integration is needed. If you add LLM-based features, you can add callbacks similar to other agents.

## Usage

### Automatic Monitoring

Once configured, LangFuse automatically tracks:
- All LLM calls across all agents
- Input prompts and responses
- Token usage and costs
- Latency metrics
- Error tracking

### Viewing Traces

1. Go to [LangFuse Cloud](https://cloud.langfuse.com) or your self-hosted instance
2. Navigate to the "Traces" section
3. Filter by:
   - Agent type (orchestrator, faq_agent, investment_agent, etc.)
   - Time range
   - User queries
   - Errors

### Adding Custom Metadata

You can add custom metadata to traces using the utility functions:

```python
from src.utils.langfuse_utils import set_trace_metadata, set_span_metadata

# Add metadata to current trace
set_trace_metadata({
    "user_id": "user123",
    "session_id": "session456",
    "query_type": "multi_query"
})

# Add metadata to current span
set_span_metadata({
    "retrieved_docs_count": 3,
    "vector_store": "investment"
})
```

## Optional: Workflow-Level Tracing

For even more detailed monitoring, you can wrap the entire workflow execution:

```python
from langfuse.decorators import observe

@observe(name="bank_application_workflow")
def run_workflow(workflow, user_input):
    result = workflow.invoke(
        AgentState(messages=[HumanMessage(content=user_input)])
    )
    return result
```

## Best Practices

1. **Don't Log Sensitive Data**: Be careful not to include sensitive information (account numbers, SSNs, etc.) in traces
2. **Use Meaningful Trace Names**: The trace names help you filter and analyze in LangFuse
3. **Add Metadata Strategically**: Add metadata that helps with debugging and analysis
4. **Monitor Costs**: Use LangFuse to track token usage and costs across agents

## Troubleshooting

### LangFuse Not Working

If monitoring isn't appearing in LangFuse:

1. **Check Environment Variables**: Ensure `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set
2. **Check Network**: Ensure your application can reach the LangFuse host
3. **Check Logs**: Look for any LangFuse-related errors in your application logs
4. **Graceful Degradation**: The system will continue to work even if LangFuse is not configured (callbacks return empty list)

### Reducing Noise

If you're getting too many traces:

- Filter in LangFuse UI by trace name
- Use metadata to categorize traces
- Consider sampling for high-volume scenarios

## Example Trace Structure

A typical multi-agent query will create traces like:

```
orchestrator_multi_query
  ├── orchestrator_single_query (if single query)
  ├── faq_agent (if FAQ query)
  ├── investment_agent (if investment query)
  ├── policy_agent (if policy query)
  └── bank_agent (if bank operation)
```

Each trace contains:
- Input prompts
- LLM responses
- Token usage
- Latency
- Metadata

