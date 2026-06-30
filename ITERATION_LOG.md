# Iteration Log

This file tracks full test runs, what each run revealed, and the implementation decision that came out of it. Each entry should point to the code commit that was tested.

## Full Test Run 001

- Date: 2026-06-30
- Code commit tested: `5801a3418eeb0e26678add2eaa1d6642bc278cdc`
- Mode: Vercel AI Gateway
- Command: `python3 run.py --steps 80 --llm gateway`
- Transcript: `logs/sample_run.md`
- Memory stream: `logs/memory.json`
- Summary: `logs/summary.json`

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
