"""AI agent for preparing for journal club."""

from typing import Final

from . import secrets
from .prompts import (
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from .tools import TavilyWrapper, think_tool
from .ui import format_message_content, format_messages, show_prompt

__all__: Final[list[str]] = [
    "RESEARCHER_INSTRUCTIONS",
    "RESEARCH_WORKFLOW_INSTRUCTIONS",
    "SUBAGENT_DELEGATION_INSTRUCTIONS",
    "TavilyWrapper",
    "format_message_content",
    "format_messages",
    "secrets",
    "show_prompt",
    "think_tool",
]
