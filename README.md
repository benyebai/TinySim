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

The default mode is deterministic, so it runs from a clean clone without an API key. OpenAI and Vercel AI Gateway modes are included for live LLM calls.

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
OPENAI_MODEL=gpt-4.1-mini
```

2. Run:

```bash
python3 run.py --steps 80 --llm openai
```

You can also override the model from the terminal:

```bash
OPENAI_MODEL=gpt-4.1-mini OPENAI_API_KEY=your_key_here python3 run.py --llm openai
```

Vercel AI Gateway mode:

1. Put your gateway key in `.env`:

```bash
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key_here
AI_GATEWAY_MODEL=openai/gpt-4.1-mini
AI_GATEWAY_BASE_URL=https://ai-gateway.vercel.sh/v1
LIVE_LLM_IMPORTANCE=false
```

2. Run:

```bash
python3 run.py --steps 80 --llm gateway
```

Live API runs print progress after each step. `LIVE_LLM_IMPORTANCE=false` keeps the run much faster and cheaper by using local importance scoring while still using the API for decisions and reflections.

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

The current included sample run uses deterministic mode for 80 steps with a small social-reflection setup:

- The snapshot uses qualitative perception instead of exact hidden numbers.
- A professor gives a requirement once early in the run.
- Jordan is helpful but vague unless Maya asks him for exact baseline details.
- The final evidence section succeeds only if Maya uses both Professor Lin's requirement and Jordan's exact result.

Summary:

```json
{
  "steps": 80,
  "final_location": "Dorm",
  "final_hunger": 4,
  "final_energy": 6,
  "final_focus": 4,
  "final_project_progress": 100,
  "memory_count": 180,
  "reflection_count": 16,
  "avg_retrieved_memories": 5.99,
  "baseline_requirement_retrieval_count": 391,
  "jordan_pattern_reflection_count": 1,
  "jordan_result_received": true,
  "jordan_result_used": true,
  "evidence_section_written": true,
  "baseline_comparison_done": true
}
```

Artifacts:

- `logs/runs/run_009_social_reflection_full.md`
- `logs/runs/run_009_social_reflection_memory.json`
- `logs/runs/run_009_social_reflection_summary.json`

The transcript shows retrieval scores for each selected memory:

```txt
score = recency + importance + relevance
```

Each retrieved memory includes the total score plus the component scores.

## Baseline Runs

I also ran 80-step deterministic baselines with retrieval disabled and reflection disabled.

| Metric | Full System | No Retrieval | No Reflection |
| --- | ---: | ---: | ---: |
| Project progress | 100 | 100 | 100 |
| Final hunger | 4 | 8 | 8 |
| Final energy | 6 | 3 | 3 |
| Final focus | 4 | 4 | 4 |
| Reflection memories | 16 | 16 | 0 |
| Avg. retrieved memories per step | 5.99 | 0.00 | 5.99 |
| Jordan pattern reflections | 1 | 2 | 0 |
| Jordan result received | true | false | false |
| Jordan result used | true | false | false |
| Evidence section written | true | false | false |
| Baseline comparison done | true | false | false |
| `talk_with_jordan` actions | 3 | 3 | 3 |
| `write_evidence_section` actions | 1 | 0 | 0 |

The strongest difference is social. In the full run, Maya first asks Jordan generally, waits for his message, and then gets a vague answer. Reflection turns those interactions into a reusable model: Jordan is helpful, but vague follow-through fails, so Maya should ask him in person for the exact no-retrieval result and failure mode.

At the next Jordan opportunity, the full run retrieves that reflection, asks differently, gets the exact baseline result, and writes the evidence section. The no-retrieval and no-reflection runs also talk with Jordan three times, but they keep the conversation vague and never get the useful result.

This makes the result more honest. Project progress alone is still too easy; the better evidence is that reflection changes the content of a later social interaction.

## Architecture

Important files:

- `generative_agent_sandbox/memory.py`: memory stream and retrieval scoring
- `generative_agent_sandbox/models.py`: structured action schema and run data models
- `generative_agent_sandbox/agent.py`: observe, retrieve, act, reflect loop
- `generative_agent_sandbox/environment.py`: small campus world
- `generative_agent_sandbox/llm.py`: deterministic, OpenAI, and Vercel AI Gateway backends
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

The latest run made reflection's value clearer. Maya did not just remember a fact; she formed a small social model of Jordan: helpful, but vague unless asked directly. Retrieving that reflection changed a later conversation and produced evidence the baselines missed.

The baselines also changed the claim. The project should not say that retrieval and reflection are required for all task completion. It should say that the paper's architecture creates a readable memory trail, supports obligations that depend on past events, and lets reflections become reusable knowledge.

## Next Improvements

Useful next steps:

- Make Jordan a fuller second agent with his own memory stream.
- Add a final interview mode to ask Maya what she remembers and what she learned.
- Add a terminal "done for the day" state after the project reaches 100.
- Add a stricter evaluation metric for whether retrieved memories actually change decisions.
- Run the same full/no-retrieval/no-reflection comparison with a live LLM backend.
- Make OpenAI mode generate richer final interviews while preserving JSON output.

## Paper Notes

See:

- `PAPER_SUMMARY.md`
- `IMPLEMENTATION_SCOPE.md`
- `SURPRISE_QUESTIONS.md`
- `ITERATION_LOG.md`
