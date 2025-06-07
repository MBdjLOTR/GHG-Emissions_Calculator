import sqlite3
import streamlit as st
from modules.electricity import show_electricity_hvac_calculator
from visualizations.electricity_visualization import electricity_visual
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect("data/emissions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

def scope2_page():
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Please login to access the dashboard.")
        return

    st.title("Scope 2 Emissions")
    st.write("Scope 2 emissions are indirect emissions from the generation of purchased electricity, heating, or cooling.")

    try:
        # Display Scope 2 calculator
        st.subheader("Scope 2 Calculator")
        event = get_latest_event()
        show_electricity_hvac_calculator(event)

        # Display Scope 2 visualizations
        st.header("Scope 2 Emission Analysis")
        electricity_visual()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"Error in scope2_page: {e}")