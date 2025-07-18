import ast
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import plotly.graph_objects as go
import logging
from streamlit_autorefresh import st_autorefresh


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



######################## - GET THE LATEST EVENT DETAILS - #############################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect("data/emissions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

event_name = get_latest_event()



##############################################################################################
def fetch_data(event_name):
    """Fetch emissions data grouped by category."""
    try:
        conn = sqlite3.connect("data/emissions.db")
        query = f"SELECT Category, SUM(Emission) AS TotalEmissions, Timestamp FROM MasterEmissions WHERE Event =? GROUP BY Category LIMIT 100;"
        df = pd.read_sql_query(query, conn, params=(event_name,))
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def fetch_total_data(event_name):
    """Fetch all emissions data."""
    try:
        conn = sqlite3.connect("data/emissions.db")
        query = f"SELECT * FROM MasterEmissions WHERE Event = ? LIMIT 100;"
        df = pd.read_sql_query(query, conn, params=(event_name,))
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching total data: {e}")
        return pd.DataFrame()

def convert_to_list(value):
    """Convert string representations of lists into actual lists."""
    try:
        if isinstance(value, str) and value.startswith("["):
            return ast.literal_eval(value)
        return value
    except Exception as e:
        logging.warning(f"Error converting to list: {e}")
        return value

def process_data(df):
    """Process and transform the emissions data."""
    processed_data = []
    event_cumulative = {}

    # Process only the first 100 rows for testing
    for _, row in df.head(100).iterrows():
        _, SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp = row
        
        # Convert lists
        Description = convert_to_list(Description)
        Quantity = convert_to_list(Quantity)
        Emission = convert_to_list(Emission)

        # If Description is a list, split into multiple rows
        if isinstance(Description, list):
            for desc, qty, emi in zip(Description, Quantity, Emission):
                processed_data.append([SourceTable, Category, Event, desc, qty, Weight, emi, Timestamp])
        else:
            processed_data.append([SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp])
    
    # Convert to DataFrame
    transformed_df = pd.DataFrame(processed_data, columns=["SourceTable", "Category", "Event", "Description", "Quantity", "Weight", "Emission", "Timestamp"])

    # Compute cumulative emissions per event
    for event in transformed_df["Event"].unique():
        event_cumulative[event] = transformed_df[transformed_df["Event"] == event]["Emission"].sum()

    # Add cumulative emissions column
    transformed_df["Cumulative Emission"] = transformed_df["Event"].map(event_cumulative)

    # Assign unique row numbers
    transformed_df.insert(0, "ID", range(1, len(transformed_df) + 1))

    return transformed_df

