# Iteration Log

This file tracks full test runs, what each run revealed, and the implementation decision that came out of it. Each entry should point to the code commit that was tested.

## Full Test Run 001

- Date: 2026-06-30
- Code commit tested: `5801a3418eeb0e26678add2eaa1d6642bc278cdc`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway`
- Transcript at tested commit: `git show 5801a3418eeb0e26678add2eaa1d6642bc278cdc:logs/sample_run.md`
- Memory stream at tested commit: `git show 5801a3418eeb0e26678add2eaa1d6642bc278cdc:logs/memory.json`
- Summary at tested commit: `git show 5801a3418eeb0e26678add2eaa1d6642bc278cdc:logs/summary.json`

### Result

```json
{
  "steps": 80,
  "final_location": "Cafe",
  "final_hunger": 10,
  "final_energy": 0,
  "final_focus": 0,
  "final_project_progress": 10,
  "memory_count": 182,
  "reflection_count": 18
}
```

### What Worked

- The full 80-step live LLM run completed.
- Checkpointing worked: transcript, memory, and summary files were updated throughout the run.
- The memory stream grew as expected with observations, actions, and reflections.
- Retrieval was inspectable in the transcript, with recency, importance, and relevance scores.
- Reflections appeared at steps 20, 40, 60, and 80.
- The agent repeatedly formed the right high-level interpretation: hunger, energy, and focus affect project progress.

### What Was Problematic

- The live model often produced vague actions instead of grounded actions.
- The most common action was `go`, which appeared 46 times.
- The agent frequently chose `go to Cafe` or `go to Dorm` with a reason implying eating or resting, but the environment treated those as movement rather than concrete recovery actions.
- Because the environment relies on action text to determine effects, most vague actions produced only modest outcomes.
- Final project progress was only 10, and Maya ended with hunger at 10, energy at 0, and focus at 0.

### Interpretation

The agent was learning the right lesson at the reflection level, but the action interface was too loose. The model could explain that Maya should eat or rest, yet still output a command that the environment could not execute as eating or resting.

This is a useful failure for the assignment because it shows that memory and reflection are not enough by themselves. A generative agent also needs a grounded action space so reasoning can become reliable behavior.

### Decision

For the next iteration, replace open-ended action text with a constrained action schema. The LLM should choose from explicit actions such as:

- `go_to_library`
- `go_to_cafe`
- `go_to_dorm`
- `eat_meal`
- `rest`
- `work_on_project`
- `review_notes`
- `take_break`

The environment should apply effects based on the structured action id instead of keyword matching the model's prose. After that change, run another 80-step gateway test and compare project progress, final needs, action distribution, and reflection quality against Full Test Run 001.

## Full Test Run 002

- Date: 2026-06-30
- Code commit tested: `6201151c38b89530a7b226801ee6fd5816aefe7f`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway`
- Transcript: `logs/runs/run_002_sample_run.md`
- Memory stream: `logs/runs/run_002_memory.json`
- Summary: `logs/runs/run_002_summary.json`

### Result

```json
{
  "steps": 80,
  "final_location": "Library",
  "final_hunger": 5,
  "final_energy": 1,
  "final_focus": 0,
  "final_project_progress": 72,
  "memory_count": 181,
  "reflection_count": 17
}
```

### Action Counts

- `work_on_project`: 34
- `go_to_library`: 20
- `eat_meal`: 13
- `rest`: 7
- `go_to_cafe`: 6

### What Worked

- The structured action schema eliminated the vague `go` action problem.
- There were zero "modest effect" outcomes.
- Project progress improved from 10 to 72.
- Food and rest actions were now executed directly instead of being lost as movement-only actions.

### What Was Problematic

- Maya still overworked when depleted.
- The final state had energy at 1 and focus at 0.
- The model never chose `take_break`, even when the observation said Maya's attention was drifting.
- Some `go_to_library` decisions still meant "go work at the library" in the model's reasoning, but the action itself only moved her.

### Decision

Keep the structured action schema, but add a needs-aware action guardrail:

- If hunger is critical, choose `eat_meal`.
- If energy is critically low or Maya is mentally foggy, choose `rest`.
- If focus is depleted and the model chooses project work, choose `take_break`.
- If the model chooses a movement action whose reason clearly implies eating, resting, or working, ground it as the concrete action.

