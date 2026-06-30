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

## Current Sample Run

The included sample run uses Vercel AI Gateway mode for 80 steps.

Summary:

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

The transcript shows retrieval scores for each selected memory:

```txt
score = recency + importance + relevance
```

Each retrieved memory includes the total score plus the component scores.

## Architecture

Important files:

- `generative_agent_sandbox/memory.py`: memory stream and retrieval scoring
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
- Multi-agent conversations
- Social coordination
- Information diffusion between agents
- Phaser or any visual game interface
- Sprite movement and pathfinding
- Complex environment tree modeling
- Recursive day/hour/minute planning
- Human believability evaluation
- Social network metrics

Those pieces are interesting, but they would make the project larger without proving the assignment's main point. A one-agent text simulation makes it easier to inspect whether memory retrieval and reflection are actually influencing behavior.

## What Surprised Me So Far

Even in deterministic mode, the architecture creates visible feedback loops.

One useful surprise was that the agent began retrieving early reflections about documenting evidence again and again once the project was mostly complete. This made the agent shift from implementation work to transcript review. That is good in one sense: reflection changed later behavior. But it also shows a failure mode: high-importance reflections can dominate retrieval for a long time.

Another surprise came from an implementation bug. An action that said "rest before doing more project work" was initially interpreted as work because of the word "work." The transcript exposed this quickly because the agent kept becoming more tired while supposedly resting. That reinforced why a visible run log is useful for agent debugging.

The live gateway run surfaced a sharper failure mode. Maya repeatedly reasoned that food and rest were needed, but the model often emitted vague actions like `go`, `go to Cafe`, or `go to Dorm`. The environment could not reliably translate those into eating or resting, so most outcomes had only a modest effect. This suggests that the next version needs a stricter action schema instead of open-ended action text.

## Next Improvements

Useful next steps:

- Add an ablation mode: run with reflection disabled and compare behavior.
- Add a final interview mode to ask Maya what she remembers and what she learned.
- Add stricter action schemas so environment effects are less keyword-based.
- Make OpenAI mode generate richer actions and reflections while preserving JSON output.
- Improve the README writeup after inspecting a live LLM run.

## Paper Notes

See:

- `PAPER_SUMMARY.md`
- `IMPLEMENTATION_SCOPE.md`
- `SURPRISE_QUESTIONS.md`
