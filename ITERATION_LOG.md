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
