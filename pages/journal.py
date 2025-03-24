import streamlit as st
from datetime import datetime
import random
from utils.sentiment_analysis import SentimentAnalyzer
from utils.data_storage import save_journal_entry
from utils.voice_input import voice_recorder

def show_journal():
    st.header("Journal")
    
    # Initialize sentiment analyzer
    sentiment_analyzer = SentimentAnalyzer()
    
    # Select module and lesson
    col1, col2 = st.columns(2)
    
    with col1:
        module = st.selectbox(
            "Select Module",
            options=[1, 2, 3, 4, 5],
            index=st.session_state.current_module - 1,
            key="journal_module",
            format_func=lambda x: f"Module {x}: {get_module_title(x)}"
        )
    
    with col2:
        lesson = st.selectbox(
            "Select Lesson",
            options=[1, 2, 3, 4],
            index=st.session_state.current_lesson - 1,
            key="journal_lesson",
            format_func=lambda x: f"Lesson {x}: {get_lesson_title(module, x)}"
        )
    
    # Get the prompt for the selected module and lesson
    prompt = get_prompt(module, lesson)
    
    # Display the prompt
    st.markdown("### Today's Reflection")
    st.markdown(f"**{prompt}**")
    
    # Option for voice input
    use_voice = st.checkbox("Use Voice Input", value=st.session_state.voice_input_enabled)
    
    # Journal entry content
    content = ""
    
    if use_voice:
        st.markdown("#### Voice Input")
        st.info("Use the voice input below for your journal entry.")
        
        # Voice input component (simulated in this environment)
        voice_text = voice_recorder()
        
        if voice_text:
            content = voice_text
    else:
        # Text area for journal entry
        content = st.text_area(
            "Your Journal Entry",
            height=200,
            key="journal_content"
        )
    
    # Only show analyze button if there's content
    if content.strip():
        analyze_button = st.button("Analyze", key="analyze_button")
        
        if analyze_button or "last_analyzed_content" in st.session_state:
            # If this is a new analysis or content has changed
            if not hasattr(st.session_state, "last_analyzed_content") or st.session_state.last_analyzed_content != content:
                with st.spinner("Analyzing your journal entry..."):
                    # Analyze sentiment
                    sentiment_data = sentiment_analyzer.analyze_sentiment(content)
                    
                    # Extract themes
                    themes = sentiment_analyzer.extract_themes(content)
                    
                    # Generate reflections
                    reflections = sentiment_analyzer.generate_reflection_suggestions(sentiment_data)
                    
                    # Store analysis in session state
                    st.session_state.last_analyzed_content = content
                    st.session_state.last_sentiment_data = sentiment_data
                    st.session_state.last_themes = themes
                    st.session_state.last_reflections = reflections
            else:
                # Use cached analysis
                sentiment_data = st.session_state.last_sentiment_data
                themes = st.session_state.last_themes
                reflections = st.session_state.last_reflections
            
            # Display analysis
            st.markdown("### Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Display sentiment category with color
                sentiment_category = sentiment_data.get('category', 'neutral')
                if sentiment_category == 'positive':
                    st.success(f"Overall Sentiment: Positive")
                elif sentiment_category == 'negative':
                    st.error(f"Overall Sentiment: Challenging")
                else:
                    st.info(f"Overall Sentiment: Balanced")
                
                # Display detected emotions
                emotions = sentiment_data.get('emotions', {})
                if emotions:
                    st.markdown("#### Emotional Content")
                    
                    # Sort emotions by value
                    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                    
                    for emotion, value in sorted_emotions:
                        if value > 0:
                            st.markdown(f"- {emotion.capitalize()}: {value:.1f}%")
                
                # Display themes
                if themes:
                    st.markdown("#### Key Themes")
                    for theme in themes:
                        st.markdown(f"- {theme.capitalize()}")
            
            with col2:
                # Display reflections
                st.markdown("#### Reflections to Consider")
                for i, reflection in enumerate(reflections[:3]):
                    st.markdown(f"{i+1}. {reflection}")
            
            # Save journal entry option
            st.markdown("---")
            if st.button("Save Journal Entry"):
                # Save the entry
                entry = save_journal_entry(
                    module=module,
                    lesson=lesson,
                    prompt=prompt,
                    content=content,
                    sentiment_data=sentiment_data,
                    themes=themes
                )
                
                # Update current module and lesson
                # Move to next lesson if available, otherwise next module
                if lesson < 4:
                    st.session_state.current_lesson = lesson + 1
                elif module < 5:
                    st.session_state.current_module = module + 1
                    st.session_state.current_lesson = 1
                
                st.success("Journal entry saved successfully!")
                
                # Clear the analyzed content state to refresh on next entry
                if "last_analyzed_content" in st.session_state:
                    del st.session_state.last_analyzed_content
                
                # Provide a button to continue
                if st.button("Continue to Next Lesson"):
                    st.rerun()
    else:
        st.info("Enter your journal entry and click 'Analyze' to receive insights.")

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

def get_prompt(module, lesson):
    """Return a journaling prompt for the specified module and lesson."""
    prompts = {
        1: {  # Module 1: Understanding Cycles and Patterns
            1: "Reflect on a recurring pattern or cycle in your life. What triggers it, and how does it typically unfold?",
            2: "Describe a recent moment when you felt in 'crisis mode.' What internal and external factors contributed to this experience?",
            3: "Think of a time when you were in 'creation mode.' What conditions or mindsets enabled this state? How did it feel different from crisis mode?",
            4: "What specific cycle or pattern would you like to break free from? What keeps this cycle in place, and what might help you step out of it?"
        },
        2: {  # Module 2: Examining Beliefs and Conditioning
            1: "Reflect on a core belief you hold about yourself. Where did this belief originate? How has it shaped your experience?",
            2: "Identify a belief that may be limiting your growth or happiness. How does this belief affect your choices and behaviors?",
            3: "Consider how your cultural, family, or social conditioning has shaped your response to challenges. What conditioning no longer serves you?",
            4: "What new belief would support your growth and well-being? How might embracing this belief change your experience?"
        },
        3: {  # Module 3: Developing Emotional Intelligence
            1: "Describe a significant emotion you've experienced recently. What information might this emotion be offering you?",
            2: "Reflect on how you typically respond to difficult emotions. What strategies help you process these emotions in healthy ways?",
            3: "How might you harness emotional energy as a creative force? Describe an emotion that feels particularly energizing to you.",
            4: "What practice would help you develop greater emotional awareness in your daily life? How might this practice transform your experience?"
        },
        4: {  # Module 4: Cultivating Intuition and Synchronicity
            1: "Describe a time when you experienced a strong intuitive signal. How did it feel, and how did you respond?",
            2: "Reflect on a meaningful coincidence or synchronicity in your life. What significance did this event hold for you?",
            3: "What practices help you access your intuitive wisdom? How might you deepen these practices?",
            4: "How do you distinguish between intuitive guidance and fear-based thinking? What helps you trust your intuition?"
        },
        5: {  # Module 5: Intentional Creation
            1: "What intention would you like to set for your life right now? Be as specific as possible about what you want to create or experience.",
            2: "How aligned are your thoughts, feelings, and actions with your intentions? What shifts might create greater alignment?",
            3: "What inspired action could you take toward your intention? What makes this action feel inspiring rather than obligatory?",
            4: "How would your life change if you fully embraced your identity as a conscious creator? What would you do differently?"
        }
    }
    
    if module in prompts and lesson in prompts[module]:
        return prompts[module][lesson]
    else:
        return "Reflect on your journey so far and what's emerging for you today."
