from ToolAgents.agents import MistralAgent
from ToolAgents.provider import LlamaCppServerProvider
from ToolAgents.utilities import ChatHistory
from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph, CharacterType, Character, CharacterQuery, BeastType, Beast, BeastQuery, LocationType, Location, LocationQuery, ItemType, Item, ItemQuery, FactionType, Faction, FactionQuery, QuestType, Quest, QuestQuery, EventType, Event, EventQuery
from code_executer import PythonCodeExecutor, system_message_code_agent, run_code_agent

provider = LlamaCppServerProvider("http://127.0.0.1:8080/")

agent = MistralAgent(provider=provider, debug_output=True)

settings = provider.get_default_settings()
settings.neutralize_all_samplers()
settings.temperature = 0.3


settings.set_stop_tokens(["</s>"], None)
settings.set_max_new_tokens(4096)

game_world = GameWorldKnowledgeGraph()
tools = game_world.get_unified_tools()

chat_history = ChatHistory()
chat_history.add_system_message("<system_instructions>\n" + system_message_code_agent + f"""\n\nYour task is to generate a world for a pen and paper game and save it to a knowledge graph.

You have access to the following predefined types and functions to add information to the world knowledge graph:

```python
{'\n\n'.join([tool.get_python_documentation() for tool in tools])}
```

You can use these predefined types and call these predefined functions in Python like in this example:

```python_interpreter
# Create characters
hero = Character(name="Elara", character_type=CharacterType.PLAYER, age=25, race="Elf", gender="Female", description="A skilled archer and protector of the forest")
villain = Character(name="Malachar", character_type=CharacterType.NPC, age=100, race="Human", gender="Male", description="A dark wizard seeking ancient artifacts")

hero_id = add_entity(hero)
villain_id = add_entity(villain)

# Create a beast
dragon = Beast(name="Fafnir", beast_type=BeastType.MYTHICAL, age=500, race="Dragon", gender="Male", description="An ancient fire-breathing dragon")
dragon_id = add_entity(dragon)

# Create locations
forest = Location(name="Whispering Woods", location_type=LocationType.WILDERNESS, description="A mystical forest filled with ancient trees and magical creatures")
castle = Location(name="Shadowspire Castle", location_type=LocationType.CASTLE, description="A foreboding castle perched atop a cliff, home to dark forces")

forest_id = add_entity(forest)
castle_id = add_entity(castle)

# Create an item
artifact = Item(name="Orb of Destiny", item_type=ItemType.ARTIFACT, description="A powerful artifact said to control the fate of the world")
artifact_id = add_entity(artifact)

# Create a quest
quest = Quest(name="Retrieve the Orb", quest_type=QuestType.FIND_ITEM, description="Find and secure the Orb of Destiny before it falls into the wrong hands")
quest_id = add_entity(quest)

# Create an event
battle = Event(name="Battle of Shadowspire", event_type=EventType.BATTLE, description="The final confrontation between good and evil forces")
battle_id = add_entity(battle)

# Create a faction
guild = Faction(name="Guardians of the Realm", faction_type=FactionType.GUILD, description="A secret society dedicated to protecting the world from dark forces")
guild_id = add_entity(guild)

# Add relationships
add_relationship(Relationship(hero_id, RelationshipType.RESIDES_IN, forest_id, "Elara's home"))
add_relationship(Relationship(villain_id, RelationshipType.RESIDES_IN, castle_id, "Malachar's lair"))
add_relationship(Relationship(hero_id, RelationshipType.SEEKS, artifact_id, "Elara's mission"))
add_relationship(Relationship(villain_id, RelationshipType.SEEKS, artifact_id, "Malachar's goal"))
add_relationship(Relationship(dragon_id, RelationshipType.GUARDS, artifact_id, "Fafnir protects the Orb"))
add_relationship(Relationship(hero_id, RelationshipType.MEMBER_OF, guild_id, "Elara is a member of the Guardians"))

# Query characters
hero_query = CharacterQuery(character_type=CharacterType.PLAYER, race="Elf")
heroes = query_entities(hero_query)
print("Heroes:", heroes)

# Query beasts
beast_query = BeastQuery(beast_type=BeastType.MYTHICAL)
mythical_beasts = query_entities(beast_query)
print("Mythical Beasts:", mythical_beasts)

# Query locations
location_query = LocationQuery(location_type=LocationType.CASTLE)
castles = query_entities(location_query)
print("Castles:", castles)

# Query items
item_query = ItemQuery(item_type=ItemType.ARTIFACT)
artifacts = query_entities(item_query)
print("Artifacts:", artifacts)

# Query quests
quest_query = QuestQuery(quest_type=QuestType.FIND_ITEM)
find_item_quests = query_entities(quest_query)
print("Find Item Quests:", find_item_quests)

# Query events
event_query = EventQuery(event_type=EventType.BATTLE)
battles = query_entities(event_query)
print("Battles:", battles)

# Query factions
faction_query = FactionQuery(faction_type=FactionType.GUILD)
guilds = query_entities(faction_query)
print("Guilds:", guilds)
```

When you add an entity, always remember to save the return value (entity id) in a variable. You need these entity ids to add relationships!
""" + "\n</system_instructions>")
python_code_executor = PythonCodeExecutor(
    tools=tools, predefined_classes=[CharacterType, Character, CharacterQuery, BeastType, Beast, BeastQuery, LocationType, Location, LocationQuery, ItemType, Item, ItemQuery, FactionType, Faction, FactionQuery, QuestType, Quest, QuestQuery, EventType, Event, EventQuery])

prompt = "Generate a detailed game world with many entities and relationships, based on the Sword Coast and Waterdeep!"

run_code_agent(agent=agent, settings=settings, chat_history=chat_history, user_input=prompt,
               python_code_executor=python_code_executor)

chat_history.save_history("./test_chat_history_after_mistral.json")
