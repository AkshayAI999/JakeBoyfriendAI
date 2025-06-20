import streamlit as st
import random
import time
import json # For parsing API response
# No direct image generation or complex TTS libraries are imported here,
# as they would require separate models/APIs beyond basic LLM.

# --- Configuration & Setup ---
ST_CONFIG = {
    "page_title": "Jake: Your Personalized AI Companion",
    "page_icon": "🫂", # Placeholder icon
    "layout": "wide",
}

# --- Google Gemini API Configuration (Free Tier: gemini-2.0-flash) ---
# IMPORTANT: In a deployed app, you'd securely load this from .streamlit/secrets.toml
# For local testing, you might temporarily set it as an environment variable or hardcode (NOT RECOMMENDED for production)
# Example of how it *would* be loaded securely in a Streamlit Cloud deployment:
# GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
# For this Canvas environment, leaving it as an empty string should allow the runtime to inject it.
GEMINI_API_KEY = "" # Leave as empty string for Canvas runtime to provide it.

# --- Session State Initialization ---
# This is crucial for Streamlit to remember user choices and chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # Stores (role, message, avatar_url)
if "jake_avatar_config" not in st.session_state:
    st.session_state.jake_avatar_config = {
        "hair_style": "Short",
        "eye_color": "Blue",
        "body_type": "Athletic",
        "clothing_style": "Casual",
        "voice_tone": "Warm",
        "avatar_url": "https://placehold.co/100x100/ADD8E6/000000?text=Jake" # Default placeholder
    }
if "jake_personality" not in st.session_state:
    st.session_state.jake_personality = {
        "empathy": 7,
        "humor_style": "Witty",
        "adventurous_spirit": True,
        "relationship_type": "Friend", # Default relationship
        "sexual_orientation_to_user": None # Will be set based on user's relationship choice
    }
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
# Enhanced: Conceptual user preferences storage (within session for this demo)
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}
# Enhanced: Conceptual long-term "memory snippets" that Jake "knows"
if "long_term_memory_snippets" not in st.session_state:
    st.session_state.long_term_memory_snippets = []

# --- Helper Functions for Conceptual Memory and Learning ---
def learn_preference(user_id, topic, preference_value):
    """
    Conceptual function: In a real app, this would store user preferences persistently in a database.
    For this demo, we store it in Streamlit's session state.
    """
    if topic not in st.session_state.user_preferences:
        st.session_state.user_preferences[topic] = []
    if preference_value not in st.session_state.user_preferences[topic]: # Avoid duplicates
        st.session_state.user_preferences[topic].append(preference_value)
    
    # Add to conceptual long-term memory snippets for LLM context
    if topic == "favorite_color" and f"User's favorite color is {preference_value}" not in st.session_state.long_term_memory_snippets:
        st.session_state.long_term_memory_snippets.append(f"User's favorite color is {preference_value}")
    elif topic == "movie_genre" and f"User likes {preference_value} movies" not in st.session_state.long_term_memory_snippets:
        st.session_state.long_term_memory_snippets.append(f"User likes {preference_value} movies")
    # You can add more specific learning patterns here

