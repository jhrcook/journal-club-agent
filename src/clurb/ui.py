"""Utility functions for displaying messages and prompts in Jupyter notebooks."""

import json
from typing import Iterable

from langchain.messages import AIMessage, HumanMessage, ToolMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

console = Console()

_DeepAgentMessage = AIMessage | HumanMessage | ToolMessage


def format_message_content(message: _DeepAgentMessage) -> Markdown:
    """Convert message content to displayable string."""
    parts = []
    tool_calls_processed = False

    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if item.get("type") == "text":
                parts.append(item["text"])
            elif item.get("type") == "tool_use":
                parts.append(f"\n🔧 Tool Call: {item['name']}")
                parts.append(f"   Args: {json.dumps(item['input'], indent=2)}")
                parts.append(f"   ID: {item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI format) -
    # only if not already processed
    if (
        not tool_calls_processed
        and hasattr(message, "tool_calls")
        and message.tool_calls
    ):
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID: {tool_call['id']}")

    formatted_content = "\n".join(parts)
    return Markdown(formatted_content)


def format_messages(messages: Iterable[_DeepAgentMessage]):
    """Format and display a list of messages with Rich formatting."""
    for m in messages:
        content = format_message_content(m)
        if isinstance(m, HumanMessage):
            console.print(Panel(content, title="Human", border_style="blue"))
        elif isinstance(m, AIMessage):
            console.print(Panel(content, title="Assistant", border_style="green"))
        elif isinstance(m, ToolMessage):
            console.print(Panel(content, title="Tool Output", border_style="yellow"))
        else:
            console.print(Panel(content, title=f"📝 {type(m)}", border_style="white"))


def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """Display a prompt with rich formatting and XML tag highlighting.

    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")

    """
    # Create a formatted display of the prompt
    formatted_text = Text(prompt_text)
    # Highlight XML tags
    formatted_text.highlight_regex(r"<[^>]+>", style="bold blue")
    # Highlight headers
    formatted_text.highlight_regex(r"##[^#\n]+", style="bold magenta")
    # Highlight sub-headers
    formatted_text.highlight_regex(r"###[^#\n]+", style="bold cyan")

    # Display in a panel for better presentation
    console.print(
        Panel(
            formatted_text,
            title=f"[bold green]{title}[/bold green]",
            border_style=border_style,
            padding=(1, 2),
        ),
    )
