# app.py (Conceptual Flask application)
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid # For generating unique user IDs

# Import your AI and search logic
from model import get_ai_response # Assuming get_ai_response is the main function in model.py
from gsearch import get_google_blog_posts
# Removed scrape import from here, will add specific import later if needed by other routes
from perfume_extractor import extract_perfume_names
from recommendation_engine import match_perfumes
from scrape import scrape_fragrantica_notes # Added for chatbot_interaction
# We might need access to message types for history context
# from azure.ai.inference.models import AssistantMessage

app = Flask(__name__,
            static_folder='../css', # Serve CSS files from the css directory
            template_folder='../')   # Serve HTML files from the root directory

# For session management (replace with a strong secret key in production)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key_here')

# --- Global Cache for User Conversation Histories ---
USER_CONVERSATION_HISTORIES = {}

# --- Dummy Database (Replace with a real database like SQLite, PostgreSQL, MongoDB) ---
# In a real app, this would be a database connection.
# users_db still exists for user profile info, but history is now in USER_CONVERSATION_HISTORIES
users_db = {} # {user_id: {email, password_hash, perfumes, profile_data}}
# Note: The 'conversation_history' field in users_db is no longer the primary source for model.py

# --- Helper function for secure user handling (conceptual) ---
def get_user_id():
    return session.get('user_id')

# --- Routes for Frontend HTML pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/perfume-entry.html')
def perfume_entry_page():
    if not get_user_id():
        return redirect(url_for('login_page'))
    return render_template('perfume-entry.html')

@app.route('/chatbot.html')
def chatbot_page():
    if not get_user_id():
        return redirect(url_for('login_page'))
    return render_template('chatbot.html')

@app.route('/settings.html')
def settings_page():
    if not get_user_id():
        return redirect(url_for('login_page'))
    return render_template('settings.html')

