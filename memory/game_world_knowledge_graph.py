import json
import os.path
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto

import graphviz
import networkx as nx
from pydantic import BaseModel, Field

from ToolAgents import FunctionTool


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

    def query_relationships(self, entity: str, relationship_type: Optional[str] = None, direction: str = 'both') -> \
            List[Dict[str, Any]]:
        relationships = []

        if direction in ['outgoing', 'both']:
            for source, target, data in self.graph.edges(entity, data=True):
                if relationship_type is None or data["relationship"] == relationship_type:
                    relationships.append({
                        "direction": "outgoing",
                        "source": source,
                        "target": target,
                        "type": data["relationship"],
                        "attributes": {k: v for k, v in data.items() if k != "relationship"}
                    })

        if direction in ['incoming', 'both']:
            for source, target, data in self.graph.in_edges(entity, data=True):
                if relationship_type is None or data["relationship"] == relationship_type:
                    relationships.append({
                        "direction": "incoming",
                        "source": source,
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
                return d["relationship"] in relationship_types

            path = nx.shortest_path(self.graph, start_entity, end_entity, weight=None, method="dijkstra",
                                    edge_filter=edge_filter)
        else:
            path = nx.shortest_path(self.graph, start_entity, end_entity)
        return path

    def get_subgraph(self, center_entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get a subgraph centered on an entity up to a certain depth."""
        subgraph = nx.ego_graph(self.graph, center_entity, radius=max_depth)
        return nx.node_link_data(subgraph)

    def visualize(self, output_file: str = "knowledge_graph", format: str = "png") -> None:
        """
        Visualize the knowledge graph using Graphviz.
        Args:
            output_file: Name of the output file (without extension)
            format: Output format (e.g., "png", "pdf", "svg")
        """
        dot = graphviz.Digraph(comment="Knowledge Graph")

        # Add nodes
        for node, data in self.graph.nodes(data=True):
            label = f"{node}\n{json.dumps(data, indent=2)}"
            dot.node(node, label)

        # Add edges
        for u, v, data in self.graph.edges(data=True):
            label = data.get("relationship", "")
            dot.edge(u, v, label=label)

        # Render the graph
        dot.render(output_file, format=format, cleanup=True)
        print(f"Graph visualization saved as {output_file}.{format}")

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


class GameEntityType(str, Enum):
    RACE = "Race"
    CHARACTER = "Character"
    CREATURE = "Creature"
    LOCATION = "Location"
    FACTION = "Faction"
    EVENT = "Event"
    ITEM = "Item"
    LORE = "Lore"
    PLANE = "Plane of Existence"
    ERA = "Era"
    CULTURE = "Culture"
    RELATIONSHIP = "Relationship"
    PROFESSION = "Profession"
    LANDMARK = "Landmark"
    ARTIFACT = "Artifact"
    LEGEND = "Legend"
    WORLD_INFO = "World Information"
    MISC = "Miscellaneous"


class GameEntity(BaseModel):
    entity_id: str = Field(default_factory=str, description="The entity id")
    entity_type: str = Field(..., description="The type of entity")
    entity_data: Dict[str, Any] = Field(..., description="The entity data")


class GameEntityQuery(BaseModel):
    entity_type: str = Field(..., description="The type of entity to query")
    entity_data_filter: Optional[Dict[str, Any]] = Field(None, description="The entity data filter")


class GameWorldKnowledgeGraph:
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.entity_counters = {}

    def generate_entity_id(self, entity_type: GameEntityType) -> str:
        if entity_type in self.entity_counters:
            self.entity_counters[entity_type] += 1
        else:
            self.entity_counters[entity_type] = 1
        return f"{entity_type}-{self.entity_counters[entity_type]}"

    def add_entity(self, game_entity: GameEntity):
        """
        Adds a game entity to the game world knowledge graph. Returns the entity id of the entity added.
        Args:
            game_entity(Union[Race, Character, Creature, Location, Item, Quest, Event, Faction]): The entity to add.
        Returns:
            (str) The entity id of the entity added.
        """
        entity_id = self.generate_entity_id(game_entity.entity_type)
        self.knowledge_graph.add_entity(entity_id, game_entity.model_dump(mode="json"))
        game_entity.__setattr__("entity_id", entity_id)
        return entity_id

    def query_entities(self, entity_query: GameEntityQuery) -> str:
        """
        Query entities of the game world knowledge graph.
        Args:
           entity_query (GameEntityQuery): The entity query.
        Returns:
           str: A formatted string containing the query results.
        """
        # First, filter entities by type
        matching_entities: List[Dict[str, Any]] = []
        for node, data in self.knowledge_graph.graph.nodes(data=True):
            if data.get('entity_type').lower() == entity_query.entity_type.lower():
                matching_entities.append({'id': node, **data})

        # Then, apply the entity_data_filter if provided
        if entity_query.entity_data_filter:
            matching_entities = [
                entity for entity in matching_entities
                if all(
                    entity['entity_data'].get(k) == v
                    for k, v in entity_query.entity_data_filter.items()
                )
            ]

        # Format the results
        if not matching_entities:
            return f"No entities found matching the query for type: {entity_query.entity_type}"

        result = f"Entities of type {entity_query.entity_type}:\n"
        for entity in matching_entities:
            result += f"- ID: {entity['id']}\n"
            result += f"  Name: {entity['entity_data'].get('name', 'Unnamed')}\n"
            for key, value in entity['entity_data'].items():
                if key != 'name':
                    result += f"  {key}: {value}\n"
            result += "\n"

        return result

    def add_relationship(self, first_game_entity_id: str, relationship_type: str, second_game_entity_id: str,
                         description: Optional[str] = None):
        """
        Adds a relationship between two entities to the game world knowledge graph.
        Args:
            first_game_entity_id(str): The first game entity id.
            relationship_type(str): The relationship type.
            second_game_entity_id(str): The second game entity id.
            description(Optional[str]): The description of the relationship type.
        """
        self.knowledge_graph.add_relationship(first_game_entity_id, second_game_entity_id,
                                              relationship_type,
                                              {"description": description} if description else {})
        return f"Relationship '{relationship_type}' added successfully between entities {first_game_entity_id} and {second_game_entity_id}"

    def query_relationships(self, game_entity_id: str, relationship_type: Optional[str]):
        """
        Query relationships of an entity of the game world knowledge graph.
        Args:
            game_entity_id(str): The game entity id.
            relationship_type(Optional[str]): The relationship type.
        """
        results = self.knowledge_graph.query_relationships(game_entity_id, relationship_type)
        return json.dumps(results, indent=2)

    def find_path(self, start_entity_id: str, end_entity_id: str, max_depth: int = 5):
        """
        Finds a path between two game entities in the knowledge graph.

        Args:
            start_entity_id (str): The ID of the starting entity.
            end_entity_id (str): The ID of the ending entity.
            max_depth (int): The maximum depth to search for a path.

        Returns:
            str: A string describing the path found or a message if no path is found.
        """
        try:
            path = self.knowledge_graph.find_path(start_entity_id, end_entity_id)
            if len(path) > max_depth:
                return f"Path found but exceeds maximum depth of {max_depth}"

            result = f"Path from {start_entity_id} to {end_entity_id}:\n"
            for i in range(len(path) - 1):
                edge_data = self.knowledge_graph.graph[path[i]][path[i + 1]]
                result += f"{path[i]} --({edge_data[0]["relationship"]})--> {path[i + 1]}\n"
            return result
        except nx.NetworkXNoPath:
            return f"No path found between {start_entity_id} and {end_entity_id}"

    def get_entity_details(self, entity_id: str):
        """
        Retrieves detailed information about a specific entity.

        Args:
            entity_id (str): The ID of the entity to retrieve details for.

        Returns:
            str: A string containing the detailed information of the entity.
        """
        try:
            entity_data = self.knowledge_graph.get_entity_attributes(entity_id)
            result = f"Details for entity {entity_id}:\n"
            for key, value in entity_data.items():
                result += f"{key}: {value}\n"
            return result
        except KeyError:
            return f"No entity found with ID {entity_id}"

    def query_entities_by_attribute(self, attribute_name: str, attribute_value: str):
        """
        Queries entities based on a specific attribute value.

        Args:
            attribute_name (str): The name of the attribute to query.
            attribute_value (Any): The value of the attribute to match.

        Returns:
            str: A string listing the entities that match the attribute criteria.
        """
        matching_entities = self.knowledge_graph.query_entities({attribute_name: attribute_value})
        if not matching_entities:
            return f"No entities found with {attribute_name} = {attribute_value}"

        result = f"Entities with {attribute_name} = {attribute_value}:\n"
        for entity_id in matching_entities:
            entity_data = self.knowledge_graph.get_entity_attributes(entity_id)
            result += f"- {entity_id}: {entity_data.get('name', 'Unnamed entity')}\n"
        return result

    def get_nearby_entities(self, location_id: str, game_entity_type: Optional[GameEntityType] = None,
                            max_distance: int = 2):
        """
        Finds entities that are near a specified location in the knowledge graph.

        Args:
            location_id (str): The ID of the location to search from.
            game_entity_type (Optional[GameEntityType]): The type of game entity to filter by.
            max_distance (int): The maximum distance (in graph edges) to search.

        Returns:
            str: A string listing the nearby entities found.
        """
        subgraph = self.knowledge_graph.get_subgraph(location_id, max_depth=max_distance)
        nearby_entities = []

        for node in subgraph['nodes']:
            if node["id"] != location_id and (
                    game_entity_type is None or node['game_entity_type'] == game_entity_type):
                nearby_entities.append((node["id"], node))

        if not nearby_entities:
            return f"No nearby entities found within {max_distance} steps of {location_id}"

        result = f"Entities near {location_id} (within {max_distance} steps):\n"
        for entity_id, entity_data in nearby_entities:
            result += f"- {entity_id}: {entity_data.get('name', 'Unnamed entity')} ({entity_data['entity_type']})\n"
        return result

    def get_unified_tools(self):
        return [FunctionTool(self.add_entity), FunctionTool(self.add_relationship), FunctionTool(self.query_entities),
                FunctionTool(self.query_relationships), FunctionTool(self.query_entities_by_attribute),
                FunctionTool(self.get_entity_details), FunctionTool(self.get_nearby_entities)]

    def save_game(self, filename: str) -> None:
        """
        Save the GameWorldKnowledgeGraph to a JSON file.

        Args:
            filename (str): The name of the file to save to.
        """
        filename_without_extension = os.path.splitext(filename)[0]
        filename_knowledge_graph = filename_without_extension + "_knowledge_graph.json"
        data = {
            "knowledge_graph_filename": filename_knowledge_graph,
            "entity_counters": self.entity_counters
        }

        self.knowledge_graph.save_to_json(filename_knowledge_graph)

        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_game(self, filename: str) -> None:
        """
        Load a GameWorldKnowledgeGraph from a JSON file.

        Args:
            filename (str): The name of the file to load from.
        """
        with open(filename, 'r', encoding="utf-8") as f:
            data = json.load(f)

        self.knowledge_graph = KnowledgeGraph.load_from_json(data['knowledge_graph_filename'])
        self.entity_counters = data['entity_counters']
