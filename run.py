from __future__ import annotations

import argparse
import os
from pathlib import Path

from generative_agent_sandbox.simulation import (
    run_simulation,
    write_markdown_log,
    write_memory_json,
    write_summary_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the generative-agent sandbox.")
    parser.add_argument("--steps", type=int, default=80, help="Number of simulation steps to run.")
    parser.add_argument(
        "--llm",
        choices=["openai", "gateway"],
        default="gateway",
        help="LLM backend. gateway uses Vercel AI Gateway.",
    )
    parser.add_argument("--seed", type=int, default=7, help="Random seed for environment observations.")
    parser.add_argument(
        "--reflection-interval",
        type=int,
        default=20,
        help="Generate reflections every N steps.",
    )
    parser.add_argument("--top-k", type=int, default=6, help="Number of memories to retrieve per step.")
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("logs/sample_run.md"),
        help="Markdown transcript output path.",
    )
    parser.add_argument(
        "--memory",
        type=Path,
        default=Path("logs/memory.json"),
        help="Memory stream JSON output path.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("logs/summary.json"),
        help="Short run summary JSON output path.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=1,
        help="Save transcript, memory, and summary every N completed steps.",
    )
    return parser.parse_args()


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if _is_placeholder_env_value(value):
            continue
        if key not in os.environ or _is_placeholder_env_value(os.environ[key]):
            os.environ[key] = value


def _is_placeholder_env_value(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {
        "",
        "put_your_api_key_here",
        "your_key_here",
        "your_actual_key_here",
        "put_your_vercel_ai_gateway_key_here",
    }


def main() -> None:
    load_dotenv()
    args = parse_args()
    if args.steps < 1:
        raise SystemExit("--steps must be at least 1")
    if args.checkpoint_every < 1:
        raise SystemExit("--checkpoint-every must be at least 1")

    agent, world, logs = run_simulation(
        steps=args.steps,
        llm_mode=args.llm,
        seed=args.seed,
        reflection_interval=args.reflection_interval,
        top_k=args.top_k,
        on_step=build_checkpoint_callback(args),
    )
    write_markdown_log(args.log, logs=logs, llm_mode=args.llm)
    write_memory_json(args.memory, agent)
    write_summary_json(args.summary, agent=agent, world=world, logs=logs)

    print(f"Ran {args.steps} steps with {args.llm} mode.")
    print(f"Transcript: {args.log}")
    print(f"Memory stream: {args.memory}")
    print(f"Summary: {args.summary}")


def build_checkpoint_callback(args: argparse.Namespace):
    def checkpoint(agent, world, logs, step: int, total_steps: int) -> None:
        should_checkpoint = step % args.checkpoint_every == 0 or step == total_steps
        if should_checkpoint:
            write_markdown_log(args.log, logs=logs, llm_mode=args.llm)
            write_memory_json(args.memory, agent)
            write_summary_json(args.summary, agent=agent, world=world, logs=logs)

        status = "checkpoint saved" if should_checkpoint else "checkpoint skipped"
        print(f"Completed step {step}/{total_steps} ({status})", flush=True)

    return checkpoint


if __name__ == "__main__":
    main()
