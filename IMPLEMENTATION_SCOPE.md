# Implementation Scope

## Assignment Goal

Build a single generative agent with the core memory architecture from the paper and run it through 50-100 time steps in a simple simulated environment.

The assignment requires:

1. A memory stream
2. Retrieval
3. Reflection
4. A completed run log
5. A README writeup explaining what we kept, what we cut, and what surprised us

## Proposed Project

We will build one agent in a small text-based environment.

Suggested agent:

Maya Chen, a student researcher trying to balance coursework, meals, rest, and progress on a behavioral simulation project.

Suggested locations:

- Dorm
- Library
- Cafe
- Classroom
- Park
- Store

Each time step represents a small slice of time. At each step, the agent observes the environment, retrieves relevant memories, chooses an action, logs the result, and stores a new memory.

## Core Loop

Each simulation step should do roughly this:

1. Read the current world state.
2. Generate or select an observation.
3. Add the observation to the memory stream.
4. Retrieve relevant memories for the current decision.
5. Ask the LLM to choose the agent's next action.
6. Apply the action to the environment.
7. Store the action as another memory.
8. Occasionally trigger reflection.

## Memory Object

Each memory should include:

- id
- timestamp or step number
- type: observation, action, reflection, or plan
- text
- importance score
- created_at step
- last_accessed step

Optional fields:

- location
- tags
- evidence ids for reflections

## Retrieval

We will keep the paper's retrieval idea but simplify where needed.

Retrieval score:

```txt
score = recency + importance + relevance
```

Possible implementation:

- Recency: newer or recently accessed memories get a higher score.
- Importance: LLM rates each memory from 1 to 10, or a fallback heuristic assigns a score.
- Relevance: embedding similarity if available, otherwise simple keyword overlap or lightweight text similarity.

We should log which memories were retrieved at each important step so we can inspect whether retrieval shaped behavior.

## Reflection

Reflection should happen a few times during the simulation.

Possible triggers:

- Every 20 steps
- When accumulated importance since last reflection crosses a threshold
- At fixed moments such as step 25, 50, and 75

Reflection prompt:

Given the recent memories below, produce 3-5 high-level insights about the agent's goals, habits, concerns, or changing priorities. Each insight should be grounded in specific memories.

The resulting reflections are saved back into the memory stream.

## What We Are Keeping From The Paper

We are keeping:

- Natural-language memory stream
- Retrieval by recency, importance, and relevance
- Importance scoring
- Reflection memories
- A simple observe-retrieve-act loop
- A transcript of the full run

We are also keeping importance scoring even though we could cut it. It is worth keeping because it gives the agent a way to distinguish mundane events from meaningful ones, and it gives us something interesting to analyze in the README.

## What We Are Discarding

We are cutting:

- 25 agents
- Multi-agent social dynamics
- Phaser or any visual game interface
- Sprite movement
- Pathfinding
- Complex environment tree modeling
- Recursive daily/hourly/minute planning
- Natural-language user intervention during the run
- Valentine party style group coordination
- Human believability evaluation
- Social network metrics

## Why We Are Discarding Those Pieces

The assignment is a six-hour exercise focused on reasoning and architectural judgment. The core test is whether one agent can accumulate experience, retrieve useful memories, reflect on them, and behave differently later because of that process.

The paper's multi-agent world is valuable research infrastructure, but it would distract from the assignment. A smaller implementation will make the memory and reflection behavior easier to inspect.

## Minimal Successful Version

A strong minimal version should:

- Run 50-100 steps from a clean clone.
- Save a transcript or log of the full run.
- Show memory entries being created.
- Show retrieval results before decisions.
- Generate at least two reflection events.
- Demonstrate at least one later action influenced by a previous memory or reflection.

## Stretch Goals

If time allows:

- Add a deterministic fallback mode so the project can run without an API key.
- Save memories as JSON for inspection.
- Add a small CLI option for number of steps.
- Add a final interview mode where we ask the agent what it learned.
- Compare behavior with reflection enabled versus disabled.
