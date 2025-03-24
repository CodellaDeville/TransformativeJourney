import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def voice_recorder():
    """
    Create a voice recording component for journal entries.
    Returns:
        str: The transcribed text or None if no recording
    """
    # Create a unique key based on timestamp
    key = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Initialize session state for voice input if not exist
    if "voice_input_text" not in st.session_state:
        st.session_state.voice_input_text = ""
    
    # Display microphone icon and visual cues
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #9c27b0, #ff7043); 
                    width: 60px; height: 60px; border-radius: 50%; 
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto;">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" 
                 stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(0,0,0,0.1); padding: 10px; border-radius: 5px;">
            <p style="margin: 0; font-size: 14px;">
                Speech recognition is not available in this environment. 
                Please use the text input below to simulate voice input.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Text area for voice input simulation
    voice_input = st.text_area(
        "Enter your journal entry here (simulating voice input):",
        value=st.session_state.voice_input_text,
        height=150,
        key=f"voice_input_{key}"
    )
    
    # Update session state with current input
    st.session_state.voice_input_text = voice_input
    
    # Add a button to "confirm" the voice input
    if st.button("✓ Use This Text as Voice Input", key=f"use_voice_{key}"):
        st.success("Voice input captured successfully!")
        return voice_input
    
    # Return the current input value if available
    if voice_input:
        return voice_input
    
    return None
