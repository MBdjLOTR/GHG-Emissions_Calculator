import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import json
import logging
from streamlit_extras.dataframe_explorer import dataframe_explorer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_data():
    """Fetch and process data from the Scope1 table."""
    try:
        conn = sqlite3.connect("data/emissions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, event, fuels, consumptions, emissions, total_emission, Timestamp FROM Scope1")
        data = cursor.fetchall()
        conn.close()

        # Process JSON fields
        processed_data = []
        for row in data:
            id_, event, fuels_json, consumptions_json, emissions_json, total_emission, timestamp = row
            fuels = json.loads(fuels_json)  # Convert JSON string to list
            consumptions = json.loads(consumptions_json)
            emissions = json.loads(emissions_json)

            for fuel, consumption, emission in zip(fuels, consumptions, emissions):
                processed_data.append([id_, event, fuel, consumption, emission, total_emission, timestamp])

        return processed_data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching Scope1 data: {e}")
        return []

def display_descriptive_analytics(df, column):
    """Display descriptive analytics for a given column."""
    total_val = round(df[column].sum(), 3)
    avg_val = round(df[column].mean(), 3)
    max_val = round(df[column].max(), 3)
    min_val = round(df[column].min(), 3)
    count_val = df[column].count()

    st.subheader("Descriptive Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f'Total {column}', value=total_val, delta_color="off")
    with col2:
        st.metric(label=f'Average {column}', value=avg_val, delta_color="off")
    with col3:
        st.metric(label=f'Highest Recorded {column}', value=max_val, delta_color="off")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label=f'Lowest Recorded {column}', value=min_val, delta_color="off")
    with col5:
        st.metric(label=f'Number of {column} Records', value=count_val, delta_color="off")
    with col6:
        max_emission_day = df.loc[df[column].idxmax(), "Timestamp"]
        st.metric(label=f"Highest {column} Recorded On", value=max_emission_day, delta_color="off")

def display():
    """Display Scope 1 emissions visualizations."""
    st.title("Scope-1 Emissions Data")

    # Fetch and prepare data
    data = fetch_data()
    if not data:
        st.warning("No data found.")
        return

    df = pd.DataFrame(data, columns=["Id", "Event", "Fuel Type", "Consumption (kWh)", "Emission (kg CO₂)", "Total Emission (kg CO₂)", "Timestamp"])

    # Interactive data explorer
    st.subheader("Data Explorer")
    dataframe = dataframe_explorer(df)
    st.dataframe(dataframe, use_container_width=True)

    # Toggle visualization
    st.write(" ")
    visualize = st.toggle("Visualize the data using Pie chart?")

    if visualize:
        fig = px.pie(df, names="Event", values="Total Emission (kg CO₂)",
                     title="Emission Distribution by Event", hole=0.3)
    else:
        fig = px.line(df, x="Event", y="Total Emission (kg CO₂)", 
                      markers=True, title="Emission Trend by Event")

    st.plotly_chart(fig, use_container_width=True)

    # Descriptive analysis
    display_descriptive_analytics(df, "Emission (kg CO₂)")

    # Select plot type
    st.subheader("Custom Visualization")
    plot_type = st.selectbox("Select the plot type:", ["Pie Chart", "Scatter", "Bar Plot"])
    column = st.selectbox("Select the column for analysis:", ["Consumption (kWh)", "Emission (kg CO₂)"])

    if plot_type == "Pie Chart":
        fig = px.pie(df, values=column, names="Fuel Type", title=f"{column} Breakdown", hole=0.3)
    elif plot_type == "Scatter":
        fig = px.scatter(df, x="Fuel Type", y=column, color="Emission (kg CO₂)",
                         title=f"{column} Distribution", template="plotly_dark")
    elif plot_type == "Bar Plot":
        fig = px.bar(df, x="Fuel Type", y=column, color="Fuel Type", title=f"{column} Bar Chart")

    st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    display()