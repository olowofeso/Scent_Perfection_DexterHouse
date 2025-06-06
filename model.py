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

# Global conversation_history removed. It will be passed as a parameter.

def get_chatbot_response(user_id, user_message_text, current_history: list, extracted_perfumes: list[str] = None, layering_info: dict = None, fetched_notes_data: dict = None):
    """
    Orchestrates the chatbot interaction, fetching data, prompting DeepSeek,
    and returning a formatted response along with the updated history.

    Args:
        user_id (str): The ID of the user.
        user_message_text (str): The raw text of the user's message.
        current_history (list): The current conversation history for this user.
        extracted_perfumes (list[str], optional): A list of perfume names extracted from the query.
        layering_info (dict, optional): A dictionary with layering suggestions from match_perfumes.
        fetched_notes_data (dict, optional): A dictionary where keys are perfume names and
                                             values are their scraped notes.
    Returns:
        tuple: (ai_content, updated_history)
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
    user_context_parts = [
        f"Here is my profile: {profile_str}.",
        f"I currently own these perfumes:\n{owned_perfumes_str}"
    ]

    if extracted_perfumes:
        user_context_parts.append(f"The user's query mentions these perfumes: {', '.join(extracted_perfumes)}.")

    if layering_info and extracted_perfumes and len(extracted_perfumes) >= 2:
        # Assuming the first two extracted_perfumes are the ones used for layering_info
        p1_name = extracted_perfumes[0]
        p2_name = extracted_perfumes[1]
        layering_details = (
            f"Layering suggestion input for {p1_name} and {p2_name}: " # Changed "details" to "input"
            f"Shared Base Notes: {layering_info.get('shared_base_notes', 'N/A')}, "
            f"Shared Top Notes: {layering_info.get('shared_top_notes', 'N/A')}, "
            f"Shared Middle Notes: {layering_info.get('shared_middle_notes', 'N/A')}, "
            f"Overall Compatibility Score: {layering_info.get('compatibility_score', 'N/A')}. " # Added "Overall"
            "Please use this data to advise the user on layering these two perfumes. Explain the compatibility based on these shared notes."
        )
        user_context_parts.append(layering_details)

    if fetched_notes_data:
        notes_details_parts = ["Here are the notes for perfumes found in the query:"]
        for perfume_name, notes in fetched_notes_data.items():
            top_n = ', '.join(notes.get('top', ['N/A']))
            middle_n = ', '.join(notes.get('middle', ['N/A']))
            base_n = ', '.join(notes.get('base', ['N/A']))
            notes_details_parts.append(f"- {perfume_name}: Top notes: [{top_n}]; Middle notes: [{middle_n}]; Base notes: [{base_n}].")
        notes_details_parts.append("Please use these notes to answer questions about perfume composition or scent profile.")
        user_context_parts.append("\n".join(notes_details_parts))

    user_context_parts.append(f"My core request: {user_message_text}") # Changed "My request" to "My core request" for clarity
    user_context_parts.append("Please provide your personalized recommendations based on all the above context.") # Changed "recommendations" to "recommendations based on all the above context"

    current_user_message = "\n\n".join(user_context_parts)
    
    # Build the full list of messages for the API call, including history
    # The first message should always be the system message.
    # History is passed in, so we use it directly.
    messages_for_api = [SystemMessage(system_prompt_content)] + current_history + [UserMessage(current_user_message)]

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

        # Add current user message and AI response to the history that was passed in
        updated_history = current_history + [UserMessage(user_message_text), AssistantMessage(ai_content)]

        return ai_content, updated_history

    except Exception as e:
        print(f"Error during DeepSeek API call: {e}")
        # Return the original history in case of error to avoid losing it
        return "I apologize, but I'm currently unable to provide a recommendation. Please try again later.", current_history

# --- Interactive Chatbot Loop for Testing ---
if __name__ == "__main__":
    print("Welcome to your Perfume & Fashion AI Chatbot!")
    print("Type your questions about perfumes or fashion. Type 'exit' or 'quit' to end the chat.")

    user_id_for_testing = "test_user_001" # A fixed user ID for testing purposes
    test_history = [] # Initialize history for the test loop

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break

        # Get response from the chatbot function
        # Example of passing mock data for new parameters:
        mock_extracted = []
        mock_layering_info = None
        mock_fetched_notes = None

        # Simulate data for a "layer" query
        if "layer" in user_input.lower() and "dior sauvage" in user_input.lower() and "tobacco vanille" in user_input.lower():
            mock_extracted = ["Dior Sauvage", "Tom Ford Tobacco Vanille"]
            mock_layering_info = {
                'base_note_score': 1,
                'shared_base_notes': ['Ambroxan', 'Vanilla'],
                'shared_top_notes': ['Bergamot'],
                'shared_middle_notes': ['Pepper', 'Tobacco Blossom'],
                'compatibility_score': 2.5
            }

        # Simulate data for a "notes" query
        elif "notes" in user_input.lower() and "ysl myslf" in user_input.lower():
            mock_extracted = ["Yves Saint Laurent MYSLF Eau de Parfum"]
            mock_fetched_notes = {
                "Yves Saint Laurent MYSLF Eau de Parfum": {
                    "top": ["Bergamot", "Calabrian bergamot"],
                    "middle": ["Orange Blossom"],
                    "base": ["Ambrofix", "Patchouli", "Woods"]
                }
            }

        # Call get_chatbot_response with the current test_history
        bot_response, test_history = get_chatbot_response(
            user_id_for_testing,
            user_input,
            current_history=test_history, # Pass the current history
            extracted_perfumes=mock_extracted,
            layering_info=mock_layering_info,
            fetched_notes_data=mock_fetched_notes
        )
        
        # Display the bot's response
        print(f"Chatbot: {bot_response}")

