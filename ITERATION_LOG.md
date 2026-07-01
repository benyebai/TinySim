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

## Live-Only Reset

- Date: 2026-07-01
- Goal: use only live LLM behavior as experiment evidence

### Why We Reset

The deterministic runs made the system look cleaner than it really was. They were useful while shaping the environment, but they are not good evidence for the assignment because the action policy was hand-authored.

The project is now being treated as live-LLM-only:

- The runner defaults to Vercel AI Gateway.
- The local environment uses `openai/gpt-5`.
- Importance scoring, action selection, and reflection use live model calls.
- Live failures should fail loudly instead of falling back to deterministic behavior.

### What Broke In The Live Runs

The first live social-reflection attempts exposed real weaknesses:

- A strong model could ask Jordan for exact details too early unless the world enforced what Jordan actually knew.
- Maya sometimes waited or messaged Jordan repeatedly instead of using a rare in-person opportunity.
- Repeated action explanations polluted the memory stream and crowded retrieval.
- Reflections noticed that Jordan was delayed, but did not always convert that into a practical strategy like asking him directly in person for exact details.

These failures are useful. They show that the experiment needs to be believable under live model behavior, not only under a policy tuned to the desired transcript.

### Current Fixes

- Jordan can only provide the exact result after the earlier failed follow-up pattern has happened.
- The memory stream stores observed outcomes rather than every action reason.
- Retrieval recency now uses when a memory was created, not when it was last retrieved, so repeated retrieval does not keep old wait/message memories artificially fresh.
- Repeated failed Jordan waits/messages now become an explicit qualitative cue that waiting is no longer useful.
- The live reflection prompt now asks the model to synthesize practical lessons from repeated social friction.
- Deterministic run artifacts were removed from the current project state.

### Next Test

Rerun the three-way comparison with GPT-5:

| Run | Purpose |
| --- | --- |
| Full live system | Tests whether retrieval plus reflection changes behavior. |
| No retrieval | Tests whether memories and reflections cannot influence action when retrieval is disabled. |
| No reflection | Tests whether direct memories are weaker than higher-level social lessons. |

The result we want is not a perfect transcript. The result we want is an honest live-model transcript where any claim about retrieval or reflection can be traced to actual retrieved memories and reflections.

## Full Test Runs 012-014: GPT-5 Social Reflection

- Date: 2026-07-01
- Mode: live Vercel AI Gateway with `openai/gpt-5`
- Full command: `python3 run.py --steps 100 --llm gateway --log logs/runs/run_012_gpt5_social_reflection_full.md --memory logs/runs/run_012_gpt5_social_reflection_memory.json --summary logs/runs/run_012_gpt5_social_reflection_summary.json`
- No-retrieval command: `python3 run.py --steps 100 --llm gateway --top-k 0 --log logs/runs/run_013_gpt5_social_reflection_no_retrieval.md --memory logs/runs/run_013_gpt5_social_reflection_no_retrieval_memory.json --summary logs/runs/run_013_gpt5_social_reflection_no_retrieval_summary.json`
- No-reflection command: `python3 run.py --steps 100 --llm gateway --reflection-interval 0 --log logs/runs/run_014_gpt5_social_reflection_no_reflection.md --memory logs/runs/run_014_gpt5_social_reflection_no_reflection_memory.json --summary logs/runs/run_014_gpt5_social_reflection_no_reflection_summary.json`

### What Failed Before The Runs Completed

Switching to GPT-5 exposed several integration issues:

- GPT-5 rejected the importance-scoring call because the requested output budget was below its minimum.
- GPT-5 sometimes returned reflection importance as labels like `"high"` instead of numbers.
- GPT-5 returned empty action content until the request used `max_completion_tokens` and minimal reasoning effort.
- The Gateway produced a transient retryable connection reset before one baseline.

### What We Changed

- Raised the importance output budget.
- Added parsing for numeric and label-based importance values.
- Used GPT-5-specific request fields: `max_completion_tokens` and `reasoning_effort: minimal`.
- Added retry handling for transient live API failures.
- Kept live failures loud: there is still no deterministic fallback.

### Results

| Metric | Run 012: Full | Run 013: No Retrieval | Run 014: No Reflection |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Reflection memories | 25 | 24 | 0 |
| Avg. retrieved memories per step | 5.99 | 0.00 | 5.99 |
| Reflection retrieval count | 106 | 0 | 0 |
| Baseline requirement retrieval count | 188 | 0 | 27 |
| Jordan result retrieval count | 58 | 0 | 0 |
| Jordan pattern reflections | 5 | 3 | 0 |
| Jordan result received | true | false | false |
| Jordan result used | true | false | false |
| Evidence section written | true | true | true |
| Baseline comparison done | true | false | false |
| Jordan conversations | 6 | 3 | 6 |
| Evidence-section actions | 23 | 31 | 24 |

### Key Transcript Moment

In the full run, GPT-5 creates a reflection at step 20:

> Repeated friction: attempts to get Jordan's baseline details via quick catch-ups and passive phone checks keep failing; practical lesson - schedule a specific meeting time and ask in person for the exact no-retrieval results or assign who will run them by when.

At step 43, Jordan is present. The full run retrieves that reflection and chooses `talk_with_jordan`. Maya asks for the exact no-retrieval result and failure mode. Jordan gives the useful result: the no-retrieval run reached progress 100, but it never wrote the professor-required baseline comparison.

