import sqlite3

def fetch_blob_data(db_path, query):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch the data
    blob_data = cursor.fetchone()

    # Close the connection
    conn.close()

<<<<<<< Updated upstream
    return blob_data
=======
    return blob_data
>>>>>>> Stashed changes