Then run a third 80-step gateway test and compare final project progress plus hunger, energy, and focus.

## Full Test Run 003

- Date: 2026-06-30
- Code commit tested: `1fb5351e8a8898ad7432aa5920e5373adf320da1`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway`
- Transcript: `logs/runs/run_003_sample_run.md`
- Memory stream: `logs/runs/run_003_memory.json`
- Summary: `logs/runs/run_003_summary.json`

### Result

```json
{
  "steps": 80,
  "final_location": "Cafe",
  "final_hunger": 2,
  "final_energy": 8,
  "final_focus": 7,
  "final_project_progress": 100,
  "memory_count": 184,
  "reflection_count": 20
}
```

### Action Counts

- `work_on_project`: 26
- `take_break`: 15
- `go_to_library`: 15
- `eat_meal`: 14
- `review_notes`: 5
- `rest`: 5

### What Worked

- Project progress reached 100.
- Maya ended in a healthier state: hunger 2, energy 8, focus 7.
- There were zero "modest effect" outcomes.
- The guardrail changed 6 decisions where needs were too depleted for the chosen action.
- The grounding repair changed 10 movement-style decisions into concrete actions.
- Reflections still appeared at steps 20, 40, 60, and 80.

### What Was Still Imperfect

- Project progress reached 100 around step 40, but Maya still continued some library movement afterward.
- The simulation needs a clearer terminal state once the main project is complete.
- The current run is stronger behaviorally, but an ablation run would be useful to show how much reflection matters.

### Decision

Use Full Test Run 003 as the current best sample run. Keep both changes:

- Structured action ids instead of open-ended action strings.
- Needs-aware guardrails for food, rest, focus recovery, and movement grounding.

For the next project iteration, add a no-reflection comparison run to test whether reflection changes behavior beyond the action schema and guardrails.

## Full Test Run 004: No-Reflection Ablation

- Date: 2026-07-01
- Code commit tested: `0efb7d4b62a812c4ad0cf7cc4df4806c0e362df7`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway --reflection-interval 0`
- Transcript: `logs/runs/run_004_no_reflection_sample_run.md`
- Memory stream: `logs/runs/run_004_no_reflection_memory.json`
- Summary: `logs/runs/run_004_no_reflection_summary.json`

### Result

```json
{
  "steps": 80,
  "final_location": "Park",
  "final_hunger": 8,
  "final_energy": 10,
  "final_focus": 9,
  "final_project_progress": 100,
  "memory_count": 164,
  "reflection_count": 0
}
```

### Action Counts

- `work_on_project`: 24
- `go_to_library`: 21
- `take_break`: 19
- `eat_meal`: 13
- `rest`: 3

### Comparison To Run 003

| Metric | Run 003: Reflection On | Run 004: Reflection Off |
| --- | ---: | ---: |
| Project progress | 100 | 100 |
| Final hunger | 2 | 8 |
| Final energy | 8 | 10 |
| Final focus | 7 | 9 |
| Reflection memories | 20 | 0 |
| `review_notes` actions | 5 | 0 |
| First reached progress 100 | Step 40 | Step 37 |
| Guardrail decisions | 6 | 10 |

### What Worked

- The no-reflection agent still completed the project.
- Structured actions and needs-aware guardrails were strong enough to maintain useful behavior without reflection memories.
- There were zero "modest effect" outcomes.
- This makes the experiment more honest: reflection is not the only reason the final agent works.

### What Was Missing Without Reflection

- No higher-level reflection memories were created.
- Maya never chose `review_notes`, while the reflected run chose it 5 times.
- Late behavior leaned into a repeated park/library cycle instead of explicitly documenting what had changed.
- Maya ended much hungrier than the reflected run.

### Interpretation

The ablation shows that reflection is not necessary for raw task completion in this simplified environment. Immediate observations, retrieval over action memories, structured actions, and guardrails can already produce competent behavior.

However, reflection still adds value that matters for this assignment: it creates explicit high-level lessons, gives the transcript stronger evidence that the agent learned from experience, and encourages behavior related to documenting the run rather than only continuing the work loop.

### Decision

