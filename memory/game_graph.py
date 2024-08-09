import json
from typing import List, Dict, Any, Optional
from enum import Enum, auto

import networkx as nx


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_entity(self, entity: str, attributes: Dict[str, Any]) -> None:
        """Add an entity (node) to the graph with attributes."""
        self.graph.add_node(entity, **attributes)

    def add_relationship(self, entity1: str, entity2: str, relationship: str,
                         attributes: Dict[str, Any] = None) -> None:
        """Add a directional relationship (edge) between two entities with optional attributes."""
        self.graph.add_edge(entity1, entity2, relationship=relationship, **attributes or {})

    def get_entity_attributes(self, entity: str) -> Dict[str, Any]:
        """Get all attributes of a given entity."""
        return dict(self.graph.nodes[entity])

    def update_entity_attributes(self, entity: str, attributes: Dict[str, Any]) -> None:
        """Update attributes for a given entity."""
        self.graph.nodes[entity].update(attributes)

    def get_relationships(self, entity: str) -> List[Dict[str, Any]]:
        """Get all relationships for a given entity."""
        relationships = []
        for _, neighbor, data in self.graph.edges(entity, data=True):
            relationships.append({
                "target": neighbor,
                "type": data["relationship"],
                "attributes": {k: v for k, v in data.items() if k != "relationship"}
            })
        return relationships

    def query_entities(self, attribute_filter: Dict[str, Any]) -> List[str]:
        """Query entities based on attribute filters."""
        return [node for node, data in self.graph.nodes(data=True)
                if all(data.get(k) == v for k, v in attribute_filter.items())]

    def query_relationships(self, start_entity: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query relationships of a specific type from a starting entity."""
        relationships = []
        for _, target, data in self.graph.edges(start_entity, data=True):
            if relationship_type is None or data["relationship"] == relationship_type:
                relationships.append({
                    "target": target,
                    "type": data["relationship"],
                    "attributes": {k: v for k, v in data.items() if k != "relationship"}
                })
        return relationships

    def find_path(self, start_entity: str, end_entity: str, relationship_types: Optional[List[str]] = None) -> List[
        str]:
        """Find a path between two entities, optionally constrained by relationship types."""
        if relationship_types:
            def edge_filter(u, v, d):
                return d["key"] in relationship_types

            path = nx.shortest_path(self.graph, start_entity, end_entity, weight=None, method="dijkstra",
                                    edge_filter=edge_filter)
        else:
            path = nx.shortest_path(self.graph, start_entity, end_entity)
        return path

    def get_subgraph(self, center_entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get a subgraph centered on an entity up to a certain depth."""
        subgraph = nx.ego_graph(self.graph, center_entity, radius=max_depth)
        return nx.node_link_data(subgraph)

    def save_to_json(self, filename: str) -> None:
        """Save the graph to a JSON file."""
        data = nx.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_from_json(cls, filename: str) -> 'KnowledgeGraph':
        """Load the graph from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        kg = cls()
        kg.graph = nx.node_link_graph(data, multigraph=True, directed=True)
        return kg


# LLM Wrapper Functions

class RelationshipType(str, Enum):
    LOCATED_AT = auto()
    POSSESSES = auto()
    KNOWS = auto()
    HOSTILE_TO = auto()
    FRIENDLY_TO = auto()
    PART_OF = auto()
    LEADS = auto()
    GUARDS = auto()
    LOCKED_BY = auto()
    REQUIRES = auto()


def add_game_entity(entity: str, attributes: Dict[str, Any]) -> str:
    """
    Add a new entity to the game world.

    Args:
        entity (str): A unique identifier for the entity (e.g., "Player1", "Sword_of_Destiny").
        attributes (Dict[str, Any]): A dictionary of attributes describing the entity.
            Example: {"name": "Alice", "class": "Warrior", "level": 5, "hp": 100}

    Returns:
        str: A confirmation message indicating the entity was added.

    """
    kg.add_entity(entity, attributes)
    return f"Added entity {entity} with attributes {attributes}"


def add_game_relationship(entity1: str, entity2: str, relationship: RelationshipType, attributes: Dict[str, Any] = None) -> str:
    """
    Add a relationship between two entities in the game world.

    Args:
        entity1 (str): The identifier of the first entity (source).
        entity2 (str): The identifier of the second entity (target).
        relationship (str): The type of relationship (e.g., "EQUIPPED", "LOCATED_AT").
        attributes (Dict[str, Any], optional): Additional attributes of the relationship.
            Example: {"since": "2023-08-09"}

    Returns:
        str: A confirmation message indicating the relationship was added.

    """
    kg.add_relationship(entity1, entity2, relationship.name, attributes)
    return f"Added relationship {relationship.name} from {entity1} to {entity2} with attributes {attributes}"


def query_game_entities(attribute_filter: Dict[str, Any]) -> List[str]:
    """
    Query entities in the game world based on their attributes.

    Args:
        attribute_filter (Dict[str, Any]): A dictionary of attribute key-value pairs to filter entities.
            Example: {"class": "Warrior", "level": 5}

    Returns:
        List[str]: A list of entity identifiers that match the given attributes.

    """
    return kg.query_entities(attribute_filter)


def get_entity_info(entity: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific entity in the game world.

    Args:
        entity (str): The identifier of the entity to query.

    Returns:
        Dict[str, Any]: A dictionary containing the entity's attributes and relationships.
            The dictionary has two keys: "attributes" and "relationships".

    """
    return {
        "attributes": kg.get_entity_attributes(entity),
        "relationships": kg.get_relationships(entity)
    }


def update_game_entity(entity: str, attributes: Dict[str, Any]) -> str:
    """
    Update the attributes of an existing entity in the game world.

    Args:
        entity (str): The identifier of the entity to update.
        attributes (Dict[str, Any]): A dictionary of attributes to update or add.
            Example: {"hp": 90, "status": "wounded"}

    Returns:
        str: A confirmation message indicating the entity was updated.

    Example:
        update_game_entity("Player1", {"hp": 90, "status": "wounded"})
    """
    kg.update_entity_attributes(entity, attributes)
    return f"Updated entity {entity} with new attributes {attributes}"


def find_game_path(start: str, end: str) -> List[str]:
    """
    Find a path between two entities in the game world.

    Args:
        start (str): The identifier of the starting entity.
        end (str): The identifier of the ending entity.

    Returns:
        List[str]: A list of entity identifiers representing the path from start to end.
            If no path is found, returns an empty list.

    Example:
        find_game_path("Player1", "Castle_Dungeon")
    """
    return kg.find_path(start, end)


def get_local_game_state(entity: str, depth: int = 2) -> Dict[str, Any]:
    """
    Get a subgraph of the game world centered on a specific entity.

    Args:
        entity (str): The identifier of the central entity.
        depth (int, optional): The maximum depth of relationships to include. Defaults to 2.

    Returns:
        Dict[str, Any]: A dictionary representation of the subgraph, including nodes and edges.

    Example:
        get_local_game_state("Player1", depth=3)
    """
    return kg.get_subgraph(entity, depth)


# Example usage
kg = GameKnowledgeGraph()

# Using the wrapper functions
print(add_game_entity("Player1", {"name": "Alice", "class": "Warrior", "level": 5, "hp": 100}))
print(add_game_entity("Sword1", {"name": "Excalibur", "type": "Weapon", "damage": 20}))
print(add_game_relationship("Player1", "Sword1", RelationshipType.POSSESSES, {"since": "2023-08-09"}))

print("Warrior entities:", query_game_entities({"class": "Warrior"}))
print("Player1 info:", get_entity_info("Player1"))

print(update_game_entity("Player1", {"hp": 90, "status": "wounded"}))
print(get_local_game_state("Player1"))
print("Updated Player1 info:", get_entity_info("Player1"))
