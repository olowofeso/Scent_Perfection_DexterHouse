import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import json

# --- Configuration for your DeepSeek API Access ---
# IMPORTANT: Replace with your actual endpoint and model if different.
# Also, NEVER hardcode your token in production. Use environment variables.
# The token type (GitHub PAT, Azure Key, etc.) must match what the endpoint expects.
DEEPSEEK_ENDPOINT = "https://models.github.ai/inference"
DEEPSEEK_MODEL = "deepseek/DeepSeek-V3-0324" # Or your desired DeepSeek model (e.g., DeepSeek-R1-0528 if available on this endpoint)

# This token type might be a GitHub Personal Access Token if it's GitHub's AI platform,
# or an Azure AI endpoint key if it's an Azure service.
# DO NOT EXPOSE YOUR ACTUAL TOKEN IN PUBLIC CODE.
# For secure usage, load from environment variable:
GITHUB_AI_TOKEN = os.getenv("GITHUB_AI_TOKEN", "xxxxx") 

# --- Initialize the AI client ---
try:
    client = ChatCompletionsClient(
        endpoint=DEEPSEEK_ENDPOINT,
        credential=AzureKeyCredential(GITHUB_AI_TOKEN),
    )
    print("Azure AI Inference client initialized successfully.")
except Exception as e:
    print(f"Error initializing Azure AI Inference client: {e}")
    print("Please ensure 'azure-ai-inference' and 'azure-core' are installed and your endpoint/token are correct.")
    # Exit or handle gracefully if client cannot be initialized
    exit()

# --- Mock Database Interaction (Replace with your actual database logic) ---
# In a real app, these would query your PostgreSQL/MongoDB database
# with user profile, owned perfumes, and perfume notes.

def get_user_profile_from_db(user_id):
    """Mocks fetching user data from a database."""
    # In a real app, this would query your 'User Data Table'
    return {
        "age": 30,
        "weight": 70,
        "height": 175,
        "sex": "male",
        "style": "classic",
        "race": "Caucasian"
    }

def get_owned_perfumes_from_db(user_id):
    """Mocks fetching owned perfumes from a database."""
    # In a real app, this would query your user's owned perfumes table
    return [
        {"name": "Dior Sauvage"},
        {"name": "Chanel Bleu de Chanel"},
        {"name": "Tom Ford Oud Wood"}
    ]

def get_perfume_notes_from_db(perfume_name):
    """Mocks fetching perfume notes from the 'Perfume Notes Table'."""
    # This data would come from your web scraping and database
    notes_data = {
        "Dior Sauvage": {"top": ["Bergamot", "Pepper"], "middle": ["Sichuan Pepper", "Geranium"], "base": ["Ambroxan", "Cedar"]},
        "Chanel Bleu de Chanel": {"top": ["Grapefruit", "Mint"], "middle": ["Ginger", "Jasmine"], "base": ["Sandalwood", "Incense"]},
        "Tom Ford Oud Wood": {"top": ["Rosewood", "Cardamom"], "middle": ["Oud", "Sandalwood"], "base": ["Vetiver", "Amber"]},
        "Jo Malone Wood Sage & Sea Salt": {"top": ["Ambrette Seeds"], "middle": ["Sea Salt"], "base": ["Sage"]},
        "Creed Aventus": {"top": ["Pineapple", "Bergamot"], "middle": ["Jasmine", "Patchouli"], "base": ["Oakmoss", "Ambergris"]}
    }
    return notes_data.get(perfume_name, {"top": [], "middle": [], "base": []})

def add_perfume_notes_to_db(perfume_name, notes):
    """Mocks adding new perfume notes to the database (after scraping)."""
    # In a real app, this would update your 'Perfume Notes Table'
    print(f"DEBUG: Simulating adding notes for '{perfume_name}' to DB: {notes}")
    # You'd have actual DB insertion logic here

# --- Main Chatbot Logic ---

# We'll store conversation history here to provide context to the bot
conversation_history = []

def get_chatbot_response(user_id, user_message_text):
    """
    Orchestrates the chatbot interaction, fetching data, prompting DeepSeek,
    and returning a formatted response.
    """
    print(f"\n--- Processing user query for user_id: {user_id} ---")
    
    # 1. Retrieve User Profile and Owned Perfumes
    user_profile = get_user_profile_from_db(user_id)
    owned_perfumes = get_owned_perfumes_from_db(user_id)

    # 2. Prepare context for the AI prompt
    profile_str = ", ".join([f"{k}: {v}" for k, v in user_profile.items()])

    owned_perfumes_details = []
    for perfume in owned_perfumes:
        notes = get_perfume_notes_from_db(perfume["name"])
        top_str = ', '.join(notes.get("top", []))
        mid_str = ', '.join(notes.get("middle", []))
        base_str = ', '.join(notes.get("base", []))
        owned_perfumes_details.append(f"- {perfume['name']} (Top: {top_str}; Middle: {mid_str}; Base: {base_str})")
    owned_perfumes_str = "\n".join(owned_perfumes_details) if owned_perfumes_details else "None"

    # Define the system message for the AI's persona
    system_prompt_content = (
        "You are a highly sophisticated and helpful AI perfume expert and fashion advisor. "
        "Your goal is to provide personalized, actionable advice based on the user's profile, "
        "their owned perfumes (including notes), the occasion, weather, and time of year. "
        "You should offer:\n"
        "1. Layering advice using their owned perfumes.\n"
        "2. New perfume recommendations (with scent notes/profile if possible) if they are looking for one, "
        "   considering their stated preferences or price range.\n"
        "3. Fashion advice that complements their style and the occasion.\n"
        "Maintain a friendly, knowledgeable, and elegant tone. Be concise but informative."
    )

    # Construct the current turn's user message
    current_user_message = (
        f"Here is my profile: {profile_str}.\n"
        f"I currently own these perfumes:\n{owned_perfumes_str}\n\n"
        f"My request: {user_message_text}\n\n"
        "Please provide your personalized recommendations."
    )
    
    # Build the full list of messages for the API call, including history
    # The first message should always be the system message
    messages_for_api = [SystemMessage(system_prompt_content)] + conversation_history + [UserMessage(current_user_message)]

    print("Sending request to DeepSeek API...")
    # print(json.dumps([m.model_dump() for m in messages_for_api], indent=2)) # For debugging prompt structure

    try:
        # 4. Call the DeepSeek API
        response = client.complete(
            messages=messages_for_api, # Send the full conversation history
            temperature=0.8,
            top_p=0.9,
            max_tokens=500,
            model=DEEPSEEK_MODEL
        )

        ai_content = response.choices[0].message.content
        # print(f"\n--- AI Raw Response ---\n{ai_content}") # Keep for debugging if needed

        # Add current user message and AI response to conversation history for next turn
        conversation_history.append(UserMessage(user_message_text)) # Add user's current query
        conversation_history.append(AssistantMessage(ai_content)) # Add AI's current response

        return ai_content

    except Exception as e:
        print(f"Error during DeepSeek API call: {e}")
        return "I apologize, but I'm currently unable to provide a recommendation. Please try again later."

# --- Interactive Chatbot Loop for Testing ---
if __name__ == "__main__":
    print("Welcome to your Perfume & Fashion AI Chatbot!")
    print("Type your questions about perfumes or fashion. Type 'exit' or 'quit' to end the chat.")

    user_id_for_testing = "test_user_001" # A fixed user ID for testing purposes

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break

        # Get response from the chatbot function
        bot_response = get_chatbot_response(user_id_for_testing, user_input)
        
        # Display the bot's response
        print(f"Chatbot: {bot_response}")

