import random, uuid, sqlite3
import uuid

from ResearchOS.config import Config
# from ResearchOS.sqlite_pool import SQLiteConnectionPool

config = Config()

abstract_id_len = config.immutable["abstract_id_len"]
instance_id_len = config.immutable["instance_id_len"]

class IDCreator():
    """Creates all ID's for the ResearchOS database."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialize the IDCreator."""        
        self.conn = conn

    def get_prefix(self, id: str) -> str:
        """Get the prefix of the given ID."""
        if not self.is_ro_id(id):
            raise ValueError("The given ID is not a valid ResearchObject ID.")
        return id[:2]
    
    def create_ro_id(self, cls, abstract: str = None, instance: str = None, is_abstract: bool = False) -> str:
        """Create a ResearchObject ID following [prefix]XXXXXX_XXX."""
        conn = self.conn
        table_name = "research_objects"
        is_unique = False
        while not is_unique:
            if not abstract:
                abstract_new = str(hex(random.randrange(0, 16**abstract_id_len))[2:]).upper()
                abstract_new = "0" * (abstract_id_len-len(abstract_new)) + abstract_new
            else:
                abstract_new = abstract
            
            if not instance:
                instance_new = str(hex(random.randrange(0, 16**instance_id_len))[2:]).upper()
                instance_new = "0" * (instance_id_len-len(instance_new)) + instance_new
            else:
                instance_new = instance
            if is_abstract:
                instance_new = ""
 
            id = cls.prefix + abstract_new + "_" + instance_new
            cursor = conn.cursor()
            cursor = conn.cursor()
            sql = f'SELECT object_id FROM {table_name} WHERE object_id = "{id}"'
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) == 0:
                is_unique = True
            elif is_abstract:
                raise ValueError("Abstract ID already exists.")
        # self.pool.return_connection(conn)
        return id   


    def create_action_id(self, check: bool = True) -> str:
        """Create an Action ID using Python's builtin uuid4."""
        is_unique = False
        conn = self.conn
        cursor = conn.cursor()
        uuid_out = str(uuid.uuid4()) # For testing dataset creation.
        if not check:
            is_unique = True # If not checking, assume it's unique.
        while not is_unique:            
            sql = f'SELECT action_id FROM actions WHERE action_id = "{uuid_out}"'
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) == 0:
                is_unique = True
                break
            uuid_out = str(uuid.uuid4())
        # self.pool.return_connection(conn)
        return uuid_out
    
    def _is_action_id(uuid: str) -> bool:
        """Check if a string is a valid UUID."""
        import uuid as uuid_module
        try:
            uuid_module.UUID(str(uuid))
        except ValueError:
            return False
        return True   
    
    def is_ro_id(self, id: str) -> bool:
        """Check if the given ID matches the pattern of a valid research object ID."""    
        # TODO: Re-implement this when I decide on what the ResearchObject ID's look like.
        from ResearchOS.research_object import ResearchObject
        from ResearchOS.research_object_handler import ResearchObjectHandler
        instance_pattern = "^[a-zA-Z]{2}[a-fA-F0-9]{6}_[a-fA-F0-9]{3}$"
        abstract_pattern = "^[a-zA-Z]{2}[a-fA-F0-9]{6}$"
        subclasses = ResearchObjectHandler._get_subclasses(ResearchObject)
        # Check for a valid prefix.
        # self.pool.return_connection(self.conn)
        # self.pool.return_connection(self.conn)
        if not any(id.startswith(cls.prefix) for cls in subclasses if hasattr(cls, "prefix")):
            return False
        return True
        # if not isinstance(id, str):
        #     raise ValueError("id must be a str!")
        # if re.match(instance_pattern, id) or re.match(abstract_pattern, id):
        #     return True
        # return False  

# def main():
#     parser = argparse.ArgumentParser(description='Generate a UUID based on the specified version.')
#     parser.add_argument('-a', '--action', action='store_const', const='3', help='Generate a UUID using uuid3 (requires -a or -r argument).')
#     parser.add_argument('-r', '--researchobject', action='store_const', const='4', help='Generate a UUID using uuid4 (requires -a or -r argument).')
#     args = parser.parse_args()

#     # Check which argument is provided
#     if args.action:
#         id = IDCreator().create_action_id()
#     elif args.researchobject:
#         id = IDCreator().create_ro_id()
#     else:
#         parser.print_help()
#         sys.exit(1)
    

if __name__ == "__main__":
    main()