import datetime, sqlite3
from datetime import timezone
import os

from ResearchOS.idcreator import IDCreator
# from ResearchOS.current_user import CurrentUser
from ResearchOS.sqlite_pool import SQLiteConnectionPool

count = 0

# Load the SQL queries from the sql directory.
queries = {}
dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql")
file_paths = []
for file_name in os.listdir(dir):
    if not file_name.endswith(".sql"):
        continue
    file_paths.append(os.path.join(dir, file_name))
for file_path in file_paths:
    file_name, ext = os.path.splitext(os.path.basename(file_path))
    with open(file_path, "r") as f:
        queries[file_name] = f.read()

class Action():
    """An action is a set of SQL queries that are executed together."""

    latest_action_id: str = None
    queries: dict = queries
    
    def __init__(self, name: str = None, action_id: str = None, redo_of: str = None, timestamp: datetime.datetime = None, commit: bool = False, exec: bool = True, force_create: bool = False):        
        pool = SQLiteConnectionPool()
        self.conn = pool.get_connection()
        if not action_id:
            action_id = IDCreator(self.conn).create_action_id(check = False)            
        if not timestamp:
            timestamp = datetime.datetime.now(timezone.utc)

        # Set up for the queries.
        self.dobjs = {}

        self.force_create = force_create        
        self.is_created = False # Indicates that the action has not been created in the database yet.        
        self.id = action_id
        self.name = name
        self.timestamp = timestamp        
        self.redo_of = redo_of
        self.commit = commit # False by default. If True, the action will be committed to the database. Overrides self.exec.
        self.exec = exec # True to run cursor.execute() and False to skip it.        
        try:
            sqlquery = "SELECT MAX(action_id_num) FROM actions"
            result = self.conn.execute(sqlquery).fetchone()[0] + 1
        except:
            sqlquery = "SELECT name FROM sqlite_master WHERE type='table' AND name='actions'"
            result = self.conn.execute(sqlquery).fetchone()
            if result is not None:
                raise ValueError("The actions table exists, but there are no rows in it.")
            else:
                result = 1 # The actions table does not exist, so the action_id_num = 1
        self.id_num = result
        self.creation_params = (action_id, self.id_num, name, timestamp, redo_of) # The parameters for the creation query.

    def add_sql_query(self, dobj_id: str, query_name: str, params: tuple = None, group_name: str = "all") -> None:
        """Add a sqlquery to the action. Can be a raw SQL query (one input) or a parameterized query (two inputs).
        Parameters can be either a tuple (for one query) or a list of tuples (for multiple queries)."""
        if query_name not in self.queries:
            raise ValueError(f"{query_name} is not a valid query name.")
        if not params:
            return # Do I need this?
        if not isinstance(params, tuple):            
            raise ValueError(f"params must be a tuple or list, not {type(params)}.")
        if group_name not in self.dobjs:
            self.dobjs[group_name] = {}
        if query_name not in self.dobjs[group_name]:
            self.dobjs[group_name][query_name] = {} # Initialize the dobj_id if it doesn't exist.
        if dobj_id not in self.dobjs[group_name][query_name]:
            self.dobjs[group_name][query_name][dobj_id] = [] # Initialize the query_name if it doesn't exist for this dobj_id        
        
        self.dobjs[group_name][query_name][dobj_id].append(params) # Allows for multiple params to be added at once with "executemany"

    def is_redundant_params(self, dobj_id: str, query_name: str, primary_key: tuple, group_name: str = "all") -> bool:
        """Check if the parameters are redundant."""
        if group_name not in self.dobjs:
            return False
        if query_name not in self.dobjs[group_name]:
            return False
        if dobj_id not in self.dobjs[group_name][query_name]:
            return False
        if any([primary_key in tup for tup in self.dobjs[group_name][query_name][dobj_id]]):
            return True
        return False

    def execute(self, return_conn: bool = True) -> None:
        """Run all of the sql queries in the action."""
        if not self.exec:
            return
        global count
        count += 1
        # print(f"Action.execute() called {count} times.")
        pool = SQLiteConnectionPool(name = "main")
        
        # The queries that use the other database.
        data_query_names = ["data_value_in_blob_insert"]

        any_queries = False
        if self.dobjs:
            any_queries = True

        if not any_queries and not self.force_create:
            if return_conn:
                pool.return_connection(self.conn)            
                self.conn = None
                return
            else:
                return
        
        cursor = self.conn.cursor()
        if not self.is_created or self.force_create:
            self.is_created = True
            cursor.execute(self.queries["action_insert"], self.creation_params)            

        uses_data = False
        for group_name in self.dobjs:
            if any(query in data_query_names for query in self.dobjs[group_name]):                
                if not hasattr(self, "conn_data"):
                    pool_data = SQLiteConnectionPool(name = "data")
                    self.conn_data = pool_data.get_connection()
                conn_data = self.conn_data
                cursor_data = conn_data.cursor()
                uses_data = True
                break

        # Execute all of the SQL queries.
        for group_name in self.dobjs:
            for query_name in self.dobjs[group_name]:
                query = self.queries[query_name]
                params_list = []
                # print("Executing SQL statement named ", query_name, " ", query)
                for dobj_id in self.dobjs[group_name][query_name]:
                    if len(self.dobjs[group_name][query_name][dobj_id]) == 0:
                        continue

                    for param in self.dobjs[group_name][query_name][dobj_id]:
                        if param not in params_list:
                            params_list.append(param)
                num_params = len(params_list)
                try:
                    for i in range(0, num_params, 50):
                        if i < num_params - 50:                        
                            curr_params = params_list[i:i+50]
                        else:
                            curr_params = params_list[i:]
                        if query_name in data_query_names:
                            cursor_data.executemany(query, curr_params)
                        else:
                            cursor.executemany(query, curr_params)
                except sqlite3.OperationalError as e:
                    self.conn.rollback()
                    if uses_data:
                        conn_data.rollback()
                    raise ValueError(f"SQL query failed: {query}")
        self.dobjs = {}

        # Commit the Action.  
        if self.commit:
            # print("Commit count:", count)
            self.conn.commit()
            if uses_data:
                conn_data.commit()
            if return_conn:
                pool.return_connection(self.conn)                
                self.conn = None   
            if uses_data:
                pool_data.return_connection(conn_data)
                del self.conn_data

if __name__=="__main__":    
    action = Action(name = "Test Action")    
    action.execute()