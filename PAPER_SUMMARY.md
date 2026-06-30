# Paper Summary: Generative Agents

Paper: "Generative Agents: Interactive Simulacra of Human Behavior"

## Big Idea

The paper argues that believable agents need more than a single LLM prompt. A believable agent should accumulate experience over time, retrieve the right experiences when making decisions, and synthesize those experiences into higher-level beliefs that shape future behavior.

In other words, the LLM is not the whole agent. The agent is the LLM plus an architecture for memory, retrieval, reflection, planning, and action.

## Core Architecture

The paper's agent architecture has three main pieces:

1. Memory stream
2. Retrieval
3. Reflection

Planning is also important in the full paper, but for our assignment the required core is memory, retrieval, and reflection.

## Memory Stream

The memory stream is a chronological record of the agent's experiences. Each memory is written in natural language.

Examples:

- "Maya noticed that the library was crowded."
- "Maya talked with a barista about feeling tired."
- "Maya spent the afternoon reading about behavioral modeling."

The paper stores observations, reflections, and plans in the same memory stream so that later decisions can draw from all of them.

## Retrieval

The agent cannot put its full life history into every prompt. Instead, it retrieves a small set of memories that are most useful for the current decision.

The paper scores memories using three signals:

- Recency: Recently accessed memories matter more.
- Importance: Emotionally or practically significant memories matter more.
- Relevance: Memories related to the current situation matter more.

The final retrieval score is a weighted combination of those signals.

This is the key mechanism that lets the agent seem coherent over time without stuffing every past event into the prompt.

## Reflection

Reflection turns raw memories into higher-level conclusions.

Raw memories might say:

- "Maya studied in the library for two hours."
- "Maya skipped lunch to finish her notes."
- "Maya felt proud after organizing her research plan."

A reflection might say:

- "Maya is becoming increasingly committed to finishing her research project."

The paper stores reflections back into the same memory stream, which means future decisions can retrieve both concrete events and abstract self-knowledge.

## Planning

The full paper also uses planning to make agents behave consistently over longer periods. Plans are generated in broad strokes and then decomposed into smaller actions.

Example:

- Broad plan: "Work on research in the afternoon."
- Smaller plan: "Go to the library, outline notes, take a break, revise draft."

This helps avoid repetitive or incoherent actions, like eating lunch three times in a row.

For our assignment, we can use a much lighter version of planning. We do not need the paper's full recursive planning system.

## What The Paper Demonstrates

The authors built Smallville, a Sims-like world with 25 agents. The agents:

- Went through daily routines.
- Remembered interactions.
- Formed relationships.
- Spread information.
- Coordinated around events.
- Reflected on past experience.

The most famous example is the Valentine's Day party. One agent starts with the intention to throw a party, and through conversations and memory, other agents hear about it, remember it, and some show up.

## Key Findings

The paper's evaluation suggests that memory, planning, and reflection all improve believability.

The biggest failures were:

- Agents sometimes failed to retrieve the right memory.
- Agents sometimes embellished beyond what they actually knew.
- Dialogue could become overly formal.
- Agents sometimes made odd choices because the environment was underspecified.

## Main Takeaway For Our Project

We should not try to rebuild Smallville. The important contribution is the cognitive architecture:

Observe the world, store memories, retrieve relevant memories, reflect into higher-level beliefs, and use those memories and reflections to decide what to do next.

Our goal is to build a small, clear version of that loop for one agent.
