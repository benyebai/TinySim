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

## Architecture

Important files:

- `generative_agent_sandbox/memory.py`: memory stream and retrieval scoring
- `generative_agent_sandbox/models.py`: structured action schema and run data models
- `generative_agent_sandbox/agent.py`: observe, retrieve, act, reflect loop
- `generative_agent_sandbox/environment.py`: small campus world
- `generative_agent_sandbox/llm.py`: OpenAI and Vercel AI Gateway live LLM backends
- `generative_agent_sandbox/simulation.py`: run orchestration and log writing

## What I Kept From The Paper

I kept the parts that define the core cognitive architecture:

- Natural-language memory stream
- Retrieval based on recency, importance, and relevance
- Importance scoring for memories
- Reflection as a second kind of memory
- Reflections stored back into the same memory stream
- A time-stepped observe-retrieve-act loop
- A transcript that makes the agent's memory use inspectable

I also kept importance scoring even though it could have been cut. It was worth keeping because it lets the agent distinguish routine observations from moments that should matter later.

## What I Cut From The Paper

I cut the parts that mostly support the full Smallville demo rather than the assignment's core:

- 25 agents
- Full multi-agent conversations
- Full social coordination between independent agents
- Information diffusion between agents
- Phaser or any visual game interface
- Sprite movement and pathfinding
- Complex environment tree modeling
- Recursive day/hour/minute planning
- Human believability evaluation
- Social network metrics

Those pieces are interesting, but they would make the project larger without proving the assignment's main point. The current project keeps Maya as the only full agent and uses Jordan as a lightweight social actor, which makes it easier to inspect whether memory retrieval and reflection are actually influencing behavior.

## What Surprised Me So Far

The biggest surprise was how easy it was to accidentally make the environment too helpful. Exact hunger, energy, focus, and project-progress numbers let the agent act competently without relying much on memory. The current version keeps those internal meters for evaluation, but the agent only sees qualitative descriptions.

The second surprise was that retrieval and reflection help in different ways. Retrieval was enough to recover the professor's explicit no-retrieval-baseline requirement. Reflection mattered when the agent had to generalize from prior experience, such as choosing a reset break after noticing that focus depends on managing basic needs.

Switching back to live LLMs made the experiment less clean but more honest. The live model exposed that the environment and retrieval setup were too fragile: Maya could over-wait for Jordan, miss a one-time in-person opportunity, or bury useful reflections under repeated action memories.

The baselines also changed the claim. The project should not say that retrieval and reflection are required for all task completion. It should say that the paper's architecture creates a readable memory trail, supports obligations that depend on past events, and lets reflections become reusable knowledge.

## Next Improvements

Useful next steps:

- Make Jordan a fuller second agent with his own memory stream.
- Add a final interview mode to ask Maya what she remembers and what she learned.
- Add a terminal "done for the day" state after the project reaches 100.
- Add a stricter evaluation metric for whether retrieved memories actually change decisions.
- Finish the full/no-retrieval/no-reflection comparison with GPT-5 live runs.
- Make OpenAI mode generate richer final interviews while preserving JSON output.

## Paper Notes

See:

- `PAPER_SUMMARY.md`
- `IMPLEMENTATION_SCOPE.md`
- `SURPRISE_QUESTIONS.md`
- `ITERATION_LOG.md`
