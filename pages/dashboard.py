import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import random

def show_dashboard():
    st.header("Your Journey Dashboard")
    
    # Layout with columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Progress overview
        progress_percentage = get_module_completion_percentage()
        st.subheader("Your Progress")
        
        # Use Streamlit's built-in progress bar instead of Plotly for simplicity
        st.markdown("""
        <style>
        /* Custom styling for progress bar */
        .stProgress > div > div {
            background-image: linear-gradient(to right, #665500, #887300, #aa8c00, #ccaa00, #edc427, #f5dc6b, #f9eaa1, #ffffff);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### Journey Completion: {progress_percentage:.1f}%")
        st.progress(progress_percentage / 100.0)
        
        # Display current module information
        st.markdown(f"### Module {st.session_state.current_module}: {get_module_title(st.session_state.current_module)}")
        st.markdown(f"**Current Lesson:** {st.session_state.current_lesson}. {get_lesson_title(st.session_state.current_module, st.session_state.current_lesson)}")
        
        # Next steps
        st.markdown("#### Next Steps")
        if not st.session_state.journal_entries or datetime.strptime(st.session_state.journal_entries[-1]['date'], '%Y-%m-%d').date() < datetime.now().date():
            st.info("✏️ Complete today's journal entry")
        
        if not st.session_state.journal_entries or len(st.session_state.journal_entries) < 7:
            st.info("🌱 Continue your journaling practice to see growth metrics")
        else:
            # Check if weekly summary is due
            last_entry_date = datetime.strptime(st.session_state.journal_entries[-1]['date'], '%Y-%m-%d')
            days_since_last_entry = (datetime.now() - last_entry_date).days
            
            if days_since_last_entry > 6:
                st.warning("📊 Generate your weekly summary - it's been over a week since your last entry")
    
    with col2:
        # Growth metrics
        st.subheader("Growth Metrics")
        
        metrics = st.session_state.growth_metrics
        
        # Create metrics visualization
        fig = go.Figure()
        
        categories = ["Emotional<br>Awareness", "Coping<br>Strategies", "Resilience"]
        values = [
            metrics['emotional_awareness'],
            metrics['coping_strategies'],
            metrics['resilience']
        ]
        
        # Add bars
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=['#ffcf54', '#ff7f00', '#c54e2c'],  # Gold, orange, rust to match our color scheme
            text=values,
            textposition='auto',
        ))
        
        # Update layout
        fig.update_layout(
            xaxis=dict(
                title="",
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                title="",
                range=[0, 100],
                showgrid=False,
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Removed the Daily check-in functionality as requested
    
    # Bottom section
    st.markdown("---")
    
    # Recent journal entries
    if st.session_state.journal_entries:
        st.subheader("Recent Journal Entries")
        
        # Create dataframe for recent entries
        recent_entries = st.session_state.journal_entries[-3:]  # Last 3 entries
        
        for entry in reversed(recent_entries):
            date_str = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d, %Y')
            module_lesson = f"Module {entry['module']}, Lesson {entry['lesson']}"
            
            expander = st.expander(f"{date_str} - {module_lesson}")
            with expander:
                st.markdown(f"**Prompt:** {entry['prompt']}")
                st.markdown(entry['content'])
                
                # Display sentiment if available
                if 'sentiment' in entry:
                    sentiment = entry['sentiment']
                    st.markdown(f"**Sentiment:** {sentiment['category'].capitalize()}")
                    
                    # Display themes if available
                    if 'themes' in entry and entry['themes']:
                        st.markdown(f"**Themes:** {', '.join(entry['themes'])}")
    else:
        st.info("Start your journaling journey by completing your first entry.")
    
    # Removed quick check-in form as requested

def get_module_completion_percentage():
    """Calculate the percentage of completed modules."""
    if 'completed_lessons' not in st.session_state:
        return 0
    
    total_lessons = 5 * 4  # 5 modules, 4 lessons each
    completed = len(st.session_state.completed_lessons)
    return (completed / total_lessons) * 100

def get_module_title(module_number):
    """Return the title for a module."""
    module_titles = [
        "",  # Module 0 doesn't exist
        "Understanding Cycles and Patterns",
        "Examining Beliefs and Conditioning",
        "Developing Emotional Intelligence",
        "Cultivating Intuition and Synchronicity",
        "Intentional Creation"
    ]
    
    return module_titles[module_number] if 0 < module_number <= len(module_titles) - 1 else "Unknown Module"

def get_lesson_title(module_number, lesson_number):
    """Return the title for a lesson."""
    # Simplified version - in a real app, this would come from a database or content file
    lesson_titles = {
        1: {  # Module 1
            1: "Recognizing Cycles",
            2: "Identifying Crisis Patterns",
            3: "Understanding Creation Mode",
            4: "Breaking Free from Cycles"
        },
        2: {  # Module 2
            1: "The Origin of Beliefs",
            2: "Identifying Limiting Beliefs",
            3: "Challenging Conditioning",
            4: "Creating New Beliefs"
        },
        3: {  # Module 3
            1: "Emotions as Information",
            2: "Working with Difficult Emotions",
            3: "Emotional Energy",
            4: "Emotional Intelligence Practices"
        },
        4: {  # Module 4
            1: "Recognizing Intuitive Signals",
            2: "Working with Synchronicities",
            3: "Deepening Intuitive Practices",
            4: "Co-creating with the Universe"
        },
        5: {  # Module 5
            1: "Clarifying Intentions",
            2: "Aligning Energy with Intentions",
            3: "Taking Inspired Action",
            4: "Living as a Conscious Creator"
        }
    }
    
    if module_number in lesson_titles and lesson_number in lesson_titles[module_number]:
        return lesson_titles[module_number][lesson_number]
    else:
        return "Unknown Lesson"

def get_mood_emoji(mood):
    """Return an emoji based on mood rating."""
    if mood <= 3:
        return "😔"
    elif mood <= 5:
        return "😐"
    elif mood <= 7:
        return "🙂"
    else:
        return "😊"
