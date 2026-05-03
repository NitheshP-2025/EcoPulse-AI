import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'ecopulse.db'

def init_db():
    """Initializes the SQLite database with the necessary schema."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Adding 'status' to track lifecycle (Pending -> Resolved)
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  location TEXT,
                  category TEXT,
                  description TEXT,
                  priority REAL,
                  sentiment_score REAL,
                  status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

def save_report(data_dict):
    """Inserts a new report from the frontend into the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO reports 
                 (timestamp, location, category, description, priority, sentiment_score, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
              (data_dict.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
               data_dict['location'], 
               data_dict['category'], 
               data_dict['description'], 
               data_dict['priority'], 
               data_dict['sentiment_score'],
               data_dict.get('status', 'Pending')))
    conn.commit()
    conn.close()

def load_reports():
    """Retrieves all reports for display in the Streamlit dashboard."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM reports ORDER BY priority DESC", conn)
    conn.close()
    return df

def update_report_status(report_id, new_status):
    """Allows Admin to update the status of a specific report."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()

def migrate_old_csv(csv_path='campus_reports.csv'):
    """Helper to move your existing CSV data into the new SQL database."""
    try:
        old_df = pd.read_csv(csv_path)
        # Ensure the 'status' column exists in the migration
        if 'status' not in old_df.columns:
            old_df['status'] = 'Pending'
            
        conn = sqlite3.connect(DB_NAME)
        old_df.to_sql('reports', conn, if_exists='append', index=False)
        conn.close()
        print("Migration complete: CSV data is now in SQL.")
    except FileNotFoundError:
        print("No old CSV found. Starting with a fresh database.")
def delete_report(report_id):
    """Permanently removes a report from the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
