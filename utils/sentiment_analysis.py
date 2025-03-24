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
                    "hope": 0.0,
                    "surprise": 0.0,
                    "gratitude": 0.0,
                    "pride": 0.0,
                    "love": 0.0,
                    "anxiety": 0.0
                }
            }
            
        scores = self.sid.polarity_scores(text)
        
        # Enhanced sentiment categorization with balanced thresholds
        if scores['compound'] >= 0.3:
            category = "positive"
        elif scores['compound'] <= -0.3:
            category = "negative"
        else:
            category = "neutral"
            
        # Detect specific emotions with enhanced context
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
        Detect specific emotions in the text using an enhanced keyword and pattern approach.
        """
        # Expanded emotion keywords with synonyms, phrases, and contextual patterns
        emotion_keywords = {
            "joy": [
                "happy", "glad", "joy", "delight", "content", "pleased", "elated", "thrilled", "excited",
                "wonderful", "amazing", "fantastic", "great", "blessed", "grateful", "thankful", "peaceful",
                "love", "loving", "enjoyed", "enjoy", "smile", "laughed", "laugh", "celebrating",
                "ecstatic", "overjoyed", "jubilant", "blissful", "cheerful", "radiant", "beaming",
                "accomplished", "satisfied", "fulfilled", "triumphant", "victorious", "playful", "giddy"
            ],
            "sadness": [
                "sad", "unhappy", "miserable", "heartbroken", "gloomy", "depressed", "melancholy", "grief",
                "lonely", "alone", "lost", "empty", "hurt", "pain", "suffering", "disappointed", "miss",
                "missing", "regret", "hopeless", "despair", "crying", "cried", "tears", "devastated",
                "heartache", "sorrow", "mourning", "grieving", "broken", "crushed", "desolate", "down",
                "blue", "heavy-hearted", "weeping", "sobbing", "melancholic", "forlorn"
            ],
            "anger": [
                "angry", "mad", "furious", "irritated", "annoyed", "enraged", "frustrated", "outraged",
                "hate", "hatred", "resent", "resentful", "bitter", "disgusted", "fed up", "upset",
                "hostile", "rage", "fuming", "livid", "offended", "unfair", "wrong", "infuriated",
                "seething", "irate", "incensed", "indignant", "provoked", "agitated", "exasperated",
                "disgruntled", "resentment", "contempt", "irritable"
            ],
            "fear": [
                "afraid", "scared", "fearful", "anxious", "worried", "terrified", "panicked", "nervous",
                "dread", "uneasy", "stress", "stressed", "overwhelmed", "insecure", "doubt", "uncertain",
                "hesitant", "apprehensive", "concern", "concerned", "panic", "terror", "frightened",
                "paranoid", "petrified", "horrified", "alarmed", "threatened", "intimidated",
                "unsettled", "disturbed", "trembling", "shaking", "tense"
            ],
            "hope": [
                "hope", "hopeful", "optimistic", "looking forward", "anticipate", "expect", "faith", "trust",
                "believe", "believing", "confident", "determined", "motivated", "inspired", "eager",
                "excited", "positive", "better", "improve", "improving", "progress", "growing",
                "aspiring", "promising", "encouraging", "reassuring", "uplifting", "brighter", "possibility"
            ],
            "surprise": [
                "surprised", "shocked", "amazed", "astonished", "stunned", "startled", "unexpected",
                "wonder", "awe", "speechless", "mindblown", "flabbergasted", "dumbfounded",
                "incredible", "unbelievable", "wow", "remarkable", "extraordinary", "sudden", "revelation"
            ],
            "gratitude": [
                "grateful", "thankful", "appreciative", "blessed", "appreciate", "indebted",
                "touched", "moved", "humbled", "honored", "fortunate", "lucky", "privileged",
                "recognition", "appreciation", "valued", "acknowledged"
            ],
            "pride": [
                "proud", "accomplished", "confident", "successful", "achieved", "triumph",
                "victory", "mastered", "earned", "deserved", "honored", "respected",
                "achievement", "excellence", "satisfaction", "impressive"
            ],
            "love": [
                "love", "adore", "cherish", "treasure", "devoted", "affection", "fond",
                "warmth", "tenderness", "attachment", "caring", "romantic", "passionate",
                "intimate", "connected", "bonded", "close", "dear", "beloved"
            ],
            "anxiety": [
                "anxious", "worried", "nervous", "tense", "restless", "uneasy", "jittery",
                "edgy", "agitated", "frazzled", "stressed", "pressured", "overwhelmed",
                "apprehensive", "troubled", "distressed", "fretful", "bothered"
            ]
        }
        
        # Normalize text and split into sentences
        text = text.lower()
        sentences = [s.strip() for s in re.split('[.!?]+', text) if s.strip()]
        
        # Initialize emotion tracking
        emotion_scores = {emotion: 0.0 for emotion in emotion_keywords}
        
        # Context modifiers for emotion intensity
        context_modifiers = {
            "very": 1.3,
            "extremely": 1.5,
            "somewhat": 0.8,
            "slightly": 0.6,
            "really": 1.2,
            "deeply": 1.3
        }
        
        # Process each sentence for emotions
        for sentence in sentences:
            words = sentence.split()
            
            # Check for negations
            negation_active = False
            for i, word in enumerate(words):
                clean_word = ''.join(c for c in word if c.isalpha())
                if clean_word in ["not", "don't", "doesn't", "didn't", "no", "never"]:
                    negation_active = True
                    break
            
            # Process words in the sentence
            for i, word in enumerate(words):
                clean_word = ''.join(c for c in word if c.isalpha())
                if not clean_word or clean_word in self.stop_words:
                    continue
                
                # Apply intensity modifier
                intensity = 1.0
                if i > 0:
                    prev_word = ''.join(c for c in words[i-1] if c.isalpha())
                    if prev_word in context_modifiers:
                        intensity = context_modifiers[prev_word]
                
                # If negation is active, flip the emotion valence
                if negation_active:
                    intensity *= -0.5  # Reduced negative impact
                
                # Check for emotion keywords
                for emotion, keywords in emotion_keywords.items():
                    if clean_word in keywords:
                        emotion_scores[emotion] += intensity
                
                # Check for two-word phrases
                if i < len(words) - 1:
                    next_word = ''.join(c for c in words[i+1] if c.isalpha())
                    phrase = f"{clean_word} {next_word}"
                    for emotion, keywords in emotion_keywords.items():
                        if phrase in keywords:
                            emotion_scores[emotion] += (intensity * 1.2)  # Higher weight for phrases
        
        # Normalize and select top emotions
        if sum(emotion_scores.values()) > 0:
            # Sort emotions by score
            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Select top emotions with positive scores
            emotions = {}
            for emotion, score in sorted_emotions[:3]:  # Top 3 emotions
                if score > 0:
                    emotions[emotion] = score
            
            # Normalize to percentages
            if emotions:
                total = sum(emotions.values())
                emotions = {k: (v/total) * 100 for k, v in emotions.items()}
        else:
            emotions = {}
        
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
        
        # Opening reflection based on emotional intensity and complexity
        if len(sorted_emotions) >= 2:
            suggestions.append(f"I notice a complex emotional landscape with strong presence of {dominant_emotion} ({sorted_emotions[0][1]:.0f}%) and {secondary_emotion} ({sorted_emotions[1][1]:.0f}%). Let's explore these feelings together.")
        elif dominant_emotion:
            suggestions.append(f"I see a clear presence of {dominant_emotion} ({sorted_emotions[0][1]:.0f}%) in your entry. Let's understand this emotion better.")
        
        # Specific emotion-based reflections
        if dominant_emotion == "sadness":
            suggestions.append("Your sadness seems to be highlighting something meaningful. What core needs or values might it be connected to?")
            if secondary_emotion == "anger":
                suggestions.append("The combination of sadness and anger often appears when we've experienced a violation of something we deeply value. What boundaries or values feel important to honor right now?")
            elif secondary_emotion == "hope":
                suggestions.append("I notice both sadness and hope present - this often emerges during times of meaningful transition or growth. What possibilities might be emerging through this experience?")
        
        elif dominant_emotion == "anger":
            suggestions.append("Your anger appears to be carrying important energy. What is it protecting or standing up for?")
            if secondary_emotion == "fear":
                suggestions.append("When anger and fear appear together, it often signals a deep need for safety or control. What would help you feel more secure in this situation?")
            elif secondary_emotion == "sadness":
                suggestions.append("The presence of both anger and sadness suggests a complex emotional response to something meaningful. What values or needs feel most important to honor?")
        
        elif dominant_emotion == "fear":
            suggestions.append("Your fear seems to be highlighting something you care about. What is it trying to protect?")
            if secondary_emotion == "hope":
                suggestions.append("The dance between fear and hope often appears at the edge of meaningful growth. What new possibility might be trying to emerge?")
            elif secondary_emotion == "anger":
                suggestions.append("When fear and anger combine, it often points to a need for boundaries or protection. What would help you feel more secure and empowered?")
        
        elif dominant_emotion == "joy":
            suggestions.append("This joy feels significant. What specific elements or conditions helped create this positive state?")
            if secondary_emotion == "hope":
                suggestions.append("The combination of joy and hope suggests you're connecting with meaningful possibilities. What vision or potential are you sensing?")
            elif secondary_emotion == "fear":
                suggestions.append("Sometimes joy mixed with fear appears when we're stepping into something meaningful but unfamiliar. What growth opportunity might be presenting itself?")
        
        elif dominant_emotion == "hope":
            suggestions.append("Your sense of hope is noteworthy. What possibilities or potential are you connecting with?")
            if secondary_emotion == "fear":
                suggestions.append("Hope and fear often dance together at the edge of growth. What new territory might you be stepping into?")
            elif secondary_emotion == "sadness":
                suggestions.append("The presence of both hope and sadness can signal a meaningful transition. What might be ending, and what might be beginning?")
        
        # Add reflections based on emotional intensity
        total_intensity = sum(emotion[1] for emotion in sorted_emotions)
        if total_intensity > 150:  # High emotional intensity
            suggestions.append("I notice particularly strong emotional energy in your entry. How might you channel this intensity in a way that serves your growth?")
        elif total_intensity < 50:  # Low emotional intensity
            suggestions.append("Your entry carries a more measured emotional tone. What subtle feelings or insights might be present just beneath the surface?")
        
        # Add forward-looking reflection
        suggestions.append("Based on these emotional insights, what one small step would feel most supportive or meaningful right now?")
        
        # Shuffle and return a diverse set of reflections
        import random
        random.shuffle(suggestions)
        
        # Return 3-5 suggestions based on emotional complexity
        num_suggestions = min(5, max(3, len(sorted_emotions) + 1))
        return suggestions[:num_suggestions]