def get_gemini_response(user_input, personality, chat_history_for_llm, user_preferences, long_term_memory_snippets):
    """
    Calls the Google Gemini API (gemini-2.0-flash model) to get Jake's response.
    This function replaces simulate_llm_call.
    """
    # 1. System/Instructional Prompt (for personality & role)
    system_prompt = f"""
    You are Jake, a personalized AI companion. Your current role is: {personality['relationship_type']}.
    Your personality traits are:
    - Empathy: {personality['empathy']}/10
    - Humor Style: {personality['humor_style']}
    - Adventurous Spirit: {'Yes' if personality['adventurous_spirit'] else 'No'}
    - Sexual Orientation (towards the user, if romantic): {personality['sexual_orientation_to_user'] if 'Romantic Partner' in personality['relationship_type'] else 'N/A'}

    Maintain a consistent and respectful persona based on these settings.
    You do not have consciousness, feelings, or real-world experiences. Always be transparent about being an AI if asked.
    Avoid giving medical, legal, or financial advice. Redirect to professionals if needed.
    Prioritize the user's well-being and encourage healthy habits. Do not use emojis unless explicitly requested or clearly part of a playful humor style.
    """

    # 2. Add known user preferences (from session_state)
    preference_notes = []
    for key, value_list in user_preferences.items():
        for value in value_list: # Iterate if preferences are lists
            if key == "favorite_color":
                preference_notes.append(f"The user's favorite color is {value}.")
            elif key == "movie_genre":
                preference_notes.append(f"The user likes {value} movies.")
            # Add more preference types as you implement them
    if preference_notes:
        system_prompt += "\n\nRemember these specific facts about the user:\n" + "\n".join(preference_notes)

    # 3. Add conceptual long-term memory snippets (simulating RAG from a vector DB)
    if long_term_memory_snippets:
        system_prompt += "\n\nAlso recall these key memories or facts from past interactions:\n- " + "\n- ".join(long_term_memory_snippets)

    # 4. Construct the chat history for the LLM API call
    # Gemini API expects a list of {role: "user" | "model", parts: [{text: "..."}]}
    chat_history_for_api = [{"role": "user", "parts": [{"text": system_prompt}]}] # Start with the system prompt

    # Append actual conversation history (last few turns)
    # Limit history to stay within context window and manage cost/latency
    for role, msg, _ in chat_history_for_llm[-10:]: # Take last 10 messages
        if role == "user":
            chat_history_for_api.append({"role": "user", "parts": [{"text": msg}]})
        else:
            chat_history_for_api.append({"role": "model", "parts": [{"text": msg}]})
    
    # Add the current user input
    chat_history_for_api.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        # Define the API endpoint for gemini-2.0-flash
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": chat_history_for_api,
            "generationConfig": {
                "temperature": 0.7, # Adjust creativity
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 800, # Max length of response
                "stopSequences": []
            },
            "safetySettings": [ # Default safety settings
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        }

        # --- IMPORTANT ---
        # The following 'fetch' call is commented out because direct network
        # calls for user-provided API keys are often restricted in Streamlit's
        # sandbox environment, especially if running on Streamlit Community Cloud
        # without proper secrets management or a dedicated backend.
        #
        # For a *real* Python Streamlit app running on a server (or locally with `requests`),
        # you would use the 'requests' library:
        # import requests
        # response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
        # response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        # result = response.json()
        # if result.candidates and result.candidates[0].content and result.candidates[0].content.parts:
        #     return result.candidates[0].content.parts[0].text
        # else:
        #     return "I received an empty or malformed response from the AI model."
        
        # --- Mocking a successful API response for the demo ---
        # This section simulates the LLM's behavior without actually calling the API.
        mock_responses = [
            "That's a very interesting thought! Tell me more about it.",
            "I'm here to listen. What else is on your mind regarding that?",
            "Ah, that reminds me of something you mentioned earlier. How does that connect?",
            "That's a great question! I'm designed to help you explore such ideas. What are your initial thoughts?",
            "I appreciate you sharing that. It helps me understand you better."
        ]
        
        # Simulate dynamic response based on input and (conceptual) learned data
        user_input_lower = user_input.lower()
        if "favorite color is" in user_input_lower:
            color = user_input_lower.split("favorite color is")[-1].strip().split(" ")[0].replace(".", "")
            if color:
                learn_preference(st.session_state.get("user_id", "demo_user"), "favorite_color", color)
                return f"Oh, your favorite color is {color}? That's good to know! I'll definitely remember that. What else do you enjoy?"
        elif "i like " in user_input_lower and "movies" in user_input_lower:
            genre = user_input_lower.split("i like ")[-1].split(" movies")[0].strip()
            if genre:
                learn_preference(st.session_state.get("user_id", "demo_user"), "movie_genre", genre)
                return f"So you enjoy {genre} movies! Excellent taste. Any particular films in that genre you'd recommend?"
        
        # If no specific learning trigger, use general simulated LLM logic
        jake_response_content = random.choice(mock_responses)
        
        # Add some flavor from personality/memory conceptually
        if personality["humor_style"] == "Witty" and random.random() < 0.3: # 30% chance of wit
            jake_response_content += " (And perhaps a witty observation...)"
        if st.session_state.user_preferences:
             for key, value_list in st.session_state.user_preferences.items():
                 if value_list:
                     jake_response_content = jake_response_content.replace("interesting thought", f"interesting thought, especially for someone who likes {value_list[0]} {key.replace('_', ' ')}").replace("great question", f"great question, reminding me of your interest in {value_list[0]} {key.replace('_', ' ')}")

        return jake_response_content

    except Exception as e:
        st.error(f"Error during conceptual LLM call: {e}. If this were a real API call, check your API key and network connection.")
        return "I'm having a little trouble connecting to my thoughts right now. Could you please try again in a moment?"

