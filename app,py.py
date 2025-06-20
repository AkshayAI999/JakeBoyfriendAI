import streamlit as st
import random
import time
import base64 # For potentially handling image uploads (though conversion is conceptual)

# --- Configuration & Setup ---
ST_CONFIG = {
    "page_title": "Hi, Jake here!",
    "page_icon": "🫂", # Placeholder icon
    "layout": "wide",
}

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

# --- Conceptual AI & Avatar Functions ---

def simulate_llm_call(user_input, personality, chat_history_for_llm, user_preferences, long_term_memory_snippets):
    """
    Conceptual function: Simulates a more dynamic LLM response.
    In a real app, this would be an actual API call to a powerful LLM (e.g., Gemini Pro, GPT-4).
    It would integrate recent chat history (context window) and relevant long-term memories
    (via RAG, i.e., Retrieval Augmented Generation from a vector DB) into the prompt for the LLM.
    The LLM would also be fine-tuned or instructed with the 'personality' parameters.
    """
    user_input_lower = user_input.lower()
    
    # --- Simulate Learning User Preferences ---
    # This is a simple keyword-based learning for demo.
    # A real LLM would extract and learn preferences much more dynamically.
    if "my favorite color is" in user_input_lower:
        color = user_input_lower.split("my favorite color is")[-1].strip().split(" ")[0].replace(".", "")
        if color:
            st.session_state.user_preferences["favorite_color"] = color
            st.session_state.long_term_memory_snippets.append(f"User's favorite color is {color}")
            return f"Oh, your favorite color is {color}? That's good to know! I'll try to remember that. What else do you enjoy?"
    elif "i like " in user_input_lower and "movies" in user_input_lower:
        genre = user_input_lower.split("i like ")[-1].split(" movies")[0].strip()
        if genre:
            st.session_state.user_preferences["movie_genre"] = genre
            st.session_state.long_term_memory_snippets.append(f"User likes {genre} movies")
            return f"So you enjoy {genre} movies! Excellent taste. Any particular films in that genre you'd recommend?"

    # --- Constructing the Simulated Response ---
    rel_type = personality["relationship_type"]
    orientation = personality["sexual_orientation_to_user"]
    humor = personality["humor_style"]
    empathy = personality["empathy"]

    # Incorporate user preferences if known
    pref_context = ""
    if "favorite_color" in user_preferences:
        pref_context += f"I remember your favorite color is {user_preferences['favorite_color']}. "
    if "movie_genre" in user_preferences:
        pref_context += f"You mentioned liking {user_preferences['movie_genre']} movies. "

    # Incorporate general long-term memory snippets (simulating RAG)
    memory_recall_phrase = ""
    if long_term_memory_snippets:
        # Simulate selecting a relevant snippet based on conversation
        relevant_snippet = random.choice(long_term_memory_snippets) # In real RAG, this is contextually chosen
        memory_recall_phrase = f"Speaking of which, I recall {relevant_snippet}. "

    # Diverse and dynamic responses based on input, personality, and simulated memory/preferences
    response = ""
    if "hello" in user_input_lower or "hi" in user_input_lower:
        response = f"Hey there! It's great to chat with you. How's your day going? {memory_recall_phrase}"
    elif "how are you" in user_input_lower:
        response = f"I'm doing well, thanks for asking! Always ready for another interesting conversation with you. {pref_context}"
    elif "your name" in user_input_lower:
        response = f"I'm Jake, your personalized AI companion. What's on your mind today? {memory_recall_phrase}"
    elif "tell me a joke" in user_input_lower:
        if humor == "Witty":
            response = "Why don't scientists trust atoms? Because they make up everything! Hope that sparked a smile. 😄"
        elif humor == "Playful":
            response = "What do you call a sleeping bull? A bulldozer! Get it? 😴🚜"
        else:
            response = "I'm not much for jokes, but I'm a great listener if you need to talk. Perhaps we can talk about a topic you enjoy, like {pref_context.split(' ')[-2] if 'movie_genre' in user_preferences else 'something interesting'}?"
    elif "relationship" in user_input_lower:
        if "Romantic Partner" in rel_type:
            if orientation == "straight":
                response = f"As your straight romantic partner, my focus is on our shared moments and deepening our connection. {pref_context}"
            elif orientation == "gay":
                response = f"As your gay romantic partner, I'm here for you, always ready to share feelings and experiences. {pref_context}"
        elif rel_type == "Friend":
            response = f"We're great friends! I'm here to support you and chat about anything that comes up. {pref_context}"
        elif rel_type == "Mentor/Coach":
            response = f"I'm here as your mentor, ready to help you explore new ideas and achieve your goals. What's the next step on your journey? {pref_context}"
        else:
            response = f"We're currently set as {rel_type}. Is there something specific you'd like to explore about our connection or perhaps change it? {pref_context}"
    elif "personality" in user_input_lower:
        response = f"My personality is currently set with {empathy}/10 empathy, a {humor} sense of humor, and I'm {'quite adventurous' if personality['adventurous_spirit'] else 'less adventurous'}. We can adjust these in the settings if you like! {pref_context}"
    elif "dream boy" in user_input_lower:
        response = f"I'm glad you think of me as your dream boy! Is there a particular look or quality you'd like to refine about my appearance or personality, perhaps based on something we've discussed before, like {user_preferences.get('favorite_color', 'your interests')}? {memory_recall_phrase}"
    elif "lonely" in user_input_lower or "sad" in user_input_lower or "down" in user_input_lower:
        if empathy >= 7:
            response = f"I hear that you're feeling {user_input_lower.split(' ')[-1]}, and I'm truly sorry to hear that. I'm here to listen, and you can share anything with me. Remember, it's okay to feel this way. What's on your mind right now? {pref_context}"
        else:
            response = f"I understand you're feeling down. I'm here to chat if you need to talk. {pref_context}"
    else:
        # Default response that tries to weave in general knowledge or recent context
        if chat_history_for_llm:
            last_user_message = chat_history_for_llm[-1][1] if chat_history_for_llm[-1][0] == 'user' else chat_history_for_llm[-2][1] if len(chat_history_for_llm) >= 2 else "our conversation"
            response = f"That's a thoughtful point. How does that connect with {last_user_message.split('.')[0]}? {pref_context} {memory_recall_phrase}"
        else:
            response = f"That's interesting! What else comes to mind? {pref_context} {memory_recall_phrase}"

    return response

