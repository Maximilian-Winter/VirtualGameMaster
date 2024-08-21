from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import graphviz
from pydantic import BaseModel, Field
import networkx as nx
import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from ToolAgents import FunctionTool


class Entity(BaseModel):
    """
    Represents an entity in the knowledge graph.
    """
    entity_id: str = Field(default="",
                           description="The entity id. Gets automatically set when added to the knowledge graph.")
    entity_type: str = Field(..., description="The type of entity")
    attributes: Dict[str, Any] = Field(..., description="The entity attributes")


class EntityQuery(BaseModel):
    """
    Represents an entity query.
    """
    entity_type: Optional[str] = Field(None, description="The type of entity to query")
    attribute_filter: Optional[Dict[str, Any]] = Field(None, description="The attribute filter")


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.entity_counters = {}
        self.embeddings = {}
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_entity_id(self, entity_type: str) -> str:
        """
        Generates a unique entity ID for a given entity type.

        Args:
            entity_type (str): The type of the entity.

        Returns:
            str: A unique entity ID.
        """
        if entity_type in self.entity_counters:
            self.entity_counters[entity_type] += 1
        else:
            self.entity_counters[entity_type] = 1
        return f"{entity_type}-{self.entity_counters[entity_type]}"

    def add_entity(self, entity: Entity) -> str:
        """
        Add an entity to the knowledge graph.

        Args:
            entity (Entity): The entity to add.

        Returns:
            str: The entity ID.
        """
        if not entity.entity_id:
            entity.entity_id = self.generate_entity_id(entity.entity_type)
        self.graph.add_node(entity.entity_id, entity_type=entity.entity_type, **entity.attributes)

        entity_text = f"{entity.entity_type}, {', '.join(str(v) for v in entity.attributes.values())}"
        self.embeddings[entity.entity_id] = self.embedding_model.encode(entity_text)

        return entity.entity_id

    def update_entity(self, entity_id: str, new_attributes: Dict[str, Any]) -> str:
        """
        Update an existing entity's attributes.

        Args:
            entity_id (str): The ID of the entity to update.
            new_attributes (Dict[str, Any]): The new attributes to update or add to the entity.

        Returns:
            str: A message confirming the update or an error message if the entity was not found.
        """
        if entity_id not in self.graph:
            return f"Error: No entity found with ID {entity_id}"

        entity_data = self.graph.nodes[entity_id]
        entity_data.update(new_attributes)

        entity_text = f"{entity_data['entity_type']} {' '.join(str(v) for v in entity_data.values() if v != entity_data['entity_type'])}"
        self.embeddings[entity_id] = self.embedding_model.encode(entity_text)

        return f"Entity {entity_id} updated successfully"

    def delete_entity(self, entity_id: str) -> str:
        """
        Delete an entity from the knowledge graph.

        Args:
            entity_id (str): The ID of the entity to delete.

        Returns:
            str: A message confirming the deletion or an error message if the entity was not found.
        """
        if entity_id not in self.graph:
            return f"Error: No entity found with ID {entity_id}"

        self.graph.remove_node(entity_id)
        del self.embeddings[entity_id]

        return f"Entity {entity_id} deleted successfully"

    def query_entities(self, entity_query: EntityQuery) -> str:
        """
        Query entities in the knowledge graph based on type and attributes.

        Args:
            entity_query (EntityQuery): The entity query parameters.

        Returns:
            str: A formatted string containing the query results.
        """
        matching_entities = []
        for node, data in self.graph.nodes(data=True):
            if (entity_query.entity_type is None or
                    data.get('entity_type').lower() == entity_query.entity_type.lower()):
                if entity_query.attribute_filter is None or all(
                        data.get(k) == v for k, v in entity_query.attribute_filter.items()
                ):
                    matching_entities.append({'id': node, **data})

        if not matching_entities:
            return "No matching entities found."

        result = "Matching entities:\n"
        for entity in matching_entities:
            result += f"- ID: {entity['id']}\n"
            result += f"  Type: {entity['entity_type']}\n"
            result += "  Attributes:\n"
            for key, value in entity.items():
                if key not in ['id', 'entity_type']:
                    result += f"    {key}: {value}\n"
            result += "\n"

        return result

    def add_relationship(self, first_entity_id: str, relationship_type: str, second_entity_id: str,
                         attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a relationship between two entities in the knowledge graph.

        Args:
            first_entity_id (str): The ID of the first entity.
            relationship_type (str): The type of the relationship.
            second_entity_id (str): The ID of the second entity.
            attributes (Optional[Dict[str, Any]]): Additional attributes for the relationship.

        Returns:
            str: A message confirming the addition of the relationship.
        """
        if first_entity_id not in self.graph:
            return f"Error: Entity with ID {first_entity_id} not found"
        if second_entity_id not in self.graph:
            return f"Error: Entity with ID {second_entity_id} not found"

        self.graph.add_edge(first_entity_id, second_entity_id,
                            relationship_type=relationship_type,
                            **attributes if attributes else {})
        return f"Relationship '{relationship_type}' added successfully between entities {first_entity_id} and {second_entity_id}"

    def query_relationships(self, entity_id: str, relationship_type: Optional[str] = None) -> str:
        """
        Query relationships of an entity in the knowledge graph.

        Args:
            entity_id (str): The ID of the entity to query relationships for.
            relationship_type (Optional[str]): The type of relationship to filter by.

        Returns:
            str: A formatted string containing the query results.
        """
        if entity_id not in self.graph:
            return f"Error: No entity found with ID {entity_id}"

        relationships = []
        for neighbor in self.graph.neighbors(entity_id):
            edge_data = self.graph[entity_id][neighbor]
            if relationship_type is None or edge_data['relationship_type'] == relationship_type:
                relationships.append({
                    'related_entity': neighbor,
                    'relationship_type': edge_data['relationship_type'],
                    'attributes': {k: v for k, v in edge_data.items() if k != 'relationship_type'}
                })

        if not relationships:
            return f"No relationships found for entity {entity_id}"

        result = f"Relationships for entity {entity_id}:\n"
        for rel in relationships:
            result += f"- Related Entity: {rel['related_entity']}\n"
            result += f"  Relationship Type: {rel['relationship_type']}\n"
            if rel['attributes']:
                result += "  Attributes:\n"
                for key, value in rel['attributes'].items():
                    result += f"    {key}: {value}\n"
            result += "\n"

        return result

    def semantic_search(self, query: str, top_k: int = 5) -> str:
        """
        Perform semantic search on the knowledge graph using embeddings.

        Args:
            query (str): The search query.
            top_k (int): The number of top results to return.

        Returns:
            str: A formatted string containing the top-k matching entities and their similarities.
        """
        query_embedding = self.embedding_model.encode(query)

        similarities = {}
        for entity_id, embedding in self.embeddings.items():
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities[entity_id] = similarity

        top_entities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

        result = f"Top {top_k} entities semantically similar to '{query}':\n"
        for entity_id, similarity in top_entities:
            entity_data = self.graph.nodes[entity_id]
            result += f"- Entity ID: {entity_id}\n"
            result += f"  Similarity: {similarity:.4f}\n"
            result += f"  Type: {entity_data['entity_type']}\n"
            result += "  Attributes:\n"
            for key, value in entity_data.items():
                if key != 'entity_type':
                    result += f"    {key}: {value}\n"
            result += "\n"

        return result

    def find_path(self, start_entity_id: str, end_entity_id: str, max_depth: int = 5) -> str:
        """
        Find a path between two entities in the knowledge graph.

        Args:
            start_entity_id (str): The ID of the starting entity.
            end_entity_id (str): The ID of the ending entity.
            max_depth (int): The maximum depth to search for a path.

        Returns:
            str: A description of the path found or an error message if no path is found.
        """
        try:
            path = nx.shortest_path(self.graph, start_entity_id, end_entity_id)
            if len(path) > max_depth:
                return f"Path found but exceeds maximum depth of {max_depth}"

            result = f"Path from {start_entity_id} to {end_entity_id}:\n"
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i + 1]]
                result += f"{path[i]} --({edge_data['relationship_type']})--> {path[i + 1]}\n"
            return result
        except nx.NetworkXNoPath:
            return f"No path found between {start_entity_id} and {end_entity_id}"
        except nx.exception.NodeNotFound:
            return f"Error: Either source {start_entity_id} or target {end_entity_id} is not in the graph"

    def get_entity_details(self, entity_id: str) -> str:
        """
        Retrieve detailed information about a specific entity.

        Args:
            entity_id (str): The ID of the entity to retrieve details for.

        Returns:
            str: A formatted string containing the detailed information of the entity.
        """
        if entity_id not in self.graph:
            return f"Error: No entity found with ID {entity_id}"

        entity_data = self.graph.nodes[entity_id]
        result = f"Details for entity {entity_id}:\n"
        result += f"Type: {entity_data['entity_type']}\n"
        result += "Attributes:\n"
        for key, value in entity_data.items():
            if key != 'entity_type':
                result += f"  {key}: {value}\n"
        return result

    def get_nearby_entities(self, entity_id: str, entity_type: Optional[str] = None, max_distance: int = 2) -> str:
        """
        Find entities that are near a specified entity in the knowledge graph.

        Args:
            entity_id (str): The ID of the entity to search from.
            entity_type (Optional[str]): The type of entity to filter by.
            max_distance (int): The maximum distance (in graph edges) to search.

        Returns:
            str: A formatted string listing the nearby entities found.
        """
        if entity_id not in self.graph:
            return f"Error: No entity found with ID {entity_id}"

        subgraph = nx.ego_graph(self.graph, entity_id, radius=max_distance)
        nearby_entities = []

        for node in subgraph.nodes():
            if node != entity_id and (entity_type is None or subgraph.nodes[node]['entity_type'] == entity_type):
                nearby_entities.append({
                    "id": node,
                    "name": subgraph.nodes[node].get('name', 'Unnamed entity'),
                    "type": subgraph.nodes[node]['entity_type']
                })

        if not nearby_entities:
            return f"No nearby entities found within {max_distance} steps of {entity_id}"

        result = f"Entities near {entity_id} (within {max_distance} steps):\n"
        for entity in nearby_entities:
            result += f"- ID: {entity['id']}\n"
            result += f"  Name: {entity['name']}\n"
            result += f"  Type: {entity['type']}\n\n"

        return result

    def save_to_file(self, filename: str) -> None:
        """
        Save the EnhancedGeneralizedKnowledgeGraph to a JSON file.

        Args:
            filename (str): The name of the file to save to.
        """
        data = {
            "graph": nx.node_link_data(self.graph),
            "entity_counters": self.entity_counters,
            "embeddings": {k: v.tolist() for k, v in self.embeddings.items()}
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_from_file(cls, filename: str) -> 'KnowledgeGraph':
        """
        Load an EnhancedGeneralizedKnowledgeGraph from a JSON file.

        Args:
            filename (str): The name of the file to load from.

        Returns:
            EnhancedGeneralizedKnowledgeGraph: The loaded knowledge graph.
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        gkg = cls()
        gkg.graph = nx.node_link_graph(data['graph'])
        gkg.entity_counters = data['entity_counters']
        gkg.embeddings = {k: np.array(v) for k, v in data['embeddings'].items()}
        return gkg

    def visualize(self, output_file: str = "knowledge_graph", format: str = "png") -> None:
        """
        Visualize the knowledge graph using Graphviz.

        Args:
            output_file (str): Name of the output file (without extension)
            format (str): Output format (e.g., "png", "pdf", "svg")
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

    def get_tools(self):
        return [FunctionTool(self.add_entity), FunctionTool(self.update_entity), FunctionTool(self.delete_entity),
                FunctionTool(self.query_entities), FunctionTool(self.add_relationship), FunctionTool(self.query_relationships),
                FunctionTool(self.semantic_search), FunctionTool(self.get_entity_details)]


