"""Command line interface."""

from pathlib import Path
from typing import Annotated

import rich
from loguru import logger
from rich.markdown import Markdown
from typer import Option, Typer

from clurb import agents

app = Typer()


@app.command()
def prepare(
    output_dir: Annotated[
        Path,
        Option(
            "--output-dir",
            "-o",
            help="Directory that will be the agent's workspace and output directory.",
        ),
    ],
    prompt: Annotated[str, Option("--prompt", "-p", help="Prompt for the agent.")],
    model: Annotated[str, Option("--model", "-m", help="Model for the core agent.")],
) -> None:
    """Prepare a paper for journal club."""
    output_dir.mkdir(exist_ok=True, parents=True)
    logger.add(output_dir / "clurb.log", level="TRACE")

    logger.info(f"Instantiating agent with primary model '{model}'.")
    agent = agents.build_research_agent(model=model, workspace=output_dir)

    try:
        logger.info("Running agent with user prompt.")
        result = agent.invoke(input={"messages": [{"role": "user", "content": prompt}]})
        logger.info("Agent finished.")
    except BaseException as err:
        logger.error(f"Agent errored: {err}")
        raise err

    rich.print(Markdown(result["messages"][-1].content))

    logger.success("Done!")
