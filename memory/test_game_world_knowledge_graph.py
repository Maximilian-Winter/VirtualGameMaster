import unittest
from game_world_knowledge_graph import (
    GameWorldKnowledgeGraph, Character, Beast, Location, Item, Quest, Event, Faction,
    Relationship, CharacterType, BeastType, LocationType, ItemType, QuestType, EventType,
    FactionType, RelationshipType
)


def create_sample_world():
    world = GameWorldKnowledgeGraph()

    # Add characters
    hero_id = world.add_character(Character(
        character_name="Aric Strongheart",
        character_type=CharacterType.PLAYER,
        age=25,
        race="Human",
        gender="Male",
        description="A brave warrior on a quest to save the kingdom."
    ))

    villain_id = world.add_character(Character(
        character_name="Malakar the Dark",
        character_type=CharacterType.NPC,
        age=150,
        race="Elf",
        gender="Male",
        description="An evil sorcerer bent on world domination."
    ))

    # Add beast
    dragon_id = world.add_beast(Beast(
        beast_name="Fafnir",
        beast_type=BeastType.MYTHICAL,
        age=500,
        race="Dragon",
        gender="Male",
        description="A fearsome dragon guarding an ancient treasure."
    ))

    # Add locations
    castle_id = world.add_location(Location(
        location_name="Castle Luminara",
        location_type=LocationType.CASTLE,
        description="The shining seat of power in the kingdom."
    ))

    dark_tower_id = world.add_location(Location(
        location_name="Tower of Shadows",
        location_type=LocationType.DUNGEON,
        description="The ominous lair of Malakar the Dark."
    ))

    # Add item
    sword_id = world.add_item(Item(
        item_name="Excalibur",
        item_type=ItemType.WEAPON,
        description="A legendary sword of immense power."
    ))

    # Add quest
    quest_id = world.add_quest(Quest(
        quest_name="Defeat Malakar",
        quest_type=QuestType.KILL_CHARACTER,
        description="Defeat the evil sorcerer Malakar and save the kingdom."
    ))

    # Add event
    battle_id = world.add_event(Event(
        event_name="Battle of Luminara",
        event_type=EventType.BATTLE,
        description="The final confrontation between Aric and Malakar."
    ))

    # Add faction
    knights_id = world.add_faction(Faction(
        faction_name="Knights of the Round Table",
        faction_type=FactionType.GUILD,
        description="A noble order of knights sworn to protect the kingdom."
    ))

    # Add relationships
    world.add_relationship(Relationship(
        first_entity_id=hero_id,
        relationship_type=RelationshipType.ENEMY,
        second_entity_id=villain_id,
        description="Aric and Malakar are mortal enemies."
    ))

    world.add_relationship(Relationship(
        first_entity_id=hero_id,
        relationship_type=RelationshipType.POSSESSES,
        second_entity_id=sword_id,
        description="Aric wields the legendary sword Excalibur."
    ))

    world.add_relationship(Relationship(
        first_entity_id=hero_id,
        relationship_type=RelationshipType.RESIDES_IN,
        second_entity_id=castle_id,
        description="Aric lives in Castle Luminara."
    ))

    world.add_relationship(Relationship(
        first_entity_id=villain_id,
        relationship_type=RelationshipType.RESIDES_IN,
        second_entity_id=dark_tower_id,
        description="Malakar resides in the Tower of Shadows."
    ))

    world.add_relationship(Relationship(
        first_entity_id=dragon_id,
        relationship_type=RelationshipType.GUARDS,
        second_entity_id=dark_tower_id,
        description="Fafnir guards the Tower of Shadows."
    ))

    world.add_relationship(Relationship(
        first_entity_id=hero_id,
        relationship_type=RelationshipType.MEMBER_OF,
        second_entity_id=knights_id,
        description="Aric is a member of the Knights of the Round Table."
    ))

    return world


class TestGameWorldKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        self.world = create_sample_world()

    def test_query_characters(self):
        heroes = self.world.query_characters(character_type=CharacterType.PLAYER)
        self.assertEqual(len(heroes), 1)
        self.assertIn("Aric", self.world.knowledge_graph.get_entity_attributes(heroes[0])["character_name"])

        villains = self.world.query_characters(character_type=CharacterType.NPC, name="Malakar")
        self.assertEqual(len(villains), 1)
        self.assertIn("Dark", self.world.knowledge_graph.get_entity_attributes(villains[0])["character_name"])

    def test_query_beasts(self):
        dragons = self.world.query_beast(beast_type=BeastType.MYTHICAL, name="Fafnir")
        self.assertEqual(len(dragons), 1)
        self.assertEqual(self.world.knowledge_graph.get_entity_attributes(dragons[0])["age"], 500)

    def test_query_locations(self):
        castles = self.world.query_location(location_type=LocationType.CASTLE)
        self.assertEqual(len(castles), 1)
        self.assertIn("Luminara", self.world.knowledge_graph.get_entity_attributes(castles[0])["location_name"])

    def test_query_items(self):
        weapons = self.world.query_items(item_type=ItemType.WEAPON)
        self.assertEqual(len(weapons), 1)
        self.assertEqual(self.world.knowledge_graph.get_entity_attributes(weapons[0])["item_name"], "Excalibur")

    def test_query_quests(self):
        kill_quests = self.world.query_quests(quest_type=QuestType.KILL_CHARACTER)
        self.assertEqual(len(kill_quests), 1)
        self.assertIn("Defeat Malakar", self.world.knowledge_graph.get_entity_attributes(kill_quests[0])["quest_name"])

    def test_query_events(self):
        battles = self.world.query_events(event_type=EventType.BATTLE)
        self.assertEqual(len(battles), 1)
        self.assertIn("Luminara", self.world.knowledge_graph.get_entity_attributes(battles[0])["event_name"])

    def test_query_factions(self):
        guilds = self.world.query_factions(faction_type=FactionType.GUILD)
        self.assertEqual(len(guilds), 1)
        self.assertIn("Knights", self.world.knowledge_graph.get_entity_attributes(guilds[0])["faction_name"])

    def test_relationships(self):
        hero = self.world.query_characters(name="Aric")[0]
        villain = self.world.query_characters(name="Malakar")[0]

        hero_relationships = self.world.knowledge_graph.get_relationships(hero)
        villain_relationships = self.world.knowledge_graph.get_relationships(villain)

        self.assertTrue(
            any(r["target"] == villain and r["type"] == RelationshipType.ENEMY.name for r in hero_relationships))
        self.assertTrue(
            any(r["target"] == hero and r["type"] == RelationshipType.ENEMY.name for r in villain_relationships))

    def test_save_and_load(self):
        # Save the world
        self.world.save("test_world.json")

        # Load the world
        loaded_world = GameWorldKnowledgeGraph.load("test_world.json")

        # Compare entities
        original_characters = self.world.query_characters()
        loaded_characters = loaded_world.query_characters()
        self.assertEqual(len(original_characters), len(loaded_characters))

        # Compare relationships
        original_hero = self.world.query_characters(name="Aric")[0]
        loaded_hero = loaded_world.query_characters(name="Aric")[0]
        original_relationships = self.world.knowledge_graph.get_relationships(original_hero)
        loaded_relationships = loaded_world.knowledge_graph.get_relationships(loaded_hero)
        self.assertEqual(len(original_relationships), len(loaded_relationships))


if __name__ == "__main__":
    # Create and populate the game world
    game_world = create_sample_world()

    # Print some information about the world
    print("Game World Overview:")
    print(f"Characters: {len(game_world.query_characters())}")
    print(f"Beasts: {len(game_world.query_beast())}")
    print(f"Locations: {len(game_world.query_location())}")
    print(f"Items: {len(game_world.query_items())}")
    print(f"Quests: {len(game_world.query_quests())}")
    print(f"Events: {len(game_world.query_events())}")
    print(f"Factions: {len(game_world.query_factions())}")

    # Run the tests
    unittest.main()
