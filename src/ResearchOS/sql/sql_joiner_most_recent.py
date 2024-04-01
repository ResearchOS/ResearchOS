import re

def sql_joiner_most_recent(sqlquery: str) -> str:
    """Takes a basic SQL query and returns a query to return the single most recent result per WHERE condition.
    NOTE: this function assumes that the SQL query is in the following format:
    SELECT <columns> FROM <table> WHERE <where_criteria>"""

    # Extract the components of the SQL query
    columns, table, where_criteria_w_tables = extract_sql_components(sqlquery)

    # Define the JOIN query    
    columns_w_table_str = ", ".join([f"{table}.{col}" for col in columns])
    columns_str = ", ".join(columns)
    where_columns = col_names_in_where(sqlquery)
    where_columns_str = ", ".join([f"{table}.{col}" for col in where_columns])
    join_query = f"""SELECT {columns_str} 
                FROM (
                    SELECT {columns_w_table_str}, ROW_NUMBER() OVER (PARTITION BY {where_columns_str} ORDER BY actions.datetime DESC) AS row_num
                    FROM {table}
                    JOIN actions ON {table}.action_id_num = actions.action_id_num
                    WHERE {where_criteria_w_tables}
                    ORDER BY actions.datetime DESC
                ) AS ranked
                WHERE row_num = 1;"""
    return join_query

def sql_joiner(sqlquery: str) -> str:
    """Takes a basic SQL query and returns a JOIN query to order the result, most recent first.
    NOTE: this function assumes that the SQL query is in the following format:
    SELECT <columns> FROM <table> WHERE <where_criteria>
    NOTE 2: this function returns all of the results per WHERE condition. i.e., it does not check for outdated values."""

    # Extract the components of the SQL query
    columns, table, where_criteria = extract_sql_components(sqlquery)

    # Define the JOIN query
    table_cols = ", ".join([f"{table}.{col}" for col in columns])
    join_query = f"SELECT {table_cols} FROM {table} JOIN actions ON {table}_num = actions.action_id_num WHERE {where_criteria} ORDER BY actions.datetime DESC"

    return join_query

def extract_sql_components(sql_statement: str) -> tuple:
    # Define regular expressions for SELECT, FROM, and WHERE clauses
    select_pattern = re.compile(r'\bSELECT\b\s*(.*?)\s*\bFROM\b', re.IGNORECASE | re.DOTALL)
    from_pattern = re.compile(r'\bFROM\b\s*(.*?)\s*(\bWHERE\b|$)', re.IGNORECASE | re.DOTALL)
    where_pattern = re.compile(r'\bWHERE\b\s*(.*)$', re.IGNORECASE | re.DOTALL)

    # Find matches for SELECT, FROM, and WHERE
    select_match = select_pattern.search(sql_statement)
    from_match = from_pattern.search(sql_statement)
    where_match = where_pattern.search(sql_statement)

    # Extract columns, table, and WHERE criteria
    columns = select_match.group(1).strip().split(',') if select_match else None
    columns = [col.strip() for col in columns]
    table = from_match.group(1).strip() if from_match else None
    where_criteria = where_match.group(1).strip() if where_match else None
    table_where_criteria = append_table_to_columns(where_criteria, table)

    return columns, table, table_where_criteria

def append_table_to_columns(where_criteria, table_name = "outerr"):
    if not where_criteria:
        return ""
    # Split the WHERE criteria into individual conditions
    conditions = where_criteria.split(' AND ')

    # Append the table name to each column name
    updated_conditions = []
    for condition in conditions:
        column, rest = condition.split(' ', 1)
        updated_conditions.append(f"{table_name}.{column} {rest}")

    # Join the updated conditions back into a string
    updated_where_criteria = ' AND '.join(updated_conditions)

    return updated_where_criteria

def col_names_in_where(sqlquery: str) -> list:

    # Define a regular expression to match column names in the WHERE clause
    where_pattern = re.compile(r'\bWHERE\b\s*(.+?)\s*$', re.IGNORECASE | re.DOTALL)

    # Find the match for the WHERE clause
    where_match = where_pattern.search(sqlquery)

    if where_match:
        # Extract and split the conditions in the WHERE clause
        where_conditions = where_match.group(1).split(' AND ')

        # Extract column names from each condition
        column_names = [condition.split()[0] for condition in where_conditions]
    
    return column_names