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
        dot.attr(rankdir="LR", size="8,5")

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


class EntityType(str, Enum):
    CHARACTER = "Character"
    BEAST = "Beast"
    LOCATION = "Location"
    ITEM = "Item"
    QUEST = "Quest"
    EVENT = "Event"
    FACTION = "Faction"


class CharacterType(str, Enum):
    NPC = "Non-Player-Character"
    PLAYER = "Player-Character"
    DEITY = "Deity"
    HISTORICAL_FIGURE = "Historical-Figure"


class BeastType(str, Enum):
    ANIMAL = "Animal"
    MONSTER = "Monster"
    NON_MONSTER = "Non-Monster"
    MYTHICAL = "Mythical"
    UNDEAD = "Undead"
    CONSTRUCT = "Construct"
    ELEMENTAL = "Elemental"


class LocationType(str, Enum):
    PLANE = "Plane"
    CITY = "City"
    CITY_DISTRICT = "City-District"
    TOWN = "Town"
    VILLAGE = "Village"
    DUNGEON = "Dungeon"
    WILDERNESS = "Wilderness"
    TEMPLE = "Temple"
    CASTLE = "Castle"
    TAVERN = "Tavern"
    INN = "Inn"
    SHOP = "Shop"
    HOUSE = "House"


class ItemType(str, Enum):
    WEAPON = "Weapon"
    ARMOR = "Armor"
    POTION = "Potion"
    EQUIPMENT = "Equipment"
    SCROLL = "Scroll"
    WAND = "Wand"
    RING = "Ring"
    ARTIFACT = "Artifact"
    MISC = "Miscellaneous"


class QuestType(str, Enum):
    FIND_CHARACTER = "Find Character"
    FIND_ITEM = "Find Item"
    KILL_MONSTER = "Kill Monster"
    KILL_CHARACTER = "Kill Character"
    ESCORT = "Escort"
    EXPLORE = "Explore"
    RESCUE = "Rescue"
    DELIVER = "Deliver"


class EventType(str, Enum):
    HISTORY = "History"
    LORE = "Lore"
    FESTIVAL = "Festival"
    MURDER = "Murder"
    BATTLE = "Battle"
    NATURAL_DISASTER = "Natural Disaster"
    RITUAL = "Ritual"


class FactionType(str, Enum):
    CORPORATION = "Corporation"
    GUILD = "Guild"
    GROUP = "Group"
    GOVERNMENT = "Government"
    CULT = "Cult"
    TRIBE = "Tribe"


class RelationshipType(str, Enum):
    # Character relationships
    ALLY = "Ally"
    ENEMY = "Enemy"
    FRIEND = "Friend"
    FAMILY = "Family"
    MENTOR = "Mentor"
    STUDENT = "Student"
    RIVAL = "Rival"
    LOVER = "Lover"
    SPOUSE = "Spouse"

    # Location relationships
    RESIDES_IN = "Resides In"
    RULES = "Rules"
    OWNS = "Owns"
    GUARDS = "Guards"
    LOCATED_IN = "Located In"

    # Item relationships
    POSSESSES = "Possesses"
    CREATED = "Created"
    SEEKS = "Seeks"

    # Quest relationships
    ASSIGNED_BY = "Assigned By"
    INVOLVES = "Involves"
    REWARDS = "Rewards"

    # Event relationships
    PARTICIPATED_IN = "Participated In"
    CAUSED = "Caused"
    AFFECTED_BY = "Affected By"

    # Faction relationships
    MEMBER_OF = "Member Of"
    ALLIED_WITH = "Allied With"
    AT_WAR_WITH = "At War With"
    TRADING_PARTNER = "Trading Partner"

    # Beast relationships
    TAMED_BY = "Tamed By"
    HUNTS = "Hunts"
    INHABITS = "Inhabits"

    # General relationships
    KNOWS_ABOUT = "Knows About"
    INTERACTS_WITH = "Interacts With"
    PROTECTS = "Protects"
    THREATENS = "Threatens"
    WORSHIPS = "Worships"


class GameEntity(BaseModel):
    entity_type: EntityType


