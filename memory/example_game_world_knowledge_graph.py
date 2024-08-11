from game_world_knowledge_graph import GameWorldKnowledgeGraph, Character, Beast, Location, Item, Quest, Event, Faction, Relationship
from game_world_knowledge_graph import CharacterType, BeastType, LocationType, ItemType, QuestType, EventType, FactionType, RelationshipType

def print_separator(title):
    print(f"\n{'-'*20} {title} {'-'*20}\n")

# Initialize the GameWorldKnowledgeGraph
game_world = GameWorldKnowledgeGraph()

print_separator("Adding Characters")

characters = [
    Character(character_name="Gandalf", character_type=CharacterType.NPC, age=2000, race="Maiar", gender="Male", description="A wise wizard"),
    Character(character_name="Frodo Baggins", character_type=CharacterType.PLAYER, age=33, race="Hobbit", gender="Male", description="The Ring-bearer"),
    Character(character_name="Aragorn", character_type=CharacterType.NPC, age=87, race="Human", gender="Male", description="Heir to the throne of Gondor"),
    Character(character_name="Galadriel", character_type=CharacterType.NPC, age=7000, race="Elf", gender="Female", description="Lady of Lothlórien"),
    Character(character_name="Saruman", character_type=CharacterType.NPC, age=2000, race="Maiar", gender="Male", description="A corrupted wizard")
]

character_ids = {}
for character in characters:
    result = game_world.add_character(character)
    print(result)
    character_ids[character.character_name] = result.split()[-1]

print_separator("Adding Beasts")

beasts = [
    Beast(beast_name="Smaug", beast_type=BeastType.MYTHICAL, age=300, race="Dragon", gender="Male", description="A fire-breathing dragon"),
    Beast(beast_name="Shadowfax", beast_type=BeastType.NON_MONSTER, age=20, race="Horse", gender="Male", description="Lord of all horses"),
    Beast(beast_name="Shelob", beast_type=BeastType.MONSTER, age=500, race="Giant Spider", gender="Female", description="An ancient evil in spider form")
]

beast_ids = {}
for beast in beasts:
    result = game_world.add_beast(beast)
    print(result)
    beast_ids[beast.beast_name] = result.split()[-1]

print_separator("Adding Locations")

locations = [
    Location(location_name="The Shire", location_type=LocationType.VILLAGE, description="Home of the Hobbits"),
    Location(location_name="Rivendell", location_type=LocationType.CITY, description="Elven outpost and home of Elrond"),
    Location(location_name="Mordor", location_type=LocationType.WILDERNESS, description="Dark land of Sauron"),
    Location(location_name="Minas Tirith", location_type=LocationType.CITY, description="Capital of Gondor"),
    Location(location_name="The Prancing Pony", location_type=LocationType.INN, description="Famous inn in Bree")
]

location_ids = {}
for location in locations:
    result = game_world.add_location(location)
    print(result)
    location_ids[location.location_name] = result.split()[-1]

print_separator("Adding Items")

items = [
    Item(item_name="The One Ring", item_type=ItemType.ARTIFACT, description="A powerful and dangerous artifact"),
    Item(item_name="Sting", item_type=ItemType.WEAPON, description="Bilbo's elvish dagger"),
    Item(item_name="Mithril Shirt", item_type=ItemType.ARMOR, description="Lightweight and strong armor"),
    Item(item_name="Palantír", item_type=ItemType.ARTIFACT, description="Seeing-stone for long-distance communication")
]

item_ids = {}
for item in items:
    result = game_world.add_item(item)
    print(result)
    item_ids[item.item_name] = result.split()[-1]

print_separator("Adding Quests")

quests = [
    Quest(quest_name="Destroy the One Ring", quest_type=QuestType.DELIVER, description="Cast the One Ring into the fires of Mount Doom"),
    Quest(quest_name="Defend Minas Tirith", quest_type=QuestType.KILL_MONSTER, description="Protect the city from Sauron's forces"),
    Quest(quest_name="Find the Heir of Isildur", quest_type=QuestType.FIND_CHARACTER, description="Locate the rightful heir to the throne of Gondor")
]

quest_ids = {}
for quest in quests:
    result = game_world.add_quest(quest)
    print(result)
    quest_ids[quest.quest_name] = result.split()[-1]

print_separator("Adding Events")

events = [
    Event(event_name="The Council of Elrond", event_type=EventType.LORE, description="A secret council to decide the fate of the One Ring"),
    Event(event_name="Battle of Helm's Deep", event_type=EventType.BATTLE, description="A great battle against Saruman's forces"),
    Event(event_name="Crowning of Aragorn", event_type=EventType.HISTORY, description="Aragorn is crowned King of Gondor")
]

event_ids = {}
for event in events:
    result = game_world.add_event(event)
    print(result)
    event_ids[event.event_name] = result.split()[-1]

