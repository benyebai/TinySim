from __future__ import annotations

import random
from dataclasses import dataclass

from .models import ACTION_BY_ID, Decision, normalize_action_id


@dataclass
class WorldSnapshot:
    step: int
    time_label: str
    location: str
    hunger: int
    energy: int
    focus: int
    progress: int
    mood: str
    evidence_section_written: bool

    def describe(self) -> str:
        body_state = _body_state(self.hunger, self.energy, self.focus)
        project_state = _project_state(self.progress, self.evidence_section_written)
        return (
            f"It is {self.time_label}. Maya is at the {self.location}. "
            f"{body_state} {project_state} Maya's mood is {self.mood}."
        )


class CampusWorld:
    """A small text world with enough pressure to make memory useful."""

    locations = ["Dorm", "Library", "Cafe", "Classroom", "Park", "Store"]

    def __init__(self, *, seed: int = 7) -> None:
        self.random = random.Random(seed)
        self.location = "Dorm"
        self.hunger = 3
        self.energy = 7
        self.focus = 5
        self.progress = 0
        self.mood = "curious"
        self.last_action = "woke up and checked the project notebook"
        self.evidence_section_written = False
        self.baseline_comparison_done = False

    def snapshot(self, step: int) -> WorldSnapshot:
        return WorldSnapshot(
            step=step,
            time_label=self.time_label(step),
            location=self.location,
            hunger=self.hunger,
            energy=self.energy,
            focus=self.focus,
            progress=self.progress,
            mood=self.mood,
            evidence_section_written=self.evidence_section_written,
        )

    def time_label(self, step: int) -> str:
        minutes = 8 * 60 + (step - 1) * 10
        hour = (minutes // 60) % 24
        minute = minutes % 60
        suffix = "am" if hour < 12 else "pm"
        display_hour = hour % 12 or 12
        return f"{display_hour}:{minute:02d} {suffix}"

    def observe(self, step: int) -> str:
        snapshot = self.snapshot(step)
        scheduled = {
            6: (
                "During discussion, Professor Lin says the final report should compare "
                "the full agent with a no-retrieval baseline, not just claim memory matters."
            ),
            12: "Maya notices her project notes are scattered across three documents.",
            18: "A quiet desk opens near the library window.",
            21: "Maya reaches a pause between work sessions and wonders whether to push ahead or reset.",
            24: "The cafe line is short and the smell of soup reminds Maya she skipped a meal.",
            31: "Maya rereads the assignment note that says the surprises matter most.",
            37: "A professor's comment in the margin asks for clearer evidence of memory retrieval.",
            44: "The park is unusually quiet, making it easier to think without pressure.",
            52: "Maya notices that the same action has appeared in her log several times.",
            61: "Maya reaches the final report section and needs to decide what evidence belongs there.",
            70: "The library is closing soon, so Maya needs to decide what matters most now.",
        }
        if step in scheduled:
            return scheduled[step]

        if self.hunger >= 8:
            return "Maya's stomach growls and she realizes she has been ignoring food."
        if self.energy <= 2:
            return "Maya feels mentally foggy and keeps rereading the same line."
        if self.focus <= 2:
            return "Maya's attention keeps drifting away from the simulation project."

        by_location = {
            "Dorm": [
                "Maya sees her notebook open to a rough plan for the agent simulation.",
                "The dorm room is quiet, but the bed is a little too tempting.",
                "A half-finished checklist sits beside Maya's laptop.",
            ],
            "Library": [
                "The library has a quiet study table and a whiteboard nearby.",
                "Someone nearby is whispering about deadlines, but the room is mostly calm.",
                "Maya sees a shelf of cognitive science books near her desk.",
            ],
            "Cafe": [
                "The cafe is warm, noisy, and full of people taking quick breaks.",
                "Maya spots a small table where she could eat and review notes.",
                "The barista is moving quickly through a short line of orders.",
            ],
            "Classroom": [
                "The classroom board still has examples about agents and bounded memory.",
                "A few students are comparing notes after the discussion.",
                "Maya sees an empty seat near the front of the classroom.",
            ],
            "Park": [
                "The park path is calm and gives Maya room to think.",
                "Maya hears distant traffic but mostly notices the wind in the trees.",
                "A bench near the path looks like a good place to pause.",
            ],
            "Store": [
                "The store shelf has trail mix, notebooks, and pens.",
                "Maya sees a small display of snacks near the checkout counter.",
                "The store is practical but not especially inspiring.",
            ],
        }
        return self.random.choice(by_location[snapshot.location])

    def apply_decision(self, decision: Decision, step: int) -> str:
        destination = self._normalize_location(decision.destination)
        self.location = destination

        action_id = decision.action_id or normalize_action_id(decision.action) or "unknown"
        if action_id == "eat_meal":
            self.hunger = max(0, self.hunger - 5)
            self.energy = min(10, self.energy + 2)
            self.focus = min(10, self.focus + 1)
            self.mood = "steadier"
            result = "Maya eats something and feels more able to think clearly."
        elif action_id == "buy_snack":
            self.hunger = max(0, self.hunger - 3)
            self.energy = min(10, self.energy + 1)
            self.focus = min(10, self.focus + 1)
            self.mood = "steadier"
            result = "Maya buys a snack and keeps hunger from taking over."
        elif action_id == "rest":
            self.hunger = min(10, self.hunger + 1)
            self.energy = min(10, self.energy + 4)
            self.focus = min(10, self.focus + 2)
            self.mood = "rested"
            result = "Maya rests and recovers energy."
        elif action_id == "review_notes":
            self.progress = min(100, self.progress + 2)
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "reflective"
            result = "Maya annotates the transcript and preserves evidence for the writeup."
        elif action_id == "write_evidence_section":
            self.progress = min(100, self.progress + 6)
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "analytical"
            self.evidence_section_written = True
            if _mentions_baseline_requirement(decision.reason):
                self.baseline_comparison_done = True
                result = (
                    "Maya writes the evidence section and explicitly compares the full run "
                    "with a no-retrieval baseline."
                )
            else:
                result = "Maya writes a general evidence section for the report."
        elif action_id == "work_on_project":
            gain = 4 if self.location == "Library" else 2
            if self.focus >= 5 and self.energy >= 4:
                gain += 2
            if self.hunger >= 8 or self.energy <= 2 or self.focus <= 2:
                gain = max(1, gain - 2)
            self.progress = min(100, self.progress + gain)
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "absorbed"
            result = f"Maya makes {gain} points of project progress."
        elif action_id == "attend_discussion":
            self.progress = min(100, self.progress + 3)
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = min(10, self.focus + 1)
            self.mood = "thoughtful"
            result = "Maya attends discussion and leaves with a clearer implementation idea."
        elif action_id == "take_break":
            self.hunger = min(10, self.hunger + 1)
            self.energy = min(10, self.energy + 1)
            self.focus = min(10, self.focus + 3)
            self.mood = "reset"
            result = "Maya takes a short reset break and returns with better focus."
        elif action_id == "organize_notes":
            self.progress = min(100, self.progress + 2)
            self.focus = min(10, self.focus + 2)
            self.energy = max(0, self.energy - 1)
            self.mood = "organized"
            result = "Maya organizes the project notes into a clearer plan."
        elif action_id in ACTION_BY_ID:
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            result = f"Maya relocates to the {self.location} and prepares for the next step."
        else:
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            result = "Maya follows through, though the effect is modest."

        self.last_action = decision.action
        return f"At {self.time_label(step)}, {result} Reason: {decision.reason}"

    def tick(self) -> None:
        if self.hunger >= 8:
            self.focus = max(0, self.focus - 1)
        if self.energy <= 2:
            self.focus = max(0, self.focus - 1)

    def _normalize_location(self, destination: str) -> str:
        destination_lower = destination.strip().lower()
        for location in self.locations:
            if location.lower() == destination_lower:
                return location
        for location in self.locations:
            if location.lower() in destination_lower:
                return location
        return self.location


def _body_state(hunger: int, energy: int, focus: int) -> str:
    cues: list[str] = []
    if hunger >= 8:
        cues.append("Maya feels very hungry")
    elif hunger >= 5:
        cues.append("Maya feels a little hungry")
    else:
        cues.append("Maya is not especially hungry")

    if energy <= 2:
        cues.append("her energy feels low")
    elif energy >= 7:
        cues.append("her energy feels steady")
    else:
        cues.append("her energy feels usable")

    if focus <= 2:
        cues.append("her attention is fragile")
    elif focus >= 7:
        cues.append("her focus feels sharp")
    else:
        cues.append("her focus feels workable")

    return ", ".join(cues) + "."


def _project_state(progress: int, evidence_section_written: bool) -> str:
    if progress < 25:
        return "The project is still in early implementation."
    if progress < 60:
        return "The project has a working core, but the evidence is thin."
    if progress < 90:
        return "The project mostly works, and the report needs stronger evidence."
    if evidence_section_written:
        return "The implementation feels complete, and the evidence section has a draft."
    return "The implementation feels complete, but the final evidence section is still blank."


def _mentions_baseline_requirement(reason: str) -> bool:
    reason_lower = reason.lower()
    return any(
        phrase in reason_lower
        for phrase in [
            "no-retrieval",
            "no retrieval",
            "without retrieval",
            "baseline",
            "compare the full",
            "compare full",
        ]
    )
