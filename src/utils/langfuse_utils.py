"""
LangFuse utilities for monitoring and observability.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Import LangFuse with fallback handling
try:
    from langfuse.langchain import CallbackHandler
    import langfuse

    LANGFUSE_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Failed to import from langfuse.langchain: {e}")
    # LangFuse not available or different version
    try:
        # Fallback to older import path
        from langfuse.callback import CallbackHandler
        import langfuse

        LANGFUSE_AVAILABLE = True
        print("DEBUG: LangFuse imported successfully from langfuse.callback")
    except ImportError as e2:
        print(f"DEBUG: Failed to import from langfuse.callback: {e2}")
        LANGFUSE_AVAILABLE = False
        CallbackHandler = None
        langfuse = None
        print("DEBUG: LangFuse not available - all imports failed")


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
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        return None

    try:
        # Initialize LangFuse client first
        langfuse.Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )

        # Create CallbackHandler with the initialized client
        handler = CallbackHandler(
            public_key=public_key, update_trace=True  # Enable trace updates
        )
        return handler
    except Exception:
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
