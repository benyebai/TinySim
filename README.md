# Generative Agent Sandbox

A small single-agent simulation inspired by "Generative Agents: Interactive Simulacra of Human Behavior."

This project implements the core architecture from the paper at assignment scale: one agent, a simple text environment, a memory stream, retrieval, reflection, and a readable transcript of a full run.

## What It Does

The simulation follows Maya Chen, a student researcher working through a day on a behavioral simulation project. At each time step, Maya:

1. Observes the current environment.
2. Stores the observation in a natural-language memory stream.
3. Retrieves relevant memories using recency, importance, and relevance.
4. Chooses an action.
5. Stores the action outcome as memory.
6. Periodically reflects on recent experience and stores those reflections as memory.

The default mode uses a live LLM through Vercel AI Gateway. This project intentionally treats live model behavior as the evidence; deterministic development runs were removed from the submission artifacts.

## Run It

```bash
python3 run.py --steps 80
```

Outputs:

- `logs/sample_run.md`: full readable transcript
- `logs/memory.json`: final memory stream
- `logs/summary.json`: short run summary

The runner checkpoints these files after every completed step by default. If a live API run stalls or is interrupted, the logs still contain the completed portion of the run.

Optional OpenAI mode:

1. Put your API key in `.env`:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5
```

2. Run:

```bash
python3 run.py --steps 80 --llm openai
```

You can also override the model from the terminal:

```bash
OPENAI_MODEL=gpt-5 OPENAI_API_KEY=your_key_here python3 run.py --llm openai
```

Vercel AI Gateway mode:

1. Put your gateway key in `.env`:

```bash
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key_here
AI_GATEWAY_MODEL=openai/gpt-5
AI_GATEWAY_BASE_URL=https://ai-gateway.vercel.sh/v1
LIVE_LLM_IMPORTANCE=true
```

2. Run:

```bash
python3 run.py --steps 80 --llm gateway
```

Live API runs print progress after each step. Importance scoring, action selection, and reflection are all live-model calls by default.

You can checkpoint less often with:

```bash
python3 run.py --steps 80 --llm gateway --checkpoint-every 5
```

Reflection can be disabled for an ablation run:

```bash
python3 run.py --steps 80 --llm gateway --reflection-interval 0
```

Retrieval can be disabled for a baseline run:

```bash
python3 run.py --steps 80 --llm gateway --top-k 0
```

## Current Sample Run

The current included sample run is a live GPT-5 Gateway run:

- `logs/runs/run_012_gpt5_social_reflection_full.md`
- `logs/runs/run_012_gpt5_social_reflection_memory.json`
- `logs/runs/run_012_gpt5_social_reflection_summary.json`

The setup tests whether memory retrieval and reflection help Maya coordinate with Jordan. Jordan is helpful but vague: broad check-ins and messages do not produce the exact no-retrieval baseline result. A useful result appears only when Maya asks Jordan in person for the exact result and failure mode.

The full GPT-5 run produced the intended causal chain:

1. Maya had vague or failed Jordan interactions.
2. Reflection synthesized a practical social lesson: ask in person for exact baseline details.
3. Retrieval surfaced that reflection when Jordan appeared again.
4. Maya asked Jordan for the exact no-retrieval result and failure mode.
5. Maya wrote the evidence section using Professor Lin's requirement and Jordan's exact result.

Summary:

```json
{
  "steps": 100,
  "final_project_progress": 100,
  "reflection_count": 25,
  "avg_retrieved_memories": 5.99,
  "reflection_retrieval_count": 106,
  "jordan_pattern_reflection_count": 5,
  "jordan_result_received": true,
  "jordan_result_used": true,
  "evidence_section_written": true,
  "baseline_comparison_done": true
}
```

The run is not perfect. After the evidence section becomes available, GPT-5 sometimes keeps choosing `write_evidence_section` repeatedly. I treat that as a remaining environment-design weakness: the simulation needs a stronger terminal or "done for the day" state.

The transcript shows retrieval scores for each selected memory:

```txt
score = recency + importance + relevance
```

Each retrieved memory includes the total score plus the component scores.

## Baseline Runs

The final comparison uses live GPT-5 runs only.

| Metric | Full | No Retrieval | No Reflection |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Reflection memories | 25 | 24 | 0 |
| Avg. retrieved memories per step | 5.99 | 0.00 | 5.99 |
| Reflection retrieval count | 106 | 0 | 0 |
| Jordan pattern reflections | 5 | 3 | 0 |
| Jordan result received | true | false | false |
| Jordan result used | true | false | false |
| Evidence section written | true | true | true |
| Baseline comparison done | true | false | false |
| `talk_with_jordan` actions | 6 | 3 | 6 |
| `write_evidence_section` actions | 23 | 31 | 24 |

Artifacts:

- Full: `logs/runs/run_012_gpt5_social_reflection_full.md`
- No retrieval: `logs/runs/run_013_gpt5_social_reflection_no_retrieval.md`
- No reflection: `logs/runs/run_014_gpt5_social_reflection_no_reflection.md`

The baselines are useful because they still complete the generic project and still write something, but they fail the specific social-memory condition. Without retrieval, reflections are generated but never brought back into the action prompt. Without reflection, direct memories are not enough to produce the higher-level Jordan strategy. In both baselines, Maya writes a general evidence section rather than a valid baseline comparison using Jordan's exact result.

## Most Important Runs

The useful story is the progression across runs, not just the final transcript. Early runs made the agent competent, then the baselines showed that competence was too weak a measure, then the final GPT-5 runs tested a more memory-dependent social task.

| Run | What It Tested | What Happened | What Changed |
| --- | --- | --- | --- |
| Run 001 | First live Gateway run with open-ended actions. | Maya reasoned about eating and resting, but often chose vague movement actions. The project only reached 10 progress, with hunger and fatigue maxed out. | Added a structured action schema so the model had to choose executable actions. |
| Run 003 | Structured actions plus needs guardrails. | Maya reached project progress 100 and ended in a healthier state. | This proved the loop could produce sensible behavior, but it also made the task too easy. |
| Runs 004-005 | No-reflection and no-retrieval baselines. | Both baselines still reached progress 100. | Reframed the claim: raw task completion was not enough evidence for reflection or retrieval. |
| Jordan redesign | A memory-dependent social requirement. | Maya needed Jordan's exact no-retrieval result later, after earlier vague follow-ups failed. | Made the experiment test whether reflection turns repeated social friction into a reusable strategy. |
| Runs 012-014 | Final live GPT-5 full/no-retrieval/no-reflection comparison. | Only the full agent got Jordan's exact result, used it, and completed the required baseline comparison. | This became the final evidence used in the README and logs. |

The final claim is intentionally narrow: this project does not prove the whole paper. It shows, in a small inspectable setting, that retrieval plus reflection can change behavior on a task where the agent must remember a prior requirement, learn from repeated failed coordination, and use that lesson later.

## Assignment Reflection

### What I Chose To Cut From The Paper And Why

I cut the parts that mostly support the full Smallville demo rather than the assignment's core:

- 25 agents
- Full independent multi-agent conversations
- Information diffusion across a town
- Phaser or any visual game interface
- Sprite movement and pathfinding
- Complex environment tree modeling
- Recursive day/hour/minute planning
- Human believability evaluation with outside raters
- Social network metrics

Those pieces are valuable in the paper, but for a seven-hour assignment they would mostly add surface area. I kept Maya as the only full generative agent and made Jordan a lightweight world actor. That is less ambitious, but it made the central question easier to inspect: do memory retrieval and reflection actually affect Maya's later actions?

### What I Kept That I Could Have Cut

I kept importance scoring, even though a simpler recency-only retrieval system would have been much faster. It was worth keeping because the paper's retrieval mechanism depends on recency, importance, and relevance, and the transcript can show those scores for each retrieved memory.

I kept reflection as a memory type rather than just printing summaries to the log. This mattered because the final run depends on a reflection being stored, retrieved later, and used to change the Jordan conversation.

I kept live LLM behavior only for the final evidence. Deterministic runs were useful during development, but they were removed from the submission artifacts because they made the system look cleaner than it really was.

I also kept the baselines. They made the story more complicated, but much more honest. The no-retrieval and no-reflection runs showed that generic project progress was too easy, while the Jordan comparison showed a more specific place where the full architecture mattered.

### What Surprised Me

The biggest surprise was how easy it was to accidentally make the environment too helpful. When the agent saw exact hunger, energy, focus, and progress numbers, it could behave well without using memory much. The current version keeps those numbers for evaluation, but gives Maya more qualitative observations.

The second surprise was that an LLM can sound thoughtful while still taking the wrong kind of action. In Run 001, Maya explained that she should eat or rest, but selected vague movement actions that the environment could not treat as eating or resting. That failure led to the structured action schema.

The third surprise was that reflection did not matter until the task actually required generalization. In the early project-progress task, no-reflection and no-retrieval baselines still succeeded. Reflection became more meaningful only after the Jordan task required Maya to notice a pattern: vague messages were not working, so she needed to ask Jordan directly in person for exact baseline details.

The most interesting broken behavior was at the end of the final full run. GPT-5 completed the evidence section, but then kept choosing `write_evidence_section` many more times. That is a real remaining weakness: the environment needs a terminal `submit_report` or "done for the day" action so the agent can stop productively.

## What We Reached

The strongest evidence is Runs 012-014:

- Full GPT-5 agent: received Jordan's exact result, used it, and completed the baseline comparison.
- No retrieval: generated reflections, but could not bring them back into the action prompt, so the Jordan result was never received or used.
- No reflection: retrieved direct memories, but never formed the higher-level Jordan strategy, so the valid baseline comparison was still missing.

The biggest lesson is that the paper's architecture is not automatically impressive just because an agent completes a task. The evidence gets stronger when the task contains a memory-dependent obligation and the transcript shows the actual path from memory to reflection to later action.

## Remaining Weaknesses

Useful next steps:

- Add a terminal `submit_report` or "done for the day" action after the evidence section is valid.
- Make Jordan a fuller second agent with his own memory stream and reflections.
- Add a final interview mode to ask Maya what she remembers and what she learned.
- Add a stricter metric for whether retrieved memories actually change decisions.
- Run multiple live seeds or models to see whether the same reflection effect survives model variation.

## Architecture

Important files:

- `generative_agent_sandbox/memory.py`: memory stream and retrieval scoring
- `generative_agent_sandbox/models.py`: structured action schema and run data models
- `generative_agent_sandbox/agent.py`: observe, retrieve, act, reflect loop
- `generative_agent_sandbox/environment.py`: small campus world
- `generative_agent_sandbox/llm.py`: OpenAI and Vercel AI Gateway live LLM backends
- `generative_agent_sandbox/simulation.py`: run orchestration and log writing

## Paper Notes

See:

- `PAPER_SUMMARY.md`
- `IMPLEMENTATION_SCOPE.md`
- `SURPRISE_QUESTIONS.md`
- `ITERATION_LOG.md`
