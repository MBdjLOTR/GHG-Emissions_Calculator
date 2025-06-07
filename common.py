import os
import sqlite3
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_directory(directory: str):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def execute_sql_script(cursor, script_path: str):
    """Execute an SQL script from a file."""
    try:
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"SQL script file not found: {script_path}")

        with open(script_path, 'r') as file:
            sql_script = file.read()

        cursor.executescript(sql_script)
        logging.info(f"Executed SQL script: {script_path}")
    except FileNotFoundError as e:
        st.warning(str(e))
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to execute SQL script: {e}")

def create_database():
    """Initialize the database and execute the schema script."""
    try:
        # Create data directory if it doesn't exist
        data_dir = 'data'
        create_directory(data_dir)

        # Connect to the database
        db_path = os.path.join(data_dir, 'emissions.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the SQL script
        sql_script_path = os.path.join(data_dir, 'emissions.sql')
        execute_sql_script(cursor, sql_script_path)

        # Commit changes and close the connection
        conn.commit()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        st.error(f"An error occurred while creating the database: {e}")
        logging.error(f"Database initialization failed: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logging.error(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed.")