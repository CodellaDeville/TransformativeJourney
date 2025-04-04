import streamlit as st
import json
from datetime import datetime
from utils.data_storage import export_user_data, import_user_data

def show_settings():
    st.header("Settings")
    
    # User preferences section
    st.subheader("User Preferences")
    
    # User name
    user_name = st.text_input("Your Name", st.session_state.user_name)
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        st.success("Name updated!")
    
    # Voice input toggle
    voice_col1, voice_col2 = st.columns([1, 2])
    with voice_col1:
        voice_input = st.toggle("Enable Voice Input", value=False, disabled=True)
    with voice_col2:
        st.info("🎙️ Voice input feature will be enabled in a future update")
    
    # Email notifications (for future implementation)
    email_notifications = st.toggle("Email Notifications", st.session_state.email_notifications)
    if email_notifications != st.session_state.email_notifications:
        st.session_state.email_notifications = email_notifications
        if email_notifications:
            st.info("This feature will be enabled in a future update.")
        st.success("Notification preferences updated!")
    
    # Data management section
    st.markdown("---")
    st.subheader("Data Management")
    
    # Export data
    if st.button("Export Your Data"):
        data_json = export_user_data()
        
        # Create a download link
        filename = f"conscious_journal_data_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Convert JSON to bytes and create a download link
        b64 = base64_encode_data(data_json)
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Download JSON</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        st.success("Data exported successfully!")
    
    # Import data
    st.markdown("### Import Data")
    st.info("""
    This feature allows you to restore your journal entries and settings from a previously exported file.
    The file should be a JSON file that was exported from this app.
    """)
    
    uploaded_file = st.file_uploader(
        "Upload your journal data JSON file",
        type=["json"],
        help="Select a JSON file that was previously exported from Your Conscious Journal"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file contents
            file_contents = uploaded_file.getvalue().decode()
            
            # Validate JSON structure before importing
            try:
                json.loads(file_contents)
                
                # Show preview of data
                st.success("File validated successfully!")
                
                # Confirm import
                if st.button("Import Data"):
                    success = import_user_data(file_contents)
                    
                    if success:
                        st.success("✅ Data imported successfully! The page will refresh in a moment...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import data. Please ensure this is a valid export file.")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please upload a file that was exported from Your Conscious Journal.")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("💡 Try downloading a fresh export and importing that file instead.")
    
    # Reset data
    st.markdown("---")
    st.subheader("Reset Data")
    st.warning("This will delete all your journal entries and reset your progress.")
    
    # Two-step confirmation for data reset
    if st.button("Reset All Data"):
        st.session_state.confirm_reset = True
    
    if st.session_state.get("confirm_reset", False):
        st.error("Are you sure? This action cannot be undone.")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("No, Cancel"):
                st.session_state.confirm_reset = False
                st.rerun()
        
        with col2:
            if st.button("Yes, Reset Data"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key not in ["user_name", "dark_mode", "voice_input_enabled", "email_notifications"]:
                        del st.session_state[key]
                
                # Reinitialize session state
                from utils.data_storage import initialize_session_state
                initialize_session_state()
                
                st.session_state.confirm_reset = False
                st.success("Data reset successfully!")
                st.rerun()
    
    # About section
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    **Your Conscious Journal** is a transformational coaching application designed to help you move from crisis to creating through guided journaling and emotional intelligence development.
    
    Version 1.0.0
    
    Based on the "From Crisis to Creating" coaching methodology.
    """)

def base64_encode_data(data_string):
    """
    Encode a string as base64.
    
    Args:
        data_string (str): The string to encode
        
    Returns:
        str: The base64-encoded string
    """
    import base64
    return base64.b64encode(data_string.encode()).decode()
