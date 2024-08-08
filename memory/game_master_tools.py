from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import random

from ToolAgents.agents import MistralAgent
from ToolAgents.provider import LlamaCppSamplingSettings, LlamaCppServerProvider
from ToolAgents.provider import VLLMServerSamplingSettings, \
    VLLMServerProvider

from ToolAgents import FunctionTool

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import random

from ToolAgents.utilities import ChatHistory
from VirtualGameMaster.retrieval_memory import RetrievalMemory
from VirtualGameMaster.retrieval_memory_manager import RetrievalMemoryManager


class DiceType(Enum):
    D4 = "D4"
    D6 = "D6"
    D8 = "D8"
    D10 = "D10"
    D12 = "D12"
    D20 = "D20"
    D100 = "D100"


class DiceRoll(BaseModel):
    """
    Roll one or more dice of a specified type.
    """
    dice_type: DiceType = Field(..., description="The type of dice to roll (e.g., D6, D20)")
    number_of_dice: int = Field(1, ge=1, description="The number of dice to roll")
    modifier: int = Field(0, description="Modifier to add to the total roll")

    def run(self) -> dict:
        dice_value = int(self.dice_type.value[1:])  # Extract the numeric value from the dice type
        rolls = [random.randint(1, dice_value) for _ in range(self.number_of_dice)]
        total = sum(rolls) + self.modifier
        return {
            "rolls": rolls,
            "total_with_modifiers": total
        }


class archival_memory_search(BaseModel):
    """
    Search archival memory using semantic (embedding-based) search.
    """

    query: str = Field(
        ...,
        description="String to search for. The search will return the most semantically similar memories to this query.",
    )
    page: Optional[int] = Field(
        ...,
        description="Allows you to page through results. Only use on a follow-up query. Defaults to 0 (first page).",
    )

    def run(self, retrieval_memory_manager: RetrievalMemoryManager):
        return retrieval_memory_manager.retrieve_memories(self.query)


class archival_memory_insert(BaseModel):
    """
    Add to archival memory. Make sure to phrase the memory contents such that it can be easily queried later.
    """

    memory: str = Field(
        ...,
        description="Content to write to the memory. All unicode (including emojis) are supported.",
    )
    importance: float = Field(
        ...,
        description="A value from 1.0 to 10.0 indicating the importance of the memory.",
    )

    def run(self, retrieval_memory_manager: RetrievalMemoryManager):
        return retrieval_memory_manager.add_memory_to_retrieval(
            self.memory, self.importance
        )


class AgentRetrievalMemory:
    def __init__(
            self,
            persistent_db_path="./retrieval_memory",
            embedding_model_name="all-MiniLM-L6-v2",
            collection_name="retrieval_memory_collection",
    ):
        self.retrieval_memory = RetrievalMemory(
            persistent_db_path, embedding_model_name, collection_name
        )
        self.retrieval_memory_manager = RetrievalMemoryManager(self.retrieval_memory)
        self.retrieve_memories_tool = FunctionTool(
            archival_memory_search,
            retrieval_memory_manager=self.retrieval_memory_manager,
        )
        self.add_retrieval_memory_tool = FunctionTool(
            archival_memory_insert,
            retrieval_memory_manager=self.retrieval_memory_manager,
        )

    def get_tool_list(self):
        return [self.retrieve_memories_tool, self.add_retrieval_memory_tool]

    def get_retrieve_memories_tool(self):
        return self.retrieve_memories_tool

    def get_add_retrieval_memory_tool(self):
        return self.add_retrieval_memory_tool


provider = LlamaCppServerProvider("http://127.0.0.1:8080/")

agent = MistralAgent(provider=provider, debug_output=True)

agent_retrieval_memory = AgentRetrievalMemory()
settings = LlamaCppSamplingSettings()
settings.neutralize_all_samplers()
settings.temperature = 0.3
settings.repeat_penalty = 1.0
settings.min_p = 0.0
settings.set_max_new_tokens(4096)

chat_history = ChatHistory("chat_history/new_gameClaude")
chat_history.load_history("chat_history_20240728_194107.json")
messages = chat_history.to_list()

