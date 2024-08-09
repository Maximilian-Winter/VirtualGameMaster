# Game Knowledge Graph: Enhancing LLM Game Masters

## Introduction

The Game Knowledge Graph is a powerful tool designed to enhance the capabilities of Large Language Models (LLMs) acting as Game Masters in pen and paper role-playing games. This graph-based system allows for efficient storage, retrieval, and manipulation of game world information, enabling the LLM to maintain a consistent and dynamic game state.

The knowledge graph represents entities (such as characters, items, and locations) as nodes, and relationships between these entities as edges. Each entity and relationship can have attributes, allowing for rich and detailed representation of the game world.

## Concept

The Game Knowledge Graph serves several key purposes:

1. **State Management**: It maintains the current state of the game world, including character stats, inventory, locations, and more.
2. **Relationship Tracking**: It keeps track of how different entities in the game world are related to each other.
3. **Dynamic Updates**: It allows for real-time updates to the game state as events unfold.
4. **Complex Queries**: It enables complex queries about the game world, such as finding paths between entities or retrieving local game states.

## Wrapper Functions

To interact with the Game Knowledge Graph, the LLM uses a set of wrapper functions. Each function is designed for a specific task and accepts JSON-formatted input. Here's an explanation of each function along with JSON examples for calling them:

1. **add_game_entity**
    - Purpose: Adds a new entity to the game world.
    - Example call:
      ```json
      [{
        "name": "add_game_entity",
        "arguments": {
          "entity": "Jack Johnson",
          "attributes": {
            "name": "Jack Johnson",
            "class": "Rogue",
            "level": 3,
            "hp": 25,
            "inventory": ["Dagger", "Lockpicks"]
          }
        }
      }]
      ```

2. **add_game_relationship**
    - Purpose: Adds a relationship between two entities in the game world.
    - Example call:
      ```json
      [{
        "name": "add_game_relationship",
        "arguments": {
          "entity1": "Jack Johnson",
          "entity2": "Shadowy Alley",
          "relationship": "LOCATED_AT",
          "attributes": {
            "since": "2023-08-09T20:30:00Z",
            "stealth_bonus": 2
          }
        }
      }]
      ```

3. **query_game_entities**
    - Purpose: Queries entities in the game world based on their attributes.
    - Example call:
      ```json
      [{
        "name": "query_game_entities",
        "arguments": {
          "attribute_filter": {
            "class": "Rogue",
            "level": 3
          }
        }
      }]
      ```

4. **get_entity_info**
    - Purpose: Retrieves detailed information about a specific entity in the game world.
    - Example call:
      ```json
      [{
        "name": "get_entity_info",
        "arguments": {
          "entity": "Jack Johnson"
        }
      }]
      ```

5. **update_game_entity**
    - Purpose: Updates the attributes of an existing entity in the game world.
    - Example call:
      ```json
      [{
        "name": "update_game_entity",
        "arguments": {
          "entity": "Jack Johnson",
          "attributes": {
            "hp": 20,
            "status": "wounded",
            "inventory": ["Dagger", "Lockpicks", "Healing Potion"]
          }
        }
      }]
      ```

6. **find_game_path**
    - Purpose: Finds a path between two entities in the game world.
    - Example call:
      ```json
      [{
        "name": "find_game_path",
        "arguments": {
          "start": "Jack Johnson",
          "end": "City Gates"
        }
      }]
      ```

7. **get_local_game_state**
    - Purpose: Retrieves a subgraph of the game world centered on a specific entity.
    - Example call:
      ```json
      [{
        "name": "get_local_game_state",
        "arguments": {
          "entity": "Jack Johnson",
          "depth": 2
        }
      }]
      ```

By using these wrapper functions, the LLM can effectively manage and query the game world, making informed decisions based on the current state and relationships between entities. This system allows for a more dynamic, consistent, and engaging game experience, as the LLM can easily track and update complex game states and relationships.