def display_emissions_summary(df):
    """Display emissions summary by scope."""
    global event_name
    if st.button("🔄 Refresh Data"):
        event_name = get_latest_event()
        st.rerun()
    st.title(f"Event: {event_name}")

    col1, col2, col3 = st.columns(3)
    with col1:
        Scope1_Emission = df[df['Category'] == 'Scope1']['TotalEmissions'].sum()
        Scope2_Emission = df[df['Category'] == 'Scope2']['TotalEmissions'].sum()
        Scope3_Emission = df[df['Category'] == 'Scope3']['TotalEmissions'].sum()

        st.write("Emissions by Category")
        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#824E6A; color:black; text-align:center; 
            max-width: 350px; margin-bottom: 10px  ">
                <h4>Scope 1 Emissions</h4>
                <h2>{Scope1_Emission:.2f} kg CO₂</h2>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#534E82; color:white; text-align:center; 
            max-width: 350px; margin-bottom: 10px ">
                <h4>Scope 2 Emissions</h4>
                <h2>{Scope2_Emission:.2f} kg CO₂</h2>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#824E6A; color:black; text-align:center; 
            max-width: 350px;">
                <h4>Scope 3 Emissions</h4>
                <h2>{Scope3_Emission:.2f} kg CO₂</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("Emissions Breakdown by Scope")
        if not df.empty:
            custom_colors = {
                "Scope1": "#534E82",
                "Scope2": "#824E6A", 
                "Scope3": "white"
            }
            fig = px.pie(
                df, 
                values='TotalEmissions', 
                names='Category', 
                title='Scope 1, 2, and 3 Emissions Distribution',
                color='Category',  # Assign colors by category
                color_discrete_map=custom_colors  # Map categories to colors
            )
            st.plotly_chart(fig, use_container_width=True, key="emissions_pie_chart")
        else:
            st.warning("No records found.")

    with col3:
        st.write("Highest Emissions recorded on")
        day_Scope1_Emission = df[df['Category'] == 'Scope1']['Timestamp'].max()
        day_Scope2_Emission = df[df['Category'] == 'Scope2']['Timestamp'].max()
        day_Scope3_Emission = df[df['Category'] == 'Scope3']['Timestamp'].max()

        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#824E6A; color:black; text-align:center; 
            max-width: 350px; margin-bottom: 10px  ">
                <h4>Scope 1 Emissions</h4>
                <h2>{day_Scope1_Emission}</h2>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#534E82; color:white; text-align:center; 
            max-width: 350px; margin-bottom: 10px ">
                <h4>Scope 2 Emissions</h4>
                <h2>{day_Scope2_Emission}</h2>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding:1px; border-radius:7px; background-color:#824E6A; color:black; text-align:center; 
            max-width: 350px;">
                <h4>Scope 3 Emissions</h4>
                <h2>{day_Scope3_Emission}</h2>
            </div>
        """, unsafe_allow_html=True)

def display_gauge_chart(transformed_df):
    """Display a gauge chart for cumulative emissions."""
    latest_emission = transformed_df["Cumulative Emission"].iloc[-1]  # Get latest emission value

    st.title("Total Emission")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", 
        value=latest_emission, 
        title={'text': "Emission Levels"}, 
        gauge={
            'axis': {'range': [0, transformed_df["Cumulative Emission"].max()]}, 
            'bar': {'color': "#003171"},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 100], 'color': "yellow"},
                {'range': [100, transformed_df["Cumulative Emission"].max()], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': latest_emission
            }
        }
    ))

    st.plotly_chart(fig, use_container_width=True, key="gauge_chart")



def vis():
    """Main function to display the overall analysis."""
    with st.spinner("Loading data..."):
        df = fetch_data(event_name)
        transformed = process_data(fetch_total_data(event_name))

    # Display emissions summary
    display_emissions_summary(df)

    # Transformed data visualizations
    c, co = st.columns(2)
    with c:
        d = st.selectbox("Select", ["SourceTable", "Category", "Event", "Description"])
        fig1 = px.bar(transformed, x=d, y="Emission", title="Emissions by Category")
        fig1.update_traces(marker_color="#5C0071")
        st.plotly_chart(fig1, use_container_width=True, key="f1")
    with co:
        display_gauge_chart(transformed)

    # Emissions trend over time
    col4, col5 = st.columns(2)
    with col4:
        st.write("Emission breakdown")
        category = st.selectbox("Select", ["SourceTable", "Category", "Event", "Description", "Cumulative Emission", "Timestamp"])
        fig1 = px.bar(transformed, x="Cumulative Emission", y=category, title="Emission Trend", color_discrete_sequence=["blue", "green", "purple"])
        st.plotly_chart(fig1, use_container_width=True, key="f2")
    with col5:
        st.subheader("📈 Emissions Over Time")
        fig2 = px.line(transformed, x="Timestamp", y="Cumulative Emission", title="Emission Trend", color_discrete_sequence=["red", "blue", "green", "purple"], markers=True)
        fig2.update_layout(hovermode="x unified", xaxis_title="Timestamp", yaxis_title="Cumulative Emission", legend_title="Legend", hoverlabel=dict(bgcolor="black", font_size=12, font_family="Arial"))
        st.plotly_chart(fig2, use_container_width=True, key="f3")

# Run the app
if __name__ == "__main__":
    vis()