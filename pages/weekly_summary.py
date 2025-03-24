import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.pdf_generator import PDFGenerator
import base64

def show_emotion_summary(emotions_data):
    """Display emotion summary with enhanced visualization."""
    if not emotions_data:
        st.write("No emotion data available for this period.")
        return

    # Prepare data for visualization
    emotions = {}
    for entry_emotions in emotions_data:
        if not entry_emotions:  # Skip empty emotion dictionaries
            continue
        for emotion, intensity in entry_emotions.items():
            if emotion in emotions:
                emotions[emotion] = max(emotions[emotion], intensity)  # Take the highest intensity
            else:
                emotions[emotion] = intensity

    if emotions:
        # Create a color map for emotions
        emotion_colors = {
            "joy": "#FFD700",  # Gold
            "sadness": "#4682B4",  # Steel Blue
            "anger": "#FF4500",  # Red Orange
            "fear": "#800080",  # Purple
            "hope": "#98FB98",  # Pale Green
            "surprise": "#FF69B4",  # Hot Pink
            "gratitude": "#DDA0DD",  # Plum
            "pride": "#FF8C00",  # Dark Orange
            "love": "#FF1493",  # Deep Pink
            "anxiety": "#20B2AA"  # Light Sea Green
        }

        # Create emotion visualization
        fig = go.Figure()

        # Add radar chart
        fig.add_trace(go.Scatterpolar(
            r=list(emotions.values()),
            theta=list(emotions.keys()),
            fill='toself',
            name='Emotions',
            line_color='rgba(255, 165, 0, 0.8)',  # Orange with some transparency
            fillcolor='rgba(255, 165, 0, 0.3)'  # Lighter orange with more transparency
        ))

        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            title="Emotional Landscape",
            height=400
        )

        # Display the radar chart
        st.plotly_chart(fig, use_container_width=True)

        # Display dominant emotions
        col1, col2 = st.columns(2)
        with col1:
            # Get top 3 emotions
            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
            st.markdown("### Dominant Emotions")
            for emotion, intensity in top_emotions:
                st.markdown(
                    f"<div style='padding: 10px; margin: 5px; background-color: {emotion_colors.get(emotion, '#808080')}30;'>"
                    f"<strong>{emotion.capitalize()}:</strong> {intensity:.1f}%"
                    f"</div>",
                    unsafe_allow_html=True
                )

        with col2:
            # Calculate emotional balance
            positive_emotions = sum(emotions[e] for e in ['joy', 'hope', 'gratitude', 'pride', 'love'] if e in emotions)
            negative_emotions = sum(emotions[e] for e in ['sadness', 'anger', 'fear', 'anxiety'] if e in emotions)
            neutral_emotions = sum(emotions[e] for e in ['surprise'] if e in emotions)
            
            total = positive_emotions + negative_emotions + neutral_emotions
            if total > 0:
                st.markdown("### Emotional Balance")
                st.markdown(
                    f"<div style='padding: 10px; margin: 5px; background-color: #98FB9830;'>"
                    f"<strong>Positive:</strong> {(positive_emotions/total)*100:.1f}%"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='padding: 10px; margin: 5px; background-color: #4682B430;'>"
                    f"<strong>Negative:</strong> {(negative_emotions/total)*100:.1f}%"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='padding: 10px; margin: 5px; background-color: #DDA0DD30;'>"
                    f"<strong>Neutral:</strong> {(neutral_emotions/total)*100:.1f}%"
                    f"</div>",
                    unsafe_allow_html=True
                )

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
    
    # Initialize default dates
    default_start = datetime.now() - timedelta(days=7)
    default_end = datetime.now()
    
    # Get min/max dates from journal entries to prevent errors
    min_date = default_start
    max_date = default_end
    
    try:
        # Try to get actual min/max dates from journal entries if they exist
        if st.session_state.journal_entries:
            all_dates = [datetime.strptime(entry['date'], '%Y-%m-%d').date() 
                        for entry in st.session_state.journal_entries]
            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)
                
                # Adjust max_date to today if it's in the future
                if max_date > datetime.now().date():
                    max_date = datetime.now().date()
    except (ValueError, KeyError, AttributeError):
        # Fallback to defaults if there's any error
        pass
    
    with col1:
        try:
            # Default start date is 7 days ago or earliest entry
            start_date = st.date_input(
                "Start Date",
                value=default_start,
                max_value=default_end
            )
        except Exception:
            # Fallback if date input fails
            start_date = default_start.date()
    
    with col2:
        try:
            # Default end date is today or latest entry
            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=start_date,
                max_value=default_end
            )
        except Exception:
            # Fallback if date input fails
            end_date = default_end.date()
    
    # Filter entries for the selected period
    entries = get_entries_for_period(start_date, end_date)
    
    if not entries:
        st.info(f"No journal entries found between {start_date.strftime('%b %d, %Y')} and {end_date.strftime('%b %d, %Y')}.")
        return
    
    # Collect emotions data from all entries
    emotions_data = []
    for entry in entries:
        if 'sentiment' in entry and 'emotions' in entry['sentiment']:
            emotions_data.append(entry['sentiment']['emotions'])
    
    # Show emotion summary
    st.header("Emotional Overview")
    show_emotion_summary(emotions_data)
    
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
            
            if emotions and len(emotions) > 0:  # Check if emotions dictionary is not empty
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
                category = sentiment['category'].lower()
                display_category = "positive" if category in ['very positive', 'positive'] else \
                                 "negative" if category in ['very negative', 'negative'] else \
                                 "neutral"
                st.markdown(f"**Sentiment:** {display_category.capitalize()}")
                
                # Display emotions if available
                if 'emotions' in sentiment and sentiment['emotions']:
                    emotions = sentiment['emotions']
                    if emotions and len(emotions) > 0:  
                        try:
                            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                            st.markdown(f"**Dominant emotion:** {dominant_emotion.capitalize()}")
                        except ValueError:
                            # Handle the case where emotions is empty
                            pass
                
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
        sentiment_categories = {"positive": 0, "neutral": 0, "negative": 0}
        entry_count = len(entries)
        
        for entry in entries:
            # Track sentiment categories
            if 'sentiment' in entry and 'category' in entry['sentiment']:
                category = entry['sentiment']['category'].lower()
                # Map legacy categories to new ones
                if category in ['very positive', 'positive']:
                    sentiment_categories['positive'] += 1
                elif category in ['very negative', 'negative']:
                    sentiment_categories['negative'] += 1
                else:
                    sentiment_categories['neutral'] += 1
            
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
            dominant_sentiment = sorted_categories[0].lower() if sorted_categories else "neutral"
            
            if dominant_sentiment == "positive":
                st.markdown("📈 **Mood Insight:** Your journal entries show a predominantly positive outlook, which suggests you're in a creative or resourceful state of mind. This is an excellent time to set goals and build on your momentum.")
            elif dominant_sentiment == "negative":
                st.markdown("🔍 **Mood Insight:** Your entries reflect more challenging emotions, which often indicate important areas for growth and healing. These feelings can provide valuable information about your needs and values.")
            else:  # neutral
                st.markdown("⚖️ **Mood Insight:** Your entries show a balanced emotional state, which can indicate either emotional stability or possibly some emotional detachment. This could be a good time for objective reflection.")
        
        # Emotional insight based on specific emotions
        if emotion_averages:
            st.markdown("### Specific Emotional Patterns")
            
            # Format emotion averages as percentages and sort
            emotion_percentages = {k.capitalize(): v for k, v in emotion_averages.items() if v > 0}
            sorted_emotions = sorted(emotion_percentages.items(), key=lambda x: x[1], reverse=True)
            
            # Create a bar chart for emotion intensities
            if sorted_emotions:  # Only create chart if there are emotions to display
                emotions = [e[0] for e in sorted_emotions]
                intensities = [e[1] for e in sorted_emotions]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=intensities,
                    y=emotions,
                    orientation='h',
                    marker_color=[
                        '#FFC107' if e == 'Joy' else
                        '#4CAF50' if e == 'Hope' else
                        '#F44336' if e == 'Anger' else
                        '#2196F3' if e == 'Sadness' else
                        '#9C27B0' for e in emotions
                    ],
                    text=[f"{v:.1f}%" for v in intensities],
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title="Emotional Intensity Distribution",
                    xaxis_title="Intensity (%)",
                    yaxis_title="Emotion",
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
                
                # Find dominant emotions (those with intensity > 30%)
                significant_emotions = [(emotion, value) for emotion, value in sorted_emotions if value > 30]
                
                # Display insight based on emotional patterns
                st.markdown("### Key Emotional Insights")
                
                if significant_emotions:
                    # Display insights for each significant emotion
                    for emotion, intensity in significant_emotions:
                        emotion_lower = emotion.lower()
                        
                        insights = {
                            'joy': {
                                'description': "indicates a period of positive energy and openness to new experiences",
                                'strength': "can fuel creativity and resilience",
                                'suggestion': "identify what activities and circumstances create this positive emotion"
                            },
                            'hope': {
                                'description': "shows an ability to envision positive possibilities even in challenges",
                                'strength': "can drive motivation and perseverance",
                                'suggestion': "set specific intentions that align with your hopeful outlook"
                            },
                            'sadness': {
                                'description': "suggests a period of processing or reflection",
                                'strength': "can deepen emotional awareness and empathy",
                                'suggestion': "explore what needs or values might need attention"
                            },
                            'anger': {
                                'description': "often signals boundary violations or unmet needs",
                                'strength': "can provide energy for positive change",
                                'suggestion': "identify what boundaries need to be established or reinforced"
                            },
                            'fear': {
                                'description': "highlights areas where support or growth is needed",
                                'strength': "can increase awareness and preparation",
                                'suggestion': "consider what resources would help you feel more secure"
                            }
                        }
                        
                        if emotion_lower in insights:
                            insight = insights[emotion_lower]
                            st.markdown(f"""
                            **{emotion} ({intensity:.1f}%)** {insight['description']}.
                            - **Strength:** This emotion {insight['strength']}.
                            - **Suggestion:** Consider how to {insight['suggestion']}.
                            """)
                    
                    # Add pattern analysis if multiple emotions are significant
                    if len(significant_emotions) > 1:
                        st.markdown("### Pattern Analysis")
                        emotions_list = [e[0].lower() for e in significant_emotions]
                        
                        if 'joy' in emotions_list and 'hope' in emotions_list:
                            st.markdown("🌟 Your entries show a positive emotional pattern that can be particularly powerful for personal growth and setting new goals.")
                        elif 'sadness' in emotions_list and 'fear' in emotions_list:
                            st.markdown("🤗 Your entries reflect a period of vulnerability that may need extra self-compassion and support.")
                        elif 'anger' in emotions_list and 'fear' in emotions_list:
                            st.markdown("💪 Your entries suggest you might be facing challenges that require both courage and boundary-setting.")
                else:
                    st.info("No dominant emotions detected. Your entries show a balanced emotional state or may need more detailed emotional expression.")
                
                # Recommendations for emotional development
                st.markdown("### Recommendations for Your Journey")
                st.markdown("Consider exploring:")
                
                recommendations = [
                    "How your emotional patterns relate to your current life circumstances",
                    "Which emotions feel most comfortable to express and which might need more attention",
                    "What specific actions could support your emotional well-being this week"
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
    
    try:
        if not hasattr(st.session_state, 'journal_entries') or not st.session_state.journal_entries:
            return entries
            
        for entry in st.session_state.journal_entries:
            try:
                entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                if start_date <= entry_date <= end_date:
                    entries.append(entry)
            except (ValueError, KeyError, TypeError):
                # Skip entries with invalid dates
                continue
    except Exception as e:
        st.error(f"Error loading journal entries: {str(e)}")
        return []
    
    return entries
