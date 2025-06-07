import streamlit as st
from streamlit_option_menu import option_menu
from app_pages.overview import overview_page
from app_pages.Login import simple_login
from app_pages.sidebar import render_sidebar  # Import the new sidebar component
from visualizations.OverallAnalysis import vis
from common import create_database

# Set page configuration
st.set_page_config(
    page_title="Emission Calculator and Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add some custom CSS to improve the overall look
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2b2b2b;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8cff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
try:
    create_database()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    st.stop()

# Function to check login and render the appropriate sidebar
def handle_authentication():
    user = simple_login()
    if not user:
        return False
    
    # Store the logged in user in session state
    st.session_state.logged_in_user = user
    # Initialize sidebar page to main upon login
    st.session_state.sidebar_page = "main"
        
    return True

# Main application flow
if "logged_in_user" in st.session_state:
    # User is already logged in
    # Initialize sidebar_page if not already set
    if "sidebar_page" not in st.session_state:
        st.session_state.sidebar_page = "main"
        
    render_sidebar(st.session_state.logged_in_user)
    
    # Only show the main dashboard content if we're not in profile or contact pages
    if st.session_state.get("sidebar_page", "main") == "main":
        # Main page title and description
        st.title("Emission Calculator and Analysis Dashboard")
        st.write("This dashboard is designed to calculate and analyze emissions for Scope 1, Scope 2, and Scope 3.")
        
        # Navigation
        pages = {
            "Overview": overview_page,
            "Analysis": vis
        }

        selected = option_menu(
            menu_title="Emissions Calculators",
            menu_icon="cloud",
            options=list(pages.keys()),
            orientation="horizontal",
        )

        # Route to the selected page
        if selected in pages:
            with st.spinner(f"Loading {selected}..."):
                pages[selected]()
else:
    # User is not logged in, show login form
    if handle_authentication():
        # Force a rerun to show dashboard after successful login
        st.rerun()
    else:
        st.stop()