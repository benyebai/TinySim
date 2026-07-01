from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from .models import (
    Decision,
    Memory,
    ReflectionDraft,
    RetrievalResult,
    action_schema_text,
    normalize_action_id,
)


class BaseLLM:
    def rate_importance(self, text: str, *, kind: str) -> float:
        raise NotImplementedError

    def choose_action(
        self,
        *,
        agent_summary: str,
        world_state: str,
        observation: str,
        retrieved: list[RetrievalResult],
    ) -> Decision:
        raise NotImplementedError

    def reflect(self, *, recent_memories: list[Memory]) -> list[ReflectionDraft]:
        raise NotImplementedError


class DeterministicLLM(BaseLLM):
    """A no-network stand-in that keeps the architecture runnable."""

    def rate_importance(self, text: str, *, kind: str) -> float:
        text_lower = text.lower()
        score = 3.0
        if kind == "reflection":
            score = 8.0
        if any(word in text_lower for word in ["deadline", "assignment", "professor", "evidence"]):
            score += 3
        if any(word in text_lower for word in ["baseline", "no-retrieval", "compare"]):
            score += 3
        if any(word in text_lower for word in ["ignored food", "stomach", "foggy", "drifting"]):
            score += 2
        if any(word in text_lower for word in ["progress", "reflection", "retrieval", "memory"]):
            score += 2
        if any(word in text_lower for word in ["quiet", "park", "coffee", "snack"]):
            score += 1
        return min(10.0, score)

    def choose_action(
        self,
        *,
        agent_summary: str,
        world_state: str,
        observation: str,
        retrieved: list[RetrievalResult],
    ) -> Decision:
        current = " ".join([world_state, observation]).lower()
        retrieved_text = " ".join(item.memory.text for item in retrieved).lower()
        retrieved_reflections = " ".join(
            item.memory.text for item in retrieved if item.memory.kind == "reflection"
        ).lower()

        ready_for_evidence = (
            "final report section" in current
            or "evidence section is still blank" in current
            or "implementation feels complete" in current
        )
        remembered_baseline_requirement = (
            "no-retrieval baseline" in retrieved_text
            or "no retrieval baseline" in retrieved_text
            or "compare the full agent" in retrieved_text
            or "compare full" in retrieved_text
        )

        if "very hungry" in current or "stomach" in current or "skipped a meal" in current:
            return Decision.from_action_id(
                "eat_meal",
                reason="Maya directly notices hunger, so eating is the most believable next action.",
            )

        if "energy feels low" in current or "mentally foggy" in current:
            return Decision.from_action_id(
                "rest",
                reason="Maya directly notices low energy, so resting is more believable than pushing ahead.",
            )

        if "professor lin says" in current or "discussion starts soon" in current:
            return Decision.from_action_id(
                "attend_discussion",
                reason="The current discussion contains assignment guidance Maya should hear.",
            )

        if "clearer evidence" in current:
            return Decision.from_action_id(
                "work_on_project",
                reason="The professor's note makes the implementation evidence more important than generic progress.",
            )

        if "same action" in current or "appeared in her log several times" in current:
            return Decision.from_action_id(
                "organize_notes",
                reason="The log suggests repetition, so Maya should adjust the plan instead of repeating blindly.",
            )

        if "attention is fragile" in current or "attention keeps drifting" in current:
            return Decision.from_action_id(
                "take_break",
                reason="Maya directly notices fragile attention, so a reset break is believable.",
            )

        if "evidence section has a draft" in current:
            return Decision.from_action_id(
                "review_notes",
                reason="The evidence section already has a draft, so Maya reviews notes instead of rewriting it.",
            )

        if ready_for_evidence and remembered_baseline_requirement:
            return Decision.from_action_id(
                "write_evidence_section",
                reason=(
                    "Maya remembers Professor Lin's requirement to compare the full agent "
                    "with a no-retrieval baseline, so the evidence section should address that."
                ),
            )

        if (
            "breaks seem to help" in retrieved_reflections
            or "focus appears tied to managing basic needs" in retrieved_reflections
        ) and ("focus feels workable" in current or "push ahead or reset" in current):
            return Decision.from_action_id(
                "take_break",
                reason=(
                    "A retrieved reflection says short reset breaks help Maya recover focus, "
                    "so she uses one before forcing more work."
                ),
            )

        if "notes are scattered" in current or "checklist" in current:
            return Decision.from_action_id(
                "organize_notes",
                reason="Scattered notes are blocking progress more than effort is.",
            )

        if ready_for_evidence and not remembered_baseline_requirement:
            return Decision.from_action_id(
                "review_notes",
                reason="Maya sees that the report needs evidence, but no specific remembered requirement is available.",
            )

        if "quiet desk" in current or "library" in current or "early implementation" in current:
            return Decision.from_action_id(
                "work_on_project",
                reason="The current setting supports focused project work.",
            )

        return Decision.from_action_id(
            "work_on_project",
            reason="With no stronger cue available, Maya continues the project work.",
        )

    def reflect(self, *, recent_memories: list[Memory]) -> list[ReflectionDraft]:
        if not recent_memories:
            return []

        text_blob = " ".join(memory.text.lower() for memory in recent_memories)
        ids_by_keyword = _ids_by_keyword(recent_memories)
        latest_step = max(memory.step for memory in recent_memories)
        drafts: list[ReflectionDraft] = []

        if any(word in text_blob for word in ["hungry", "stomach", "meal", "food", "snack"]):
            drafts.append(
                ReflectionDraft(
                    text=f"By step {latest_step}, Maya's focus appears tied to managing basic needs; ignoring meals makes project work less effective.",
                    evidence_ids=ids_by_keyword(["hungry", "stomach", "meal", "food", "snack"]),
                    importance=8.0,
                )
            )

        if "no-retrieval baseline" in text_blob or "no retrieval baseline" in text_blob:
            drafts.append(
                ReflectionDraft(
                    text=(
                        f"By step {latest_step}, Maya has a concrete reporting requirement: "
                        "compare the full agent with a no-retrieval baseline rather than only claiming memory matters."
                    ),
                    evidence_ids=ids_by_keyword(["no-retrieval", "no retrieval", "baseline", "compare"]),
                    importance=10.0,
                )
            )

        if any(word in text_blob for word in ["library", "quiet desk", "whiteboard", "progress"]):
            drafts.append(
                ReflectionDraft(
                    text=f"By step {latest_step}, Maya tends to make the clearest project progress in structured, quiet spaces.",
                    evidence_ids=ids_by_keyword(["library", "quiet", "whiteboard", "progress"]),
                    importance=8.0,
                )
            )

        if any(word in text_blob for word in ["professor", "evidence", "retrieval", "memory"]):
            drafts.append(
                ReflectionDraft(
                    text=f"By step {latest_step}, the project looks stronger when the run log explicitly shows which memories shaped each action.",
                    evidence_ids=ids_by_keyword(["professor", "evidence", "retrieval", "memory"]),
                    importance=9.0,
                )
            )

        if any(word in text_blob for word in ["park", "walk", "break", "focus"]):
            drafts.append(
                ReflectionDraft(
                    text=f"By step {latest_step}, short reset breaks seem to help Maya recover focus instead of forcing low-quality work.",
                    evidence_ids=ids_by_keyword(["park", "walk", "break", "focus"]),
                    importance=7.0,
                )
            )

        if not drafts:
            drafts.append(
                ReflectionDraft(
                    text=f"By step {latest_step}, Maya is gradually turning scattered observations into an implementation plan.",
                    evidence_ids=[memory.id for memory in recent_memories[-5:]],
                    importance=7.0,
                )
            )

        return _dedupe_reflections(drafts)[:4]


