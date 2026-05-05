"""Command line interface."""

import time
from pathlib import Path
from typing import Annotated

import rich
from langchain.messages import HumanMessage
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

    tic = time.perf_counter()
    try:
        logger.info("Running agent with user prompt.")
        human_message = HumanMessage(prompt)
        result = agent.invoke(human_message)
        logger.info("Agent finished.")
    except BaseException as err:
        logger.error(f"Agent errored: {err}")
        raise err

    toc = time.perf_counter()
    runtime = (toc - tic) / 60
    rich.print(Markdown(result["messages"][-1].content))
    logger.success(f"Done (total agent runtime: {runtime:0.2f} min.)!")
