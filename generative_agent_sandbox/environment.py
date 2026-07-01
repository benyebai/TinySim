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
    jordan_promised_baseline: bool
    jordan_result_received: bool

    def describe(self) -> str:
        body_state = _body_state(self.hunger, self.energy, self.focus)
        project_state = _project_state(self.progress, self.evidence_section_written)
        jordan_state = _jordan_state(self.jordan_promised_baseline, self.jordan_result_received)
        return (
            f"It is {self.time_label}. Maya is at the {self.location}. "
            f"{body_state} {project_state} {jordan_state} Maya's mood is {self.mood}."
        )


class CampusWorld:
    """A small text world with enough pressure to make memory useful."""

    locations = ["Dorm", "Library", "Cafe", "Classroom", "Park", "Store", "Campus"]

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
        self.jordan_promised_baseline = False
        self.jordan_wait_count = 0
        self.jordan_vague_replies = 0
        self.jordan_result_received = False
        self.jordan_result_used = False

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
            jordan_promised_baseline=self.jordan_promised_baseline,
            jordan_result_received=self.jordan_result_received,
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
            9: "Jordan catches Maya after class and asks whether she still needs help with baseline comparisons.",
            12: "Maya notices her project notes are scattered across three documents.",
            16: "Maya checks her phone and sees no useful message from Jordan about the baseline yet.",
            18: "A quiet desk opens near the library window.",
            21: "Maya reaches a pause between work sessions and wonders whether to push ahead or reset.",
            24: "The cafe line is short and the smell of soup reminds Maya she skipped a meal.",
            28: "Maya spots Jordan in the cafe; he looks friendly but distracted.",
            31: "Maya rereads the assignment note that says the surprises matter most.",
            37: "A professor's comment in the margin asks for clearer evidence of memory retrieval.",
            39: "Maya reviews the outline and notices Jordan's exact no-retrieval baseline result is still missing.",
            43: "Jordan is studying near the library window before leaving for lab.",
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
            "Campus": [
                "Students cross the campus path between classes.",
                "Maya sees classmates moving between the cafe, library, and classrooms.",
                "The campus path is busy enough that a quick conversation could happen naturally.",
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
        elif action_id == "wait_for_reply":
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "waiting"
            if self.jordan_promised_baseline and not self.jordan_result_received:
                self.jordan_wait_count += 1
                result = (
                    "Maya waits for Jordan's promised baseline message, but no useful "
                    "result arrives."
                )
            else:
                result = "Maya waits for a reply, but there is no useful update."
        elif action_id == "send_message":
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "checking in"
            if self.jordan_result_received:
                result = "Maya messages Jordan, but she already has his exact baseline result in her notes."
            elif self.jordan_promised_baseline:
                self.jordan_vague_replies += 1
                result = (
                    "Maya sends Jordan a follow-up message. Jordan replies that he thinks "
                    "the no-retrieval run mostly worked, then says he will check the details later."
                )
            else:
                self.jordan_promised_baseline = True
                result = (
                    "Maya messages Jordan about baseline runs. Jordan says he can help "
                    "and will send the no-retrieval result later."
                )
        elif action_id == "talk_with_jordan":
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "social"
            if self.jordan_result_received:
                result = "Maya chats with Jordan, but the useful baseline result is already in her notes."
            elif _asks_for_exact_jordan_result(decision.reason):
                self.jordan_promised_baseline = True
                self.jordan_result_received = True
                result = (
                    "Maya asks Jordan for the exact no-retrieval result and failure mode. "
                    "Jordan checks his notes: the no-retrieval run reached progress 100, "
                    "but it never wrote the professor-required baseline comparison."
                )
            elif not self.jordan_promised_baseline:
                self.jordan_promised_baseline = True
                result = (
                    "Maya talks with Jordan about baseline runs. Jordan is helpful and says "
                    "he can check the no-retrieval result later, then hurries to class."
                )
            else:
                self.jordan_vague_replies += 1
                result = (
                    "Maya talks with Jordan again. Jordan admits he got distracted and says "
                    "the no-retrieval run mostly worked, but he does not give the exact failure mode."
                )
        elif action_id == "write_evidence_section":
            self.progress = min(100, self.progress + 6)
            self.hunger = min(10, self.hunger + 1)
            self.energy = max(0, self.energy - 1)
            self.focus = max(0, self.focus - 1)
            self.mood = "analytical"
            self.evidence_section_written = True
            uses_jordan_result = self.jordan_result_received and _mentions_jordan_result(decision.reason)
            if _mentions_baseline_requirement(decision.reason) and uses_jordan_result:
                self.baseline_comparison_done = True
                self.jordan_result_used = True
                result = (
                    "Maya writes the evidence section using Professor Lin's comparison "
                    "requirement and Jordan's exact no-retrieval baseline result."
                )
            elif _mentions_baseline_requirement(decision.reason):
                result = (
                    "Maya writes a comparison section, but it lacks Jordan's exact "
                    "no-retrieval baseline result."
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


def _jordan_state(jordan_promised_baseline: bool, jordan_result_received: bool) -> str:
    if jordan_result_received:
        return "Maya has Jordan's exact no-retrieval baseline result in her notes."
    if jordan_promised_baseline:
        return "Maya is still waiting on Jordan's exact no-retrieval baseline details."
    return "Maya does not yet have Jordan's baseline details."


def _asks_for_exact_jordan_result(reason: str) -> bool:
    reason_lower = reason.lower()
    mentions_jordan = "jordan" in reason_lower
    asks_for_specifics = any(
        phrase in reason_lower
        for phrase in [
            "exact",
            "specific",
            "failure mode",
            "what failed",
            "missed",
            "progress 100",
            "precise",
            "concrete",
        ]
    )
    mentions_baseline = "baseline" in reason_lower or "no-retrieval" in reason_lower
    return mentions_jordan and mentions_baseline and asks_for_specifics


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


def _mentions_jordan_result(reason: str) -> bool:
    reason_lower = reason.lower()
    return "jordan" in reason_lower and any(
        phrase in reason_lower
        for phrase in [
            "exact",
            "specific",
            "progress 100",
            "missed",
            "failure mode",
            "baseline comparison",
            "professor-required",
        ]
    )
