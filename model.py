# model.py
import os
import json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Constants for AI Configuration ---
AZURE_AI_CHAT_ENDPOINT = os.getenv("AZURE_AI_CHAT_ENDPOINT")
AZURE_AI_API_KEY = os.getenv("AZURE_AI_API_KEY")
DEFAULT_AZURE_OPENAI_DEPLOYMENT = "gpt-35-turbo" # Or your specific deployment name

# Ensure the Azure AI endpoint and key are set
if not AZURE_AI_CHAT_ENDPOINT or not AZURE_AI_API_KEY:
    raise ValueError("Azure AI chat endpoint or API key is not set. Please check your .env file.")

# Initialize the ChatCompletionsClient
# Using a simple AzureKeyCredential; for production, consider more secure options like DefaultAzureCredential
client = ChatCompletionsClient(
    endpoint=AZURE_AI_CHAT_ENDPOINT,
    credential=AzureKeyCredential(AZURE_AI_API_KEY)
)

def get_ai_response(user_profile, owned_perfumes, current_user_message, conversation_history_list):
    """
    Generates an AI response based on user profile, owned perfumes, current message, and conversation history.

    Args:
        user_profile (dict): User's profile data (age, style, etc.).
        owned_perfumes (list of dicts): List of perfumes the user owns (e.g., [{"name": "Dior Sauvage"}]).
        current_user_message (str): The latest message from the user.
        conversation_history_list (list of dicts): The existing conversation log,
                                                   e.g., [{"role": "user", "content": "..."},
                                                          {"role": "assistant", "content": "..."}].
                                                   This function expects `current_user_message` to be already
                                                   appended to this list by the caller if that's the desired flow,
                                                   or handle it internally if not. For this implementation,
                                                   we assume `current_user_message` is the newest and not yet in history.

    Returns:
        str: The AI-generated response.
    """
    if not isinstance(user_profile, dict):
        user_profile = {} # Default to empty if not a dict
    if not isinstance(owned_perfumes, list):
        owned_perfumes = [] # Default to empty list
    if not isinstance(conversation_history_list, list):
        conversation_history_list = [] # Default to empty list

    # --- Construct the System Message ---
    system_message_content = (
        "You are a sophisticated AI perfume consultant. Your goal is to help users discover new perfumes "
        "they might like based on their preferences, owned perfumes, and ongoing conversation. "
        "You can also provide information about perfumes, notes, and general fragrance advice. "
        "Be friendly, knowledgeable, and engaging. Ask clarifying questions if needed. "
        "When recommending, explain your reasoning clearly."
    )
    
    # Incorporate user profile into the system message context if available
    profile_details = ", ".join([f"{key}: {value}" for key, value in user_profile.items() if value is not None])
    if profile_details:
        system_message_content += f"\nUser Profile: {profile_details}."

    # Incorporate owned perfumes into the system message context
    if owned_perfumes:
        perfume_names = ", ".join([p.get("name", "Unknown Perfume") for p in owned_perfumes])
        system_message_content += f"\nUser Owns: {perfume_names}."
    else:
        system_message_content += "\nUser has not specified any owned perfumes yet."

    # --- Construct the message list for the API ---
    messages_for_api = [SystemMessage(content=system_message_content)]

    # Add existing conversation history
    for message_data in conversation_history_list:
        role = message_data.get("role")
        content = message_data.get("content")
        if role == "user":
            messages_for_api.append(UserMessage(content=content))
        elif role == "assistant":
            messages_for_api.append(AssistantMessage(content=content))
        # Silently ignore messages with unknown roles for now

    # Add the current user message (already appended by app.py to conversation_history_list before calling)
    # So, no need to append current_user_message separately here as it's part of the history now.

    try:
        # Make the API call to Azure AI
        response = client.complete(
            messages=messages_for_api,
            model=DEFAULT_AZURE_OPENAI_DEPLOYMENT,
            # Optional parameters (adjust as needed):
            # max_tokens=150,
            # temperature=0.7,
            # top_p=0.95,
            # frequency_penalty=0,
            # presence_penalty=0,
            # stop=None # e.g., ["\n"]
        )

        # Extract the response content
        if response.choices and len(response.choices) > 0:
            ai_content = response.choices[0].message.content
            return ai_content if ai_content else "I'm sorry, I couldn't generate a response at this moment."
        else:
            return "I'm sorry, I received an empty response from the AI service."

    except Exception as e:
        print(f"Error calling Azure AI: {e}")
        # In a real app, you might want to log this error more formally
        return "I'm having trouble connecting to my brain right now. Please try again later."