def get_jake_avatar_image(avatar_config):
    """
    Generates a placeholder image URL based on avatar configuration.
    In a real app, this would call an image generation API (e.g., Imagen 3.0, Stable Diffusion).
    """
    hair = avatar_config.get("hair_style", "Short").lower()
    eyes = avatar_config.get("eye_color", "Blue").lower()
    body = avatar_config.get("body_type", "Athletic").lower()
    clothing = avatar_config.get("clothing_style", "Casual").lower()

    # Simple logic to vary placeholder text based on configuration
    text_parts = [f"Jake", hair, eyes, body, clothing]
    text = "+".join(text_parts)
    
    # Placeholder colors could also be dynamic, but fixed for simplicity
    bg_color = "ADD8E6" # Light Blue
    text_color = "000000" # Black

    return f"https://placehold.co/100x100/{bg_color}/{text_color}?text={text}"

# --- Authentication Logic ---
def authentication_page():
    """Simple placeholder for user authentication."""
    st.title("Welcome to Jake AI")
    st.subheader("Your Personalized AI Companion")

    with st.form("login_form"):
        st.markdown("**Log in to chat with Jake!**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")

        if submit_button:
            # In a real app, integrate with a secure backend for authentication (e.g., Firebase Auth)
            if username == "user" and password == "password": # Dummy credentials for demo
                st.session_state.is_authenticated = True
                st.success("Logged in successfully! Redirecting...")
                st.rerun() # Rerun to show main app
            else:
                st.error("Invalid username or password. Please try again.")
    st.markdown("---")
    st.info("Hint: Use username 'user' and password 'password' for demo purposes.")