class Character(GameEntity):
    """
    Represents a Character.
    """
    entity_type: EntityType = EntityType.CHARACTER
    name: str = Field(..., description="The name of the character.")
    character_type: CharacterType = Field(..., description="The type of character.")
    age: int = Field(..., description="The age of the character.")
    race: str = Field(..., description="The race of the character.")
    gender: str = Field(..., description="The gender of the character.")
    description: str = Field(..., description="The description of the character.")


class Beast(GameEntity):
    """
    Represents a Beast.
    """
    entity_type: EntityType = EntityType.BEAST
    name: str = Field(..., description="The name of the beast.")
    beast_type: BeastType = Field(..., description="The type of the beast.")
    age: int = Field(..., description="The age of the beast.")
    race: str = Field(..., description="The race of the beast.")
    gender: str = Field(..., description="The gender of the beast.")
    description: str = Field(..., description="The description of the beast.")


class Location(GameEntity):
    """
    Represents a Location.
    """
    entity_type: EntityType = EntityType.LOCATION
    name: str = Field(..., description="The name of the location.")
    location_type: LocationType = Field(..., description="The type of the location.")
    description: str = Field(..., description="The description of the location.")


class Item(GameEntity):
    """
    Represents an Item.
    """
    entity_type: EntityType = EntityType.ITEM
    name: str = Field(..., description="The name of the item.")
    item_type: ItemType = Field(..., description="The type of item.")
    description: str = Field(..., description="The description of the item.")


class Quest(GameEntity):
    """
    Represents a Quest.
    """
    entity_type: EntityType = EntityType.QUEST
    name: str = Field(..., description="The name of the quest.")
    quest_type: QuestType = Field(..., description="The type of quest.")
    description: str = Field(..., description="The description of the quest.")


class Event(GameEntity):
    """
    Represents an Event.
    """
    entity_type: EntityType = EntityType.EVENT
    name: str = Field(..., description="The name of the event.")
    event_type: EventType = Field(..., description="The type of event.")
    description: str = Field(..., description="The description of the event.")


class Faction(GameEntity):
    """
    Represents a Faction.
    """
    entity_type: EntityType = EntityType.FACTION
    name: str = Field(..., description="The name of the faction.")
    faction_type: FactionType = Field(..., description="The type of faction.")
    description: str = Field(..., description="The description of the faction.")


class Relationship(BaseModel):
    """
    Represents a Relationship.
    """
    first_entity_id: str = Field(..., description="The entity id of the first entity.")
    relationship_type: RelationshipType = Field(..., description="The type of relationship.")
    second_entity_id: str = Field(..., description="The entity id of the second entity.")
    description: str = Field(..., description="The description of the relationship.")


class CharacterQuery(BaseModel):
    character_type: Optional[CharacterType] = Field(None, description="The type of character to query.")
    name: Optional[str] = Field(None, description="The name of the character to query. Allows partial matches.")
    age: Optional[int] = Field(None, description="The age of the character to query.")
    race: Optional[str] = Field(None, description="The race of the character to query. Allows partial matches.")
    gender: Optional[str] = Field(None, description="The gender of the character to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the character to query. Allows partial matches.")


class BeastQuery(BaseModel):
    beast_type: Optional[BeastType] = Field(None, description="The type of beast to query.")
    name: Optional[str] = Field(None, description="The name of the beast to query. Allows partial matches.")
    age: Optional[int] = Field(None, description="The age of the beast to query.")
    race: Optional[str] = Field(None, description="The race of the beast to query. Allows partial matches.")
    gender: Optional[str] = Field(None, description="The gender of the beast to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the beast to query. Allows partial matches.")


class LocationQuery(BaseModel):
    location_type: Optional[LocationType] = Field(None, description="The type of location to query.")
    name: Optional[str] = Field(None, description="The name of the location to query. Allows partial matches.")


class ItemQuery(BaseModel):
    item_type: Optional[ItemType] = Field(None, description="The type of item to query.")
    name: Optional[str] = Field(None, description="The name of the item to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the item to query. Allows partial matches.")


class QuestQuery(BaseModel):
    quest_type: Optional[QuestType] = Field(None, description="The type of quest to query.")
    name: Optional[str] = Field(None, description="The name of the quest to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the quest to query. Allows partial matches.")


