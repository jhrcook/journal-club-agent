"""Miscellaneous utilities."""

import json
from pathlib import Path
from typing import Iterable

from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

_DeepAgentMessage = AIMessage | HumanMessage | ToolMessage | SystemMessage


def format_message_content(m: _DeepAgentMessage) -> str:
    """Format message content to a string."""
    txt = ""
    if isinstance(m.content, str):
        txt = m.content.strip()
    else:
        for item in m.content:
            if isinstance(item, str):
                txt += item.strip() + "\n"
            else:
                txt += json.dumps(item, indent=2)

    txt = txt.strip()
    if not txt:
        txt = "(Empty.)"

    return txt


def _format_ai_message_metadata(m: AIMessage, txt: list[str]) -> None:
    txt.append("")
    if not m.tool_calls:
        txt.append("Tool calls: None.")
    else:
        txt.append("Tool calls:")
        txt.append("")
        for tool_call in m.tool_calls:
            txt.append(f"- tool: {tool_call.get('name')}")
            txt.append(f"  ID: {tool_call.get('id')}")
            txt.append(f"  args: {tool_call.get('args')}")

    txt.append("")

    if m.usage_metadata:
        txt.append("Usage metadata:")
        txt.append("")
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = m.usage_metadata.get(key)
            value_str = "None" if value is None else f"{value:,d}"
            txt.append(f"- {key}: {value_str}")
    else:
        txt.append("Usage metadata: None.")
    txt.append("")


def format_message_metadata(m: _DeepAgentMessage) -> str:
    """Format message metadata into a string."""
    txt: list[str] = [f"Message type: {type(m).__name__}"]
    txt.append(f"Name: {m.name}")
    txt.append(f"ID: {m.id}")

    if isinstance(m, AIMessage):
        _format_ai_message_metadata(m, txt)
    # Can insert additional type-specific formatting branches here.

    return "\n".join(txt)


def write_chat_to_file(messages: Iterable[_DeepAgentMessage], output_md: Path) -> None:
    """Write a sequence of messages to file.

    Args:
        messages (Iterable[_DeepAgentMessage]): AI agent message thread.
        output_md (Path): Output markdown file.

    """
    with output_md.open("w") as fh:
        fh.write("# AI Agent Thread\n")
        for i, m in enumerate(messages, start=1):
            fh.write(f"\n## Message {i}\n\n")
            fh.write("### Metadata\n\n")
            fh.write(f"{format_message_metadata(m)}\n\n")
            fh.write("### Message content\n\n")
            fh.write(f"{format_message_content(m)}\n")
            fh.write(f"\n{'-' * 80}\n")
