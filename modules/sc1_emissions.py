import streamlit as st
import sqlite3
import json
import logging
from typing import List, Dict


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Emission factors dictionary
EMISSION_FACTORS = {
    "Diesel": 0.2496,
    "Coal": 0.3230,
    "Petroleum Gas (LPG)": 0.2106,
    "Electricity": 0.82,
}

# 🧮 Calculate Emission
def calculate_emission(fuel_type: str, consumption: float) -> float:
    """Calculate emission based on fuel type and consumption."""
    return consumption * EMISSION_FACTORS.get(fuel_type, 0)

# 📌 Insert Scope 1 Data into DB
def insert_scope1_data(event: str, fuels: List[str], consumptions: List[float], emissions: List[float], total_emission: float):
    """Insert multiple fuel entries into the database."""
    try:
        with sqlite3.connect("data/emissions.db") as conn:
            c = conn.cursor()

            # Convert lists to JSON strings
            fuels_json = json.dumps(fuels)
            consumptions_json = json.dumps(consumptions)
            emissions_json = json.dumps(emissions)

            c.execute("""
                INSERT INTO Scope1 (event, fuels, consumptions, emissions, total_emission)
                VALUES (?, ?, ?, ?, ?)""",
                (event, fuels_json, consumptions_json, emissions_json, total_emission)
            )

            conn.commit()
            st.success("Emission data saved successfully!")
            logging.info(f"Inserted Scope 1 data for event: {event}")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Failed to insert Scope 1 data: {e}")

# 🏭 Display Scope 1 Calculator
def display_scope1(event):
    """Display the Scope 1 emissions calculator."""
    st.title("Scope 1 Emissions Calculator")
    st.write("Scope 1 emissions refer to direct greenhouse gas (GHG) emissions from sources that are owned or controlled by an organization.")
    
    # Initialize session state variables
    if "fuel_entries" not in st.session_state:
        st.session_state.fuel_entries = [{"id": 0, "fuel_type": "Diesel", "consumption": 0.0}]

    total_emission = 0  # Reset total emissions each time
    fuels, consumptions, emissions = [], [], []

    # Display fuel entries using columns
    for entry in st.session_state.fuel_entries:
        index = entry["id"]
        cols = st.columns([3, 3, 2])  # Set column widths

        with cols[0]:  # Fuel Type Selection
            fuel_type = st.selectbox(
                f"Fuel Type {index + 1}:", EMISSION_FACTORS.keys(),
                key=f"fuel_{index}", index=list(EMISSION_FACTORS.keys()).index(entry["fuel_type"])
            )

        with cols[1]:  # Consumption Input
            consumption = st.number_input(
                f"Consumption {index + 1} (kWh):",
                min_value=0.0, step=0.1, value=entry["consumption"],
                key=f"consumption_{index}"
            )

        with cols[2]:  # Remove Entry Button
            if st.button("Remove", key=f"remove_{index}"):
                st.session_state.fuel_entries = [e for e in st.session_state.fuel_entries if e["id"] != index]
                st.rerun()

        emission = calculate_emission(fuel_type, consumption)
        total_emission += emission

        # Store values for database insertion
        fuels.append(fuel_type)
        consumptions.append(consumption)
        emissions.append(emission)

    # Display total emissions
    st.subheader(f"Total Emission: {total_emission:.3f} kg CO₂")

    # Save all fuel data
    if st.button("Save Emission Data"):
        if not event:
            st.warning("Event name is not set. Please go to the Overview page and save an event first.")

        else:
            insert_scope1_data(event, fuels, consumptions, emissions, total_emission)

    # Add another fuel entry
    if st.button("Add Another Fuel"):
        new_id = max([e["id"] for e in st.session_state.fuel_entries], default=-1) + 1
        st.session_state.fuel_entries.append({"id": new_id, "fuel_type": "Diesel", "consumption": 0.0})
        st.rerun()