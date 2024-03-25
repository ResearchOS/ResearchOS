from ResearchOS.action import Action
from ResearchOS.sqlite_pool import SQLiteConnectionPool
from ResearchOS.current_user import CurrentUser
   
def get_action_ids_within_range(action: Action, action_id1: str, action_id2: str) -> list:
    """Get the action IDs within a range of two action IDs."""
    cursor = action.conn.cursor()
    sqlquery = "SELECT action_id FROM actions WHERE action_id >= ? AND action_id <= ?"
    result = cursor.execute(sqlquery, (action_id1, action_id2)).fetchall()
    return [r[0] for r in result]

def get_action_ids_within_time_range(action: Action, timestamp1: str, timestamp2: str) -> list:
    """Get the action IDs within a range of two timestamps."""
    cursor = action.conn.cursor()
    sqlquery = "SELECT action_id FROM actions WHERE timestamp >= ? AND timestamp <= ?"
    result = cursor.execute(sqlquery, (timestamp1, timestamp2)).fetchall()
    return [r[0] for r in result]


def get_latest_action(user_id: str = None) -> Action:
    """Get the most recent action performed chronologically for the current user."""
    pool = SQLiteConnectionPool()
    conn = pool.get_connection()
    current_user = CurrentUser(conn)
    if not user_id:
        user_id = current_user.get_current_user_id()
    current_user_timestamps = current_user.get_timestamps_when_current_user(user = user_id)
    action_ids = get_action_ids_within_time_range(action = Action(conn = conn), timestamp1 = current_user_timestamps[0][0], timestamp2 = current_user_timestamps[-1][1])
    return Action(id = action_ids[-1]) # Return the latest one.
    

def get_next_action(action: Action) -> Action:
    """Get the next action after this action."""
    timestamp = action.timestamp
    sqlquery = f"SELECT action_id FROM actions WHERE timestamp > ? AND action_id IN ? ORDER BY timestamp ASC LIMIT 1"
    user_action_ids = CurrentUser(action.conn).get_user_action_ids()
    params = (timestamp, user_action_ids)
    cursor = action.conn.cursor()
    result = cursor.execute(sqlquery, params).fetchone()
    if result is None:
        return None
    id = result[0]
    return Action(id = id)

def get_previous_action(action: Action) -> "Action":
    """Get the previous action before this action."""
    timestamp = action.timestamp
    sqlquery = f"SELECT action_id FROM actions WHERE timestamp < ? AND action_id IN ? ORDER BY timestamp DESC LIMIT 1"
    user_action_ids = CurrentUser(action.conn).get_user_action_ids()
    params = (timestamp, user_action_ids)
    cursor = action.conn.cursor()
    result = cursor.execute(sqlquery, params).fetchone()
    if result is None:
        return None
    id = result[0]
    return Action(id = id)

# def redo(self) -> None:
#     """Execute the action, causing the current state of the referenced widgets and research objects to be the state in this Action."""        
#     # Create a new action, where "redo_of" is set to self.id.        
#     next_action = Action.next(id = self.id)
#     if next_action is None:
#         return
#     Action.set_current_action(action = next_action)
#     next_action.execute()

# def undo(self) -> None:
#     """Undo the action, causing the current state of the referenced widgets and research objects to be the state of the previous Action."""
#     # Log the action to the database.        
#     prev_action = Action.previous(id = self.id)
#     if prev_action is None:
#         return        
#     prev_action.redo()    

# def _get_rows_of_action(action: Action, table_name: str) -> list:
#     """Get the rows of a table that were created by an action."""
#     cursor = action.conn.cursor()
#     sqlquery = f"SELECT * FROM ? WHERE action_id = ?"
#     params = (table_name, action.id,)
#     return cursor.execute(sqlquery, params).fetchall() 