# --- Placeholder for future functions (e.g., specific perfume matching) ---
def find_similar_perfumes(perfume_name, user_preferences):
    """
    (Placeholder) Finds perfumes similar to a given one, considering user preferences.
    """
    # This would involve logic to query a perfume database, compare notes,
    # factor in user_preferences (e.g., preferred notes, style, brands).
    return f"Placeholder: Finding perfumes similar to {perfume_name} based on {user_preferences}."

if __name__ == '__main__':
    # --- Example Usage (for testing model.py directly) ---
    print("Testing AI response generation...")

    # Mock data for testing
    mock_user_profile = {
        "age": 30,
        "style": "elegant",
        "preferred_notes": ["vanilla", "sandalwood"]
    }
    mock_owned_perfumes = [
        {"name": "Chanel No. 5"},
        {"name": "Dior J'adore"}
    ]
    mock_history = [
        {"role": "user", "content": "Hi, I'm looking for a new perfume."},
        {"role": "assistant", "content": "Hello! I can help with that. What kind of scents do you usually enjoy?"},
    ]

    # Scenario 1: User asks a general question, history includes this message
    print("\n--- Scenario 1: General question with history ---")
    test_message_1 = "I like floral and woody notes."
    history_for_scenario1 = mock_history + [{"role": "user", "content": test_message_1}]
    ai_response_1 = get_ai_response(
        mock_user_profile,
        mock_owned_perfumes,
        test_message_1, # current_user_message is the last one in history
        history_for_scenario1
    )
    print(f"User: {test_message_1}")
    print(f"AI: {ai_response_1}")

    # Scenario 2: User asks for a recommendation based on owned perfumes
    print("\n--- Scenario 2: Recommendation based on owned ---")
    test_message_2 = "Can you recommend something new based on what I own?"
    history_for_scenario2 = mock_history + [
        {"role": "user", "content": "I like floral and woody notes."}, # from previous turn
        {"role": "assistant", "content": ai_response_1}, # AI's response from previous turn
        {"role": "user", "content": test_message_2} # current message
    ]
    ai_response_2 = get_ai_response(
        mock_user_profile,
        mock_owned_perfumes,
        test_message_2,
        history_for_scenario2
    )
    print(f"User: {test_message_2}")
    print(f"AI: {ai_response_2}")

    # Scenario 3: No specific profile or owned perfumes, fresh conversation
    print("\n--- Scenario 3: Fresh conversation, no profile/perfumes ---")
    test_message_3 = "What are some popular men's fragrances for summer?"
    history_for_scenario3 = [{"role": "user", "content": test_message_3}]
    ai_response_3 = get_ai_response(
        {}, # Empty profile
        [], # No owned perfumes
        test_message_3,
        history_for_scenario3
    )
    print(f"User: {test_message_3}")
    print(f"AI: {ai_response_3}")

    # Scenario 4: Conversation history is empty, first message from user
    print("\n--- Scenario 4: Empty history, first message ---")
    test_message_4 = "Tell me about citrus notes."
    history_for_scenario4 = [{"role": "user", "content": test_message_4}] # History includes this first message
    ai_response_4 = get_ai_response(
        mock_user_profile,
        [], # No owned perfumes yet
        test_message_4,
        history_for_scenario4
    )
    print(f"User: {test_message_4}")
    print(f"AI: {ai_response_4}")
```