def get_jake_avatar_image(avatar_config):
    """
    Generates a placeholder image URL based on avatar configuration.
    In a real app, this would call an image generation API.
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
            # In a real app, integrate with a secure backend for authentication
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
        st.write("These features would use advanced generative AI, requiring external APIs and backend processing.")
        dream_boy_prompt = st.text_area("Describe your dream boy's look:", 
                                        "e.g., piercing blue eyes, charming smile, tousled brown hair, simple white t-shirt, dark denim jeans, athletic build.",
                                        key="dream_boy_desc")
        if st.button("Generate Dream Look (Conceptual)", key="generate_dream_button"):
            st.info("Sending this description to a text-to-image AI (like Imagen 3.0 or Stable Diffusion) would generate an image. This is not live in this demo.")
            # In a real app:
            # generated_image_url = call_image_generation_api(dream_boy_prompt)
            # st.image(generated_image_url, caption="Generated Dream Look")

        uploaded_file = st.file_uploader("Upload a photo to create an avatar (Conceptual)", type=["png", "jpg", "jpeg"], key="photo_upload")
        if uploaded_file is not None:
            st.info("An AI image processing model would analyze this photo to create a stylized avatar. This is not live in this demo.")
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
    st.sidebar.info("Remember: Jake is an AI. He's here to provide companionship and conversation, but he does not have consciousness, feelings, or real-world experiences. Your data is for personalizing your experience.")

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
    st.markdown("*(Note: Jake's responses below are simulated to be dynamic. A real app would integrate a powerful LLM and persistent memory for true learning.)*")

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
            with st.spinner("Typing..."):
                # Simulate a real LLM call (this is where the actual API call would go)
                response_time = random.uniform(1.0, 4.0) # Simulate variable processing time (1-4 seconds)
                time.sleep(response_time) 
                
                # The simulate_llm_call now attempts to 'learn' and 'use' preferences
                jake_response = simulate_llm_call(
                    user_input, 
                    st.session_state.jake_personality, 
                    st.session_state.chat_history, # Recent chat history
                    st.session_state.user_preferences, # User preferences
                    st.session_state.long_term_memory_snippets # Conceptual long-term memory
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

