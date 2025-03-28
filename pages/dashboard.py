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
        
        # Create progress bar with custom styling
        progress_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': "Journey Completion",
                'font': {'size': 16, 'color': '#ffcf54'}
            },
            number={'font': {'color': '#ffffff'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "rgba(255, 207, 84, 0.5)"},
                'bar': {'color': "rgba(0,0,0,0)"},  # Make default bar transparent
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    # Create a multi-step gradient for the bar
                    {'range': [0, 5], 'color': "#665500"},                 # Darkest yellow
                    {'range': [5, 15], 'color': "#887300"},                # Dark yellow
                    {'range': [15, 30], 'color': "#aa8c00"},               # Medium dark yellow
                    {'range': [30, 45], 'color': "#ccaa00"},               # Medium yellow
                    {'range': [45, 60], 'color': "#edc427"},               # Medium light yellow
                    {'range': [60, 75], 'color': "#f5dc6b"},               # Light yellow
                    {'range': [75, 90], 'color': "#f9eaa1"},               # Very light yellow
                    {'range': [90, 100], 'color': "#ffffff"}               # White
                ],
                # Add a custom shape to create a smooth gradient overlay
                'shape': 'bullet'
            }
        ))
        
        # Add a custom shape to simulate a gradient
        progress_fig.add_trace(go.Scatter(
            x=[0, progress_percentage/100],
            y=[0, 0],
            mode='lines',
            line=dict(
                color='rgba(0,0,0,0)',
                width=20,
            ),
            fill='tozeroy',
            fillcolor=f'linear-gradient(90deg, #665500, #ffffff)',
            hoverinfo='none',
            showlegend=False
        ))
        
        progress_fig.update_layout(
            height=300,  # Increased height for better spacing
            margin=dict(l=20, r=20, t=80, b=20),  # Increased top margin
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#ffcf54",
                size=14
            )
        )
        
        st.plotly_chart(progress_fig, use_container_width=True)
        
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
            marker_color=['#9c27b0', '#ff7043', '#3f51b5'],
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