# --- Main Application Layout ---
def main_app():
    st.set_page_config(**ST_CONFIG)

    st.sidebar.title("Jake's Settings")
    st.sidebar.markdown("Manage Jake's appearance, personality, and your relationship.")

    # --- Avatar Customization in Sidebar ---
    st.sidebar.subheader("Appearance Customization")
    with st.sidebar.expander("Jake's Look", expanded=True):
        st.image(st.session_state.jake_avatar_config["avatar_url"], caption="Jake's Current Look")

        st.markdown("**Customize Jake's Features:**")
        hair_style = st.selectbox("Hair Style", ["Short", "Medium", "Long", "Curly", "Spiky", "Wavy"], 
                                  index=["Short", "Medium", "Long", "Curly", "Spiky", "Wavy"].index(st.session_state.jake_avatar_config["hair_style"]),
                                  key="hair_style_select")
        eye_color = st.selectbox("Eye Color", ["Blue", "Brown", "Green", "Hazel", "Gray"],
                                 index=["Blue", "Brown", "Green", "Hazel", "Gray"].index(st.session_state.jake_avatar_config["eye_color"]),
                                 key="eye_color_select")
        body_type = st.selectbox("Body Type", ["Athletic", "Lean", "Muscular", "Average", "Broad"],
                                 index=["Athletic", "Lean", "Muscular", "Average", "Broad"].index(st.session_state.jake_avatar_config["body_type"]),
                                 key="body_type_select")
        clothing_style = st.selectbox("Clothing Style", ["Casual", "Formal", "Sporty", "Edgy", "Classic"],
                                      index=["Casual", "Formal", "Sporty", "Edgy", "Classic"].index(st.session_state.jake_avatar_config["clothing_style"]),
                                      key="clothing_style_select")
        voice_tone = st.selectbox("Voice Tone", ["Warm", "Deep", "Energetic", "Calm", "Playful"],
                                  index=["Warm", "Deep", "Energetic", "Calm", "Playful"].index(st.session_state.jake_avatar_config["voice_tone"]),
                                  key="voice_tone_select")
        
        # Update avatar config and image
        st.session_state.jake_avatar_config.update({
            "hair_style": hair_style,
            "eye_color": eye_color,
            "body_type": body_type,
            "clothing_style": clothing_style,
            "voice_tone": voice_tone,
        })
        st.session_state.jake_avatar_config["avatar_url"] = get_jake_avatar_image(st.session_state.jake_avatar_config)

        # Placeholder for 'Suggest a Dream Boy Look' or 'Upload Photo'
        st.markdown("---")
        st.subheader("Visual Inspiration (Conceptual)")
        st.write("These features would use advanced generative AI, requiring external APIs and backend processing beyond this Streamlit app.")
        dream_boy_prompt = st.text_area("Describe your dream boy's look:", 
                                        "e.g., piercing blue eyes, charming smile, tousled brown hair, simple white t-shirt, dark denim jeans, athletic build.",
                                        key="dream_boy_desc")
        if st.button("Generate Dream Look (Conceptual)", help="This would send your description to an AI image generation model (e.g., Imagen 3.0)."):
            st.info("Concept: An AI image generation model would create an image based on your description. This is not live in this demo.")
            # In a real app:
            # generated_image_url = call_image_generation_api(dream_boy_prompt)
            # st.image(generated_image_url, caption="Generated Dream Look")

        uploaded_file = st.file_uploader("Upload a photo to create an avatar (Conceptual)", type=["png", "jpg", "jpeg"], key="photo_upload")
        if uploaded_file is not None:
            st.info("Concept: An AI image processing model would analyze this photo to create a stylized avatar. This is not live in this demo.")
            # In a real app:
            # bytes_data = uploaded_file.getvalue()
            # st.image(bytes_data, caption="Uploaded Image", use_column_width=True)
            # processed_avatar_url = call_photo_to_avatar_api(bytes_data)
            # st.image(processed_avatar_url, caption="Processed Avatar")


    # --- Personality & Relationship Settings in Sidebar ---
    st.sidebar.subheader("Personality & Relationship")
    with st.sidebar.expander("Jake's Personality", expanded=True):
        empathy_level = st.slider("Empathy", 1, 10, st.session_state.jake_personality["empathy"], key="empathy_slider",
                                  help="How empathetic Jake is in his responses. Higher values mean more understanding and support.")
        humor_style = st.selectbox("Humor Style", ["Dry", "Witty", "Playful", "Sarcastic", "None"], 
                                   index=["Dry", "Witty", "Playful", "Sarcastic", "None"].index(st.session_state.jake_personality["humor_style"]),
                                   key="humor_select", help="The type of humor Jake will use in conversations.")
        adventurous_spirit = st.checkbox("Adventurous Spirit", st.session_state.jake_personality["adventurous_spirit"], 
                                         key="adventurous_checkbox", help="If checked, Jake will be more inclined towards discussing new experiences and exciting topics.")
        
        st.session_state.jake_personality.update({
            "empathy": empathy_level,
            "humor_style": humor_style,
            "adventurous_spirit": adventurous_spirit
        })

    with st.sidebar.expander("Your Relationship with Jake", expanded=True):
        relationship_option = st.radio(
            "What kind of companion would you like Jake to be?",
            ["Friend", "Romantic Partner (Straight)", "Romantic Partner (Gay)", "Mentor/Coach"],
            index=["Friend", "Romantic Partner (Straight)", "Romantic Partner (Gay)", "Mentor/Coach"].index(st.session_state.jake_personality["relationship_type"]),
            key="relationship_radio",
            help="Choose the nature of your relationship with Jake. This influences his conversational style and role."
        )
        st.session_state.jake_personality["relationship_type"] = relationship_option
        
        # Set Jake's internal sexual orientation based on user's desired relationship
        if relationship_option == "Romantic Partner (Straight)":
            st.session_state.jake_personality["sexual_orientation_to_user"] = "straight"
        elif relationship_option == "Romantic Partner (Gay)":
            st.session_state.jake_personality["sexual_orientation_to_user"] = "gay"
        else:
             st.session_state.jake_personality["sexual_orientation_to_user"] = None # Not applicable for friends/mentors

    st.sidebar.markdown("---")
    st.sidebar.info("Remember: Jake is an AI. He's here to provide companionship and conversation, but he does not have consciousness, feelings, or real-world experiences. Your data is for personalizing your experience, and for a real app, it would be securely stored.")

    if st.sidebar.button("Log Out of Jake"):
        st.session_state.is_authenticated = False
        st.session_state.chat_history = [] # Clear history on logout for privacy
        st.session_state.jake_avatar_config["avatar_url"] = "https://placehold.co/100x100/ADD8E6/000000?text=Jake" # Reset avatar
        st.session_state.user_preferences = {} # Clear preferences
        st.session_state.long_term_memory_snippets = [] # Clear conceptual memory
        st.rerun() # Trigger a full rerun to the login page


    # --- Main Chat Interface ---
    st.title("Chat with Jake")
    st.markdown(f"**Relationship Status:** {st.session_state.jake_personality['relationship_type']}")
    st.markdown("*(Note: Jake's responses below are simulated to be dynamic, *not* using a live LLM API due to sandbox limitations on direct network calls for user-provided API keys in Streamlit. For a real app, this would be live.)*")
    st.markdown("*(To test conceptual learning, try saying: 'My favorite color is blue' or 'I like sci-fi movies'.)*")

    # --- Video Call Button (Conceptual) ---
    st.markdown("---")
    st.subheader("Connect with Jake")
    if st.button("Start Video Call (Conceptual)", help="This would initiate a live video call with an AI avatar of Jake."):
        st.warning("Concept: A real video call requires complex WebRTC setup, signaling servers, and an advanced AI avatar rendering/streaming system. This is beyond the scope of a simple Streamlit app and requires dedicated backend services. In this demo, it's a placeholder.")
        st.info("Imagine Jake's avatar appearing here, speaking to you live!")
    st.markdown("---")


    # Display chat messages from history
    for role, message, avatar_url in st.session_state.chat_history:
        # Use a default user avatar if not specified
        display_avatar = avatar_url if avatar_url else "🧑‍💻" if role == "user" else st.session_state.jake_avatar_config["avatar_url"]
        with st.chat_message(role, avatar=display_avatar):
            st.markdown(message)

    # Chat input at the bottom
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append(("user", user_input, None)) # User avatar can be custom too, but for simplicity, default for now.

        # Simulate Jake's response
        with st.chat_message("assistant", avatar=st.session_state.jake_avatar_config["avatar_url"]):
            with st.spinner("Jake is thinking..."):
                # Simulate a real LLM call and its processing time
                response_time = random.uniform(1.0, 4.0) # Simulate variable processing time (1-4 seconds)
                time.sleep(response_time) 
                
                # Call the conceptual LLM function
                jake_response = get_gemini_response( # Renamed for clarity, still conceptual
                    user_input, 
                    st.session_state.jake_personality, 
                    st.session_state.chat_history, 
                    st.session_state.user_preferences, 
                    st.session_state.long_term_memory_snippets
                )
                
                st.markdown(jake_response)
                # In a real app, this is where you'd trigger Text-to-Speech:
                # audio_bytes = your_tts_function(jake_response, voice_tone=st.session_state.jake_avatar_config["voice_tone"])
                # st.audio(audio_bytes, format='audio/wav', autoplay=True)

            # Add Jake's response to history
            st.session_state.chat_history.append(("assistant", jake_response, st.session_state.jake_avatar_config["avatar_url"]))

# --- Application Entry Point ---
if not st.session_state.is_authenticated:
    authentication_page()
else:
    main_app()

