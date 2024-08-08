from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'

    location_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))

    npcs = relationship("NPC", back_populates="location")
    players = relationship("Player", back_populates="location")
    items = relationship("Item", back_populates="location")


class NPC(Base):
    __tablename__ = 'npcs'

    npc_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    current_location_id = Column(Integer, ForeignKey('locations.location_id'))

    location = relationship("Location", back_populates="npcs")


class Interaction(Base):
    __tablename__ = 'interactions'

    interaction_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    initiator_type = Column(Enum('player', 'npc', 'system', name='initiator_types'), nullable=False)
    initiator_id = Column(Integer)
    target_type = Column(Enum('player', 'npc', 'location', 'item', name='target_types'))
    target_id = Column(Integer)


class Item(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    current_location_id = Column(Integer, ForeignKey('locations.location_id'))
    current_owner_type = Column(Enum('player', 'npc', 'location', name='owner_types'))
    current_owner_id = Column(Integer)

    location = relationship("Location", back_populates="items")