Keep reflection enabled in the main sample. Report the ablation as a useful limitation and nuance: the experiment supports the paper's memory/reflection idea, but it also shows that evaluation metrics matter. If we only measure project progress, reflection looks optional; if we measure high-level self-explanation and evidence for changed behavior, reflection becomes important.

For the next project iteration, add a final interview mode or a clearer "done for the day" terminal state.

## Full Test Run 005: No-Retrieval Baseline

- Date: 2026-07-01
- Code commit tested: `c3219d777a2d141e73fa4c207171e7f6cd14c428`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway --top-k 0`
- Transcript: `logs/runs/run_005_no_retrieval_sample_run.md`
- Memory stream: `logs/runs/run_005_no_retrieval_memory.json`
- Summary: `logs/runs/run_005_no_retrieval_summary.json`

### Result

```json
{
  "steps": 80,
  "final_location": "Dorm",
  "final_hunger": 5,
  "final_energy": 8,
  "final_focus": 8,
  "final_project_progress": 100,
  "memory_count": 184,
  "reflection_count": 20
}
```

### Action Counts

- `organize_notes`: 25
- `work_on_project`: 20
- `eat_meal`: 10
- `review_notes`: 9
- `rest`: 9
- `take_break`: 6
- `go_to_library`: 1

### Comparison To Run 003 And Run 004

| Metric | Run 003: Full System | Run 004: No Reflection | Run 005: No Retrieval |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Final hunger | 2 | 8 | 5 |
| Final energy | 8 | 10 | 8 |
| Final focus | 7 | 9 | 8 |
| Reflection memories | 20 | 0 | 20 |
| Avg. retrieved memories per step | 5.99 | 5.99 | 0 |
| `review_notes` actions | 5 | 0 | 9 |
| Guardrail decisions | 6 | 10 | 2 |

### What Worked

- The run completed with zero retrieved memories at every step.
- Maya still reached project progress 100.
- Reflections were still generated at steps 20, 40, 60, and 80 because reflection uses recent memories directly rather than action retrieval.
- The transcript clearly shows empty "Retrieved memories" sections, making the baseline easy to inspect.

### What Was Surprising

- Removing retrieval did not break task completion.
- The agent compensated using the current world state, the current observation, the static agent goal, and the structured action schema.
- The run chose `organize_notes` much more often than the full system.
- The agent still chose `review_notes` 9 times, which shows that the static goal and current state can induce documentation behavior even without retrieved memories.

### Interpretation

This baseline weakens any overly simple claim that retrieval is required for task completion in this toy environment. It shows that a sufficiently informative current-state prompt plus guardrails can produce competent behavior.

However, the baseline still supports the value of the paper's architecture in a more careful way. Retrieval is not just about reaching a numeric goal; it is about making the cause of behavior inspectable. In the full system, the transcript can show exactly which past memories were selected and how their recency, importance, and relevance contributed to the next action. With retrieval disabled, the agent may still behave well, but the decision process has less explicit historical grounding.

### Decision

Keep Run 005 as an important baseline. In the final writeup, avoid claiming that retrieval or reflection are necessary for task completion. Instead, claim that the full architecture provides continuity, inspectability, and higher-level self-explanation, while the baselines show that simple task completion is an insufficient evaluation metric.

### Weakness Found After Baselines

The baseline runs exposed a weakness in the experiment design. The environment gives the agent a very informative current state on every step: hunger, energy, focus, project progress, location, and the current observation. The action schema and guardrails also encode useful behavioral rules such as eating when hungry, resting when tired, and taking a break when focus is depleted.

Because of this, the agent can often act competently without needing retrieval. The no-retrieval run still reached project progress 100, which means the current task is not memory-dependent enough to prove that retrieval is necessary for success.

The next experiment should include information that appears once and must be remembered later. Examples:

- A professor gives a specific requirement early in the day that must be used in the final writeup.
- A useful source, deadline, or constraint is mentioned once and disappears from the current state.
- The cafe or library changes availability, and Maya has to remember that change later.
- The assignment asks for a specific kind of surprise, but that instruction is stored only as a memory rather than repeated in the agent summary.

For the next project iteration, add a memory-dependent task or an evaluation metric that checks whether retrieved memories actually change the chosen action.

## Full Test Runs 006-008: Paper-Faithful Memory Test

- Date: 2026-07-01
- Code tested: working tree after paper-faithful guardrail and snapshot edits
- Mode: deterministic
- Full command: `python3 run.py --steps 80 --log logs/runs/run_006_paper_faithful_full.md --memory logs/runs/run_006_paper_faithful_memory.json --summary logs/runs/run_006_paper_faithful_summary.json`
- No-retrieval command: `python3 run.py --steps 80 --top-k 0 --log logs/runs/run_007_paper_faithful_no_retrieval.md --memory logs/runs/run_007_paper_faithful_no_retrieval_memory.json --summary logs/runs/run_007_paper_faithful_no_retrieval_summary.json`
- No-reflection command: `python3 run.py --steps 80 --reflection-interval 0 --log logs/runs/run_008_paper_faithful_no_reflection.md --memory logs/runs/run_008_paper_faithful_no_reflection_memory.json --summary logs/runs/run_008_paper_faithful_no_reflection_summary.json`

### Implementation Change

The earlier experiment gave the agent too much help through the current snapshot and guardrails. It exposed exact hunger, energy, focus, and progress numbers, and the static goal told the agent too directly what the assignment was supposed to demonstrate.

This iteration changed that:

- The snapshot now gives qualitative perception instead of exact internal meters.
- The static summary no longer tells Maya to prove retrieval and reflection.
- A professor gives a no-retrieval-baseline requirement once, early in the run.
- Writing the final evidence section only counts as a baseline comparison if the decision reason mentions the remembered baseline requirement.
- A later "push ahead or reset" moment tests whether reflection creates reusable self-knowledge beyond direct event recall.

### Results

| Metric | Run 006: Full | Run 007: No Retrieval | Run 008: No Reflection |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Final hunger | 4 | 4 | 4 |
| Final energy | 6 | 4 | 8 |
| Final focus | 3 | 9 | 5 |
| Memory count | 180 | 180 | 164 |
| Reflection count | 16 | 16 | 0 |
| Avg. retrieved memories per step | 5.99 | 0.00 | 5.99 |
| Reflection retrieval count | 170 | 0 | 0 |
| Baseline requirement retrieval count | 244 | 0 | 122 |
| Evidence section written | true | false | true |
| Baseline comparison done | true | false | true |

### Action Counts

| Action | Run 006: Full | Run 007: No Retrieval | Run 008: No Reflection |
| --- | ---: | ---: | ---: |
| `eat_meal` | 13 | 11 | 13 |
| `organize_notes` | 1 | 13 | 1 |
| `rest` | 2 | 6 | 2 |
| `review_notes` | 29 | 23 | 26 |
| `take_break` | 15 | 7 | 16 |
| `work_on_project` | 19 | 20 | 21 |
| `write_evidence_section` | 1 | 0 | 1 |

### Evidence From The Transcripts

- In Run 006, Professor Lin's requirement appears once at step 6. The full agent repeatedly retrieves it and later chooses `write_evidence_section` because Maya remembers the no-retrieval-baseline requirement.
- In Run 007, the same professor event appears in the observation stream, but retrieval is disabled. Maya reviews notes repeatedly with the reason that no specific remembered requirement is available, and never chooses `write_evidence_section`.
- In Run 008, direct retrieval still recovers the professor requirement, so Maya writes the evidence section. But at the "push ahead or reset" moment, the no-reflection agent chooses `work_on_project` while the full agent chooses `take_break` because it retrieves a reflection about reset breaks and focus.

### Interpretation

This is a stronger match to the paper than the earlier runs. The current state no longer acts like an all-knowing dashboard, and the main success condition depends on the memory stream.

The result is nuanced:

- Retrieval matters for remembering a one-time instruction that disappears from the current snapshot.
- Reflection matters for turning repeated experience into reusable guidance.
- Generic project completion is still too weak as an evaluation metric, because every variant reached progress 100.

### Decision

Use Run 006 as the current best sample run and keep Runs 007 and 008 as the main baselines. In the writeup, avoid claiming that the architecture is necessary for simple task completion. The better claim is that the paper's architecture supports memory-dependent obligations, reflection-driven behavior changes, and an inspectable causal trail from past experience to current action.

## Iteration 006-008 Postmortem And Next Test Plan

### Why This Iteration Happened

The earlier version felt too guided. The current snapshot exposed exact hidden state, and the static agent summary told Maya too directly that the project should prove memory, retrieval, and reflection. That made the behavior look more competent than the paper's architecture alone deserved credit for.

This iteration was an attempt to remove that extra help and test a sharper question:

Can the agent use memory retrieval to act on information that appeared once and is no longer visible in the current state?

### How The Iteration Ran

The iteration ran three deterministic 80-step comparisons:

- Full architecture: memory retrieval and reflection enabled.
- No retrieval: reflection still enabled, but top-k retrieval set to 0.
- No reflection: retrieval still enabled, but reflection interval set to 0.

The environment included one important early instruction from Professor Lin: the final report should compare the full agent with a no-retrieval baseline. Later, when Maya reached the final evidence section, the environment did not repeat that requirement. Maya had to recover it from memory.

The environment also included a later "push ahead or reset" moment. That was meant to test whether reflection could produce reusable self-knowledge, not just factual recall.

### What Was Good About It

- The snapshot is less leaky. Maya sees qualitative cues like hunger, usable energy, and project stage instead of exact hidden meters.
- The one-time professor instruction creates a real memory-dependent obligation.
- The no-retrieval baseline gives a clear contrast: it still completes generic project work, but it fails to write the final evidence section.
- The no-reflection baseline gives a different contrast: it remembers the explicit professor requirement through retrieval, but lacks the reflection-driven reset-break decision.
- The transcript makes the causal trail inspectable. We can point to the retrieved memory or reflection that shaped a later action.

The strongest result is not "the full agent finished the project." Every variant did that. The stronger result is that the full agent remembered and used a past requirement that the no-retrieval agent could not access.

### What Was Bad Or Still Weak

- This is still not strong evidence of believable human behavior. It is stronger evidence of the memory architecture working.
- The deterministic policy has hand-authored decision logic, so the run is useful for testing architecture but not enough for a believability claim.
- The world is still solitary. The paper's most compelling behavior comes from social coordination, information spreading, and agents remembering interactions with each other.
- The metric "project progress reached 100" is too easy and should not be used as the main success claim.
- The baseline requirement retrieval count is inflated by repeated retrieval of the same important memory. That shows persistence, but not necessarily natural behavior.
- Maya's actions are still bounded by a small action list, so some choices are believable only at the coarse level.

The honest claim after this iteration is:

The sandbox now gives good evidence that memory retrieval and reflection can affect later behavior in an inspectable way. It does not yet give strong evidence that the agent is broadly believable as a human.

### What We Should Test Next

The next experiment should test believability through a small social coordination task, not by adding a large world.

Recommended next setup:

- Add one more student agent, Jordan.
- Professor Lin gives Maya a requirement once: compare the full agent with a no-retrieval baseline.
- Jordan separately has useful baseline information or promises to run the no-retrieval comparison.
- Maya and Jordan have a chance to meet later.
- Maya must remember to ask Jordan for the baseline result.
- The final evidence section only counts as complete if Maya uses both the professor's requirement and Jordan's transferred information.

This would test a more paper-like behavior:

- Remembering a social obligation.
- Coordinating with another agent.
- Transferring information through conversation.
- Using remembered conversation later in a written task.

### Proposed Baselines For The Next Test

| Run | Purpose |
| --- | --- |
| Full two-agent system | Tests whether memory, reflection, and conversation support coordination. |
| No retrieval | Tests whether Maya fails to remember the professor instruction or Jordan's baseline information. |
| No reflection | Tests whether Maya remembers facts but fails to adapt strategy after friction. |
| No social exchange | Tests whether the second agent actually matters, not just the extra scripted event. |

### Metrics For The Next Test

Better metrics than project progress:

- Did Maya attend or remember the relevant conversation?
- Did Jordan's information enter Maya's memory stream?
- Did Maya later retrieve Jordan's information?
- Did the final evidence section include both the professor requirement and Jordan's baseline result?
- Did reflection change a later action that was not directly forced by the current observation?
- Does the transcript show a believable reason for the coordination, or only a scripted handoff?

### Next Decision

Do not add a large multi-agent world. Add exactly one more agent and one focused social coordination requirement. The goal should be to show one small version of the paper's social believability argument while keeping the run easy to inspect.

## Full Test Runs 009-011: Social Reflection With Jordan

- Date: 2026-07-01
- Code tested: working tree after adding lightweight Jordan interactions
- Mode: deterministic
- Full command: `python3 run.py --steps 80 --log logs/runs/run_009_social_reflection_full.md --memory logs/runs/run_009_social_reflection_memory.json --summary logs/runs/run_009_social_reflection_summary.json`
- No-retrieval command: `python3 run.py --steps 80 --top-k 0 --log logs/runs/run_010_social_reflection_no_retrieval.md --memory logs/runs/run_010_social_reflection_no_retrieval_memory.json --summary logs/runs/run_010_social_reflection_no_retrieval_summary.json`
- No-reflection command: `python3 run.py --steps 80 --reflection-interval 0 --log logs/runs/run_011_social_reflection_no_reflection.md --memory logs/runs/run_011_social_reflection_no_reflection_memory.json --summary logs/runs/run_011_social_reflection_no_reflection_summary.json`

### Experiment Idea

This iteration tested a clearer reflection effect: Maya should learn something about Jordan's behavior.

Jordan is helpful, but vague follow-through fails. If Maya asks generally, he promises to help or says the baseline "mostly worked." If she asks in person for the exact no-retrieval result and failure mode, he gives the useful result.

The important design choice is that the action list does not include a special "ask Jordan specific question" button. Maya only has generic social actions like `talk_with_jordan`, `send_message`, and `wait_for_reply`. The specificity has to come from retrieved memory and the decision reason.

### Results

| Metric | Run 009: Full | Run 010: No Retrieval | Run 011: No Reflection |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Reflection memories | 16 | 16 | 0 |
| Avg. retrieved memories per step | 5.99 | 0.00 | 5.99 |
| Reflection retrieval count | 30 | 0 | 0 |
| Jordan pattern reflections | 1 | 2 | 0 |
| Jordan result retrieved | 73 | 0 | 0 |
| Jordan result received | true | false | false |
| Jordan result used | true | false | false |
| Evidence section written | true | false | false |
| Baseline comparison done | true | false | false |
| Jordan conversations | 3 | 3 | 3 |
| Jordan vague replies | 1 | 2 | 2 |

### Key Transcript Moment

In the full run, Maya first talks with Jordan generally. Jordan promises to help. Later, Maya waits for the message and nothing useful arrives. Later still, Jordan gives a vague answer: the no-retrieval run "mostly worked," but he does not provide the exact failure mode.

At step 40, reflection creates the important social inference:

> Jordan seems helpful but vague follow-through fails; Maya gets useful baseline information only by asking him in person for the exact no-retrieval result and failure mode.

At step 43, Jordan is available. The full run retrieves that reflection and chooses `talk_with_jordan` with a specific reason. Jordan then provides the useful result: the no-retrieval run reached progress 100, but it never wrote the professor-required baseline comparison.

At step 44, Maya writes the evidence section using both Professor Lin's requirement and Jordan's exact result.

### Baseline Behavior

The no-retrieval run actually generated Jordan-pattern reflections, because reflection still sees recent memories. But with retrieval disabled, Maya could not bring those reflections back into the decision at step 43. She talked with Jordan generally and got another vague answer.

The no-reflection run retrieved the earlier Jordan conversations and remembered the professor's requirement, but it never formed the higher-level social model. At step 43 it also talked with Jordan generally and got another vague answer.

This is the strongest reflection evidence so far. The difference is not that the full agent had a special action. All three runs used `talk_with_jordan` three times. The difference is that only the full agent retrieved a reflection that changed the content of the conversation.

### What Was Good

- Reflection now represents a social pattern, not just a task reminder.
- The effect is easy to inspect in the transcript.
- The full and baseline runs diverge at a natural human moment: how to ask a helpful but distracted collaborator for information.
- The result is closer to the paper's believability argument because it involves social memory and coordination.

### What Is Still Weak

- Jordan is still a lightweight world actor, not a full generative agent with his own planner and memory retrieval.
- The deterministic policy is still hand-authored, so this proves the architecture and experiment shape more than it proves open-ended human believability.
- The retrieval query needed a small improvement to surface social reflections when Jordan was salient. That is defensible, but it means retrieval design matters a lot.
- The world still has scripted opportunities for Jordan, rather than emergent meetings.

### Decision

This is a better next sample than the earlier one-agent memory test. The honest claim is:

The sandbox now demonstrates a small social-reflection effect: reflection can turn repeated interactions into a reusable model of another person's behavior, and retrieval of that model can change a later conversation.

## Reflection After Runs 009-011: What This Iteration Taught Us

- Date: 2026-07-01
- Focus: whether the Jordan setup makes reflection feel important, not just present

### The Shift In This Iteration

This iteration moved the project from "Maya remembers an instruction" to "Maya forms a small interpretation of another person's behavior."

That matters because the paper's most interesting claim is not that an agent can store facts. The stronger claim is that memories can accumulate into higher-level beliefs, and those beliefs can shape later behavior. The Jordan experiment is our clearest version of that so far.

The useful reflection was not a direct task note like "write the evidence section." It was a social model:

> Jordan is helpful, but vague follow-through fails; ask him in person for the exact result and failure mode.

That feels closer to human behavior. People often do not just remember what someone said. They remember how that person tends to act, then adjust how they coordinate with them.

### Why This Is Better Evidence

The best part of the result is that all three runs had the same visible social opportunity. Maya talked with Jordan three times in the full run, the no-retrieval run, and the no-reflection run.

So the difference was not "the full run got more chances." The difference was what Maya brought into the same chance:

- Full run: retrieved the Jordan reflection, asked a specific question, got the useful baseline result, and wrote the evidence section.
- No retrieval: generated some useful reflections, but could not bring them back at the right moment.
- No reflection: remembered earlier Jordan interactions, but did not compress them into a reusable social lesson.

That is a cleaner argument than project progress alone. Project progress reached 100 in every run, which means progress is not the right evidence. The better evidence is the causal trail:

1. repeated vague Jordan interactions,
2. reflection creates a higher-level social inference,
3. retrieval surfaces that inference when Jordan appears again,
4. Maya changes the content of the conversation,
5. the final written evidence becomes possible.

### What Still Feels Artificial

We should be honest that this is still not a full proof of believable human behavior.

Jordan is a lightweight world actor, not a second generative agent with his own memory stream, needs, plans, and retrieval. The environment creates the moments where Jordan appears. The deterministic policy also contains hand-authored logic for recognizing when the Jordan reflection matters.

So the current claim should stay narrow:

This experiment shows that reflection can create a useful social abstraction, and retrieval of that abstraction can change later behavior.

It does not yet show that believable multi-agent social life emerges naturally from the system.

### What We Learned About Reflection

Reflection is most convincing when the current observation is not enough by itself.

If the observation says, "Professor Lin requires a baseline comparison," then direct memory retrieval can solve the task. Reflection is helpful but not necessary.

If the observation says, "Jordan is nearby," the right action depends on a pattern across time. Maya has to know that general check-ins with Jordan have failed before. That is where reflection becomes more visibly important.

This is probably the design rule for future experiments:

Reflection should matter when the agent needs a compressed lesson from multiple past events, not when it only needs one remembered fact.

### What We Should Test Next

The next step should make Jordan more independent without making the whole project too large.

Recommended next iteration:

- Give Jordan his own small memory stream.
- Let Jordan remember being asked, getting distracted, and later finding the baseline result.
- Let Maya and Jordan exchange actual message content rather than using only outcome text.
- Keep the same three baselines: full, no retrieval, no reflection.
- Add a "no Jordan memory" baseline if Jordan becomes a real agent.

The key question should be:

Can Maya and Jordan coordinate through their own remembered histories, rather than through a single scripted world state?

### Current Best Claim

Our best claim after this iteration is:

The sandbox now gives a small, inspectable example of the paper's memory-reflection loop. Reflection turns repeated experience into a reusable belief, retrieval brings that belief back in context, and the agent's later social behavior changes in a way the baselines do not reproduce.

That is not full human believability yet. But it is finally evidence for why reflection matters.
