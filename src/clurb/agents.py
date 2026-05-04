"""Research agent."""

from datetime import datetime
from pathlib import Path
from typing import Literal

import ollama
from deepagents import SubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.chat_models import init_chat_model
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from clurb.middleware import log_model_calls, log_tool_calls
from clurb.prompts import (
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from clurb.secrets import load_secrets
from clurb.tools import TavilyWrapper, think_tool


def list_ollama_models() -> list[str]:
    """List available Ollama models."""
    return [m.model for m in ollama.list().models if m.model]


def check_ollama_model(model: str) -> bool:
    """Check an Ollama model."""
    res = ollama.generate(
        model=model,
        prompt=(
            "Confirm you are operational by responding 'true'. "
            "Otherwise, respond 'false'."
        ),
        stream=False,
    )
    if not res.done:
        logger.warning("Incomplete response returned by model.")
        return False

    response = res.response.strip()
    if response == "true":
        return True

    if response == "false":
        logger.warning("Model says it is not ready.")
        return False

    logger.warning(f"Model did not respond as prompted. Models response: {res}.")
    return False


def build_research_agent(
    model: str,
    provider: Literal["ollama"] = "ollama",
    *,
    workspace: Path = Path("./agent-workspace"),
    secrets_yaml: Path = Path("./secrets.yaml"),
) -> CompiledStateGraph:
    """Build a research AI agent."""
    # Limits
    max_concurrent_research_units = 1
    max_researcher_iterations = 1

    workspace.mkdir(exist_ok=True, parents=True)
    backend = FilesystemBackend(root_dir=workspace, virtual_mode=True)

    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Combine orchestrator instructions (RESEARCHER_INSTRUCTIONS only for sub-agents)
    instructions = (
        RESEARCH_WORKFLOW_INSTRUCTIONS
        + "\n\n"
        + "=" * 80
        + "\n\n"
        + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
            max_concurrent_research_units=max_concurrent_research_units,
            max_researcher_iterations=max_researcher_iterations,
        )
    )

    tavily_wrapper = TavilyWrapper(load_secrets(secrets_yaml).api_keys.tavily)
    tavily_search = tavily_wrapper.build_tavily_search_func()

    custom_middleware = [log_model_calls, log_tool_calls]

    # Create research sub-agent
    research_sub_agent = SubAgent(
        name="research-agent",
        description=(
            "Delegate research to the sub-agent researcher. Only give "
            "this researcher one topic at a time."
        ),
        system_prompt=RESEARCHER_INSTRUCTIONS.format(date=current_date),
        tools=[tavily_search, think_tool],
        middleware=custom_middleware,
        model=init_chat_model(model="qwen3.6:latest", model_provider=provider),
    )

    # Create the base chat model.
    chat_model = init_chat_model(model=model, model_provider=provider)

    # Create the agent
    return create_deep_agent(
        model=chat_model,
        tools=[tavily_search, think_tool],
        system_prompt=instructions,
        subagents=[research_sub_agent],
        middleware=custom_middleware,
        backend=backend,
    )
