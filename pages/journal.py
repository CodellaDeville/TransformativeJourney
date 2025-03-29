import streamlit as st
from datetime import datetime
import random
from utils.sentiment_analysis import SentimentAnalyzer
from utils.data_storage import save_journal_entry

def clear_input_field():
    """Clear only the journal input field and its associated analysis"""
    st.session_state.journal_content = ""
    if 'last_analyzed_content' in st.session_state:
        del st.session_state.last_analyzed_content
    if 'last_sentiment_data' in st.session_state:
        del st.session_state.last_sentiment_data
    if 'last_themes' in st.session_state:
        del st.session_state.last_themes
    if 'last_reflections' in st.session_state:
        del st.session_state.last_reflections
        
    # Make sure the current page stays as "journal" to prevent reverting to dashboard
    st.session_state.current_page = "journal"
    
    st.success("Journal input field cleared. You can start a new entry.")

def clear_journal_entries():
    """Clear all journal entries from session state"""
    if 'journal_entries' in st.session_state:
        st.session_state.journal_entries = []
    if 'last_analyzed_content' in st.session_state:
        del st.session_state.last_analyzed_content
    if 'last_sentiment_data' in st.session_state:
        del st.session_state.last_sentiment_data
    if 'last_themes' in st.session_state:
        del st.session_state.last_themes
    if 'last_reflections' in st.session_state:
        del st.session_state.last_reflections
        
    # Make sure the current page stays as "journal" to prevent reverting to dashboard
    st.session_state.current_page = "journal"
    
    st.success("All journal entries have been cleared.")

