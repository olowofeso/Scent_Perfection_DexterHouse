# app.py (Conceptual Flask application)
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid # For generating unique user IDs

# Import your AI and search logic
from model import get_ai_response # Assuming get_ai_response is the main function in model.py
from gsearch import get_google_blog_posts
from scrape import scrape_fragrantica_notes

app = Flask(__name__,
            static_folder='../css', # Serve CSS files from the css directory
            template_folder='../')   # Serve HTML files from the root directory

# For session management (replace with a strong secret key in production)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key_here')

# --- Dummy Database (Replace with a real database like SQLite, PostgreSQL, MongoDB) ---
# In a real app, this would be a database connection.
users_db = {} # {user_id: {email, password_hash, perfumes, profile_data, conversation_history}}

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

    # Retrieve conversation history for the current user
    conversation_history = users_db[user_id].get('conversation_history', [])

    # Call your AI model
    # Potentially integrate gsearch and scrape within get_ai_response or call them here
    ai_response_text = get_ai_response(user_message, conversation_history)

    # Update conversation history
    users_db[user_id]['conversation_history'] = conversation_history # get_ai_response should update this list

    return jsonify({"response": ai_response_text}), 200

# Integrate perfume scraping (if needed as a separate endpoint or within chatbot)
@app.route('/api/scrape_perfume_notes', methods=['POST'])
def get_perfume_notes():
    data = request.get_json()
    perfume_name = data.get('perfumeName')
    if not perfume_name:
        return jsonify({"message": "Perfume name is required"}), 400

    try:
        notes = scrape_fragrantica_notes(perfume_name)
        if notes:
            return jsonify(notes), 200
        else:
            return jsonify({"message": "Could not find notes for this perfume."}), 404
    except Exception as e:
        return jsonify({"message": f"Error scraping notes: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 