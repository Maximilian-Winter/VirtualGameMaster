from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database import Base, Location, NPC


class GameMasterDatabase:
    """
    A database wrapper for managing game master data including locations and NPCs.

    This class provides methods to interact with a SQLite database for storing and
    retrieving game-related information. It uses SQLAlchemy as an ORM to handle
    database operations.

    Attributes:
        engine: SQLAlchemy database engine
        Session: SQLAlchemy session maker

    Usage:
        db = GameMasterDatabase()
        # Use db methods to interact with the database
    """

    def __init__(self, db_url='sqlite:///game_master.db'):
        """
        Initialize the GameMasterDatabase.

        Args:
            db_url (str): The database URL. Defaults to a local SQLite database.

        Usage:
            db = GameMasterDatabase()
            # or
            db = GameMasterDatabase('postgresql://user:password@localhost/dbname')
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _paginate_query(self, query, page=1, items_per_page=10):
        """
        Helper method to paginate query results.

        Args:
            query: SQLAlchemy query object
            page (int): The page number (1-indexed)
            items_per_page (int): Number of items per page

        Returns:
            SQLAlchemy query object with pagination applied

        Note: This is an internal method and should not be called directly.
        """
        return query.limit(items_per_page).offset((page - 1) * items_per_page)

    def _get_location_by_id(self, location_id):
        """
        Retrieve a location by its ID.

        Args:
            location_id (int): The ID of the location to retrieve

        Returns:
            Location object if found, None otherwise
        """
        session = self.Session()
        try:
            location = session.query(Location).filter(Location.location_id == location_id).one()
            return location
        except NoResultFound:
            return None
        finally:
            session.close()

    def _get_npc_by_id(self, npc_id):
        """
        Retrieve an NPC by its ID.

        Args:
            npc_id (int): The ID of the NPC to retrieve

        Returns:
            NPC object if found, None otherwise

        """
        session = self.Session()
        try:
            npc = session.query(NPC).filter(NPC.npc_id == npc_id).one()
            return npc
        except NoResultFound:
            return None
        finally:
            session.close()

    def add_location(self, name, description, type):
        """
        Add a new location to the database.

        Args:
            name (str): The name of the location
            description (str): A detailed description of the location
            type (str): The type or category of the location

        Returns:
            int: The ID of the newly created location
        """
        session = self.Session()
        new_location = Location(name=name, description=description, type=type)
        session.add(new_location)
        session.commit()
        location_id = new_location.location_id
        session.close()
        return location_id

    def add_npc(self, name, description, location_id):
        """
        Add a new NPC to the database.

        Args:
            name (str): The name of the NPC
            description (str): A detailed description of the NPC
            location_id (int): The ID of the location where the NPC is currently situated

        Returns:
            int: The ID of the newly created NPC
        """
        session = self.Session()
        new_npc = NPC(name=name, description=description, current_location_id=location_id)
        session.add(new_npc)
        session.commit()
        npc_id = new_npc.npc_id
        session.close()
        return npc_id

    def update_location(self, location_id, name=None, description=None, type=None):
        """
        Update an existing location in the database.

        Args:
            location_id (int): The ID of the location to update
            name (str, optional): The new name for the location
            description (str, optional): The new description for the location
            type (str, optional): The new type for the location
        """
        session = self.Session()
        location = session.query(Location).filter(Location.location_id == location_id).one()
        if name:
            location.name = name
        if description:
            location.description = description
        if type:
            location.type = type
        session.commit()
        session.close()

    def update_npc(self, npc_id, name=None, description=None, location_id=None):
        """
        Update an existing NPC in the database.

        Args:
            npc_id (int): The ID of the NPC to update
            name (str, optional): The new name for the NPC
            description (str, optional): The new description for the NPC
            location_id (int, optional): The new location ID for the NPC
        """
        session = self.Session()
        npc = session.query(NPC).filter(NPC.npc_id == npc_id).one()
        if name:
            npc.name = name
        if description:
            npc.description = description
        if location_id:
            npc.current_location_id = location_id
        session.commit()
        session.close()

    def _query_locations(self, name=None, page=1, items_per_page=10):
        """
        Query locations with optional name filter and pagination.

        Args:
            name (str, optional): Filter locations by name (case-insensitive, partial match)
            page (int): The page number for pagination (1-indexed)
            items_per_page (int): Number of items per page

        Returns:
            tuple: (list of Location objects, total count of matching locations)
        """
        session = self.Session()
        query = session.query(Location)

        if name:
            query = query.filter(Location.name.ilike(f'%{name}%'))

        total = query.count()
        locations = self._paginate_query(query, page, items_per_page).all()

        session.close()
        return locations, total

    def _query_npcs(self, name=None, location_name=None, page=1, items_per_page=10):
        """
        Query NPCs with optional name and location filters, and pagination.

        Args:
            name (str, optional): Filter NPCs by name (case-insensitive, partial match)
            location_name (str, optional): Filter NPCs by location name (case-insensitive, partial match)
            page (int): The page number for pagination (1-indexed)
            items_per_page (int): Number of items per page

        Returns:
            tuple: (list of NPC objects, total count of matching NPCs)
        """
        session = self.Session()
        query = session.query(NPC)

        if name:
            query = query.filter(NPC.name.ilike(f'%{name}%'))

        if location_name:
            query = query.join(Location).filter(Location.name.ilike(f'%{location_name}%'))

        total = query.count()
        npcs = self._paginate_query(query, page, items_per_page).all()

        session.close()
        return npcs, total

    def locations_to_string(self, locations, total_count, page, items_per_page):
        """
        Convert a list of Location objects to a formatted string.

        Args:
            locations (list): List of Location objects
            total_count (int): Total number of locations matching the query
            page (int): Current page number
            items_per_page (int): Number of items per page

        Returns:
            str: Formatted string representation of the locations

        Usage:
            locations, total = db._query_locations()
            print(db.locations_to_string(locations, total, page, items_per_page))
        """
        if not locations:
            return "No locations found."

        total_pages = (total_count + items_per_page - 1) // items_per_page
        result = f"Locations (Page {page} of {total_pages}, Total: {total_count}):\n"
        for loc in locations:
            result += f"ID: {loc.location_id}\n"
            result += f"Name: {loc.name}\n"
            result += f"Type: {loc.type}\n"
            result += f"Description: {loc.description}\n"
            result += f"NPCs: {', '.join([npc.name for npc in loc.npcs])}\n"
            result += f"Items: {', '.join([item.name for item in loc.items])}\n"
            result += "---\n"
        return result.strip()

    def npcs_to_string(self, npcs, total_count, page, items_per_page):
        """
        Convert a list of NPC objects to a formatted string.

        Args:
            npcs (list): List of NPC objects
            total_count (int): Total number of NPCs matching the query
            page (int): Current page number
            items_per_page (int): Number of items per page

        Returns:
            str: Formatted string representation of the NPCs

        Usage:
            npcs, total = db._query_npcs()
            print(db.npcs_to_string(npcs, total, page, items_per_page))
        """
        if not npcs:
            return "No NPCs found."

        total_pages = (total_count + items_per_page - 1) // items_per_page
        result = f"NPCs (Page {page} of {total_pages}, Total: {total_count}):\n"
        for npc in npcs:
            result += f"ID: {npc.npc_id}\n"
            result += f"Name: {npc.name}\n"
            result += f"Description: {npc.description}\n"
            result += f"Location: {npc.location.name if npc.location else 'Unknown'}\n"
            result += "---\n"
        return result.strip()

    def query_locations(self, name=None, page=1, items_per_page=10):
        """
        Query locations and return a formatted string representation.

        Args:
            name (str, optional): Filter locations by name (case-insensitive, partial match)
            page (int): The page number for pagination (1-indexed)
            items_per_page (int): Number of items per page

        Returns:
            str: Formatted string of locations, including pagination information
        """
        locations, total = self._query_locations(name, page, items_per_page)
        return self.locations_to_string(locations, total, page, items_per_page)

    def query_npcs(self, name=None, location_name=None, page=1, items_per_page=10):
        """
        Query NPCs and return a formatted string representation.

        Args:
            name (str, optional): Filter NPCs by name (case-insensitive, partial match)
            location_name (str, optional): Filter NPCs by location name (case-insensitive, partial match)
            page (int): The page number for pagination (1-indexed)
            items_per_page (int): Number of items per page

        Returns:
            str: Formatted string of NPCs, including pagination information
        """
        npcs, total = self._query_npcs(name, location_name, page, items_per_page)
        return self.npcs_to_string(npcs, total, page, items_per_page)

    def get_location_by_id(self, location_id):
        """
        Retrieve a location by its ID and return a formatted string representation.

        Args:
            location_id (int): The ID of the location to retrieve

        Returns:
            str: Formatted string representation of the location or an error message if not found
        """
        location = self._get_location_by_id(location_id)
        return self.locations_to_string([location], 1, 1, 1) if location else "Location not found."

    def get_npc_by_id(self, npc_id):
        """
        Retrieve an NPC by its ID and return a formatted string representation.

        Args:
            npc_id (int): The ID of the NPC to retrieve

        Returns:
            str: Formatted string representation of the NPC or an error message if not found
        """
        npc = self._get_npc_by_id(npc_id)
        return self.npcs_to_string([npc],1, 1, 1) if npc else "NPC not found."
