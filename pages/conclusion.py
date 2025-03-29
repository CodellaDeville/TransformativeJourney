import streamlit as st
from datetime import datetime
import pandas as pd
import os
import sys

# Add the current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import utilities
from utils.data_storage import initialize_session_state

def show_conclusion():
    """Show the conclusion page after completing all modules."""
    initialize_session_state()
    
    st.markdown("# Conclusion: I Am Conscious, I Am Creating")
    
    st.markdown("""
    ## Congratulations on Completing Your Transformative Journey!
    
    You've completed all five modules and twenty lessons of this program, embracing the process of moving from crisis to creating. This is a significant achievement worthy of celebration and reflection.
    
    ### Your Transformation
    
    Through this journey, you have:
    
    - Defined and understood the Origin of crises and learned how to break free from cycles of suffering
    - Learned how to manifest a new reality by aligning your actions with your authentic core beliefs
    - Elevated your self-talk, self-care, and communication to stay on the path of transformation
    - Trusted your intuition and embraced challenges as opportunities for growth
    - Recognized your role as the creator of your reality
    
    ### Your Journal Entries
    
    Below you'll find a summary of your journey through your journal entries:
    """)
    
    # Display journal statistics
    if len(st.session_state.journal_entries) > 0:
        # Count entries per module
        entries_per_module = {}
        for entry in st.session_state.journal_entries:
            module = entry.get('module', 0)
            if module in entries_per_module:
                entries_per_module[module] += 1
            else:
                entries_per_module[module] = 1
        
        # Show statistics
        st.markdown(f"**Total Journal Entries:** {len(st.session_state.journal_entries)}")
        
        # Create a dataframe for the module breakdown
        module_titles = [
            "Introduction",
            "Learning to Go Beyond Conditioning",
            "Remembering Your Commitment",
            "How Choices Influence Change",
            "Noticing Clarity"
        ]
        
        module_counts = []
        for i in range(1, 6):
            module_counts.append(entries_per_module.get(i, 0))
        
        module_df = pd.DataFrame({
            'Module': module_titles,
            'Entries': module_counts
        })
        
        st.bar_chart(data=module_df, x='Module', y='Entries')
        
        # Display first and last entries to show growth
        st.markdown("### Your Journey From Start to Finish")
        
        # Sort entries by timestamp
        sorted_entries = sorted(st.session_state.journal_entries, key=lambda x: x.get('timestamp', datetime.now()))
        
        if len(sorted_entries) >= 2:
            first_entry = sorted_entries[0]
            last_entry = sorted_entries[-1]
            
            # First entry
            st.markdown("#### Your First Journal Entry")
            st.markdown(f"**Module {first_entry.get('module', 0)}, Lesson {first_entry.get('lesson', 0)}**")
            st.markdown(f"**Prompt:** {first_entry.get('prompt', '')}")
            st.markdown(f"**Your Response:**")
            st.markdown(first_entry.get('content', ''))
            
            # Last entry
            st.markdown("#### Your Most Recent Journal Entry")
            st.markdown(f"**Module {last_entry.get('module', 0)}, Lesson {last_entry.get('lesson', 0)}**")
            st.markdown(f"**Prompt:** {last_entry.get('prompt', '')}")
            st.markdown(f"**Your Response:**")
            st.markdown(last_entry.get('content', ''))
    else:
        st.info("You haven't created any journal entries yet during your journey.")
    
    st.markdown("""
    ### Continue Your Practice
    
    While you've completed the structured modules of this course, your journey of consciousness and creation is ongoing. Consider these practices to continue your growth:
    
    1. **Daily Journaling:** Set aside time each day to reflect on your thoughts, feelings, and experiences
    2. **Regular Review:** Return to your past journal entries monthly to observe patterns and growth
    3. **Community Connection:** Share your journey with others who are on a similar path
    4. **Expanded Learning:** Explore additional resources to deepen your understanding
    
    Remember: You are conscious, and you are creating your reality in every moment.
    """)
    
    # Reset button to start a new journey
    if st.button("Start a New Journey"):
        # Reset to Module 1, Lesson 1
        st.session_state.current_module = 1
        st.session_state.current_lesson = 1
        st.session_state.conclusion_completed = False
        st.session_state.current_page = "dashboard"
        st.rerun()
