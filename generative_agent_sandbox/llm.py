from __future__ import annotations

import json
import os
import re
import time
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


class OpenAIChatLLM(BaseLLM):
    """OpenAI-compatible chat client for live simulation runs."""

    def __init__(self, *, provider: str = "openai") -> None:
        self.provider = provider
        self.live_importance = not _env_falsey("LIVE_LLM_IMPORTANCE")

        if provider == "gateway":
            self.api_key = (
                os.getenv("AI_GATEWAY_API_KEY")
                or os.getenv("VERCEL_AI_GATEWAY_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("AI_GATEWAY_MODEL", "openai/gpt-5")
            self.base_url = (
                os.getenv("AI_GATEWAY_BASE_URL")
                or os.getenv("OPENAI_BASE_URL")
                or "https://ai-gateway.vercel.sh/v1"
            ).rstrip("/")
            required_key_name = "AI_GATEWAY_API_KEY"
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-5")
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            required_key_name = "OPENAI_API_KEY"

        if not self.api_key:
            raise RuntimeError(f"{required_key_name} is required when --llm {provider} is used.")

    def rate_importance(self, text: str, *, kind: str) -> float:
        if not self.live_importance:
            raise RuntimeError("LIVE_LLM_IMPORTANCE=false is disabled for live-only experiments.")

        prompt = (
            "Rate the likely importance of this memory for a human-like agent from 1 to 10. "
            "Return only a number.\n\n"
            f"Memory type: {kind}\nMemory: {text}"
        )
        try:
            response = self._complete(prompt, temperature=0.0, max_tokens=64)
            match = re.search(r"\d+(?:\.\d+)?", response)
            return min(10.0, max(1.0, float(match.group(0)))) if match else 3.0
        except Exception as error:
            raise RuntimeError("Live importance scoring failed.") from error

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
Choose one useful 10-minute action, not a long plan.
Prefer a substantive action over moving if Maya can already make progress where she is.
Only choose talk_with_jordan when the current observation says Jordan is present or a retrieved memory says a Jordan follow-up is urgent.
When Jordan is present and Maya is waiting on his follow-up, treat the conversation as time-sensitive because the opportunity may pass.
Do not keep waiting or sending messages after repeated failed Jordan follow-ups if Maya can make project progress instead.
If Jordan is physically present and about to leave, prefer a short direct conversation over routine eating, resting, or moving unless Maya is completely unable to function.
If the implementation is ready to write up and Maya has the needed comparison evidence, choose write_evidence_section instead of more generic project work.

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
            raw = self._complete(prompt, temperature=0.35, max_tokens=800)
            data = _extract_json(raw)
            action_id = normalize_action_id(str(data.get("action_id", data.get("action", ""))))
            if action_id is None:
                raise ValueError(f"Unknown action id: {data}")
            reason = str(data["reason"])
            return Decision.from_action_id(action_id, reason=reason)
        except Exception as error:
            detail = f" Raw response: {raw!r}" if "raw" in locals() else ""
            raise RuntimeError(f"Live action selection failed.{detail}") from error

    def reflect(self, *, recent_memories: list[Memory]) -> list[ReflectionDraft]:
        numbered = "\n".join(f"{memory.id}. {memory.text}" for memory in recent_memories)
        prompt = f"""
Given the memories below, infer 3 to 5 higher-level insights about Maya's goals, habits, concerns, relationships, or changing priorities.
When memories show repeated social friction, synthesize the practical lesson Maya should use later. For example, if messages or broad check-ins keep failing, state that she should ask in person for exact details.
Return strict JSON as an array of objects with keys: text, evidence_ids, importance.
Evidence ids must refer to memory numbers below.

Memories:
{numbered}
""".strip()
        try:
            raw = self._complete(prompt, temperature=0.25, max_tokens=1200)
            parsed = _extract_json(raw)
            drafts = []
            for item in parsed:
                drafts.append(
                    ReflectionDraft(
                        text=str(item["text"]),
                        evidence_ids=[int(value) for value in item.get("evidence_ids", [])],
                        importance=_coerce_importance(item.get("importance", 8.0)),
                    )
                )
            return drafts[:5]
        except Exception as error:
            detail = f" Raw response: {raw!r}" if "raw" in locals() else ""
            raise RuntimeError(f"Live reflection failed.{detail}") from error

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
        if "gpt-5" in self.model:
            payload.pop("max_tokens")
            payload["max_completion_tokens"] = max(max_tokens, 2048)
            payload["reasoning_effort"] = "minimal"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")
                if attempt < 3 and _is_retryable_http_error(error, detail):
                    time.sleep(2 * attempt)
                    continue
                raise RuntimeError(f"OpenAI request failed: {detail}") from error
            except urllib.error.URLError as error:
                if attempt < 3:
                    time.sleep(2 * attempt)
                    continue
                raise RuntimeError(f"OpenAI request failed: {error}") from error
        raise RuntimeError("OpenAI request failed after retries.")


def build_llm(mode: str) -> BaseLLM:
    if mode == "openai":
        return OpenAIChatLLM(provider="openai")
    if mode == "gateway":
        return OpenAIChatLLM(provider="gateway")
    raise ValueError(f"Unknown LLM mode: {mode}")


def _env_falsey(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"0", "false", "no", "off"}


def _is_retryable_http_error(error: urllib.error.HTTPError, detail: str) -> bool:
    return error.code >= 500 or '"isRetryable":true' in detail


def _coerce_importance(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().lower()
    label_scores = {
        "critical": 10.0,
        "very high": 9.5,
        "high": 9.0,
        "medium": 6.0,
        "moderate": 6.0,
        "low": 3.0,
    }
    if text in label_scores:
        return label_scores[text]

    match = re.search(r"\d+(?:\.\d+)?", text)
    if match:
        return float(match.group(0))

    return 8.0


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