At step 44, Maya writes the evidence section using both Professor Lin's comparison requirement and Jordan's exact no-retrieval baseline result.

### Baseline Behavior

The no-retrieval run still generates Jordan-pattern reflections because reflection can inspect recent memories. But with retrieval disabled, those reflections never enter the decision prompt. Maya talks with Jordan and writes many evidence sections, but never receives or uses Jordan's exact result. The final evidence section remains general.

The no-reflection run retrieves direct memories and talks with Jordan several times, but it never creates the higher-level lesson about how to handle Jordan. It also writes general evidence sections and never completes the valid baseline comparison.

### What Worked

- The final evidence claim is now based on live GPT-5 behavior.
- The full run has an inspectable causal chain from failed social interactions to reflection, from reflection to retrieval, from retrieval to a changed Jordan conversation, and from that conversation to the final evidence section.
- The baselines are meaningful: all runs complete generic project progress and write something, but only the full run completes the specific memory/reflection-dependent comparison.

### What Still Failed Or Stayed Weak

- GPT-5 repeatedly chose `write_evidence_section` after the evidence section already existed.
- The world still needs a terminal state or a clearer "done for the day" action.
- Jordan is still a lightweight world actor, not a full second generative agent with his own memory stream.
- The action schema remains coarse; the exact social content lives in the model's reason and the environment outcome.

### Decision

Use Runs 012-014 as the current best evidence. The honest claim is:

The GPT-5 live runs show that reflection and retrieval can matter for a specific social-memory task. The full agent turns repeated failed coordination with Jordan into a reusable strategy, retrieves that strategy when Jordan appears, obtains the missing baseline result, and writes the valid evidence section. The no-retrieval and no-reflection baselines complete generic work but fail that specific comparison.

## Failure Ledger Across Iterations

This is the quick-read version of the project history. Each iteration should be judged by what failed, what changed because of that failure, and what weakness remained.

| Iteration | What We Tried | What Failed | What We Changed | What Still Needed Work |
| --- | --- | --- | --- | --- |
| Run 001 | First 80-step live Gateway run with open-ended actions. | The model reasoned about eating/resting, but output vague movement actions. The environment treated those as weak movement, so Maya ended depleted and project progress stayed low. | Added a structured action schema so the model had to choose executable actions. | The agent could now act, but still pushed through low energy/focus too often. |
| Run 002 | Live Gateway run with structured actions. | Project progress improved, but Maya still overworked while depleted and never chose breaks naturally. Some movement actions still meant "go work/eat/rest" in the model's prose. | Added needs-aware grounding and guardrails for hunger, energy, focus, and movement-action repair. | The run became competent, but competence alone did not prove reflection or retrieval mattered. |
| Run 003 | Live Gateway run with structured actions plus guardrails. | Maya reached progress 100, but the task became too easy. The agent kept acting after completion, and we did not yet know whether reflection caused useful behavior. | Added no-reflection and no-retrieval ablations. | Needed better evidence than project progress. |
| Run 004 | Live no-reflection ablation. | The no-reflection agent still completed the project. This weakened any claim that reflection was required for simple task completion. | Reframed reflection as inspectability and higher-level self-explanation, not raw completion. | Needed a task where reflection changes a later action, not just a transcript explanation. |
| Run 005 | Live no-retrieval baseline. | The no-retrieval agent still completed the project because current state, observations, and action schema were too informative. | Planned a memory-dependent task where a one-time requirement must matter later. | Needed a cleaner test where retrieval and reflection affect behavior, not only logs. |
| Paper-faithful memory redesign | Reduced leaky state, added one-time professor requirement, and added baseline-comparison success metrics. | Deterministic development runs looked too clean because the policy was hand-authored. They were useful for shaping the environment but not acceptable as final evidence. | Removed deterministic runs from submission artifacts and reset the project to live-LLM-only evidence. | Needed to rerun the core comparison with real model behavior. |
| Jordan social-reflection redesign | Added lightweight Jordan coordination so reflection could form a social lesson. | The deterministic version produced the desired causal story, but live runs exposed that the real model could ask too early, over-wait, miss in-person chances, or bury reflections under repeated messages. | Enforced what Jordan knows by stage, removed action rationales from memory, made recency based on memory creation, added qualitative failed-follow-up cues, and sharpened the live reflection prompt. | Needed fresh GPT-5 full/no-retrieval/no-reflection runs. |
| Runs 012-014 | Re-ran the Jordan social-reflection experiment with live GPT-5. | GPT-5 needed request/parsing fixes, and after success it still repeated evidence-writing too often. | Added GPT-5 request handling, importance-label parsing, and live retry handling. | Add a terminal "done for the day" state and make Jordan a fuller second agent if continuing. |

### Current Honest Status

The project is stronger now because the failures changed the design instead of being hidden. The current state is not "we have proved the paper." The current state is:

1. The architecture is implemented.
2. Early live runs showed why action grounding matters.
3. Baselines showed that simple completion is a weak metric.
4. Deterministic social runs were removed as evidence.
5. Fresh GPT-5 live runs now provide the current best evidence, while also exposing the need for a terminal state and a fuller Jordan agent.
