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
                        
                        // Update session state via Streamlit
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
                    if st.button("Continue to Next Lesson"):
                        # Only update the module and lesson when the continue button is clicked
                        if lesson < 4:
                            st.session_state.current_lesson = lesson + 1
                        elif module < 5:
                            st.session_state.current_module = module + 1
                            st.session_state.current_lesson = 1
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"Error saving journal entry: {str(e)}")
                    st.info("Please try analyzing your entry again before saving.")

def get_module_title(module_number):
    """Return the title for a module."""
    titles = {
        1: "Understanding Cycles and Patterns",
        2: "Examining Beliefs and Conditioning",
        3: "Developing Emotional Intelligence",
        4: "Cultivating Intuition and Synchronicity",
        5: "Intentional Creation"
    }
    return titles.get(module_number, f"Module {module_number}")

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
