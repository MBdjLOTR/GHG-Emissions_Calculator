import sqlite3
import streamlit as st
from modules.sc1_emissions import display_scope1
from visualizations.scope_1Visual import display
import logging



def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect("data/emissions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scope1_page():
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Please login to access the dashboard.")
        return

    st.title("Scope 1 Emissions")
    st.write("Scope 1 emissions are direct emissions from sources owned or controlled by your organization.")

    try:
        event = get_latest_event()
        # Display Scope 1 calculator
        display_scope1(event)

        # Display Scope 1 visualizations
        st.header("Scope 1 Emission Analysis")
        display()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"Error in scope1_page: {e}")