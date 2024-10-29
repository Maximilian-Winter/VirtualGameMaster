from typing import Dict, Any
from pydantic import BaseModel, Field
from enhanced_knowledge_graph import KnowledgeGraph, Entity, EntityQuery

# Initialize the knowledge graph
kg = KnowledgeGraph()

# Add locations
tavern = Entity(entity_type="Location", attributes={"name": "The Prancing Pony", "type": "Tavern", "description": "A cozy tavern in the heart of Bree"})
tavern_id = kg.add_entity(tavern)

forest = Entity(entity_type="Location", attributes={"name": "Fangorn Forest", "type": "Forest", "description": "An ancient and mysterious forest"})
forest_id = kg.add_entity(forest)

castle = Entity(entity_type="Location", attributes={"name": "Winterfell", "type": "Castle", "description": "A formidable fortress in the North"})
castle_id = kg.add_entity(castle)

cave = Entity(entity_type="Location", attributes={"name": "Dragon's Lair", "type": "Cave", "description": "A treacherous cave filled with treasure"})
cave_id = kg.add_entity(cave)

village = Entity(entity_type="Location", attributes={"name": "Riverwood", "type": "Village", "description": "A peaceful village near a flowing river"})
village_id = kg.add_entity(village)

# Add characters
bartender = Entity(entity_type="Character", attributes={"name": "Barliman Butterbur", "role": "Bartender", "location": tavern_id})
bartender_id = kg.add_entity(bartender)

ranger = Entity(entity_type="Character", attributes={"name": "Strider", "role": "Ranger", "location": tavern_id})
ranger_id = kg.add_entity(ranger)

wizard = Entity(entity_type="Character", attributes={"name": "Gandalf", "role": "Wizard", "location": forest_id})
wizard_id = kg.add_entity(wizard)

knight = Entity(entity_type="Character", attributes={"name": "Sir Lancelot", "role": "Knight", "location": castle_id})
knight_id = kg.add_entity(knight)

dragon = Entity(entity_type="Character", attributes={"name": "Smaug", "role": "Dragon", "location": cave_id})
dragon_id = kg.add_entity(dragon)

blacksmith = Entity(entity_type="Character", attributes={"name": "Gendry", "role": "Blacksmith", "location": village_id})
blacksmith_id = kg.add_entity(blacksmith)

# Add items
ring = Entity(entity_type="Item", attributes={"name": "The One Ring", "type": "Artifact", "description": "A powerful and dangerous ring", "location": tavern_id})
ring_id = kg.add_entity(ring)

sword = Entity(entity_type="Item", attributes={"name": "Excalibur", "type": "Weapon", "description": "A legendary sword", "location": castle_id})
sword_id = kg.add_entity(sword)

potion = Entity(entity_type="Item", attributes={"name": "Elixir of Life", "type": "Consumable", "description": "A potion that grants temporary immortality", "location": forest_id})
potion_id = kg.add_entity(potion)

treasure = Entity(entity_type="Item", attributes={"name": "Dragon's Hoard", "type": "Treasure", "description": "A vast collection of gold and jewels", "location": cave_id})
treasure_id = kg.add_entity(treasure)

# Add relationships
kg.add_relationship(tavern_id, "contains", bartender_id)
kg.add_relationship(tavern_id, "contains", ranger_id)
kg.add_relationship(tavern_id, "contains", ring_id)
kg.add_relationship(ranger_id, "knows about", ring_id)
kg.add_relationship(forest_id, "contains", wizard_id)
kg.add_relationship(forest_id, "contains", potion_id)
kg.add_relationship(castle_id, "contains", knight_id)
kg.add_relationship(castle_id, "contains", sword_id)
kg.add_relationship(cave_id, "contains", dragon_id)
kg.add_relationship(cave_id, "contains", treasure_id)
kg.add_relationship(village_id, "contains", blacksmith_id)
kg.add_relationship(wizard_id, "knows", ranger_id)
kg.add_relationship(knight_id, "serves", castle_id)
kg.add_relationship(dragon_id, "guards", treasure_id)
kg.add_relationship(blacksmith_id, "can craft", sword_id)
kg.add_relationship(wizard_id, "created", potion_id)

# Querying all locations
location_query = EntityQuery(entity_type="Location")
print(kg.query_entities(location_query))

# Querying characters in the tavern
character_query = EntityQuery(entity_type="Character", attribute_filter={"location": tavern_id})
print(kg.query_entities(character_query))

# Updating Strider's location to the forest
kg.update_entity(ranger_id, {"location": forest_id})
print(kg.get_entity_details(ranger_id))

# Querying relationships for the wizard
print(kg.query_relationships(wizard_id))

# Performing semantic search for 'powerful artifact'
print(kg.semantic_search("powerful artifact"))

# Finding path between the blacksmith and the dragon
print(kg.find_path(blacksmith_id, dragon_id))

# Getting nearby entities for the castle
print(kg.get_nearby_entities(castle_id))

# Deleting the potion
print(kg.delete_entity(potion_id))

# Visualizing the graph
kg.visualize("expanded_dnd_game_world")

# Saving the knowledge graph
kg.save_to_file("expanded_dnd_game_world.json")

# Loading the knowledge graph
loaded_kg = KnowledgeGraph.load_from_file("expanded_dnd_game_world.json")

# Verifying loaded knowledge graph
print(loaded_kg.query_entities(EntityQuery(entity_type="Character")))