# --- API Endpoints ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Check if user already exists (conceptual)
    for user_id, user_data in users_db.items():
        if user_data['email'] == email:
            return jsonify({"message": "User with this email already exists"}), 409

    hashed_password = generate_password_hash(password)
    user_id = str(uuid.uuid4()) # Generate a unique ID
    users_db[user_id] = {
        "email": email,
        "password_hash": hashed_password,
        "perfumes": [],
        "profile_data": {},
        "conversation_history": []
    }
    session['user_id'] = user_id
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user_found = False
    for user_id, user_data in users_db.items():
        if user_data['email'] == email:
            if check_password_hash(user_data['password_hash'], password):
                session['user_id'] = user_id
                user_found = True
                return jsonify({"message": "Login successful", "user_id": user_id}), 200
            break
    
    if not user_found:
        return jsonify({"message": "Invalid email or password"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/perfumes', methods=['GET', 'POST'])
def handle_perfumes():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    if request.method == 'GET':
        return jsonify({"perfumes": users_db[user_id].get('perfumes', [])}), 200
    elif request.method == 'POST':
        data = request.get_json()
        perfume_name = data.get('perfumeName')
        if perfume_name and perfume_name not in users_db[user_id]['perfumes']:
            users_db[user_id]['perfumes'].append(perfume_name)
            return jsonify({"message": "Perfume added", "perfumes": users_db[user_id]['perfumes']}), 201
        return jsonify({"message": "Invalid input or perfume already exists"}), 400

# Integrate Chatbot
@app.route('/api/chatbot', methods=['POST'])
def chatbot_interaction():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user_message = request.get_json().get('message')
    if not user_message:
        return jsonify({"message": "No message provided"}), 400

    # Retrieve the user's history from the global cache
    current_user_history = USER_CONVERSATION_HISTORIES.get(user_id, [])
    print(f"DEBUG: Retrieved history for user {user_id}: {len(current_user_history)} messages.")

    # Extract perfume names from the user query
    extracted_perfumes = extract_perfume_names(user_message)
    print(f"DEBUG: Extracted perfume names: {extracted_perfumes}")

    # --- Prepare context for classification ---
    # Using the content of the last assistant message from the history as context
    context_for_classification = ""
    if current_user_history:
        # History items are BaseMessage objects (UserMessage, AssistantMessage)
        # We need to check the type/role of the last message
        last_message_in_history = current_user_history[-1]
        if hasattr(last_message_in_history, 'role') and last_message_in_history.role == 'assistant':
            context_for_classification = last_message_in_history.content
    print(f"DEBUG: Context for classification: '{context_for_classification[:100]}...'")


    # --- Simulated classification logic (using context_for_classification) ---
    # Replace with actual classifier: classification = classifier.classify(user_message, context_for_classification)
    classification = "unknown"
    user_message_lower = user_message.lower()

    # Simple keyword-based classification for now, context could be used by a real classifier
    if "note" in user_message_lower or "notes" in user_message_lower or "smell like" in user_message_lower or "composition" in user_message_lower:
        classification = "note"
    elif "layer" in user_message_lower and len(extracted_perfumes) >= 2:
        classification = "layer"
    elif "blog" in user_message_lower or "article" in user_message_lower: # Assuming gsearch is for blogs
        classification = "blog"
    elif "hello" in user_message_lower or "hi" in user_message_lower or "help" in user_message_lower:
        classification = "bot"
    else:
        classification = "factual"

    print(f"DEBUG: Classified intent as: {classification}")

    ai_response_text = ""
    updated_user_history = current_user_history # Initialize with current history

    if classification == 'note' and extracted_perfumes:
        fetched_notes_data = {}
        print(f"DEBUG: Attempting to fetch notes for: {extracted_perfumes}")
        for perfume_name in extracted_perfumes:
            print(f"DEBUG: Scraping notes for '{perfume_name}' (non-interactive)...")
            notes = scrape_fragrantica_notes(perfume_name, interactive=False)
            if notes:
                fetched_notes_data[perfume_name] = notes
            # else: notes remain empty for this perfume

        ai_response_text, updated_user_history = get_ai_response(
            user_id, user_message, current_history=current_user_history,
            extracted_perfumes=extracted_perfumes, layering_info=None, fetched_notes_data=fetched_notes_data
        )

    elif classification == 'layer' and len(extracted_perfumes) >= 2:
        notes1_name = extracted_perfumes[0]
        notes2_name = extracted_perfumes[1]
        print(f"DEBUG: Attempting to fetch notes for layering: {notes1_name}, {notes2_name}")
        notes1 = scrape_fragrantica_notes(notes1_name, interactive=False)
        notes2 = scrape_fragrantica_notes(notes2_name, interactive=False)

        if notes1 and notes2:
            layering_suggestions = match_perfumes(notes1, notes2)
            print(f"DEBUG: Layering suggestions for {notes1_name} & {notes2_name}: {layering_suggestions}")
            ai_response_text, updated_user_history = get_ai_response(
                user_id, user_message, current_history=current_user_history,
                extracted_perfumes=extracted_perfumes, layering_info=layering_suggestions, fetched_notes_data=None
            )
        else:
            ai_response_text = f"Sorry, I couldn't find detailed notes for {notes1_name} or {notes2_name} to suggest a layering combination. Please ensure the names are correct or try again later."
            # Even if we have an error, we should record this interaction in history
            # The model.py's get_chatbot_response handles adding user_message and this ai_response_text to history if called.
            # For a direct error message like this, we can manually add to history or decide not to.
            # For consistency, let's call get_ai_response to formulate a polite message and record history.
            # This means model needs to be robust to empty layering_info/fetched_notes even if intent was layer/note.
            # The current model call structure in the "else" block handles this.
            # So, if scraping fails, it will fall into the general "else" block.
            # To provide a more specific error for this case and still use the model for history:
            if not (notes1 and notes2): # This ensures it only runs if scraping failed
                print(f"DEBUG: Falling back to get_ai_response due to missing notes for layering for {notes1_name} or {notes2_name}")
                # We pass the error message as part of the user_message for the model to acknowledge or rephrase
                user_message_with_error_context = f"{user_message}\n\n(System note: Could not retrieve notes for {notes1_name} or {notes2_name} for layering. Please inform the user politely.)"
                ai_response_text, updated_user_history = get_ai_response(
                    user_id, user_message_with_error_context, current_history=current_user_history,
                    extracted_perfumes=extracted_perfumes, layering_info=None, fetched_notes_data=None
                )

    else: # Handles 'factual', 'blog', 'bot', or cases where note/layer conditions weren't fully met (e.g., scraping failed above)
        print(f"DEBUG: Passing to get_ai_response for classification '{classification}'")
        ai_response_text, updated_user_history = get_ai_response(
            user_id, user_message, current_history=current_user_history,
            extracted_perfumes=extracted_perfumes, layering_info=None, fetched_notes_data=None
        )

    # Store the updated history back into the global cache
    USER_CONVERSATION_HISTORIES[user_id] = updated_user_history
    print(f"DEBUG: Updated history for user {user_id}: {len(updated_user_history)} messages.")

    return jsonify({"response": ai_response_text}), 200

# The /api/scrape_perfume_notes endpoint can remain if direct scraping access is desired
# For this task, we are integrating scraping into the chatbot flow.
# @app.route('/api/scrape_perfume_notes', methods=['POST'])
# def get_perfume_notes():
# data = request.get_json()
# perfume_name = data.get('perfumeName')
# if not perfume_name:
# return jsonify({"message": "Perfume name is required"}), 400
#
# try:
# notes = scrape_fragrantica_notes(perfume_name, interactive=True) # Or False depending on desired behavior for this endpoint
# if notes:
# return jsonify(notes), 200
# else:
# return jsonify({"message": "Could not find notes for this perfume."}), 404
# except Exception as e:
# return jsonify({"message": f"Error scraping notes: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 