"""Research agent."""

from datetime import datetime
from typing import Any, Literal

import ollama
from deepagents import SubAgent, create_deep_agent
from langchain.chat_models import init_chat_model
from loguru import logger

from clurb.prompts import (
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from clurb.tools import tavily_search, think_tool


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


def build_research_agent(model: str, provider: Literal["ollama"] = "ollama") -> Any:
    """Build a research AI agent."""
    # Limits
    max_concurrent_research_units = 1
    max_researcher_iterations = 1

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

    # Create research sub-agent
    research_sub_agent = SubAgent(
        name="research-agent",
        description=(
            "Delegate research to the sub-agent researcher. Only give "
            "this researcher one topic at a time."
        ),
        system_prompt=RESEARCHER_INSTRUCTIONS.format(date=current_date),
        tools=[tavily_search, think_tool],
    )

    # Create the base chat model.
    chat_model = init_chat_model(model=f"{provider}:{model}")

    # Create the agent
    return create_deep_agent(
        model=chat_model,
        tools=[tavily_search, think_tool],
        system_prompt=instructions,
        subagents=[research_sub_agent],
    )
