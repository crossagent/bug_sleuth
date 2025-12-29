import sqlite3
import json
import os
import sys

# Path to the sessions database in the mounted directory
DB_PATH = r"adk_data\sessions.db"
# Default to the one user provided, or take arg
SESSION_ID = "bugsleuth-default"
if len(sys.argv) > 1:
    SESSION_ID = sys.argv[1]

def inspect_session():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Determine table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        event_table = next((t for t in tables if 'event' in t.lower()), None)
        
        if not event_table:
            print("No event table found.")
            return

        print(f"Reading from {event_table} for session {SESSION_ID}...")
        
        query = f"SELECT * FROM {event_table} WHERE session_id = ? ORDER BY id ASC"
        cursor.execute(query, (SESSION_ID,))
        rows = cursor.fetchall()
        
        if not rows:
            print("No events found for this session.")
        
        for row in rows:
            # Simple heuristic dump
            for cell in row:
                if isinstance(cell, str) and (cell.strip().startswith('{') or cell.strip().startswith('[')):
                    try:
                        data = json.loads(cell)
                        if isinstance(data, dict):
                            print("-" * 20)
                            print(f"Type: {data.get('type')}")
                            # Check for tool call
                            if 'function_call' in str(data):
                                print(f"TOOL CALL: {data}")
                            elif 'function_response' in str(data):
                                print(f"TOOL RESP: {data}")
                            elif 'text' in str(data):
                                print(f"TEXT: {data.get('content', {}).get('parts', [{}])[0].get('text')}")
                            else:
                                print(f"RAW: {str(data)[:200]}")
                    except:
                        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_session()
