import streamlit as st
import logging
import os
from hashlib import sha256

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Environment variables for sensitive data
USER_CREDENTIALS = {
    "ops_manager": os.getenv("OPS_MANAGER_PASSWORD", "admin123"),
    "event_coordinator": os.getenv("EVENT_COORDINATOR_PASSWORD", "admin123"),
    "sustain_consultant": os.getenv("SUSTAIN_CONSULTANT_PASSWORD", "admin123"),
}

# 🧮 Hash Password
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return sha256(password.encode()).hexdigest()

##############################################
# Simple Login with Role Selection (in Sidebar)
##############################################
def simple_login():
    # If already logged in, immediately return the stored user
    if "logged_in_user" in st.session_state:
        return st.session_state.logged_in_user

    st.sidebar.header("Login")

    # Role selection from a drop-down
    role = st.sidebar.selectbox(
        "Select Your Role:",
        options=["Operations Manager", "Event Coordinator", "Sustainability Consultant"]
    )
    # Map role selection to the expected username
    role_mapping = {
        "Operations Manager": "ops_manager",
        "Event Coordinator": "event_coordinator",
        "Sustainability Consultant": "sustain_consultant"
    }

    # Username and password input fields
    username = st.sidebar.text_input("Username:").strip().lower()
    password = st.sidebar.text_input("Password:", type="password")
    login_button = st.sidebar.button("Login", key="login_button")

    if login_button:
        if not username or not password:
            st.sidebar.error("Username and password are required.")
            return None

        expected_username = role_mapping[role]
        expected_password_hash = hash_password(USER_CREDENTIALS.get(expected_username, ""))

        if username == expected_username and hash_password(password) == expected_password_hash:
            st.sidebar.success(f"Logged in as {role}")
            st.session_state.logged_in_user = expected_username
            logging.info(f"User {username} logged in successfully.")
            return st.session_state.logged_in_user
        else:
            st.sidebar.error("Invalid role, username, or password")
            logging.warning(f"Failed login attempt for username: {username}")
            return None
    else:
        return None

##############################################
# Call Function: Handles Login and sets up Sidebar UI after login
##############################################
def call():
    user = simple_login()
    if not user:
        # Instead of halting execution, return False so the caller knows login didn’t succeed.
        return False

    # Post-Login Sidebar UI: Replace login form with welcome message and additional options.
    with st.sidebar:
        st.markdown("---")
        st.title(f"Welcome, {user}")
        st.button("Profile", key="profile_button")
        st.button("Contact Us", key="support_button")
        if st.button("Logout", key="logout_button"):
            if "logged_in_user" in st.session_state:
                del st.session_state.logged_in_user
                logging.info(f"User {user} logged out.")
            # Force a reload using an HTML meta refresh.
            st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
    return True