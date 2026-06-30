from __future__ import annotations

import json
from pathlib import Path
from collections.abc import Callable

from .agent import GenerativeAgent
from .environment import CampusWorld
from .llm import build_llm
from .memory import MemoryStream
from .models import StepLog


AGENT_SUMMARY = (
    "Maya Chen is a careful, curious student researcher. She is building a small "
    "generative-agent sandbox for a take-home assignment. She wants the simulation "
    "to produce readable evidence that memory retrieval and reflection affected "
    "later behavior. She values simple, inspectable systems over flashy scope."
)


def run_simulation(
    *,
    steps: int,
    llm_mode: str,
    seed: int,
    reflection_interval: int,
    top_k: int,
    on_step: Callable[[GenerativeAgent, CampusWorld, list[StepLog], int, int], None] | None = None,
) -> tuple[GenerativeAgent, CampusWorld, list[StepLog]]:
    memory = MemoryStream()
    llm = build_llm(llm_mode)
    world = CampusWorld(seed=seed)
    agent = GenerativeAgent(
        name="Maya Chen",
        summary=AGENT_SUMMARY,
        memory=memory,
        llm=llm,
        reflection_interval=reflection_interval,
        top_k=top_k,
    )
    agent.seed_memories()

    logs: list[StepLog] = []
    for step in range(1, steps + 1):
        logs.append(agent.step(world, step))
        if on_step:
            on_step(agent, world, logs, step, steps)
    return agent, world, logs


def write_markdown_log(path: Path, *, logs: list[StepLog], llm_mode: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Generative Agent Sandbox Run",
        "",
        f"LLM mode: `{llm_mode}`",
        f"Steps: `{len(logs)}`",
        "",
        "This transcript shows observations, retrieved memories, actions, and reflections.",
        "",
    ]

    for entry in logs:
        lines.extend(
            [
                f"## Step {entry.step} - {entry.time_label}",
                "",
                f"Location before: `{entry.location_before}`",
                "",
                f"Observation #{entry.observation.id}: {entry.observation.text}",
                "",
                "Retrieved memories:",
            ]
        )
        for result in entry.retrieved:
            lines.append(
                "- "
                f"#{result.memory.id} [{result.memory.kind}, score={result.score:.2f}, "
                f"R={result.recency:.2f}, I={result.importance:.2f}, Rel={result.relevance:.2f}] "
                f"{result.memory.text}"
            )
        lines.extend(
            [
                "",
                (
                    f"Decision: `{entry.decision.action_id}` "
                    f"({entry.decision.action}) -> `{entry.decision.destination}`"
                ),
                "",
                f"Reason: {entry.decision.reason}",
                "",
                f"Outcome #{entry.outcome.id}: {entry.outcome.text}",
                "",
            ]
        )
        if entry.reflection:
            lines.append("Reflection:")
            for memory in entry.reflection:
                evidence = ", ".join(f"#{memory_id}" for memory_id in memory.evidence_ids)
                lines.append(f"- #{memory.id}: {memory.text} Evidence: {evidence or 'recent memories'}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_memory_json(path: Path, agent: GenerativeAgent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(agent.memory.to_dicts(), indent=2),
        encoding="utf-8",
    )


def write_summary_json(path: Path, *, agent: GenerativeAgent, world: CampusWorld, logs: list[StepLog]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reflection_count = sum(1 for memory in agent.memory.memories if memory.kind == "reflection")
    path.write_text(
        json.dumps(
            {
                "steps": len(logs),
                "final_location": world.location,
                "final_hunger": world.hunger,
                "final_energy": world.energy,
                "final_focus": world.focus,
                "final_project_progress": world.progress,
                "memory_count": len(agent.memory.memories),
                "reflection_count": reflection_count,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