print_separator("Adding Factions")

factions = [
    Faction(faction_name="The Fellowship of the Ring", faction_type=FactionType.GROUP, description="A group formed to destroy the One Ring"),
    Faction(faction_name="Elves of Rivendell", faction_type=FactionType.TRIBE, description="Elves residing in Rivendell"),
    Faction(faction_name="Riders of Rohan", faction_type=FactionType.GOVERNMENT, description="Horsemen of the kingdom of Rohan")
]

faction_ids = {}
for faction in factions:
    result = game_world.add_faction(faction)
    print(result)
    faction_ids[faction.faction_name] = result.split()[-1]

print_separator("Adding Relationships")

relationships = [
    Relationship(first_entity_id=character_ids["Gandalf"], relationship_type=RelationshipType.MENTOR, second_entity_id=character_ids["Frodo Baggins"], description="Gandalf mentors Frodo"),
    Relationship(first_entity_id=character_ids["Frodo Baggins"], relationship_type=RelationshipType.POSSESSES, second_entity_id=item_ids["The One Ring"], description="Frodo carries the One Ring"),
    Relationship(first_entity_id=character_ids["Aragorn"], relationship_type=RelationshipType.ALLY, second_entity_id=faction_ids["Riders of Rohan"], description="Aragorn is allied with the Riders of Rohan"),
    Relationship(first_entity_id=character_ids["Galadriel"], relationship_type=RelationshipType.RESIDES_IN, second_entity_id=location_ids["Rivendell"], description="Galadriel resides in Rivendell"),
    Relationship(first_entity_id=character_ids["Saruman"], relationship_type=RelationshipType.ENEMY, second_entity_id=faction_ids["The Fellowship of the Ring"], description="Saruman is an enemy of the Fellowship"),
    Relationship(first_entity_id=beast_ids["Smaug"], relationship_type=RelationshipType.THREATENS, second_entity_id=location_ids["The Shire"], description="Smaug threatens the Shire"),
    Relationship(first_entity_id=quest_ids["Destroy the One Ring"], relationship_type=RelationshipType.INVOLVES, second_entity_id=location_ids["Mordor"], description="The quest involves traveling to Mordor"),
    Relationship(first_entity_id=event_ids["The Council of Elrond"], relationship_type=RelationshipType.LOCATED_IN, second_entity_id=location_ids["Rivendell"], description="The Council takes place in Rivendell")
]

for relationship in relationships:
    print(game_world.add_relationship(relationship))

print_separator("Querying Characters")

print("All Hobbits:")
print(game_world.query_characters(race="Hobbit"))

print("\nAll NPCs:")
print(game_world.query_characters(character_type=CharacterType.NPC))

print("\nAll characters over 1000 years old:")
print(game_world.query_characters(age=1000))  # Note: This won't work as intended because age is compared with exact equality. You might want to modify the query_characters method to allow for range queries.

print_separator("Querying Beasts")

print("All Mythical beasts:")
print(game_world.query_beasts(beast_type=BeastType.MYTHICAL))

print("\nAll beasts in Mordor:")
print(game_world.query_beasts(location="Mordor"))

print_separator("Querying Locations")

print("All Cities:")
print(game_world.query_locations(location_type=LocationType.CITY))

print("\nAll locations with 'Mordor' in the name:")
print(game_world.query_locations(name="Mordor"))

print_separator("Querying Items")

print("All Artifacts:")
print(game_world.query_items(item_type=ItemType.ARTIFACT))

print("\nAll items in Rivendell:")
print(game_world.query_items(location="Rivendell"))

print_separator("Querying Quests")

print("All Delivery quests:")
print(game_world.query_quests(quest_type=QuestType.DELIVER))

print("\nAll quests involving Mordor:")
print(game_world.query_quests(location="Mordor"))

print_separator("Querying Events")

print("All Lore events:")
print(game_world.query_events(event_type=EventType.LORE))

print("\nAll events in Rivendell:")
print(game_world.query_events(location="Rivendell"))

print_separator("Querying Factions")

print("All Group factions:")
print(game_world.query_factions(faction_type=FactionType.GROUP))

print("\nAll factions in Rivendell:")
print(game_world.query_factions(location="Rivendell"))

print_separator("Saving and Loading")

# Save the game world
game_world.save("middle_earth.json")
print("Game world saved to 'middle_earth.json'")

# Load the game world
loaded_game_world = GameWorldKnowledgeGraph.load("middle_earth.json")
print("Game world loaded from 'middle_earth.json'")

print("\nQuerying characters from loaded game world:")
print(loaded_game_world.query_characters(race="Hobbit"))

print("\nQuerying events from loaded game world:")
print(loaded_game_world.query_events(event_type=EventType.BATTLE))