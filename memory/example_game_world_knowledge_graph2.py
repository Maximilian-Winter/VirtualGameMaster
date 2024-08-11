from game_world_knowledge_graph import (
    GameWorldKnowledgeGraph, Character, Beast, Location, Item, Quest, Event, Faction,
    Relationship, CharacterType, BeastType, LocationType, ItemType, QuestType, EventType,
    FactionType, RelationshipType
)

def main():
    # Create a new GameWorldKnowledgeGraph
    game_world = GameWorldKnowledgeGraph()

    # Add entities
    print(game_world.add_character(Character(
        name="Elara Moonwhisper",
        character_type=CharacterType.NPC,
        age=150,
        race="Elf",
        gender="Female",
        description="A wise elven mage with silvery hair and piercing blue eyes."
    )))

    print(game_world.add_character(Character(
        name="Grommash Ironheart",
        character_type=CharacterType.NPC,
        age=45,
        race="Dwarf",
        gender="Male",
        description="A stout dwarf warrior with a fiery red beard and battle-worn armor."
    )))

    print(game_world.add_beast(Beast(
        name="Shadowfang",
        beast_type=BeastType.MONSTER,
        age=100,
        race="Dire Wolf",
        gender="Male",
        description="A massive, black-furred dire wolf with glowing red eyes."
    )))

    print(game_world.add_location(Location(
        name="Mistwood Forest",
        location_type=LocationType.WILDERNESS,
        description="A dense, misty forest with ancient trees and hidden mysteries."
    )))

    print(game_world.add_item(Item(
        name="Moonstone Amulet",
        item_type=ItemType.ARTIFACT,
        description="A silver amulet with a glowing moonstone that enhances magical abilities."
    )))

    print(game_world.add_quest(Quest(
        name="The Curse of Shadowfang",
        quest_type=QuestType.KILL_MONSTER,
        description="Defeat the monstrous dire wolf Shadowfang to lift the curse on Mistwood Forest."
    )))

    print(game_world.add_event(Event(
        name="The Great Mist",
        event_type=EventType.NATURAL_DISASTER,
        description="A supernatural mist that engulfed Mistwood Forest, bringing dark creatures with it."
    )))

    print(game_world.add_faction(Faction(
        name="Order of the Silver Moon",
        faction_type=FactionType.GUILD,
        description="A secretive guild of mages dedicated to protecting the realm from supernatural threats."
    )))

    # Add relationships
    print(game_world.add_relationship(Relationship(
        first_entity_id="Character-1",  # Elara Moonwhisper
        relationship_type=RelationshipType.MEMBER_OF,
        second_entity_id="Faction-1",  # Order of the Silver Moon
        description="Elara is a high-ranking member of the Order of the Silver Moon."
    )))

    print(game_world.add_relationship(Relationship(
        first_entity_id="Character-2",  # Grommash Ironheart
        relationship_type=RelationshipType.LOCATED_IN,
        second_entity_id="Location-1",  # Mistwood Forest
        description="Grommash is currently exploring Mistwood Forest."
    )))

    print(game_world.add_relationship(Relationship(
        first_entity_id="Beast-1",  # Shadowfang
        relationship_type=RelationshipType.INHABITS,
        second_entity_id="Location-1",  # Mistwood Forest
        description="Shadowfang lurks in the depths of Mistwood Forest."
    )))

    print(game_world.add_relationship(Relationship(
        first_entity_id="Character-1", # Elara Moonwhisper
        relationship_type=RelationshipType.POSSESSES,
        second_entity_id="Item-1",  # Moonstone Amulet
        description="Elara wears the Moonstone Amulet, enhancing her magical powers."
    )))

    # Perform queries
    print("\nQuerying characters:")
    print(game_world.query_characters(race="Elf"))

    print("\nQuerying beasts:")
    print(game_world.query_beasts(beast_type=BeastType.MONSTER))

    print("\nQuerying locations:")
    print(game_world.query_locations(location_type=LocationType.WILDERNESS))

    print("\nQuerying items:")
    print(game_world.query_items(item_type=ItemType.ARTIFACT))

    print("\nQuerying quests:")
    print(game_world.query_quests(quest_type=QuestType.KILL_MONSTER))

    print("\nQuerying events:")
    print(game_world.query_events(event_type=EventType.NATURAL_DISASTER))

    print("\nQuerying factions:")
    print(game_world.query_factions(faction_type=FactionType.GUILD))

    print("\nQuerying relationships:")
    print(game_world.query_relationships("Character-1"))

    print("\nFinding path:")
    print(game_world.find_path("Character-1", "Beast-1"))

    print("\nGetting entity details:")
    print(game_world.get_entity_details("Character-1"))

    print("\nQuerying entities by attribute:")
    print(game_world.query_entities_by_attribute("race", "Elf"))

    print("\nGetting nearby entities:")
    print(game_world.get_nearby_entities("Location-1"))

    print(game_world.query_relationships("Location-1"))
    print(game_world.query_relationships("Beast-1"))

    # Save the game world
    game_world.save("my_game_world.json")

    # Load the game world
    loaded_game_world = GameWorldKnowledgeGraph.load("my_game_world.json")

    print("\nVerifying loaded game world:")
    print(loaded_game_world.get_entity_details("Character-1"))

if __name__ == "__main__":
    main()