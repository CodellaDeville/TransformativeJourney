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

# App styling
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Satisfy&family=Montserrat:wght@400;700&display=swap');
    
    .main {
        background-color: #913923;
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
        background-color: rgba(255, 206, 84, 0.1);
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 10px;
        padding-right: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 206, 84, 0.3);
    }
    .gradient-text {
        font-family: 'Satisfy', cursive;
        background: linear-gradient(90deg, #ffcf54, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
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
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }
    h4 {
        color: #ffcf54;
    }
    /* Button styling */
    .stButton button {
        background: linear-gradient(to right, #ffd700, #ff7f00, #c54e2c);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 30px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(to right, #ffec00, #ff9500, #e85d35);
        box-shadow: 0 0 15px rgba(255, 206, 84, 0.7);
        transform: translateY(-2px);
    }
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: rgba(145, 57, 35, 0.8);
    }
    .stSidebar button {
        background: linear-gradient(to right, #ffd700, #ff7f00, #c54e2c);
        color: white;
        border: none;
        border-radius: 30px;
        text-align: left;
        width: 100%;
        margin: 5px 0;
        transition: all 0.3s;
    }
    .stSidebar button:hover {
        background: linear-gradient(to right, #ffec00, #ff9500, #e85d35);
        box-shadow: 0 0 15px rgba(255, 206, 84, 0.7);
        transform: translateY(-2px);
    }
    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
        border-radius: 8px;
        border: 1px solid rgba(255, 206, 84, 0.3);
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
