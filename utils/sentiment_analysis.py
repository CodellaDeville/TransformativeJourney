import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import streamlit as st

# Download necessary NLTK data
@st.cache_resource
def download_nltk_data():
    # Only download the vader_lexicon which we need for sentiment analysis
    nltk.download('vader_lexicon')
    
    # Return common English stopwords as a list - simpler than using NLTK's stopwords
    return [
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
        'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
        'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
        'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
        'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
        'with', 'about', 'against', 'between', 'into', 'through', 'during', 
        'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 
        'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 
        'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
        'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
        's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
    ]

# Make sure we download the data
STOPWORDS = download_nltk_data()

class SentimentAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.stop_words = set(STOPWORDS)
        
    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of the given text and return scores and category.
        """
        if not text:
            return {
                "compound": 0.0,
                "pos": 0.0,
                "neu": 0.0,
                "neg": 0.0,
                "category": "neutral",
                "emotions": {
                    "joy": 0.0,
                    "sadness": 0.0,
                    "anger": 0.0,
                    "fear": 0.0,
                    "hope": 0.0
                }
            }
            
        scores = self.sid.polarity_scores(text)
        
        # Categorize the sentiment
        if scores['compound'] >= 0.05:
            category = "positive"
        elif scores['compound'] <= -0.05:
            category = "negative"
        else:
            category = "neutral"
            
        # Detect specific emotions
        emotions = self.detect_emotions(text)
        
        results = {
            "compound": scores['compound'],
            "pos": scores['pos'],
            "neu": scores['neu'],
            "neg": scores['neg'],
            "category": category,
            "emotions": emotions
        }
        
        return results
    
    def detect_emotions(self, text):
        """
        Detect specific emotions in the text.
        """
        # Simple keyword-based emotion detection
        emotion_keywords = {
            "joy": ["happy", "glad", "joy", "delight", "content", "pleased", "elated", "thrilled", "excited"],
            "sadness": ["sad", "unhappy", "miserable", "heartbroken", "gloomy", "depressed", "melancholy", "grief"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "enraged", "frustrated", "outraged"],
            "fear": ["afraid", "scared", "fearful", "anxious", "worried", "terrified", "panicked", "nervous"],
            "hope": ["hope", "hopeful", "optimistic", "looking forward", "anticipate", "expect", "faith", "trust"]
        }
        
        # Normalize text and simple tokenization without NLTK
        text = text.lower()
        # Simple word tokenization by spaces and removing punctuation
        words = []
        for word in text.split():
            # Remove punctuation
            word = ''.join(c for c in word if c.isalpha())
            if word and word not in self.stop_words:
                words.append(word)
        
        # Count emotion keywords
        emotion_counts = {emotion: 0 for emotion in emotion_keywords}
        for word in words:
            for emotion, keywords in emotion_keywords.items():
                if word in keywords:
                    emotion_counts[emotion] += 1
        
        # Calculate percentages
        emotions = {
            emotion: count / max(len(words), 1) * 100
            for emotion, count in emotion_counts.items()
        }
        
        return emotions
    
    def extract_themes(self, text, top_n=3):
        """
        Extract main themes from the text.
        """
        if not text:
            return []
            
        # Normalize text and simple tokenization
        text = text.lower()
        # Simple word tokenization by spaces and removing punctuation
        words = []
        for word in text.split():
            # Remove punctuation
            word = ''.join(c for c in word if c.isalpha())
            if word and word not in self.stop_words:
                words.append(word)
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N themes
        themes = [word for word, freq in sorted_words[:top_n]]
        return themes
        
    def generate_reflection_suggestions(self, sentiment_data):
        """
        Generate dynamic reflection suggestions based on sentiment analysis.
        """
        category = sentiment_data["category"]
        emotions = sentiment_data["emotions"]
        compound_score = sentiment_data.get("compound", 0)
        
        # Find dominant and secondary emotions
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        dominant_emotion = sorted_emotions[0][0] if sorted_emotions and sorted_emotions[0][1] > 0 else None
        secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0 else None
        
        suggestions = []
        
        # Opening reflection based on sentiment category
        if category == "negative":
            if compound_score < -0.5:  # Strongly negative
                suggestions.append("I notice significant emotional weight in your entry. Remember that challenging feelings often contain important wisdom.")
            else:
                suggestions.append("I notice some challenging emotions in your entry. How might these feelings be guiding you toward greater awareness?")
            
            # Specific emotion-based reflections
            if dominant_emotion == "sadness":
                suggestions.append("Your sadness may be highlighting something you deeply value. What matters most to you in this situation?")
                suggestions.append("What form of compassion or gentle support would be most helpful for you right now?")
                if secondary_emotion == "hope":
                    suggestions.append("I see both sadness and hope in your entry. How might this combination be showing you a path forward?")
            
            elif dominant_emotion == "anger":
                suggestions.append("Your anger appears to be protecting something important. What boundary or value might it be defending?")
                suggestions.append("How might you channel this energetic emotion into constructive action that honors your needs?")
                if secondary_emotion == "fear":
                    suggestions.append("The combination of anger and fear often appears when something deeply important feels threatened. What's at the core of this for you?")
            
            elif dominant_emotion == "fear":
                suggestions.append("Fear often contains information about what we care about. What is your fear trying to protect?")
                suggestions.append("What small, manageable step might help you move through this fear with greater confidence?")
                if secondary_emotion == "hope":
                    suggestions.append("I notice both fear and hope present. How might this tension be creating an opportunity for growth?")
                    
            # General growth-oriented reflection for challenging emotions
            suggestions.append("Which of your personal strengths or past experiences might help you navigate this situation with more resilience?")
            
        elif category == "positive":
            if compound_score > 0.5:  # Strongly positive
                suggestions.append("There's wonderful positive energy flowing through your entry! How can you amplify and share this vibrant state?")
            else:
                suggestions.append("I notice uplifting energy in your words. How might you build on these positive feelings in a meaningful way?")
            
            # Specific emotion-based reflections
            if dominant_emotion == "joy":
                suggestions.append("This joy seems significant. What specific elements created this feeling, and how might you cultivate more of this experience?")
                suggestions.append("How does this joyful state connect to your deeper values or sense of purpose?")
                if secondary_emotion == "sadness":
                    suggestions.append("Joy and sadness often appear together during meaningful transitions. What might be transitioning in your life right now?")
            
            elif dominant_emotion == "hope":
                suggestions.append("Your hope reveals what matters to you. What vision or possibility are you connecting with that energizes you?")
                suggestions.append("What inspired action would align with and strengthen this hopeful outlook?")
                if secondary_emotion == "fear":
                    suggestions.append("Hope alongside fear often appears at the edge of growth opportunities. What new possibility might be emerging for you?")
                    
            # Expression and sharing of positive states
            suggestions.append("How might you express or share this positive energy in a way that amplifies its impact for yourself and others?")
            
        else:  # neutral
            suggestions.append("Your entry has a balanced or neutral tone. What feelings or insights might be present just beneath the surface?")
            suggestions.append("What patterns or themes do you notice when you reflect on your thoughts from a place of neutrality?")
            suggestions.append("Sometimes neutrality creates space for deeper awareness. What might emerge if you sit with this topic a bit longer?")
        
        # Module-specific reflections could be added here based on current module/lesson
        
        # Always add a forward-looking, action-oriented question
        suggestions.append("Based on today's reflection, what one small intention or action would feel most aligned for you moving forward?")
        
        # Shuffle and return a diverse set of reflections
        import random
        random.shuffle(suggestions)
        
        return suggestions