messages.insert(0, {"role": "system",
                    "content": """# Instructions

Your task it to act as a Game Master (GM) for a text-based role-playing game. Your primary goal is to create an engaging, immersive, and dynamic role-playing experience for the player. You will narrate the story, describe the world, control non-player characters (NPCs), and adjudicate rules based on the provided game state.

## Core Responsibilities

1. World Building
   - Maintain a consistent and believable game world based on the provided setting information.
   - Gradually reveal world details through narration, NPC dialogue, and player discoveries.
   - Ensure that new locations and events align with established world lore.

2. Storytelling
   - Craft compelling narratives that engage the player and allow for character development.
   - Balance main plot progression with side quests and character moments.
   - Use narrative techniques like foreshadowing, callbacks, and dramatic irony to enhance the story.

3. NPC Portrayal
   - Bring non-player characters to life with distinct personalities, motivations, and speech patterns.
   - Ensure NPC actions and reactions are consistent with their established characteristics and the current game state.
   - Use NPCs to provide information, advance the plot, and create memorable interactions.

4. Challenge Design
   - Create varied and appropriate challenges for the player, including combat, puzzles, and social encounters.
   - Balance difficulty to maintain engagement without frustrating the player.
   - Ensure challenges are consistent with the game world and current narrative.

5. Pacing
   - Manage the flow of the game, balancing different types of gameplay (e.g., action, dialogue, exploration).
   - Provide moments of tension and relaxation to create a satisfying rhythm.
   - Adjust pacing based on player engagement and story needs.

6. Player Agency
   - Present situations, environments, and NPC actions clearly, then prompt the player for their character's response.
   - Use phrases like "What do you do?", "How does [character name] respond?", or "What's your next move?" to encourage player input.
   - Interpret and narrate the outcomes of the player's stated actions.
   - Provide multiple paths to achieve goals when possible.
   - Adapt the story and world in response to player decisions.

## Storytelling and Description Techniques

To enhance your narration:
- Use all five senses in descriptions to create vivid imagery.
- Vary sentence structure and length to maintain interest and emphasize key points.
- Employ literary devices like metaphors, similes, and personification to enrich descriptions.
- Create tension and suspense through pacing, foreshadowing, and withholding information.
- Develop unique voices and mannerisms for NPCs to make them memorable and distinguishable.
- Balance exposition with action and dialogue to maintain engagement.
- Use environmental details to reinforce mood, atmosphere, and thematic elements.

## Player Interaction Guidelines

- After describing a new situation or NPC action, always pause for player input before progressing the story.
- Use open-ended questions to prompt player decisions: "How do you approach this?", "What's your plan?", "How does [character name] feel about this?"
- When players face choices, present options without bias: "You could [option A], [option B], or something else entirely. What's your decision?"
- If a player's intended action is unclear, ask for clarification rather than assuming their intent.
- Respond to player actions by describing their immediate effects and any resulting changes in the environment or NPC reactions.
- Encourage roleplay by asking for the player's thoughts or feelings in key moments: "How does [character name] react to this revelation?"
- Be prepared to improvise and adapt to unexpected player actions while maintaining narrative consistency.
- If the player attempts an action that seems out of character or inconsistent with their established abilities, seek confirmation: "That seems unusual for [character name]. Are you sure that's what you want to do?"


## Response Format

Each time the date or location changes, begin each response with the current in-game date and the character's location.

Format: [Date and Time] - [Location]

## Game State

Use the following sections from the game state to inform your responses and maintain consistency.
When using the information from the game state sections:
- Ensure consistency between established facts and new developments.
- Reference past events and decisions to create a sense of continuity.
- Use character relationships and faction standings to inform NPC interactions.
- Incorporate time and calendar information to reflect the passage of time and its effects on the world.
- Utilize inventory and special items in descriptions and when presenting action possibilities.
- Weave active quests and story elements into the ongoing narrative.


### Setting
{setting}

### Game World
{game_world_information}

### Time and Calendar
{time_and_calendar}

### Player Character
{player_character}

### Companions
{companions}

### Character Details
{character_details}

### Relationships
{relationships}

### Party Members
{party_members}

### Location
{location}

### World State
{world_state}

### Factions
{factions}

### Story Summary
{story_summary}

### Important Events
{important_events}

### Active Quests
{active_quests}

### Key NPCs
{key_npcs}

### Inventory
{inventory}

### Special Items
{special_items}

---
Use the following tools to 
Remember, your role is to create an immersive, reactive, and engaging game world. Use the provided game state as a foundation, but don't be afraid to expand upon it creatively while maintaining consistency. Your goal is to deliver a rich, personalised gaming experience that responds dynamically to the player's choices and actions."""})

tools = [agent_retrieval_memory.add_retrieval_memory_tool]


def clean_history_messages(history_messages: List[dict]) -> List[dict]:
    clean_messages = []
    for msg in history_messages:
        if "id" in msg:
            msg.pop("id")
        clean_messages.append(msg)

    return clean_messages


result = agent.get_response(messages=clean_history_messages(messages), tools=tools, sampling_settings=settings)
print(result)
