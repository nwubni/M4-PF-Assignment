"""
LangFuse utilities for monitoring and observability.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import LangFuse - make it optional
try:
    # LangFuse 3.x uses langfuse.langchain for CallbackHandler
    from langfuse.langchain import CallbackHandler
    from langfuse.decorators import langfuse_context, observe

    LANGFUSE_AVAILABLE = True
except ImportError:
    # LangFuse not available or different version
    try:
        # Try older import path
        from langfuse.callback import CallbackHandler
        from langfuse.decorators import langfuse_context, observe

        LANGFUSE_AVAILABLE = True
    except ImportError:
        LANGFUSE_AVAILABLE = False
        CallbackHandler = None
        langfuse_context = None
        observe = None


def get_langfuse_handler(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[object]:
    """
    Get a LangFuse callback handler for LangChain/LangGraph.

    Args:
        user_id: Optional user identifier
        session_id: Optional session identifier
        trace_name: Optional trace name for this operation
        metadata: Optional metadata dictionary to attach to the trace

    Returns:
        LangFuse CallbackHandler instance, or None if not available/configured
    """
    # Check if LangFuse is available
    if not LANGFUSE_AVAILABLE or CallbackHandler is None:
        return None

    # Check if LangFuse is configured
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        # Return None if not configured - monitoring is optional
        return None

    try:
        handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            user_id=user_id,
            session_id=session_id,
            trace_name=trace_name,
        )
        # Set metadata if provided
        if metadata and langfuse_context is not None:
            try:
                langfuse_context.update_current_trace(metadata=metadata)
            except Exception:
                pass
        return handler
    except Exception:
        # Return None if handler creation fails
        return None


def get_langfuse_callbacks(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> list:
    """
    Get LangFuse callbacks as a list (for LangChain compatibility).

    Args:
        user_id: Optional user identifier
        session_id: Optional session identifier
        trace_name: Optional trace name for this operation
        metadata: Optional metadata dictionary to attach to the trace

    Returns:
        List containing LangFuse handler, or empty list if not configured
    """
    handler = get_langfuse_handler(user_id, session_id, trace_name, metadata)
    return [handler] if handler else []


def set_trace_metadata(metadata: dict):
    """
    Set metadata for the current LangFuse trace.

    Args:
        metadata: Dictionary of metadata to attach to the trace
    """
    if not LANGFUSE_AVAILABLE or langfuse_context is None:
        return
    try:
        langfuse_context.update_current_trace(metadata=metadata)
    except Exception:
        # Silently fail if LangFuse is not configured
        pass


def set_span_metadata(metadata: dict):
    """
    Set metadata for the current LangFuse span.

    Args:
        metadata: Dictionary of metadata to attach to the span
    """
    if not LANGFUSE_AVAILABLE or langfuse_context is None:
        return
    try:
        langfuse_context.update_current_observation(metadata=metadata)
    except Exception:
        # Silently fail if LangFuse is not configured
        pass
