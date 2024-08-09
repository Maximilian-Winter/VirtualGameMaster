from collections import deque

import networkx as nx
import json


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_entity(self, entity, attributes=None):
        """Add an entity (node) to the graph with optional attributes."""
        self.graph.add_node(entity, **attributes or {})

    def add_relationship(self, entity1, entity2, relationship):
        """Add a relationship (edge) between two entities."""
        self.graph.add_edge(entity1, entity2, relationship=relationship)

    def get_relationships(self, entity):
        """Get all relationships for a given entity."""
        relationships = []
        for neighbor in self.graph.neighbors(entity):
            relationship = self.graph[entity][neighbor]['relationship']
            relationships.append((neighbor, relationship))
        return relationships

    def query(self, start_entity, relationship):
        """Find entities related to the start_entity by the given relationship."""
        related_entities = []
        for neighbor in self.graph.neighbors(start_entity):
            if self.graph[start_entity][neighbor]['relationship'] == relationship:
                related_entities.append(neighbor)
        return related_entities

    def get_entity_attributes(self, entity):
        """Get all attributes of a given entity."""
        return self.graph.nodes[entity]

    def set_entity_attributes(self, entity, attributes):
        """Set attributes for a given entity."""
        nx.set_node_attributes(self.graph, {entity: attributes})

    def save_to_json(self, filename):
        """Serialize the graph to a JSON file."""
        data = nx.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_from_json(cls, filename):
        """Deserialize the graph from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        kg = cls()
        kg.graph = nx.node_link_graph(data)
        return kg

    def depth_first_search(self, start_entity, max_depth=None):
        """
        Perform a depth-first search starting from the given entity.
        Returns a list of entities visited.
        """
        visited = set()
        stack = [(start_entity, 0)]
        path = []

        while stack:
            entity, depth = stack.pop()
            if entity not in visited and (max_depth is None or depth <= max_depth):
                visited.add(entity)
                path.append(entity)
                for neighbor in self.graph.neighbors(entity):
                    if neighbor not in visited:
                        stack.append((neighbor, depth + 1))

        return path

    def breadth_first_search(self, start_entity, max_depth=None):
        """
        Perform a breadth-first search starting from the given entity.
        Returns a list of entities visited.
        """
        visited = set()
        queue = deque([(start_entity, 0)])
        path = []

        while queue:
            entity, depth = queue.popleft()
            if entity not in visited and (max_depth is None or depth <= max_depth):
                visited.add(entity)
                path.append(entity)
                for neighbor in self.graph.neighbors(entity):
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))

        return path

    def find_shortest_path(self, start_entity, end_entity):
        """
        Find the shortest path between two entities.
        Returns a list of entities representing the path.
        """
        try:
            path = nx.shortest_path(self.graph, start_entity, end_entity)
            return path
        except nx.NetworkXNoPath:
            return None

    def find_related_entities(self, start_entity, max_depth=2):
        """
        Find all entities related to the start entity up to a certain depth.
        Returns a dictionary with depths as keys and lists of entities as values.
        """
        related_entities = {0: [start_entity]}
        visited = set([start_entity])
        queue = deque([(start_entity, 0)])

        while queue:
            entity, depth = queue.popleft()
            if depth < max_depth:
                for neighbor in self.graph.neighbors(entity):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_depth = depth + 1
                        if new_depth not in related_entities:
                            related_entities[new_depth] = []
                        related_entities[new_depth].append(neighbor)
                        queue.append((neighbor, new_depth))

        return related_entities
# Example usage
kg = KnowledgeGraph()

# Adding entities with attributes
kg.add_entity("Alice", {"age": 30, "occupation": "Data Scientist"})
kg.add_entity("Bob", {"age": 35, "occupation": "Software Engineer"})
kg.add_entity("Charlie", {"age": 40, "occupation": "Project Manager"})
kg.add_entity("DataScience", {"field": "Interdisciplinary"})
kg.add_entity("MachineLearning", {"type": "AI Subset"})

# Adding relationships
kg.add_relationship("Alice", "Bob", "friend")
kg.add_relationship("Bob", "Charlie", "colleague")
kg.add_relationship("Alice", "DataScience", "studies")
kg.add_relationship("Bob", "MachineLearning", "expert_in")

# Querying the graph
print("Alice's relationships:", kg.get_relationships("Alice"))
print("Bob's friends:", kg.query("Bob", "friend"))
print("Experts in Machine Learning:", kg.query("MachineLearning", "expert_in"))

# Getting and setting attributes
print("Alice's attributes:", kg.get_entity_attributes("Alice"))
kg.set_entity_attributes("Alice", {"age": 31, "occupation": "Senior Data Scientist"})
print("Alice's updated attributes:", kg.get_entity_attributes("Alice"))

# Saving the graph to a file
kg.save_to_json("knowledge_graph.json")

# Loading the graph from a file
loaded_kg = KnowledgeGraph.load_from_json("knowledge_graph.json")
print("Loaded graph nodes:", list(loaded_kg.graph.nodes()))
print("Loaded Alice's attributes:", loaded_kg.get_entity_attributes("Alice"))


# Example usage
kg = KnowledgeGraph()

# Adding entities with attributes
kg.add_entity("Alice", {"age": 30, "occupation": "Data Scientist"})
kg.add_entity("Bob", {"age": 35, "occupation": "Software Engineer"})
kg.add_entity("Charlie", {"age": 40, "occupation": "Project Manager"})
kg.add_entity("David", {"age": 28, "occupation": "Data Analyst"})
kg.add_entity("Eve", {"age": 45, "occupation": "CEO"})
kg.add_entity("DataScience", {"field": "Interdisciplinary"})
kg.add_entity("MachineLearning", {"type": "AI Subset"})

# Adding relationships
kg.add_relationship("Alice", "Bob", "friend")
kg.add_relationship("Bob", "Charlie", "colleague")
kg.add_relationship("Alice", "David", "mentor")
kg.add_relationship("Charlie", "Eve", "reports_to")
kg.add_relationship("Alice", "DataScience", "studies")
kg.add_relationship("Bob", "MachineLearning", "expert_in")
kg.add_relationship("David", "DataScience", "works_in")

# Using the new traversal methods
print("DFS from Alice:", kg.depth_first_search("Alice"))
print("BFS from Alice:", kg.breadth_first_search("Alice"))
print("Shortest path from Alice to Eve:", kg.find_shortest_path("Alice", "Eve"))
print("Related entities to Alice:")
for depth, entities in kg.find_related_entities("Alice").items():
    print(f"  Depth {depth}: {entities}")
