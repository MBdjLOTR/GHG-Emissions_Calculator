import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_electricity_data():
    """Fetch electricity emissions data from the database."""
    try:
        conn = sqlite3.connect('data/emissions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT event, Usage, Value, Emission, Timestamp FROM ElectricityEmissions")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching electricity data: {e}")
        return []

def fetch_hvac_data():
    """Fetch HVAC emissions data from the database."""
    try:
        conn = sqlite3.connect('data/emissions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT event, Refrigerant, MassLeak, Emission, Timestamp FROM HVACEmissions")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching HVAC data: {e}")
        return []

def display_electricity_analytics(df):
    """Display descriptive analytics for electricity emissions."""
    total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
    avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
    max_emission = round(df["Emission (kg CO₂)"].max(), 3)
    min_emission = round(df["Emission (kg CO₂)"].min(), 3)
    day_with_max_emission = df["Timestamp"].max()
    no_of_emissions = df["Emission (kg CO₂)"].count()

    st.subheader("Descriptive Analytics")
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
        st.metric(label='Day with Highest Emission', value=day_with_max_emission, delta_color="off")

def display_hvac_analytics(df):
    """Display descriptive analytics for HVAC emissions."""
    total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
    avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
    max_emission = round(df["Emission (kg CO₂)"].max(), 3)
    min_emission = round(df["Emission (kg CO₂)"].min(), 3)
    date_with_high_em = df["Timestamp"].max()
    no_of_emissions = df["Emission (kg CO₂)"].count()

    st.subheader("Descriptive Analytics")
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
        st.metric(label='Day with Highest Emission', value=date_with_high_em, delta_color="off")

def electricity_visual():
    """Display electricity and HVAC emissions visualizations."""
    tab1, tab2 = st.tabs(["Electricity Emissions", "HVAC Emissions"])

    with tab1:
        st.subheader("⚡ Electricity Emission Data")
        electricity_data = fetch_electricity_data()

        if electricity_data:
            df = pd.DataFrame(electricity_data, columns=["event", "Usage", "Consumption (kWh)", "Emission (kg CO₂)", "Timestamp"])
            dataframe = dataframe_explorer(df)
            st.dataframe(dataframe, use_container_width=True)

            display_electricity_analytics(df)

            st.write("Breakdown Between Consumption and Emission")
            st.area_chart(df[["Consumption (kWh)", "Emission (kg CO₂)"]])

            d1, d2 = st.tabs(["Pie Chart", "Bar Plot"])
            with d1:
                fig = px.pie(df, names='Usage', values="Emission (kg CO₂)", color="Consumption (kWh)", title="Emissions Breakdown", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            with d2:
                fig = px.bar(df, x="Usage", y="Emission (kg CO₂)", text="Emission (kg CO₂)", color="Consumption (kWh)", color_continuous_scale="blues", title="Emission Distribution")
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(xaxis=dict(tickmode="linear"), plot_bgcolor="white", font=dict(size=14))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No electricity emission records found.")

    with tab2:
        st.subheader("❄️ HVAC Emission Data")
        hvac_data = fetch_hvac_data()

        if hvac_data:
            df = pd.DataFrame(hvac_data, columns=["event", "Refrigerant", "Mass Leak (kg)", "Emission (kg CO₂)", "Timestamp"])
            dataframe = dataframe_explorer(df)
            st.dataframe(dataframe, use_container_width=True)

            display_hvac_analytics(df)

            st.write("Breakdown between Mass Leak & Emission by Refrigerant")
            fig = px.scatter_3d(df, x="event", y="Emission (kg CO₂)", z="Mass Leak (kg)")
            fig.update_layout(width=700, height=500)
            st.plotly_chart(fig, use_container_width=True)

            d1, d2 = st.tabs(["Pie Chart", "Bar Plot"])
            with d1:
                fig = px.pie(df, names='Refrigerant', values="Emission (kg CO₂)", color="Mass Leak (kg)", title="Emissions Breakdown", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            with d2:
                fig = px.bar(df, x="Refrigerant", y="Emission (kg CO₂)", text="Emission (kg CO₂)", color="Mass Leak (kg)", color_continuous_scale="blues", title="Emission Distribution")
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(xaxis=dict(tickmode="linear"), plot_bgcolor="white", font=dict(size=14))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No HVAC emission records found.")