def show_journal():
    st.header("Journal")
    
    # Add JavaScript to handle Ctrl+Enter
    st.markdown("""
        <script>
        // Wait for the text area to be available
        const waitForTextArea = setInterval(() => {
            const textArea = document.querySelector('textarea[data-testid="stTextArea"]');
            if (textArea) {
                clearInterval(waitForTextArea);
                
                // Add event listener for keydown
                textArea.addEventListener('keydown', (e) => {
                    // Check for Ctrl+Enter
                    if (e.ctrlKey && e.key === 'Enter') {
                        e.preventDefault();  // Prevent default form submission
                        
                        // First ensure we stay on journal page
                        window.parent.postMessage(
                            {
                                type: "streamlit:setComponentValue",
                                key: "current_page",
                                value: "journal"
                            },
                            "*"
                        );
                        
                        // Then trigger the analysis
                        window.parent.postMessage(
                            {
                                type: "streamlit:setComponentValue",
                                key: "journal_content_submitted",
                                value: true
                            },
                            "*"
                        );
                    }
                });
            }
        }, 100);
        </script>
    """, unsafe_allow_html=True)
    
    # Initialize sentiment analyzer
    sentiment_analyzer = SentimentAnalyzer()
    
    # Add clear input button in the sidebar with clarifying tooltip
    if st.sidebar.button("Clear Journal Input", help="Reset the journal input field to write a new entry. Your previously saved entries will remain intact."):
        clear_input_field()
    
    # Add clear entries button in the sidebar
    if st.sidebar.button("Clear All Journal Entries", help="Remove all saved journal entries"):
        clear_journal_entries()
    
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
    
    # Voice input notice
    voice_col1, voice_col2 = st.columns([1, 4])
    with voice_col1:
        voice_enabled = st.checkbox("Use Voice Input", disabled=True)
    with voice_col2:
        if voice_enabled:
            st.info("🎙️ Voice input feature will be enabled in a future update.")
    
    # Text area for journal entry with on_change handler
    content = st.text_area(
        "Your Journal Entry",
        value=st.session_state.get('journal_content', ''),
        height=200,
        key="journal_content",
        on_change=lambda: None  # Prevent default form submission
    )
    
    # Only show analyze button if there's content
    if content.strip():
        # Handle Ctrl+Enter submission
        if st.session_state.get('journal_content_submitted', False):
            st.session_state.journal_content_submitted = False
            # Ensure we stay on the journal page
            st.session_state.current_page = "journal"
            analyze_button = True
        else:
            analyze_button = st.button("Analyze", key="analyze_button")
        
        # Clear previous analysis when content changes
        if 'last_analyzed_content' in st.session_state and st.session_state.last_analyzed_content != content:
            del st.session_state.last_analyzed_content
            del st.session_state.last_sentiment_data
            del st.session_state.last_themes
            del st.session_state.last_reflections
        
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
                    st.success(f"Overall Sentiment: {sentiment_category.title()}")
                elif sentiment_category == 'negative':
                    st.error(f"Overall Sentiment: {sentiment_category.title()}")
                else:
                    st.info(f"Overall Sentiment: {sentiment_category.title()}")
                
                # Display emotional content
                st.markdown("#### Emotional Content")
                emotions = sentiment_data.get('emotions', {})
                for emotion, intensity in emotions.items():
                    # Show emotions with their intensities
                    progress_color = (
                        "#4CAF50" if intensity > 66 else  # Green for high intensity
                        "#FFC107" if intensity > 33 else  # Yellow for medium intensity
                        "#90A4AE"  # Grey for low intensity
                    )
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="flex: 1;">{emotion.capitalize()}</div>
                            <div style="flex: 2; margin-left: 10px;">
                                <div style="background-color: #1E1E1E; border-radius: 10px; height: 10px; width: 100%;">
                                    <div style="background-color: {progress_color}; width: {intensity}%; height: 100%; border-radius: 10px;"></div>
                                </div>
                            </div>
                            <div style="margin-left: 10px; min-width: 45px;">{intensity:.0f}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Display key themes
                st.markdown("#### Key Themes")
                for theme in themes:
                    st.write(f"• {theme}")
            
            with col2:
                # Display reflection suggestions with better formatting
                st.markdown("#### Reflections to Consider")
                for i, reflection in enumerate(reflections, 1):
                    st.markdown(f"""
                    <div style="
                        background-color: rgba(151, 166, 195, 0.1);
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                    ">
                        <strong>{i}.</strong> {reflection}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Save button
        if st.button("Save Journal Entry"):
            # Check if content has been analyzed
            if not content.strip():
                st.error("Please write a journal entry before saving.")
            elif not hasattr(st.session_state, "last_analyzed_content") or st.session_state.last_analyzed_content != content:
                st.error("Please analyze your entry before saving.")
            else:
                # Initialize default values outside the try block to prevent UnboundLocalError
                sentiment_data = {'category': 'neutral', 'emotions': {'neutral': 50}}
                themes = []
                
                try:
                    # Get the analyzed data from session state with default fallbacks
                    if hasattr(st.session_state, "last_sentiment_data"):
                        sentiment_data = st.session_state.last_sentiment_data
                    if hasattr(st.session_state, "last_themes"):
                        themes = st.session_state.last_themes
                except Exception as e:
                    st.warning(f"Could not retrieve analysis data: {str(e)}. Using default values.")
                
                try:
                    # Save the entry
                    save_journal_entry(
                        module=module,
                        lesson=lesson,
                        prompt=prompt,
                        content=content,
                        sentiment_data=sentiment_data,
                        themes=themes
                    )
                    
                    st.success("Journal entry saved successfully!")
                    
                    # Add continue button that forces a page reload when clicked
                    if st.button("Continue to Next Lesson", key="next_lesson_button"):
                        # Directly update the module and lesson when continue button is clicked
                        if lesson < 4:
                            st.session_state.current_lesson = lesson + 1
                        elif module < 5:
                            st.session_state.current_module = module + 1
                            st.session_state.current_lesson = 1
                            
                        # Clear input for the next lesson
                        st.session_state.journal_content = ""
                        # Stay on journal page
                        st.session_state.current_page = "journal"
                        
                        # Show a message for the new lesson (this will appear on the next run)
                        st.session_state.show_lesson_advanced = True
                        st.session_state.new_module = st.session_state.current_module
                        st.session_state.new_lesson = st.session_state.current_lesson
                        
                        # Force a refresh
                        st.rerun()
                    
                    # Check if we should show the "advanced to next lesson" message
                    if st.session_state.get('show_lesson_advanced', False):
                        new_module = st.session_state.get('new_module')
                        new_lesson = st.session_state.get('new_lesson')
                        st.success(f"Advanced to Module {new_module}: {get_module_title(new_module)}, Lesson {new_lesson}: {get_lesson_title(new_module, new_lesson)}")
                        # Reset the flag so we don't show this message again
                        st.session_state.show_lesson_advanced = False
                except Exception as e:
                    st.error(f"Error saving journal entry: {str(e)}")
                    st.info("Please try analyzing your entry again before saving.")

def get_module_title(module_number):
    """Return the title for a module."""
    titles = {
        1: "Introduction",
        2: "Learning to Go Beyond Conditioning",
        3: "Remembering Your Commitment",
        4: "How Choices Influence Change",
        5: "Noticing Clarity"
    }
    return titles.get(module_number, f"Module {module_number}")

def get_lesson_title(module_number, lesson_number):
    """Return the title for a lesson."""
    lesson_titles = {
        1: {  # Module 1: Introduction
            1: "Welcome to Our Course",
            2: "Defining Crisis",
            3: "How to Understand Your Conflict",
            4: "How to Notice Cycles"
        },
        2: {  # Module 2: Learning to Go Beyond Conditioning
            1: "Learning to Go Beyond Conditioning",
            2: "Exploring Your Core Beliefs",
            3: "Closing the Gap of Cognitive Dissonance",
            4: "The Source of Creating"
        },
        3: {  # Module 3: Remembering Your Commitment
            1: "Remembering Your Commitment",
            2: "Communicating Successfully",
            3: "Learning to Compartmentalize",
            4: "Guiding Your Conversation"
        },
        4: {  # Module 4: How Choices Influence Change
            1: "How Choices Influence Change",
            2: "Taking Things Into Consideration",
            3: "Recognizing the (Co)incidences",
            4: "Focusing on Competency"
        },
        5: {  # Module 5: Noticing Clarity
            1: "Noticing Clarity",
            2: "Becoming Cognitively Aware",
            3: "Making the Connection",
            4: "Feeling the Conversion"
        }
    }
    
    if module_number in lesson_titles and lesson_number in lesson_titles[module_number]:
        return lesson_titles[module_number][lesson_number]
    else:
        return "Unknown Lesson"

def get_prompt(module, lesson):
    """Return a journaling prompt for the specified module and lesson."""
    prompts = {
        1: {  # Module 1: Introduction
            1: "Reflect on what brings you to this course and what you hope to gain from it.",
            2: "Think about areas of your life where you feel stagnant or in crisis. Write down any recurring thoughts, feelings, or beliefs contributing to your crisis.",
            3: "Describe aspects of yourself that you usually hide or avoid. What is your Conflicting self? How do they influence your behavior?",
            4: "Identify cycles or negative cycles that seem to repeat in your life. List areas where you feel like a victim."
        },
        2: {  # Module 2: Learning to Go Beyond Conditioning
            1: "Reflect on how your past conditioning affects your present choices. What patterns do you notice?",
            2: "Examine your core beliefs about yourself and the world. Which ones serve you and which ones limit you?",
            3: "Where do you experience cognitive dissonance in your life? What beliefs conflict with your actions?",
            4: "Consider how you might be the creator of your reality. What would you create if you embraced this perspective?"
        },
        3: {  # Module 3: Remembering Your Commitment
            1: "What commitment have you made to yourself that you're finding difficult to honor?",
            2: "How do you communicate with yourself during challenging times? What language do you use?",
            3: "In what areas of your life would compartmentalizing be beneficial? How might this help you stay focused?",
            4: "Think about a difficult conversation you need to have. How could you guide it toward a positive outcome?"
        },
        4: {  # Module 4: How Choices Influence Change
            1: "Reflect on a recent choice you made that led to significant change. What did you learn from this?",
            2: "What factors do you consider when making important decisions? Are there aspects you typically overlook?",
            3: "Describe coincidences or synchronicities you've experienced. What might they be teaching you?",
            4: "What skills or competencies would you like to develop further? How would these enhance your life?"
        },
        5: {  # Module 5: Noticing Clarity
            1: "Describe a moment when you experienced absolute clarity about something important. How did it feel?",
            2: "How aware are you of your thoughts and their impact on your reality? What helps you stay conscious of them?",
            3: "Reflect on connections between your thoughts, emotions, and life circumstances. What patterns do you notice?",
            4: "How have you experienced transformational change in your life? What supported this conversion process?"
        }
    }
    
    if module in prompts and lesson in prompts[module]:
        return prompts[module][lesson]
    else:
        return "Reflect on your journey so far. What insights have you gained and how are you applying them?"
