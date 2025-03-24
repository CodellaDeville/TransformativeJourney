import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.pdf_generator import PDFGenerator
import base64

def show_weekly_summary():
    st.header("Weekly Summary")
    
    # Initialize PDF generator
    pdf_generator = PDFGenerator()
    
    # Check if there are journal entries
    if not st.session_state.journal_entries:
        st.warning("You haven't created any journal entries yet. Start your journaling practice to see your weekly summary.")
        return
    
    # Date selection
    st.subheader("Select Period for Summary")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        # Default start date is 7 days ago
        default_start = datetime.now() - timedelta(days=7)
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            max_value=datetime.now()
        )
    
    with col2:
        # Default end date is today
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            min_value=start_date,
            max_value=datetime.now()
        )
    
    # Filter entries for the selected period
    entries = get_entries_for_period(start_date, end_date)
    
    if not entries:
        st.info(f"No journal entries found between {start_date.strftime('%b %d, %Y')} and {end_date.strftime('%b %d, %Y')}.")
        return
    
    # Display summary metrics
    st.markdown("---")
    st.subheader("Activity Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Entries", len(entries))
    
    with col2:
        total_words = sum(len(entry['content'].split()) for entry in entries)
        st.metric("Total Words", total_words)
    
    with col3:
        avg_words = round(total_words / len(entries))
        st.metric("Avg. Words per Entry", avg_words)
    
    # Emotional trends visualization
    st.markdown("---")
    st.subheader("Emotional Trends")
    
    # Prepare data for visualization
    emotion_data = []
    
    for entry in entries:
        date = datetime.strptime(entry['date'], '%Y-%m-%d')
        
        if 'sentiment' in entry and 'emotions' in entry['sentiment']:
            emotions = entry['sentiment']['emotions']
            
            for emotion, value in emotions.items():
                emotion_data.append({
                    'Date': date,
                    'Emotion': emotion.capitalize(),
                    'Value': value
                })
    
    if emotion_data:
        # Create DataFrame for plotting
        df = pd.DataFrame(emotion_data)
        
        # Create line chart of emotions over time
        fig = px.line(
            df,
            x='Date',
            y='Value',
            color='Emotion',
            title="Emotional Content Over Time",
            labels={'Value': 'Intensity (%)', 'Date': ''},
            line_shape='spline',
            color_discrete_map={
                'Joy': '#FFC107',
                'Sadness': '#2196F3',
                'Anger': '#F44336',
                'Fear': '#9C27B0',
                'Hope': '#4CAF50'
            }
        )
        
        fig.update_layout(
            legend_title_text='',
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient emotional data for the selected period to visualize trends.")
    
    # Journal entries with insights
    st.markdown("---")
    st.subheader("Journal Entries & Insights")
    
    for entry in entries:
        date_str = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%B %d, %Y')
        module_lesson = f"Module {entry['module']}, Lesson {entry['lesson']}"
        
        expander = st.expander(f"{date_str} - {module_lesson}")
        with expander:
            st.markdown(f"**Prompt:** {entry['prompt']}")
            st.markdown(entry['content'])
            
            # Display sentiment if available
            if 'sentiment' in entry:
                sentiment = entry['sentiment']
                st.markdown(f"**Sentiment:** {sentiment['category'].capitalize()}")
                
                # Display emotions if available
                if 'emotions' in sentiment:
                    emotions = sentiment['emotions']
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                    st.markdown(f"**Dominant emotion:** {dominant_emotion.capitalize()}")
                
                # Display themes if available
                if 'themes' in entry and entry['themes']:
                    st.markdown(f"**Themes:** {', '.join(entry['themes'])}")
    
    # Growth highlights and recommendations
    st.markdown("---")
    st.subheader("Growth Highlights & Recommendations")
    
    # Generate growth highlights based on journal entries
    if entries:
        # Calculate emotional trends
        emotion_averages = {}
        sentiment_categories = {"positive": 0, "negative": 0, "neutral": 0}
        entry_count = len(entries)
        
        for entry in entries:
            # Track sentiment categories
            if 'sentiment' in entry and 'category' in entry['sentiment']:
                category = entry['sentiment']['category']
                sentiment_categories[category] += 1
            
            # Track emotion intensities
            if 'sentiment' in entry and 'emotions' in entry['sentiment']:
                emotions = entry['sentiment']['emotions']
                
                for emotion, value in emotions.items():
                    if emotion in emotion_averages:
                        emotion_averages[emotion].append(value)
                    else:
                        emotion_averages[emotion] = [value]
        
        # Calculate averages for emotions
        for emotion, values in emotion_averages.items():
            emotion_averages[emotion] = sum(values) / len(values)
        
        # Calculate percentages for sentiment categories
        sentiment_percentages = {
            category: (count / entry_count) * 100 
            for category, count in sentiment_categories.items() 
            if count > 0
        }
        
        # Display sentiment trend percentages
        st.markdown("### Emotional Trend Analysis")
        
        # Create a horizontal bar chart for sentiment categories
        if sentiment_percentages:
            categories = list(sentiment_percentages.keys())
            percentages = list(sentiment_percentages.values())
            
            # Sort by percentage (highest first)
            sorted_indices = sorted(range(len(percentages)), key=lambda i: percentages[i], reverse=True)
            sorted_categories = [categories[i].capitalize() for i in sorted_indices]
            sorted_percentages = [percentages[i] for i in sorted_indices]
            
            # Color mapping
            color_map = {
                "Positive": "#4CAF50",  # Green
                "Negative": "#F44336",  # Red
                "Neutral": "#2196F3"    # Blue
            }
            
            colors = [color_map[cat] for cat in sorted_categories]
            
            # Create bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sorted_percentages,
                y=sorted_categories,
                orientation='h',
                marker_color=colors,
                text=[f"{p:.1f}%" for p in sorted_percentages],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Overall Mood Distribution in Journal Entries",
                xaxis_title="Percentage of Entries",
                yaxis_title="Mood Category",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=250,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    range=[0, 100],
                    ticksuffix="%"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add interpretation based on dominant sentiment
            dominant_sentiment = sorted_categories[0] if sorted_categories else "Neutral"
            
            if dominant_sentiment == "Positive":
                st.markdown("📈 **Mood Insight:** Your journal entries show a predominantly positive outlook, which suggests you're in a creative or resourceful state of mind. This is an excellent time to set goals and build on your momentum.")
            elif dominant_sentiment == "Negative":
                st.markdown("🔍 **Mood Insight:** Your entries reflect more challenging emotions, which often indicate important areas for growth and healing. These feelings can provide valuable information about your needs and values.")
            else:  # Neutral
                st.markdown("⚖️ **Mood Insight:** Your entries show a balanced emotional state, which can indicate either emotional stability or possibly some emotional detachment. This could be a good time for objective reflection.")
        
        # Emotional insight based on specific emotions
        if emotion_averages:
            st.markdown("### Specific Emotional Patterns")
            
            # Format emotion averages as percentages and sort
            emotion_percentages = {k.capitalize(): v for k, v in emotion_averages.items()}
            sorted_emotions = sorted(emotion_percentages.items(), key=lambda x: x[1], reverse=True)
            
            # Display top emotions
            for emotion, value in sorted_emotions[:3]:
                if value > 0:
                    st.markdown(f"- **{emotion}:** {value:.1f}% intensity")
            
            # Find dominant emotion
            dominant_emotion = sorted_emotions[0][0].lower() if sorted_emotions else None
            
            # Display insight based on dominant emotion
            if dominant_emotion:
                st.markdown("### Key Emotional Insight")
                
                if dominant_emotion == "joy":
                    st.markdown("Your entries show a strong presence of **joy**. This positive emotion can fuel creative energy and open you to new possibilities.")
                    st.markdown("**Recommendation:** Consider what activities and circumstances create this positive emotion and how you might incorporate more of them into your daily life.")
                elif dominant_emotion == "hope":
                    st.markdown("**Hope** is prominent in your entries. This is a powerful emotion for transformation and can help you envision new possibilities.")
                    st.markdown("**Recommendation:** Consider setting specific intentions that align with your hopeful outlook. What small steps might move you toward your vision?")
                elif dominant_emotion == "sadness":
                    st.markdown("Your entries reflect **sadness** during this period. This emotion often points to what matters deeply to us and what we may need to process.")
                    st.markdown("**Recommendation:** Consider what losses or unmet needs might be beneath this feeling. What form of gentle self-compassion might support you?")
                elif dominant_emotion == "anger":
                    st.markdown("**Anger** appears as a significant emotion in your entries. Anger often signals boundary violations or unmet needs.")
                    st.markdown("**Recommendation:** Reflect on what boundaries you might need to establish or reinforce. What constructive action might channel this energy?")
                elif dominant_emotion == "fear":
                    st.markdown("**Fear** emerges as a key emotion in your journal entries. Fear often highlights areas where we need more support or information.")
                    st.markdown("**Recommendation:** Consider what resources might help you move through this fear. What small step would help you feel more secure?")
            
                # Overall pattern suggestions
                st.markdown("### For Your Coaching Session")
                st.markdown("Consider discussing:")
                
                recommendations = [
                    f"How your experience with {dominant_emotion} relates to your growth journey",
                    "Any patterns you notice in your emotional trends that you'd like to explore further",
                    "Specific goals or intentions for emotional development in the coming week"
                ]
                
                for recommendation in recommendations:
                    st.markdown(f"- {recommendation}")
    else:
        st.info("More journal entries are needed to generate meaningful growth insights.")
    
    # Export to PDF
    st.markdown("---")
    st.subheader("Export Summary")
    
    if st.button("Generate PDF Summary"):
        with st.spinner("Generating PDF..."):
            # Convert date objects to datetime
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Generate PDF
            pdf_bytes = pdf_generator.create_weekly_summary_pdf(
                user_data={
                    'journal_entries': entries
                },
                start_date=start_datetime,
                end_date=end_datetime
            )
            
            # Display download link
            st.markdown(
                pdf_generator.create_download_link(
                    pdf_bytes,
                    filename=f"journal_summary_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf"
                ),
                unsafe_allow_html=True
            )
            
            st.success("PDF generated successfully!")

def get_entries_for_period(start_date, end_date):
    """
    Get journal entries for a specific date range.
    
    Args:
        start_date (date): Start date
        end_date (date): End date
        
    Returns:
        list: Journal entries within the date range
    """
    entries = []
    
    for entry in st.session_state.journal_entries:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
        if start_date <= entry_date <= end_date:
            entries.append(entry)
    
    return entries
