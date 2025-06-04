from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json # Added for robust JSON handling in scrape_perfume_notes

# Import AI, search, and scrape functions (to be adapted later)
from model import get_ai_response
from gsearch import get_google_blog_posts
from scrape import scrape_fragrantica_notes

# SQLAlchemy and model imports
from flask_sqlalchemy import SQLAlchemy
from database_setup import User, UserPerfume, PerfumeNote, Article, ConversationHistory

app = Flask(__name__,
            static_folder='frontend/static',
            template_folder='frontend/html')

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_CHANGE_THIS_IN_PROD')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./perfume_app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define public endpoints that do not require login
# These are the names of the view functions or blueprint.view_function
PUBLIC_ENDPOINTS = [
    'login_page',  # Route for /login.html
    'signup',      # API endpoint /api/signup
    'login',       # API endpoint /api/login
    'index',       # Route for / (which is the signup page)
    'static'       # Flask's endpoint for serving static files
]
# Additionally, allow specific paths if they are not covered by endpoints (e.g. favicons)
# For this app, /frontend/css/* and /frontend/js/* might be requested if HTML isn't using url_for('static', ...)
# However, the Flask static folder is 'frontend/static', so correct URLs should be /static/css/*
# We will rely on the 'static' endpoint and correct HTML linking.
# If CSS/JS are directly under /css or /js, they need to be explicitly allowed by path if not using 'static' endpoint.

@app.before_request
def require_login():
    # Check if the user is logged in
    is_logged_in = 'user_id' in session

    # If the user is not logged in and the requested endpoint is not public
    if not is_logged_in and request.endpoint not in PUBLIC_ENDPOINTS:
        # Also check if the request path is for static assets served directly by development server
        # (e.g., if not using the 'static' endpoint for some reason, like /css/style.css)
        # This check is a bit of a fallback. Ideally, all static assets use the 'static' endpoint.
        # For this project, static_folder is 'frontend/static', so URLs should be like /static/css/file.css
        # The 'static' endpoint check should cover these.
        # If HTML uses paths like '../css/style.css', these resolve to '/css/style.css'.
        # These won't match 'static' endpoint.
        # A more lenient check for paths (less secure, more permissive):
        # if request.path.startswith('/css/') or request.path.startswith('/js/'):
        #     return # Allow access to CSS and JS files directly by path

        app.logger.debug(f"Unauthorized access attempt to {request.endpoint} (path: {request.path}). User not logged in. Redirecting to login.")
        return redirect(url_for('login_page'))

    # If user is logged in, set g.user if needed for other parts of the app (optional here)
    # if is_logged_in:
    #     g.user = db.session.get(User, session['user_id']) # Example
    # else:
    #     g.user = None

# --- Helper function ---
def get_current_user_id():
    return session.get('user_id')

# --- Frontend Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/perfume-entry.html')
def perfume_entry_page():
    user_id = get_current_user_id() # Uses existing helper
    if not user_id:
        return redirect(url_for('login_page'))
    # If first login is done and they aren't coming from a specific edit flow (future), send to chatbot.
    # For now, this simplifies the first-time flow.
    if session.get('first_login_completed'):
         # Check if they have any perfumes, if not, maybe allow them back?
         # For now, strict redirect if first_login_completed is true.
         # This handles the case where they try to URL-navigate back after completion.
        return redirect(url_for('chatbot_page'))
    return render_template('perfume-entry.html')

@app.route('/chatbot.html')
def chatbot_page():
    if not get_current_user_id():
        return redirect(url_for('login_page'))
    return render_template('chatbot.html')

@app.route('/settings.html')
def settings_page():
    if not get_current_user_id():
        return redirect(url_for('login_page'))
    return render_template('settings.html')

@app.route('/first-time-login.html')
def first_time_login_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    # If user somehow lands here after completing first login, send to chatbot
    if session.get('first_login_completed'):
        return redirect(url_for('chatbot_page'))
    return render_template('first-time-login.html')

@app.route('/admin_dashboard.html')
def admin_dashboard_page():
    if not session.get('user_id') or not session.get('is_admin'):
        return redirect(url_for('login_page')) # Or an unauthorized page
    return render_template('admin_dashboard.html')

