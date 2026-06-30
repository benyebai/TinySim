# Questions For What Might Surprise Us

This file collects questions to guide the "what surprised you" section of the final README.

The assignment says this is the most important part, so we should watch for both successful emergence and broken behavior.

## Memory And Retrieval

- Did the agent retrieve memories that actually made sense for the current decision?
- Did recency dominate too much, causing the agent to forget older but important events?
- Did importance dominate too much, causing the agent to obsess over one dramatic memory?
- Did relevance retrieve surprising connections between unrelated-seeming events?
- Did the agent ever ignore a memory that seemed obviously relevant to us?
- Did the agent repeat actions because it failed to retrieve that it had already done them?

## Reflection

- Did reflections make the agent more coherent over time?
- Did reflections create useful higher-level beliefs, or did they just restate recent events?
- Did a reflection cause a later action to change in a visible way?
- Did the agent overgeneralize from too little evidence?
- Did the agent form a self-story that was not really supported by its memories?
- Were reflections more useful than raw observations?

## Behavior

- Did the agent develop a routine without being explicitly programmed to have one?
- Did the agent balance goals in a believable way, such as work, food, rest, and curiosity?
- Did it get stuck in a repetitive loop?
- Did it make a decision that felt oddly human?
- Did it make a decision that felt obviously artificial?
- Did it become more focused or more scattered as the run progressed?

## Environment

- Did the simple environment produce enough interesting pressure on the agent?
- Were the locations too generic to create meaningful choices?
- Did the agent act as if the world had details we never gave it?
- Did missing environment constraints cause unrealistic behavior?
- Did the agent invent objects, people, or events that were not in the simulation?

## LLM Behavior

- Did the agent hallucinate details not present in memory?
- Did it speak or act too formally?
- Did it become too agreeable or too cautious?
- Did the model's general world knowledge overpower the actual simulated experience?
- Did prompts need stricter instructions to keep the agent grounded?

## Evaluation Questions

- If we disable reflection, does the run feel flatter or less coherent?
- If we disable importance, does retrieval become too shallow?
- If we use only recent memories, does the agent lose long-term continuity?
- Which part of the architecture seemed to matter most in practice?
- Which part felt overbuilt for a one-agent simulation?

## Possible README Framing

Useful surprise statements might look like:

- "I expected reflection to be decorative, but it changed later behavior by..."
- "The retrieval system worked best when..."
- "The agent was most believable when..."
- "The agent broke down when..."
- "The simplest environment constraint that mattered was..."
- "The most useful thing I kept from the paper was..."
- "The biggest thing I cut from the paper was..."
