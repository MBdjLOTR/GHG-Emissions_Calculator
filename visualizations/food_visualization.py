import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from streamlit_extras.dataframe_explorer import dataframe_explorer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_food_data():
    """Fetch food emissions data from the database."""
    try:
        conn = sqlite3.connect("data/emissions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT event, food_items, quantity, emission, total_emission, Timestamp FROM FoodItemsEmissions")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching food data: {e}")
        return []

def process_food_data(data):
    """Process food data to extract individual food items."""
    processed_data = []
    for row in data:
        event, food_items, quantity, emission, total_emission, timestamp = row
        food_items = json.loads(food_items)  # Convert JSON string to list
        quantities = json.loads(quantity)
        emissions = json.loads(emission)

        for food_item, quantity, emission in zip(food_items, quantities, emissions):
            processed_data.append([event, food_item, quantity, emission, total_emission, timestamp])

    return processed_data

def fetch_food_data1():
    """Fetch food emissions data for curries from the database."""
    try:
        conn = sqlite3.connect("data/emissions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT event, FoodItem, Quantity, Emission, Timestamp FROM FoodItems")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching food data: {e}")
        return []

def display_descriptive_analytics(df):
    """Display descriptive analytics for food emissions."""
    df["Emission (kg CO₂)"] = pd.to_numeric(df["Emission (kg CO₂)"], errors="coerce")

    total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
    avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
    max_emission = round(df["Emission (kg CO₂)"].max(), 3)
    min_emission = round(df["Emission (kg CO₂)"].min(), 3)
    no_of_emissions = round(df["Emission (kg CO₂)"].count(), 3)
    day_with_highest_emission = df.loc[df["Emission (kg CO₂)"].idxmax(), "Timestamp"]

    st.subheader("Descriptive Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Total Emission (kg CO₂)', value=total_emission, delta_color="off")
    with col2:
        st.metric(label='Average Emission (kg CO₂)', value=avg_emission, delta_color="off")
    with col3:
        st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission, delta_color="off")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission, delta_color="off")
    with col5:
        st.metric(label='Number of Emissions Recorded', value=no_of_emissions, delta_color="off")
    with col6:
        st.metric(label='Day with Highest Emission', value=day_with_highest_emission, delta_color="off")

def food_visual():
    """Display food emissions visualizations."""
    table = st.selectbox("Select The Table:", ["Food Items", "Food Curries"])
    st.subheader("🍎 Food Emission Data")

    if table == "Food Items":
        data = fetch_food_data()
        processed = process_food_data(data)
        df = pd.DataFrame(processed, columns=["event", "FoodItem", "Quantity", "Emission (kg CO₂)", "Total Emission", "Timestamp"])
        dataframe = dataframe_explorer(df)
        st.dataframe(dataframe, use_container_width=True)

        st.subheader("Emission Breakdown by Events")
        fig = px.scatter(dataframe, x="event", y="Total Emission", color_continuous_scale="Blues", template="plotly_dark", size_max=15)
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")))
        st.plotly_chart(fig, use_container_width=True)
    else:
        data = fetch_food_data1()
        df = pd.DataFrame(data, columns=["event", "FoodItem", "Quantity", "Emission (kg CO₂)", "Timestamp"])
        dataframe = dataframe_explorer(df)
        st.dataframe(dataframe, use_container_width=True)

        st.subheader("Emission Breakdown by Events")
        fig = px.scatter(dataframe, x="event", y="Emission (kg CO₂)", color_continuous_scale="Blues", template="plotly_dark", size_max=15)
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")))
        st.plotly_chart(fig, use_container_width=True)

    display_descriptive_analytics(df)

    st.subheader("Quantity of Food Items")
    fig = px.scatter(df, x="Quantity", y="FoodItem", color_continuous_scale="Blues", template="plotly_dark", size_max=15)
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")), hovertemplate="<b>Quantity:</b> %{x}")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Emissions")
    cat = st.selectbox("Select Visualization:", ["Pie Chart", "Scatter Plot", "Bar Plot", "Line Graph"])

    if cat == "Pie Chart":
        fig = px.pie(df, names='FoodItem', values="Emission (kg CO₂)", title="Emissions Breakdown", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    elif cat == "Scatter Plot":
        fig = px.scatter(df, x="FoodItem", y="Emission (kg CO₂)", title="Emission Distribution", color='Emission (kg CO₂)', color_continuous_scale="Blues", template="plotly_dark", size_max=15)
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")), hovertemplate="<b>Quantity:</b> %{x} kg<br><b>CO₂ Emission:</b> %{y} kg")
        st.plotly_chart(fig, use_container_width=True)
    elif cat == "Bar Plot":
        fig = px.bar(df, x="FoodItem", y="Emission (kg CO₂)", text="Emission (kg CO₂)", color="Emission (kg CO₂)", color_continuous_scale="blues", labels={"FoodItem": "Food Item", "Emission (kg CO₂)": "CO₂ Emission (kg)"}, title="Emission Distribution")
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(xaxis=dict(tickmode="linear"), plot_bgcolor="white", font=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    elif cat == "Line Graph":
        fig = px.line(df, x="Emission (kg CO₂)", y="FoodItem", markers=True, title="Emission Trend by Food Item")
        st.plotly_chart(fig, use_container_width=True)