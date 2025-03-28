import streamlit as st
import os
import sys
from datetime import datetime
import base64

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Your Conscious Journal",
    page_icon="generated-icon.png",
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

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(img_path, **css):
    with open(img_path, 'rb') as f:
        img_data = f.read()
    b64 = base64.b64encode(img_data).decode()
    css_str = ' '.join([f'{k}: {v};' for k, v in css.items()])
    return f'<img src="data:image/png;base64,{b64}" style="{css_str}">'

# App styling - load CSS from file
def load_css():
    # First load the CSS file
    with open(os.path.join(os.path.dirname(__file__), 'style.css'), 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Also add some inline CSS for any dynamic elements
    st.markdown("""
    <style>
    .app-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .app-icon {
        width: 50px;
        height: 50px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(255, 206, 84, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Initialize session state
initialize_session_state()

# Get the icon as base64
icon_path = os.path.join(os.path.dirname(__file__), 'generated-icon.png')
icon_html = get_img_with_href(
    icon_path,
    width='50px',
    height='50px',
    border_radius='10px',
    box_shadow='0 0 20px rgba(255, 206, 84, 0.3)'
)

# Application header with icon
st.markdown(
    f"""
    <div class="app-header">
        {icon_html}
        <h1 class="gradient-text">Your Conscious Journal</h1>
    </div>
    <h4>Transform from Crisis to Creating with Guided Journaling</h4>
    <hr>
    """,
    unsafe_allow_html=True
)

# Navigation
def navigation():
    tabs = ["Dashboard", "Journal", "Weekly Summary", "Settings"]
    icons = ["📊", "📝", "📅", "⚙️"]
    
    # Create sidebar navigation
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("📱 App"):
        st.session_state.current_page = "app"
        
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.current_page = "dashboard"
        
    if st.sidebar.button("📝 Journal"):
        st.session_state.current_page = "journal"
        
    if st.sidebar.button("📅 Weekly Summary"):
        st.session_state.current_page = "weekly_summary"
        
    if st.sidebar.button("⚙️ Settings"):
        st.session_state.current_page = "settings"
    
    # Initialize current page if not set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "app"
    
    # Show content based on current page
    if st.session_state.current_page == "app":
        tab1, tab2, tab3, tab4 = st.tabs([f"{icons[i]} {tabs[i]}" for i in range(4)])
        
        with tab1:
            show_dashboard()
        with tab2:
            show_journal()
        with tab3:
            show_weekly_summary()
        with tab4:
            show_settings()
    elif st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "journal":
        show_journal()
    elif st.session_state.current_page == "weekly_summary":
        show_weekly_summary()
    elif st.session_state.current_page == "settings":
        show_settings()

if __name__ == "__main__":
    navigation()
