from game_world_knowledge_graph import GameWorldKnowledgeGraph, Character, Beast, Location, Item, Quest, Event, Faction, Relationship
from game_world_knowledge_graph import EntityType, CharacterType, BeastType, LocationType, ItemType, QuestType, EventType, FactionType, RelationshipType



# Create a new GameWorldKnowledgeGraph instance
game_world = GameWorldKnowledgeGraph()

# Add a character
hero = Character(
    character_name="Aria Starlight",
    character_type=CharacterType.PLAYER,
    age=25,
    race="Elf",
    gender="Female",
    description="A skilled archer and mage from the Starlight clan."
)
hero_id = game_world.add_character(hero)

# Add a beast
dragon = Beast(
    beast_name="Fyreborn",
    beast_type=BeastType.MYTHICAL,
    age=500,
    race="Dragon",
    gender="Male",
    description="An ancient fire-breathing dragon that guards a vast treasure hoard."
)
dragon_id = game_world.add_beast(dragon)

# Add a location
city = Location(
    location_name="Silvermoon City",
    location_type=LocationType.CITY,
    description="A bustling metropolis known for its magical academies and grand architecture."
)
city_id = game_world.add_location(city)

# Add an item
magic_bow = Item(
    item_name="Whisperwind",
    item_type=ItemType.WEAPON,
    description="An enchanted bow that never misses its target and whispers secrets of the wind to its wielder."
)
bow_id = game_world.add_item(magic_bow)

# Add a quest
dragon_slayer_quest = Quest(
    quest_name="Slay the Dragon",
    quest_type=QuestType.KILL_MONSTER,
    description="Defeat the fearsome dragon Fyreborn and claim its treasure for Silvermoon City."
)
quest_id = game_world.add_quest(dragon_slayer_quest)

# Add an event
annual_festival = Event(
    event_name="Festival of Lights",
    event_type=EventType.FESTIVAL,
    description="An annual celebration in Silvermoon City where magical lanterns illuminate the night sky."
)
event_id = game_world.add_event(annual_festival)

# Add a faction
mages_guild = Faction(
    faction_name="Order of the Arcane",
    faction_type=FactionType.GUILD,
    description="A powerful organization of mages dedicated to the study and preservation of magical knowledge."
)
faction_id = game_world.add_faction(mages_guild)

# Add relationships
game_world.add_relationship(Relationship(
    first_entity_id=hero_id,
    relationship_type=RelationshipType.RESIDES_IN,
    second_entity_id=city_id,
    description="Aria Starlight currently resides in Silvermoon City."
))

game_world.add_relationship(Relationship(
    first_entity_id=hero_id,
    relationship_type=RelationshipType.POSSESSES,
    second_entity_id=bow_id,
    description="Aria Starlight wields the magical bow Whisperwind."
))

game_world.add_relationship(Relationship(
    first_entity_id=quest_id,
    relationship_type=RelationshipType.INVOLVES,
    second_entity_id=dragon_id,
    description="The quest involves slaying the dragon Fyreborn."
))

# Perform some queries
print("Characters in Silvermoon City:")
characters_in_city = game_world.query_characters(location="Silvermoon")
for char_id in characters_in_city:
    char_data = game_world.knowledge_graph.get_entity_attributes(char_id)
    print(f"- {char_data['character_name']} ({char_data['character_type']})")

print("\nItems possessed by Aria Starlight:")
hero_relationships = game_world.knowledge_graph.get_relationships(hero_id)
for rel in hero_relationships:
    if rel['type'] == RelationshipType.POSSESSES.name:
        item_data = game_world.knowledge_graph.get_entity_attributes(rel['target'])
        print(f"- {item_data['item_name']} ({item_data['item_type']})")

print("\nQuests involving dragons:")
dragon_quests = game_world.query_quests(quest_type=QuestType.KILL_MONSTER)
for quest_id in dragon_quests:
    quest_data = game_world.knowledge_graph.get_entity_attributes(quest_id)
    quest_relationships = game_world.knowledge_graph.get_relationships(quest_id)
    for rel in quest_relationships:
        if rel['type'] == RelationshipType.INVOLVES.name:
            target_data = game_world.knowledge_graph.get_entity_attributes(rel['target'])
            if target_data['entity_type'] == EntityType.BEAST.name and target_data['beast_type'] == BeastType.MYTHICAL.name:
                print(f"- {quest_data['quest_name']}: {quest_data['description']}")

# Save the game world to a file
game_world.save("my_game_world.json")

# Later, you can load the game world from the file
loaded_game_world = GameWorldKnowledgeGraph.load("my_game_world.json")