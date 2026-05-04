"""Project commands."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Final

import nox
from nox.command import CommandFailed

nox.options.default_venv_backend = "uv"

BENCHMARK_DIR: Final[Path] = Path("./benchmarks/").resolve()
BENCHMARK_DATETIME_FMT: Final[str] = "%Y-%m-%d_%H-%M-%S"


@nox.session
def lint(s: nox.Session) -> None:
    """Run linters."""
    s.install("ruff")
    s.run("ruff", "check", "--fix", "src/")
    s.run("ruff", "format", "src/")


@nox.session(name="bench")
def benchmark(s: nox.Session) -> None:
    """Execute benchmark."""
    s.install(".")
    dt = datetime.now()
    output_dir = BENCHMARK_DIR / f"{dt.strftime(BENCHMARK_DATETIME_FMT)}"
    output_dir.mkdir(parents=True, exist_ok=False)
    s.log(f"Output dir: {output_dir.relative_to(Path().resolve())}")
    clurb_prompt = (
        "Download the scientific publication at this URL "
        "https://www.jbc.org/article/S0021-9258(20)39070-0/fulltext and parse it to "
        "Markdown. Save the result to a file 'paper.md'. Read the paper and identify "
        "the top results and key take-aways. What are the next steps? Who are the "
        "primary and anchor authors of the paper? What can you tell me about these two "
        "authors? In your final message, please summarize what steps you performed and "
        "the tool calls you made."
    )
    model = "gemma4:26b"  # "gemma4:e4b"

    with (output_dir / "inputs.json").open("w") as f:
        data = {
            "model": model,
            "timestamp": dt.strftime(BENCHMARK_DATETIME_FMT),
            "prompt": clurb_prompt,
        }
        json.dump(data, f, indent=4)

    exit_code_file = output_dir / "exitcode.txt"
    try:
        s.run(
            "clurb",
            "--output-dir",
            str(output_dir),
            "--prompt",
            clurb_prompt,
            "--model",
            model,
        )
        with exit_code_file.open("w") as fh:
            fh.write("0")
    except CommandFailed as err:
        with exit_code_file.open("w") as fh:
            fh.write("1")
        raise err


@nox.session(name="rm-old-bench", tags=["clean"], default=False)
def clear_old_benchmarks(s: nox.Session) -> None:
    """Remove all but the most recent benchmark."""
    all_benches = {
        datetime.strptime(p.name, BENCHMARK_DATETIME_FMT): p
        for p in BENCHMARK_DIR.iterdir()
    }
    latest_bench = max(all_benches.keys())
    s.log(f"Latest bench: {latest_bench}")

    c = 0
    for dt, bench_dir in all_benches.items():
        if dt == latest_bench:
            continue
        shutil.rmtree(bench_dir)
        c += 1
    s.log(f"Removed {c} old benchmark outputs.")
