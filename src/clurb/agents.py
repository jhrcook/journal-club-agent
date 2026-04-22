"""Research agent."""

from datetime import datetime
from typing import Any

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

from clurb.prompts import (
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from clurb.tools import tavily_search, think_tool


def build_research_agent() -> Any:
    """Build a research AI agent."""
    # Limits
    max_concurrent_research_units = 3
    max_researcher_iterations = 3

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
    research_sub_agent = {
        "name": "research-agent",
        "description": "Delegate research to the sub-agent researcher. Only give "
        "this researcher one topic at a time.",
        "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
        "tools": [tavily_search, think_tool],
    }

    # Model Gemini 3
    # model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.0)

    # Model Claude 4.5
    model = init_chat_model(
        model="anthropic:claude-sonnet-4-5-20250929",
        temperature=0.0,
    )

    # Create the agent
    return create_deep_agent(
        model=model,
        tools=[tavily_search, think_tool],
        system_prompt=instructions,
        subagents=[research_sub_agent],  # type: ignore
    )
