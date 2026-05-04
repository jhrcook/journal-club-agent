"""Custom middleware."""

import time
from typing import Any, Callable

from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    ToolCallRequest,
    wrap_model_call,
    wrap_tool_call,
)
from loguru import logger


@wrap_model_call(name="modelcall-logging-middleware")
def log_model_calls(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Log all model calls."""
    model_name = request.model.get_name()
    logger.debug(f"[Middleware] Making request to model '{model_name}'.")
    tic = time.perf_counter()
    result = handler(request)
    toc = time.perf_counter()
    duration_minutes = (toc - tic) / 60
    logger.debug(
        f"[Middleware] Result returned from model '{model_name}' "
        f"(duration: {duration_minutes:.2f} min.)."
    )
    return result


@wrap_tool_call(name="toolcall-logging-middleware")
def log_tool_calls(
    request: ToolCallRequest, handler: Callable[[ToolCallRequest], Any]
) -> Any:
    """Log every tool call."""
    tool_name = str(
        request.tool.get_name() if request.tool else type(request.tool_call["name"])
    )
    logger.debug(f"[Middleware] Running tool '{tool_name}'.")
    tic = time.perf_counter()
    result = handler(request)
    toc = time.perf_counter()
    duration_minutes = (toc - tic) / 60
    logger.debug(
        f"[Middleware] Tool '{tool_name}' call completed "
        f"(duration: {duration_minutes:.2f} min.)."
    )
    return result
