from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import and_, or_

Base = declarative_base()

db_uri = "sqlite:///knowledge_graph.db"
engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Association table for relationships
relationships_table = Table(
    'relationships', Base.metadata,
    Column('left_entity_id', String, ForeignKey('entities.entity_id')),
    Column('right_entity_id', String, ForeignKey('entities.entity_id')),
    Column('relationship_type', String),
    Column('attributes', JSON, nullable=True)
)


class Entity(Base):
    __tablename__ = 'entities'

    entity_id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False)
    attributes = Column(JSON, nullable=False)

    @declared_attr
    def relationships(cls):
        return relationship(
            "Entity",
            secondary=relationships_table,
            primaryjoin=lambda: relationships_table.c.left_entity_id == cls.entity_id,
            secondaryjoin=lambda: relationships_table.c.right_entity_id == cls.entity_id,
            backref="related_entities",
        )

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "attributes": self.attributes
        }


class KnowledgeGraphDatabase:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session = session

    def add_entity(self, entity_type: str, attributes: Dict[str, Any]) -> str:
        # Generate unique entity ID for the new entity
        new_entity_id = f"{entity_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        entity = Entity(entity_id=new_entity_id, entity_type=entity_type, attributes=attributes)
        self.session.add(entity)
        self.session.commit()
        return entity.entity_id

    def update_entity(self, entity_id: str, new_attributes: Dict[str, Any]) -> str:
        entity = self.session.query(Entity).filter(Entity.entity_id == entity_id).first()
        if not entity:
            return f"Error: No entity found with ID {entity_id}"
        entity.attributes.update(new_attributes)
        self.session.commit()
        return f"Entity {entity_id} updated successfully"

    def delete_entity(self, entity_id: str) -> str:
        entity = self.session.query(Entity).filter(Entity.entity_id == entity_id).first()
        if not entity:
            return f"Error: No entity found with ID {entity_id}"
        self.session.delete(entity)
        self.session.commit()
        return f"Entity {entity_id} deleted successfully"

    def query_entities(self, entity_type: Optional[str] = None, attribute_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = self.session.query(Entity)
        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)
        if attribute_filter:
            filters = [Entity.attributes[k] == v for k, v in attribute_filter.items()]
            query = query.filter(and_(*filters))
        result = query.all()
        return [entity.to_dict() for entity in result]

    def add_relationship(self, first_entity_id: str, relationship_type: str, second_entity_id: str,
                         attributes: Optional[Dict[str, Any]] = None) -> str:
        first_entity = self.session.query(Entity).filter(Entity.entity_id == first_entity_id).first()
        second_entity = self.session.query(Entity).filter(Entity.entity_id == second_entity_id).first()
        if not first_entity or not second_entity:
            return f"Error: Entity not found"
        relationship = {
            'left_entity_id': first_entity_id,
            'right_entity_id': second_entity_id,
            'relationship_type': relationship_type,
            'attributes': attributes if attributes else {}
        }
        ins = relationships_table.insert().values(**relationship)
        self.session.execute(ins)
        self.session.commit()
        return f"Relationship '{relationship_type}' added successfully between entities {first_entity_id} and {second_entity_id}"

    def query_relationships(self, entity_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.session.query(relationships_table).filter(
            or_(relationships_table.c.left_entity_id == entity_id, relationships_table.c.right_entity_id == entity_id)
        )
        if relationship_type:
            query = query.filter(relationships_table.c.relationship_type == relationship_type)
        relationships = query.all()
        result = []
        for rel in relationships:
            related_entity_id = rel.right_entity_id if rel.left_entity_id == entity_id else rel.left_entity_id
            result.append({
                'related_entity': related_entity_id,
                'relationship_type': rel.relationship_type,
                'attributes': rel.attributes
            })
        return result


# Usage example
if __name__ == "__main__":
    kgdb = KnowledgeGraphDatabase()

    # Add entity
    entity_id = kgdb.add_entity(entity_type="Person", attributes={"name": "Alice", "age": 30})
    print(f"Added entity with ID: {entity_id}")

    # Update entity
    print(kgdb.update_entity(entity_id, {"age": 31}))

    # Query entities
    entities = kgdb.query_entities(entity_type="Person")
    print("Entities found:", entities)

    # Add relationship
    second_entity_id = kgdb.add_entity(entity_type="Person", attributes={"name": "Bob", "age": 25})
    print(kgdb.add_relationship(entity_id, "friends_with", second_entity_id))

    # Query relationships
    relationships = kgdb.query_relationships(entity_id)
    print("Relationships:", relationships)

    # Delete entity
    print(kgdb.delete_entity(second_entity_id))
