# INFO: This file contains static utility functions
import sqlite3

# NOTE: This should only be called when an connection to the database is already established
# and connection should be closed after this call MANUALLY
def query_next_bid_id(table):
    # Query the database for the next available bid id
    # INFO: This is used to add new bids to the database, as the user can have multiple bids
    conn = sqlite3.connect('Database/Main.db')
    cursor = None
    if table == "bids":
        cursor = conn.execute("SELECT MAX(id) FROM bids")
    elif table == "offers":
        cursor = conn.execute("SELECT MAX(id) FROM offers")

    # Determine the next id to be used as an bid id (row id)
    last_id = cursor.fetchone()[0]
    print("Last id: ", last_id)
    next_id = 1 if last_id is None else last_id + 1
    print("Next id: ", next_id)

    # NOTE: We don't close the connection here, as the caller should close the connection

    return next_id