class EventQuery(BaseModel):
    event_type: Optional[EventType] = Field(None, description="The type of event to query.")
    name: Optional[str] = Field(None, description="The name of the event to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the event to query. Allows partial matches.")


class FactionQuery(BaseModel):
    faction_type: Optional[FactionType] = Field(None, description="The type of faction to query.")
    name: Optional[str] = Field(None, description="The name of the faction to query. Allows partial matches.")
    location: Optional[str] = Field(None, description="The location of the faction to query. Allows partial matches.")


class GameWorldKnowledgeGraph:
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.entity_counters = {
            EntityType.CHARACTER: 0,
            EntityType.BEAST: 0,
            EntityType.LOCATION: 0,
            EntityType.ITEM: 0,
            EntityType.QUEST: 0,
            EntityType.EVENT: 0,
            EntityType.FACTION: 0
        }

    def generate_entity_id(self, entity_type: EntityType) -> str:
        self.entity_counters[entity_type] += 1
        return f"{entity_type.value}-{self.entity_counters[entity_type]}"

    def add_entity(self, game_entity: Union[Character, Beast, Location, Item, Quest, Event, Faction]):
        """
        Adds a game entity to the game world knowledge graph. Returns the entity id of the entity added.
        Args:
            game_entity(Union[Character, Beast, Location, Item, Quest, Event, Faction]): The entity to add.
        """
        entity_id = self.generate_entity_id(game_entity.entity_type)
        self.knowledge_graph.add_entity(entity_id, game_entity.model_dump(mode="json"))

    def query_entities(self, entity_query: Union[
        CharacterQuery, BeastQuery, LocationQuery, ItemQuery, QuestQuery, EventQuery, FactionQuery]) -> str:
        """
        Query entities of the game world knowledge graph.
        Args:
           entity_query(Union[CharacterQuery, BeastQuery, LocationQuery, ItemQuery, QuestQuery, EventQuery, FactionQuery]): The entity query to query.
        """
        if isinstance(entity_query, CharacterQuery):
            return self.query_characters(
                character_type=entity_query.character_type,
                name=entity_query.name,
                age=entity_query.age,
                race=entity_query.race,
                gender=entity_query.gender,
                location=entity_query.location
            )
        elif isinstance(entity_query, BeastQuery):
            return self.query_beasts(
                beast_type=entity_query.beast_type,
                name=entity_query.name,
                age=entity_query.age,
                race=entity_query.race,
                gender=entity_query.gender,
                location=entity_query.location
            )
        elif isinstance(entity_query, LocationQuery):
            return self.query_locations(
                location_type=entity_query.location_type,
                name=entity_query.name
            )
        elif isinstance(entity_query, ItemQuery):
            return self.query_items(
                item_type=entity_query.item_type,
                name=entity_query.name,
                location=entity_query.location
            )
        elif isinstance(entity_query, QuestQuery):
            return self.query_quests(
                quest_type=entity_query.quest_type,
                name=entity_query.name,
                location=entity_query.location
            )
        elif isinstance(entity_query, EventQuery):
            return self.query_events(
                event_type=entity_query.event_type,
                name=entity_query.name,
                location=entity_query.location
            )
        elif isinstance(entity_query, FactionQuery):
            return self.query_factions(
                faction_type=entity_query.faction_type,
                name=entity_query.name,
                location=entity_query.location
            )
        else:
            return "Invalid query type provided."

    def add_character(self, character: Character):
        """
        Adds a character to the game world knowledge graph. Returns the entity id of the character added.
        Args:
            character(Character): The character to add.
        """
        entity_id = self.generate_entity_id(EntityType.CHARACTER)
        self.knowledge_graph.add_entity(entity_id, character.model_dump(mode="json"))
        return f"Character '{character.name}' added successfully with ID: {entity_id}"

    def add_beast(self, beast: Beast):
        """
        Adds a beast to the game world knowledge graph. Returns the entity id of the beast added.
        Args:
            beast(Beast): The beast to add.
        """
        entity_id = self.generate_entity_id(EntityType.BEAST)
        self.knowledge_graph.add_entity(entity_id, beast.model_dump(mode="json"))
        return f"Beast '{beast.name}' added successfully with ID: {entity_id}"

    def add_location(self, location: Location):
        """
        Adds a location to the game world knowledge graph. Returns the entity id of the location added.
        Args:
            location(Location): The location to add.
        """
        entity_id = self.generate_entity_id(EntityType.LOCATION)
        self.knowledge_graph.add_entity(entity_id, location.model_dump(mode="json"))
        return f"Location '{location.name}' added successfully with ID: {entity_id}"

    def add_item(self, item: Item):
        """
        Adds an item to the game world knowledge graph. Returns the entity id of the item added.
        Args:
            item(Item): The item to add.
        """
        entity_id = self.generate_entity_id(EntityType.ITEM)
        self.knowledge_graph.add_entity(entity_id, item.model_dump(mode="json"))
        return f"Item '{item.name}' added successfully with ID: {entity_id}"

    def add_quest(self, quest: Quest):
        """
        Adds a quest to the game world knowledge graph. Returns the entity id of the quest added.
        Args:
            quest(Quest): The quest to add.
        """
        entity_id = self.generate_entity_id(EntityType.QUEST)
        self.knowledge_graph.add_entity(entity_id, quest.model_dump(mode="json"))
        return f"Quest '{quest.name}' added successfully with ID: {entity_id}"

    def add_event(self, event: Event):
        """
        Adds an event to the game world knowledge graph. Returns the entity id of the event added.
        Args:
            event(Event): The event to add.
        """
        entity_id = self.generate_entity_id(EntityType.EVENT)
        self.knowledge_graph.add_entity(entity_id, event.model_dump(mode="json"))
        return f"Event '{event.name}' added successfully with ID: {entity_id}"

    def add_faction(self, faction: Faction):
        """
        Adds a faction to the game world knowledge graph. Returns the entity id of the faction added.
        Args:
            faction(Faction): The faction to add.
        """
        entity_id = self.generate_entity_id(EntityType.FACTION)
        self.knowledge_graph.add_entity(entity_id, faction.model_dump(mode="json"))
        return f"Faction '{faction.name}' added successfully with ID: {entity_id}"

    def add_relationship(self, relationship: Relationship):
        """
        Adds a relationship between two entities to the game world knowledge graph.
        Args:
            relationship(Relationship): The relationship to add.
        """
        self.knowledge_graph.add_relationship(relationship.first_entity_id, relationship.second_entity_id,
                                              relationship.relationship_type.value,
                                              {"description": relationship.description})
        return f"Relationship '{relationship.relationship_type.value}' added successfully between entities {relationship.first_entity_id} and {relationship.second_entity_id}"

    def query_characters(self, character_type: Optional[CharacterType] = None, name: Optional[str] = None,
                         age: Optional[int] = None, race: Optional[str] = None,
                         gender: Optional[str] = None, location: Optional[str] = None):
        """
        Queries the characters stored in the game world knowledge graph.
        Args:
            character_type(Optional[CharacterType]): The type of character to query.
            name(Optional[str]): The name of the character to query. Allows partial matches.
            age(Optional[int]): The age of the character to query.
            race(Optional[str]): The race of the character to query. Allows partial matches.
            gender(Optional[str]): The gender of the character to query. Allows partial matches.
            location(Optional[str]): The location of the character to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.CHARACTER.value:
                return False
            if character_type and data['character_type'] != character_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if age is not None and data['age'] != age:
                return False
            if race and race.lower() not in data['race'].lower():
                return False
            if gender and gender.lower() not in data['gender'].lower():
                return False
            if location:
                # Check if character is related to the given location
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if ((edge_data['relationship'] == RelationshipType.INHABITS.value or edge_data[
                        'relationship'] == RelationshipType.LOCATED_IN.value or edge_data[
                             'relationship'] == RelationshipType.RESIDES_IN.value) and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No characters found matching the given criteria."
        return "\n".join(
            [f"Character ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in
             results])

    def query_beasts(self, beast_type: Optional[BeastType] = None, name: Optional[str] = None,
                     age: Optional[int] = None,
                     race: Optional[str] = None,
                     gender: Optional[str] = None, location: Optional[str] = None):
        """
        Queries the beasts stored in the game world knowledge graph.
        Args:
            beast_type(Optional[BeastType]): The type of beast to query.
            name(Optional[str]): The name of the beast to query. Allows partial matches.
            age(Optional[int]): The age of the beast to query.
            race(Optional[str]): The race of the beast to query. Allows partial matches.
            gender(Optional[str]): The gender of the beast to query. Allows partial matches.
            location(Optional[str]): The location of the beast to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.BEAST.value:
                return False
            if beast_type and data['beast_type'] != beast_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if age is not None and data['age'] != age:
                return False
            if race and race.lower() not in data['race'].lower():
                return False
            if gender and gender.lower() not in data['gender'].lower():
                return False
            if location:
                # Check if beast is related to the given location
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if ((edge_data['relationship'] == RelationshipType.INHABITS.value or edge_data[
                        'relationship'] == RelationshipType.LOCATED_IN.value or edge_data[
                             'relationship'] == RelationshipType.RESIDES_IN.value) and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No beasts found matching the given criteria."
        return "\n".join(
            [f"Beast ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in results])

    def query_locations(self, location_type: Optional[LocationType] = None, name: Optional[str] = None):
        """
        Queries the locations stored in the game world knowledge graph.
        Args:
            location_type(Optional[LocationType]): The type of location to query.
            name(Optional[str]): The name of the location to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.LOCATION.value:
                return False
            if location_type and data['location_type'] != location_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No locations found matching the given criteria."
        return "\n".join(
            [f"Location ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in
             results])

    def query_items(self, item_type: Optional[ItemType] = None, name: Optional[str] = None,
                    location: Optional[str] = None):
        """
        Queries the items stored in the game world knowledge graph.
        Args:
            item_type(Optional[ItemType]): The type of item to query.
            name(Optional[str]): The name of the item to query. Allows partial matches.
            location(Optional[str]): The location of the item to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.ITEM.value:
                return False
            if item_type and data['item_type'] != item_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if location:
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if (edge_data['relationship'] == RelationshipType.LOCATED_IN.value and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No items found matching the given criteria."
        return "\n".join(
            [f"Item ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in results])

    def query_quests(self, quest_type: Optional[QuestType] = None, name: Optional[str] = None,
                     location: Optional[str] = None):
        """
        Queries the quests stored in the game world knowledge graph.
        Args:
            quest_type(Optional[QuestType]): The type of quest to query.
            name(Optional[str]): The name of the quest to query. Allows partial matches.
            location(Optional[str]): The location of the quest to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.QUEST.value:
                return False
            if quest_type and data['quest_type'] != quest_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if location:
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if (edge_data['relationship'] == RelationshipType.LOCATED_IN.value and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No quests found matching the given criteria."
        return "\n".join(
            [f"Quest ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in results])

    def query_events(self, event_type: Optional[EventType] = None, name: Optional[str] = None,
                     location: Optional[str] = None):
        """
        Queries the events stored in the game world knowledge graph.
        Args:
            event_type(Optional[EventType]): The type of event to query.
            name(Optional[str]): The name of the event to query. Allows partial matches.
            location(Optional[str]): The location of the event to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.EVENT.value:
                return False
            if event_type and data['event_type'] != event_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if location:
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if (edge_data['relationship'] == RelationshipType.LOCATED_IN.value and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No events found matching the given criteria."
        return "\n".join(
            [f"Event ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in results])

    def query_factions(self, faction_type: Optional[FactionType] = None, name: Optional[str] = None,
                       location: Optional[str] = None):
        """
        Queries the factions stored in the game world knowledge graph.
        Args:
            faction_type(Optional[FactionType]): The type of faction to query.
            name(Optional[str]): The name of the faction to query. Allows partial matches.
            location(Optional[str]): The location of the faction to query. Allows partial matches.
        """

        def filter_func(node, data):
            if data['entity_type'] != EntityType.FACTION.value:
                return False
            if faction_type and data['faction_type'] != faction_type.value:
                return False
            if name and name.lower() not in data['name'].lower():
                return False
            if location:
                for _, target, edge_data in self.knowledge_graph.graph.edges(node, data=True):
                    if (edge_data['relationship'] == RelationshipType.LOCATED_IN.value and
                            location.lower() in self.knowledge_graph.graph.nodes[target]['name'].lower()):
                        return True
                return False
            return True

        results = [node for node, data in self.knowledge_graph.graph.nodes(data=True) if filter_func(node, data)]
        if not results:
            return "No factions found matching the given criteria."
        return "\n".join(
            [f"Faction ID: {node}, Name: {self.knowledge_graph.graph.nodes[node]['name']}" for node in results])

    def query_relationships(self, entity_id: str, relationship_type: Optional[RelationshipType] = None):
        """
        Queries the relationships of a specific entity.

        Args:
            entity_id (str): The ID of the entity to query relationships for.
            relationship_type (Optional[RelationshipType]): The type of relationship to filter by.

        Returns:
            str: A string describing the relationships found.
        """
        relationships = self.knowledge_graph.query_relationships(entity_id,
                                                                 relationship_type.value if relationship_type else None)
        if not relationships:
            return f"No relationships found for entity {entity_id}"

        result = f"Relationships for entity {entity_id}:\n"
        for rel in relationships:
            result += f"- {rel['source']} '{rel['type']}' {rel["target"]} ({rel['attributes'].get('description', 'No description')})\n"
        return result

    def find_path(self, start_entity_id: str, end_entity_id: str, max_depth: int = 5):
        """
        Finds a path between two entities in the knowledge graph.

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

    def get_nearby_entities(self, location_id: str, entity_type: Optional[EntityType] = None, max_distance: int = 2):
        """
        Finds entities that are near a specified location in the knowledge graph.

        Args:
            location_id (str): The ID of the location to search from.
            entity_type (Optional[EntityType]): The type of entity to filter by.
            max_distance (int): The maximum distance (in graph edges) to search.

        Returns:
            str: A string listing the nearby entities found.
        """
        subgraph = self.knowledge_graph.get_subgraph(location_id, max_depth=max_distance)
        nearby_entities = []

        for node in subgraph['nodes']:
            if node["id"] != location_id and (entity_type is None or node['entity_type'] == entity_type.value):
                nearby_entities.append((node["id"], node))

        if not nearby_entities:
            return f"No nearby entities found within {max_distance} steps of {location_id}"

        result = f"Entities near {location_id} (within {max_distance} steps):\n"
        for entity_id, entity_data in nearby_entities:
            result += f"- {entity_id}: {entity_data.get('name', 'Unnamed entity')} ({entity_data['entity_type']})\n"
        return result

    def get_single_tools(self):
        return [FunctionTool(self.add_character), FunctionTool(self.add_beast), FunctionTool(self.add_location),
                FunctionTool(self.add_item), FunctionTool(self.add_quest), FunctionTool(self.add_event),
                FunctionTool(self.add_faction), FunctionTool(self.add_relationship),
                FunctionTool(self.query_characters),
                FunctionTool(self.query_beasts), FunctionTool(self.query_locations), FunctionTool(self.query_items),
                FunctionTool(self.query_quests), FunctionTool(self.query_events), FunctionTool(self.query_factions),
                FunctionTool(self.query_relationships), FunctionTool(self.query_entities_by_attribute),
                FunctionTool(self.get_entity_details), FunctionTool(self.get_nearby_entities)]

    def get_unified_tools(self):
        return [FunctionTool(self.add_entity), FunctionTool(self.add_relationship), FunctionTool(self.query_entities),
                FunctionTool(self.query_relationships), FunctionTool(self.query_entities_by_attribute),
                FunctionTool(self.get_entity_details), FunctionTool(self.get_nearby_entities)]

    def save(self, filename: str) -> None:
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

    @classmethod
    def load(cls, filename: str) -> 'GameWorldKnowledgeGraph':
        """
        Load a GameWorldKnowledgeGraph from a JSON file.

        Args:
            filename (str): The name of the file to load from.

        Returns:
            GameWorldKnowledgeGraph: The loaded GameWorldKnowledgeGraph instance.
        """
        with open(filename, 'r', encoding="utf-8") as f:
            data = json.load(f)

        game_world = cls()
        game_world.knowledge_graph = KnowledgeGraph.load_from_json(data['knowledge_graph_filename'])
        game_world.entity_counters = data['entity_counters']
        return game_world
