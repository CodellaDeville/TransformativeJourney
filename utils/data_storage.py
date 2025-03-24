import streamlit as st
from datetime import datetime, timedelta
import json

def initialize_session_state():
    """Initialize the session state with default values if not already set."""
    
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "User"
        
    if 'current_module' not in st.session_state:
        st.session_state.current_module = 1
        
    if 'current_lesson' not in st.session_state:
        st.session_state.current_lesson = 1
        
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
        
    if 'completed_lessons' not in st.session_state:
        st.session_state.completed_lessons = set()
        
    if 'daily_check_in' not in st.session_state:
        st.session_state.daily_check_in = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'mood': 5,
            'reflection': ''
        }
    
    if 'growth_metrics' not in st.session_state:
        st.session_state.growth_metrics = {
            'emotional_awareness': 0,
            'coping_strategies': 0,
            'resilience': 0
        }
    
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
        
    if 'voice_input_enabled' not in st.session_state:
        st.session_state.voice_input_enabled = True
        
    if 'email_notifications' not in st.session_state:
        st.session_state.email_notifications = False

def save_journal_entry(module, lesson, prompt, content, sentiment_data, themes):
    """
    Save a journal entry to the session state.
    
    Args:
        module (int): The module number
        lesson (int): The lesson number
        prompt (str): The journaling prompt
        content (str): The journal entry content
        sentiment_data (dict): Sentiment analysis results
        themes (list): Extracted themes from the content
    """
    entry = {
        'id': len(st.session_state.journal_entries) + 1,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M'),
        'module': module,
        'lesson': lesson,
        'prompt': prompt,
        'content': content,
        'sentiment': sentiment_data,
        'themes': themes
    }
    
    st.session_state.journal_entries.append(entry)
    
    # Mark the lesson as completed
    lesson_key = f"{module}-{lesson}"
    st.session_state.completed_lessons.add(lesson_key)
    
    # Update growth metrics based on journaling activity
    update_growth_metrics(sentiment_data)
    
    return entry

def update_growth_metrics(sentiment_data):
    """
    Update growth metrics based on journal entry sentiment.
    
    Args:
        sentiment_data (dict): Sentiment analysis results
    """
    # Make the growth metrics more noticeable for testing in this environment
    # Update emotional awareness based on detection of emotions
    emotion_values = list(sentiment_data.get('emotions', {}).values())
    if emotion_values:
        # Calculate the average emotion intensity
        avg_emotion = sum(emotion_values) / len(emotion_values)
        
        # Increase emotional awareness proportionally to emotion intensity but more significantly
        # Scale is 0-100
        current = st.session_state.growth_metrics['emotional_awareness']
        # More significant increase with each entry, max value is 100
        st.session_state.growth_metrics['emotional_awareness'] = min(100, current + 5 + (avg_emotion * 2))
    else:
        # Even without detected emotions, add a small increase
        current = st.session_state.growth_metrics['emotional_awareness']
        st.session_state.growth_metrics['emotional_awareness'] = min(100, current + 2)
    
    # Update coping strategies based on positive sentiment in challenging emotions
    if sentiment_data.get('category') == 'positive':
        if any(sentiment_data.get('emotions', {}).get(e, 0) > 0 for e in ['sadness', 'anger', 'fear']):
            # Being able to maintain positive outlook despite challenging emotions
            # shows development of coping strategies
            current = st.session_state.growth_metrics['coping_strategies']
            st.session_state.growth_metrics['coping_strategies'] = min(100, current + 7)
        else:
            # Any positive sentiment adds some improvement
            current = st.session_state.growth_metrics['coping_strategies']
            st.session_state.growth_metrics['coping_strategies'] = min(100, current + 4)
    else:
        # Even without positive sentiment, add a small increase
        current = st.session_state.growth_metrics['coping_strategies']
        st.session_state.growth_metrics['coping_strategies'] = min(100, current + 2)
    
    # Update resilience based on balanced emotional expression
    # If both positive and challenging emotions are present, it indicates resilience
    positive_emotions = sentiment_data.get('emotions', {}).get('joy', 0) + sentiment_data.get('emotions', {}).get('hope', 0)
    challenging_emotions = sum(sentiment_data.get('emotions', {}).get(e, 0) for e in ['sadness', 'anger', 'fear'])
    
    if positive_emotions > 0 and challenging_emotions > 0:
        # Both types of emotions present indicates emotional range and resilience
        current = st.session_state.growth_metrics['resilience']
        st.session_state.growth_metrics['resilience'] = min(100, current + 6)
    else:
        # Even without balanced emotions, add a small increase
        current = st.session_state.growth_metrics['resilience']
        st.session_state.growth_metrics['resilience'] = min(100, current + 3)

def save_daily_check_in(mood, reflection):
    """
    Save the daily check-in data.
    
    Args:
        mood (int): Mood rating (1-10)
        reflection (str): Brief reflection text
    """
    st.session_state.daily_check_in = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'mood': mood,
        'reflection': reflection
    }

def get_journal_entries_for_period(start_date, end_date):
    """
    Get journal entries for a specific date range.
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        
    Returns:
        list: Journal entries within the date range
    """
    entries = []
    
    for entry in st.session_state.journal_entries:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
        if start_date <= entry_date <= end_date:
            entries.append(entry)
    
    return entries

def get_module_completion_percentage():
    """
    Calculate the percentage of completed modules.
    
    Returns:
        float: Percentage of completed modules (0-100)
    """
    total_lessons = 5 * 4  # 5 modules, 4 lessons each
    completed = len(st.session_state.completed_lessons)
    return (completed / total_lessons) * 100

def export_user_data():
    """
    Export user data as JSON.
    
    Returns:
        str: JSON string containing user data
    """
    data = {
        'user_name': st.session_state.user_name,
        'current_module': st.session_state.current_module,
        'current_lesson': st.session_state.current_lesson,
        'journal_entries': st.session_state.journal_entries,
        'completed_lessons': list(st.session_state.completed_lessons),
        'daily_check_in': st.session_state.daily_check_in,
        'growth_metrics': st.session_state.growth_metrics,
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return json.dumps(data, indent=2)

def import_user_data(json_data):
    """
    Import user data from JSON.
    
    Args:
        json_data (str): JSON string containing user data
        
    Returns:
        bool: Success status
    """
    try:
        data = json.loads(json_data)
        
        # Update session state
        st.session_state.user_name = data.get('user_name', 'User')
        st.session_state.current_module = data.get('current_module', 1)
        st.session_state.current_lesson = data.get('current_lesson', 1)
        st.session_state.journal_entries = data.get('journal_entries', [])
        st.session_state.completed_lessons = set(data.get('completed_lessons', []))
        st.session_state.daily_check_in = data.get('daily_check_in', {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'mood': 5,
            'reflection': ''
        })
        st.session_state.growth_metrics = data.get('growth_metrics', {
            'emotional_awareness': 0,
            'coping_strategies': 0,
            'resilience': 0
        })
        
        return True
    except Exception as e:
        st.error(f"Error importing data: {str(e)}")
        return False
