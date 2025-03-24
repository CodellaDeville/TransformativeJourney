"""
This module contains the content for the "From Crisis to Creating" course.
It includes module and lesson titles, descriptions, and journaling prompts.
"""

# Module Structure
MODULES = {
    1: {
        "title": "Understanding Cycles and Patterns",
        "description": "Explore how cycles and patterns shape your experience and learn to recognize when you're in crisis mode versus creation mode.",
        "lessons": {
            1: {
                "title": "Recognizing Cycles",
                "description": "Identify recurring cycles and patterns in your experience.",
                "prompt": "Reflect on a recurring pattern or cycle in your life. What triggers it, and how does it typically unfold?"
            },
            2: {
                "title": "Identifying Crisis Patterns",
                "description": "Recognize the specific patterns that emerge when you're in crisis mode.",
                "prompt": "Describe a recent moment when you felt in 'crisis mode.' What internal and external factors contributed to this experience?"
            },
            3: {
                "title": "Understanding Creation Mode",
                "description": "Explore the conditions and mindsets that facilitate creation mode.",
                "prompt": "Think of a time when you were in 'creation mode.' What conditions or mindsets enabled this state? How did it feel different from crisis mode?"
            },
            4: {
                "title": "Breaking Free from Cycles",
                "description": "Develop strategies for stepping out of limiting cycles and patterns.",
                "prompt": "What specific cycle or pattern would you like to break free from? What keeps this cycle in place, and what might help you step out of it?"
            }
        }
    },
    2: {
        "title": "Examining Beliefs and Conditioning",
        "description": "Uncover how your beliefs and conditioning influence your experience of crisis and your capacity for creation.",
        "lessons": {
            1: {
                "title": "The Origin of Beliefs",
                "description": "Explore how core beliefs form and shape your experience.",
                "prompt": "Reflect on a core belief you hold about yourself. Where did this belief originate? How has it shaped your experience?"
            },
            2: {
                "title": "Identifying Limiting Beliefs",
                "description": "Recognize beliefs that may be limiting your growth or reinforcing crisis patterns.",
                "prompt": "Identify a belief that may be limiting your growth or happiness. How does this belief affect your choices and behaviors?"
            },
            3: {
                "title": "Challenging Conditioning",
                "description": "Examine cultural, family, and social conditioning that influences your response to challenges.",
                "prompt": "Consider how your cultural, family, or social conditioning has shaped your response to challenges. What conditioning no longer serves you?"
            },
            4: {
                "title": "Creating New Beliefs",
                "description": "Develop new beliefs that support your growth and creative capacity.",
                "prompt": "What new belief would support your growth and well-being? How might embracing this belief change your experience?"
            }
        }
    },
    3: {
        "title": "Developing Emotional Intelligence",
        "description": "Build your capacity to work with emotions as information and energy that can be channeled into creative expression.",
        "lessons": {
            1: {
                "title": "Emotions as Information",
                "description": "Explore how emotions provide valuable information about your needs and values.",
                "prompt": "Describe a significant emotion you've experienced recently. What information might this emotion be offering you?"
            },
            2: {
                "title": "Working with Difficult Emotions",
                "description": "Develop strategies for processing challenging emotions in healthy ways.",
                "prompt": "Reflect on how you typically respond to difficult emotions. What strategies help you process these emotions in healthy ways?"
            },
            3: {
                "title": "Emotional Energy",
                "description": "Learn to harness emotional energy as a creative force.",
                "prompt": "How might you harness emotional energy as a creative force? Describe an emotion that feels particularly energizing to you."
            },
            4: {
                "title": "Emotional Intelligence Practices",
                "description": "Develop daily practices to cultivate emotional awareness and regulation.",
                "prompt": "What practice would help you develop greater emotional awareness in your daily life? How might this practice transform your experience?"
            }
        }
    },
    4: {
        "title": "Cultivating Intuition and Synchronicity",
        "description": "Develop your intuitive capacities and learn to recognize and work with meaningful coincidences as guidance.",
        "lessons": {
            1: {
                "title": "Recognizing Intuitive Signals",
                "description": "Learn to identify and trust your intuitive signals.",
                "prompt": "Describe a time when you experienced a strong intuitive signal. How did it feel, and how did you respond?"
            },
            2: {
                "title": "Working with Synchronicities",
                "description": "Explore the significance of meaningful coincidences in your life.",
                "prompt": "Reflect on a meaningful coincidence or synchronicity in your life. What significance did this event hold for you?"
            },
            3: {
                "title": "Deepening Intuitive Practices",
                "description": "Develop practices that strengthen your intuitive capacities.",
                "prompt": "What practices help you access your intuitive wisdom? How might you deepen these practices?"
            },
            4: {
                "title": "Co-creating with the Universe",
                "description": "Explore how intuition and synchronicity guide the co-creative process.",
                "prompt": "How do you distinguish between intuitive guidance and fear-based thinking? What helps you trust your intuition?"
            }
        }
    },
    5: {
        "title": "Intentional Creation",
        "description": "Learn to clarify your intentions and align your energy, attention, and actions to manifest what matters most to you.",
        "lessons": {
            1: {
                "title": "Clarifying Intentions",
                "description": "Learn to set clear, aligned intentions for what you want to create or experience.",
                "prompt": "What intention would you like to set for your life right now? Be as specific as possible about what you want to create or experience."
            },
            2: {
                "title": "Aligning Energy with Intentions",
                "description": "Explore how to align your thoughts, feelings, and beliefs with your intentions.",
                "prompt": "How aligned are your thoughts, feelings, and actions with your intentions? What shifts might create greater alignment?"
            },
            3: {
                "title": "Taking Inspired Action",
                "description": "Learn to distinguish between forced action and inspired action.",
                "prompt": "What inspired action could you take toward your intention? What makes this action feel inspiring rather than obligatory?"
            },
            4: {
                "title": "Living as a Conscious Creator",
                "description": "Embrace your identity as a conscious creator in all areas of your life.",
                "prompt": "How would your life change if you fully embraced your identity as a conscious creator? What would you do differently?"
            }
        }
    }
}

def get_module_title(module_number):
    """Return the title for a module."""
    if module_number in MODULES:
        return MODULES[module_number]["title"]
    return "Unknown Module"

def get_module_description(module_number):
    """Return the description for a module."""
    if module_number in MODULES:
        return MODULES[module_number]["description"]
    return ""

def get_lesson_title(module_number, lesson_number):
    """Return the title for a lesson."""
    if module_number in MODULES and lesson_number in MODULES[module_number]["lessons"]:
        return MODULES[module_number]["lessons"][lesson_number]["title"]
    return "Unknown Lesson"

def get_lesson_description(module_number, lesson_number):
    """Return the description for a lesson."""
    if module_number in MODULES and lesson_number in MODULES[module_number]["lessons"]:
        return MODULES[module_number]["lessons"][lesson_number]["description"]
    return ""

def get_lesson_prompt(module_number, lesson_number):
    """Return the journaling prompt for a lesson."""
    if module_number in MODULES and lesson_number in MODULES[module_number]["lessons"]:
        return MODULES[module_number]["lessons"][lesson_number]["prompt"]
    return "Reflect on your journey so far and what's emerging for you today."
