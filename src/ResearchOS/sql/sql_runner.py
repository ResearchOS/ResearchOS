from typing import TYPE_CHECKING

from ResearchOS.action import Action

# from sql_joiner_most_recent import col_names_in_where, extract_sql_components, append_table_to_columns
from ResearchOS.sql.sql_joiner_most_recent import extract_sql_components
from ResearchOS.current_user import CurrentUser

def sql_order_result(action: Action, sqlquery: str, unique_cols: list = None, single: bool = True, user: bool = True, computer: bool = True) -> None:
    """Takes in a basic SQL query, parses it, and returns the rows of that table ordered by the datetime column of the Actions table
    If "single" is True, returns only the single most recent value for each unique combination of WHERE conditions."""
    
    # Get the action_id nums of the current user & computer in the Actions table.
    if action is None:
        raise ValueError("Need to pass in an action object.")
    current_user = CurrentUser(action)
    current_user_timestamps = current_user.get_timestamps_when_current(user = user, computer = computer)

    # FOR THE QUERY THAT DOES NOT LIMIT THE NUMBER OF ROWS
    sqlquery_inner = "SELECT action_id_num, datetime FROM actions WHERE "
    placeholders = []
    for start, end in current_user_timestamps:
        placeholders.append(f"(datetime >= '{start}' AND datetime < '{end}')") # Inclusive, exclusive.
    sqlquery_inner += " OR ".join(placeholders)    

    # Extract the components of the SQL query
    columns, table, where_criteria = extract_sql_components(sqlquery)
    columns_w_table = ", ".join([f"{table}.{col}" for col in columns])
    
    if unique_cols is None:
        unique_cols = where_criteria
    else:
        unique_cols_w_table = ", ".join([f"{table}.{col}" for col in unique_cols])      

    if not single:
        sqlquery_final = "SELECT " + columns_w_table + " FROM (" + sqlquery_inner + ") AS current_user_actions JOIN " + table + " ON current_user_actions.action_id_num = " + table + ".action_id_num WHERE " + where_criteria + " ORDER BY current_user_actions.datetime DESC"
    else:
        columns_w_result_table = ", ".join([f"result.{col}" for col in columns])
        sqlquery_inner2 = "SELECT " + columns_w_table + ", ROW_NUMBER() OVER (PARTITION BY " + unique_cols_w_table + " ORDER BY current_user_actions.datetime DESC) AS row_num FROM (" + sqlquery_inner + ") AS current_user_actions JOIN " + table + " ON current_user_actions.action_id_num = " + table + ".action_id_num WHERE " + where_criteria

        sqlquery_final = "SELECT " + columns_w_result_table + " FROM (" + sqlquery_inner2 + ") AS result WHERE result.row_num = 1;"

    return sqlquery_final