class OpenAIChatLLM(BaseLLM):
    """OpenAI-compatible chat client. Falls back to deterministic behavior on errors."""

    def __init__(self, *, provider: str = "openai", fallback: BaseLLM | None = None) -> None:
        self.fallback = fallback or DeterministicLLM()
        self.provider = provider
        self.live_importance = _env_truthy("LIVE_LLM_IMPORTANCE")

        if provider == "gateway":
            self.api_key = (
                os.getenv("AI_GATEWAY_API_KEY")
                or os.getenv("VERCEL_AI_GATEWAY_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("AI_GATEWAY_MODEL", "openai/gpt-4.1-mini")
            self.base_url = (
                os.getenv("AI_GATEWAY_BASE_URL")
                or os.getenv("OPENAI_BASE_URL")
                or "https://ai-gateway.vercel.sh/v1"
            ).rstrip("/")
            required_key_name = "AI_GATEWAY_API_KEY"
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            required_key_name = "OPENAI_API_KEY"

        if not self.api_key:
            raise RuntimeError(f"{required_key_name} is required when --llm {provider} is used.")

    def rate_importance(self, text: str, *, kind: str) -> float:
        if not self.live_importance:
            return self.fallback.rate_importance(text, kind=kind)

        prompt = (
            "Rate the likely importance of this memory for a human-like agent from 1 to 10. "
            "Return only a number.\n\n"
            f"Memory type: {kind}\nMemory: {text}"
        )
        try:
            response = self._complete(prompt, temperature=0.0, max_tokens=8)
            match = re.search(r"\d+(?:\.\d+)?", response)
            return min(10.0, max(1.0, float(match.group(0)))) if match else 3.0
        except Exception:
            return self.fallback.rate_importance(text, kind=kind)

    def choose_action(
        self,
        *,
        agent_summary: str,
        world_state: str,
        observation: str,
        retrieved: list[RetrievalResult],
    ) -> Decision:
        memories = "\n".join(
            f"- #{item.memory.id} ({item.memory.kind}, score={item.score:.2f}): {item.memory.text}"
            for item in retrieved
        )
        prompt = f"""
You control one text-based generative agent. Keep the agent grounded in the provided perceptual state and memories.
Return strict JSON with keys: action_id, reason.
action_id must be exactly one of the allowed ids below. Do not invent ids.
Use retrieved memories when they contain a specific remembered requirement. Do not assume hidden numeric state.

Allowed actions:
{action_schema_text()}

Agent:
{agent_summary}

World state:
{world_state}

Current observation:
{observation}

Retrieved memories:
{memories}
""".strip()
        try:
            data = _extract_json(self._complete(prompt, temperature=0.35, max_tokens=220))
            action_id = normalize_action_id(str(data.get("action_id", data.get("action", ""))))
            if action_id is None:
                raise ValueError(f"Unknown action id: {data}")
            reason = str(data["reason"])
            return Decision.from_action_id(action_id, reason=reason)
        except Exception:
            return self.fallback.choose_action(
                agent_summary=agent_summary,
                world_state=world_state,
                observation=observation,
                retrieved=retrieved,
            )

    def reflect(self, *, recent_memories: list[Memory]) -> list[ReflectionDraft]:
        numbered = "\n".join(f"{memory.id}. {memory.text}" for memory in recent_memories)
        prompt = f"""
Given the memories below, infer 3 to 5 higher-level insights about Maya's goals, habits, concerns, or changing priorities.
Return strict JSON as an array of objects with keys: text, evidence_ids, importance.
Evidence ids must refer to memory numbers below.

Memories:
{numbered}
""".strip()
        try:
            raw = self._complete(prompt, temperature=0.25, max_tokens=500)
            parsed = _extract_json(raw)
            drafts = []
            for item in parsed:
                drafts.append(
                    ReflectionDraft(
                        text=str(item["text"]),
                        evidence_ids=[int(value) for value in item.get("evidence_ids", [])],
                        importance=float(item.get("importance", 8.0)),
                    )
                )
            return drafts[:5]
        except Exception:
            return self.fallback.reflect(recent_memories=recent_memories)

    def _complete(self, prompt: str, *, temperature: float, max_tokens: int) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a concise simulation component. Follow output format exactly.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI request failed: {detail}") from error
        return body["choices"][0]["message"]["content"]


def build_llm(mode: str) -> BaseLLM:
    if mode == "deterministic":
        return DeterministicLLM()
    if mode == "openai":
        return OpenAIChatLLM(provider="openai")
    if mode == "gateway":
        return OpenAIChatLLM(provider="gateway")
    raise ValueError(f"Unknown LLM mode: {mode}")


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _ids_by_keyword(memories: list[Memory]):
    def find(keywords: list[str]) -> list[int]:
        found: list[int] = []
        for memory in memories:
            text = memory.text.lower()
            if any(keyword in text for keyword in keywords):
                found.append(memory.id)
        return found[-6:]

    return find


def _dedupe_reflections(drafts: list[ReflectionDraft]) -> list[ReflectionDraft]:
    seen: set[str] = set()
    unique: list[ReflectionDraft] = []
    for draft in drafts:
        key = draft.text.lower()
        if key not in seen:
            seen.add(key)
            unique.append(draft)
    return unique


def _extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_candidates = [index for index in [text.find("{"), text.find("[")] if index != -1]
        if not start_candidates:
            raise
        start = min(start_candidates)
        end = max(text.rfind("}"), text.rfind("]"))
        return json.loads(text[start : end + 1])
