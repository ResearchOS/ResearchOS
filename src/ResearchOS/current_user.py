from typing import TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from ResearchOS.action import Action

from ResearchOS.idcreator import IDCreator
from ResearchOS.get_computer_id import COMPUTER_ID
# from ResearchOS.sql.sql_joiner_most_recent import sql_joiner_most_recent

default_current_user = "default_user"

class CurrentUser():
    """Singular purpose is to return the current user object ID."""

    current_user = ""    

    def __init__(self, action: "Action") -> None:
        """Initialize the CurrentUser class."""
        self.action = action
    
    def get_current_user_id(self) -> str:
        """Get the current user from the actions table in the database.
        Reads the most recent action (by timestamp) and returns the user. User will always exist if an action exists because user is NOT NULL in SQLite table.
        If no actions exist, raise an error."""
        if len(CurrentUser.current_user) > 0:
            return CurrentUser.current_user
        cursor = self.action.conn.cursor()

        sqlquery = "SELECT user_id FROM users_computers WHERE computer_id = ?"
        result = cursor.execute(sqlquery, (COMPUTER_ID,)).fetchone()
        if result is None:
            raise ValueError("current user does not exist because there are no users for this computer")

        CurrentUser.current_user = result[0]
        return CurrentUser.current_user
    
    def set_current_user_computer_id(self, user: str = default_current_user) -> None:
        """Set the current user in the user_computer_id table in the database.
        This is the only action that does not affect any other table besides Actions. It is a special case."""
        params = (self.action.id, user, COMPUTER_ID)
        self.action.db_init_params = params
        CurrentUser.current_user = user
        CurrentUser.computer_id = COMPUTER_ID

    def _get_timestamps_when_current(self, type: str, user_or_computer_id: str = None, ) -> list:
        """Get the timestamps when the current user OR computer was active, across all computers/users, respectively.
        Returns an N x 2 list of timestamps, where N is the number of times that this user was set to current.
        Note that the timestamps are "[)", meaning the end time is not included. This is because the end time is the start time of the next action."""
        cursor = self.action.conn.cursor()
        if user_or_computer_id is None:
            if type == "user":
                col_name = "user_id"
                user_or_computer_id = self.get_current_user_id()
            elif type == "computer":
                col_name = "computer_id"
                user_or_computer_id = COMPUTER_ID
        sqlquery = f"SELECT action_id, {col_name} FROM users_computers"
        result = cursor.execute(sqlquery).fetchall()
        action_ids = []
        idx_last_current = -1 # Initialize
        for idx, r in enumerate(result):
            # This row is the current user.
            if r[1] == user_or_computer_id:
                idx_last_current = idx
                action_ids.append([r[0]])

            if idx==0:
                continue

            # The previous row was the current user. Not using elif covers the case of two consecutive rows being the current user.
            if idx_last_current == idx-1:
                action_ids[-2].append(r[0]) # Insert into the second to last row.
            
        # Make it a 1D list.
        action_ids_vector = []
        for t in action_ids:
            action_ids_vector.extend(t) 

        sqlquery = "SELECT datetime FROM actions WHERE action_id IN ({})".format(",".join("?" * len(action_ids_vector)))
        result = cursor.execute(sqlquery, action_ids_vector).fetchall()

        timestamp_2d = []
        for i in range(0, len(result), 2):
            if i+1 < len(result):
                timestamp_2d.append([result[i][0], result[i+1][0]]) # [start, end) format.
            else:
                # Cover the case where the user is the current user at the end of the list.
                end_time = str(datetime.max.replace(tzinfo=timezone.utc)) # Make it a string.
                timestamp_2d.append([result[i][0], end_time])

        return timestamp_2d

    def get_overlapping_timestamps(self, timestamps_1: list, timestamps_2: list) -> list:
        """Get the overlapping timestamps between the two lists."""
        overlapping_timestamps = []
        for t1 in timestamps_1:
            for t2 in timestamps_2:
                start = max(t1[0], t2[0])
                end = min(t1[1], t2[1])
                if start <= end:
                    overlapping_timestamps.append([start, end])
        
        # Sort the list by the start times
        overlapping_timestamps.sort(key=lambda x: x[0])

        # Merge overlapping intervals
        merged_timestamps = []
        for start, end in overlapping_timestamps:
            if not merged_timestamps or merged_timestamps[-1][1] < start:
                merged_timestamps.append([start, end])
            else:
                merged_timestamps[-1][1] = max(merged_timestamps[-1][1], end)

        return merged_timestamps
        
    def get_action_ids_when_current(self, user_id: str = None, computer_id: str = None, user: bool = False, computer: bool = True) -> list:
        """Get the action_ids when the current user was using the current computer."""
        timestamps = self.get_timestamps_when_current(user_id = user_id, computer_id = computer_id, user = user, computer = computer)

        sqlquery = "SELECT action_id FROM actions WHERE "
        placeholders = []
        params = []
        cursor = self.action.conn.cursor()
        for start, end in timestamps:
            placeholders.append("(timestamp >= ? AND timestamp < ?)") # Inclusive, exclusive.
            params.extend([start, end])
        sqlquery += " OR ".join(placeholders)
        result = cursor.execute(sqlquery, params).fetchall()
        action_ids = [row[0] for row in result]
        return action_ids
    
    def get_timestamps_when_current(self, user_id: str = None, computer_id: str = None, user: bool = True, computer: bool = True) -> list:
        """Get the timestamps when the current user and/or computer was active."""
        if user:
            user_timestamps = self._get_timestamps_when_current(type = "user", user_or_computer_id = user_id)
        if computer:
            computer_timestamps = self._get_timestamps_when_current(type = "computer", user_or_computer_id = computer_id)
        if user and computer:
            timestamps = self.get_overlapping_timestamps(user_timestamps, computer_timestamps)
        elif user:
            timestamps = user_timestamps
        elif computer:
            timestamps = computer_timestamps
        return timestamps