# --- API Endpoints ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    if db.session.query(User).filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    new_conversation_history = ConversationHistory(user_id=new_user.id, history_json=[])
    db.session.add(new_conversation_history)
    db.session.commit()

    session['user_id'] = new_user.id
    session['first_login_completed'] = new_user.first_login_completed # Store this in session too
    return jsonify({
        "message": "User registered successfully",
        "user_id": new_user.id,
        "redirect_url": url_for('first_time_login_page') # Use the function name of the route
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['first_login_completed'] = user.first_login_completed
        session['is_admin'] = user.is_admin

        redirect_url = ''
        if user.is_admin: # check_password_hash already confirmed the password for this user
            redirect_url = url_for('admin_dashboard_page')
        elif not user.first_login_completed:
            redirect_url = url_for('first_time_login_page')
        else:
            redirect_url = url_for('chatbot_page')

        return jsonify({"message": "Login successful", "user_id": user.id, "redirect_url": redirect_url}), 200
    
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/api/user/complete_first_login', methods=['POST'])
def complete_first_login():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.first_login_completed:
        user.first_login_completed = True
        db.session.commit()
        session['first_login_completed'] = True
        return jsonify({"message": "First login process completed.", "redirect_url": url_for('chatbot_page')}), 200
    else:
        # Already completed, just send them along
        return jsonify({"message": "First login already completed.", "redirect_url": url_for('chatbot_page')}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('first_login_completed', None) # Clear this on logout too
    session.pop('is_admin', None) # Clear this on logout too
    session.pop('first_login_completed', None)
    session.pop('is_admin', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/perfumes', methods=['GET', 'POST'])
def handle_perfumes():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    if request.method == 'GET':
        user_perfumes = db.session.query(UserPerfume).filter_by(user_id=user_id).all()
        perfume_names = [up.perfume_name for up in user_perfumes]
        return jsonify({"perfumes": perfume_names}), 200

    elif request.method == 'POST':
        data = request.get_json()
        perfume_name = data.get('perfumeName')
        if not perfume_name:
            return jsonify({"message": "Perfume name is required"}), 400

        existing_perfume = db.session.query(UserPerfume).filter_by(user_id=user_id, perfume_name=perfume_name).first()
        if existing_perfume:
            return jsonify({"message": "Perfume already in list"}), 409

        new_user_perfume = UserPerfume(user_id=user_id, perfume_name=perfume_name)
        db.session.add(new_user_perfume)
        db.session.commit()

        user_perfumes = db.session.query(UserPerfume).filter_by(user_id=user_id).all()
        perfume_names = [up.perfume_name for up in user_perfumes]
        return jsonify({"message": "Perfume added", "perfumes": perfume_names}), 201

@app.route('/api/chatbot', methods=['POST'])
def chatbot_interaction():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user_message_text = request.get_json().get('message')
    if not user_message_text:
        return jsonify({"message": "No message provided"}), 400

    current_user = db.session.get(User, user_id)
    if not current_user:
        session.pop('user_id', None)
        return jsonify({"message": "User not found, please log in again."}), 404

    user_conversation = db.session.query(ConversationHistory).filter_by(user_id=user_id).first()
    if not user_conversation: # Fallback, should be created at signup
        user_conversation = ConversationHistory(user_id=user_id, history_json=[])
        db.session.add(user_conversation)
        # db.session.commit() # Commit later after appending messages

    conversation_history_list = list(user_conversation.history_json) # Make a mutable copy
    conversation_history_list.append({"role": "user", "content": user_message_text})

    user_profile_data = {
        "age": current_user.age, "weight": current_user.weight, "height": current_user.height,
        "sex": current_user.sex, "style": current_user.style, "race": current_user.race
    }
    owned_perfumes_data = [{"name": p.perfume_name} for p in current_user.perfumes]

    # Call to model.py's get_ai_response (to be refactored in next plan step)
    ai_response_text = get_ai_response(
        user_profile_data,
        owned_perfumes_data,
        user_message_text,
        conversation_history_list
    )

    conversation_history_list.append({"role": "assistant", "content": ai_response_text})
    user_conversation.history_json = conversation_history_list
    db.session.commit()

    return jsonify({"response": ai_response_text}), 200

@app.route('/api/scrape_perfume_notes', methods=['POST'])
def api_get_perfume_notes(): # Renamed to avoid conflict with imported scrape_fragrantica_notes
    data = request.get_json()
    perfume_name = data.get('perfumeName')
    if not perfume_name:
        return jsonify({"message": "Perfume name is required"}), 400

    try:
        existing_notes_model = db.session.query(PerfumeNote).filter_by(perfume_name=perfume_name).first()

        if existing_notes_model and existing_notes_model.notes_json:
            notes_data = existing_notes_model.notes_json
            if isinstance(notes_data, str): # If stored as a string, try to parse
                try:
                    notes_data = json.loads(notes_data)
                except json.JSONDecodeError:
                    # Invalid JSON string, proceed to scrape
                    pass # Fall through to scraping
            if isinstance(notes_data, dict): # Successfully loaded or already a dict
                 # Basic check for expected structure, e.g. if it has 'top', 'middle', 'base'
                if all(k in notes_data for k in ('top', 'middle', 'base')):
                    return jsonify(notes_data), 200
                # else, data is not as expected, fall through to re-scrape

        scraped_notes_data = scrape_fragrantica_notes(perfume_name) # Expected to return a dict

        if scraped_notes_data and isinstance(scraped_notes_data, dict):
            if existing_notes_model:
                existing_notes_model.notes_json = scraped_notes_data # Update existing entry
            else:
                new_note_entry = PerfumeNote(perfume_name=perfume_name, notes_json=scraped_notes_data)
                db.session.add(new_note_entry)
            db.session.commit()
            return jsonify(scraped_notes_data), 200
        else:
            # If scrape_fragrantica_notes returned None or not a dict
            error_message = "Could not find or scrape notes for this perfume."
            if existing_notes_model and existing_notes_model.notes_json: # Check again if there was old valid data
                 notes_data_fallback = existing_notes_model.notes_json
                 if isinstance(notes_data_fallback, str): notes_data_fallback = json.loads(notes_data_fallback) # basic attempt
                 if isinstance(notes_data_fallback, dict): return jsonify(notes_data_fallback), 200 # Return old data if scrape failed
            return jsonify({"message": error_message}), 404

    except Exception as e:
        app.logger.error(f"Error processing perfume notes for {perfume_name}: {str(e)}")
        return jsonify({"message": f"Error processing perfume notes: {str(e)}"}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "email": user.email, # Email is read-only for this example
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "sex": user.sex,
        "style": user.style,
        "race": user.race
    }), 200

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    # Update fields if they are provided in the request
    user.age = data.get('age', user.age)
    user.weight = data.get('weight', user.weight)
    user.height = data.get('height', user.height)
    user.sex = data.get('sex', user.sex)
    user.style = data.get('style', user.style)
    user.race = data.get('race', user.race)

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating profile for user {user_id}: {str(e)}")
        return jsonify({"message": "Error updating profile"}), 500

@app.route('/api/user/password', methods=['PUT'])
def update_user_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"message": "Current password and new password are required"}), 400

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"message": "Invalid current password"}), 403

    if len(new_password) < 6: # Example: Basic password length validation
        return jsonify({"message": "New password must be at least 6 characters long"}), 400

    user.password_hash = generate_password_hash(new_password)
    try:
        db.session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating password for user {user_id}: {str(e)}")
        return jsonify({"message": "Error updating password"}), 500

# --- Placeholder for Google Login ---
@app.route('/api/login/google')
def login_google_placeholder():
    return jsonify({"message": "Google login not yet implemented"}), 501

if __name__ == '__main__':
    # For development, it can be useful to ensure tables are created if the db file is missing.
    # from database_setup import engine, Base
    # Base.metadata.create_all(bind=engine) # Creates tables if they don't exist
    app.run(debug=True, port=5000)