import streamlit as st
import os
import sys
from datetime import datetime

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Your Conscious Journal",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import utilities
from utils.data_storage import initialize_session_state
from pages.dashboard import show_dashboard
from pages.journal import show_journal
from pages.weekly_summary import show_weekly_summary
from pages.settings import show_settings

# App styling
def load_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #0e1117, #1a1f2e);
    }
    .stApp header {
        background-color: rgba(0,0,0,0);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(151, 166, 195, 0.1);
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 10px;
        padding-right: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(151, 166, 195, 0.2);
    }
    .gradient-text {
        background: linear-gradient(90deg, #9c27b0, #ff7043);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Initialize session state
initialize_session_state()

# Application header
st.markdown('<h1 class="gradient-text">Your Conscious Journal</h1>', unsafe_allow_html=True)
st.markdown("#### Transform from Crisis to Creating with Guided Journaling")
st.markdown("---")

# Navigation
def navigation():
    tabs = ["Dashboard", "Journal", "Weekly Summary", "Settings"]
    icons = ["📊", "📝", "📅", "⚙️"]
    
    tab1, tab2, tab3, tab4 = st.tabs([f"{icons[i]} {tabs[i]}" for i in range(4)])
    
    with tab1:
        show_dashboard()
    with tab2:
        show_journal()
    with tab3:
        show_weekly_summary()
    with tab4:
        show_settings()

if __name__ == "__main__":
    navigation()
