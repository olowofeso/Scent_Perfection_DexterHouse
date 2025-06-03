import requests
import os
import json
import logging
import time
from datetime import datetime

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Google Custom Search API Configuration ---
# WARNING: For production, set these as environment variables and REMOVE the default values.
# For example, in your terminal (before running the script):
# export GOOGLE_API_KEY="AIzaSyB6h1cZyOlsE6zZyoV3b471cPGRPxKhlxA"
# export GOOGLE_CSE_ID="754fb4283ecf34455"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyB6h1cZyOlsE6zZyoV3b471cPGRPxKhlxA") 
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "754fb4283ecf34455") 

SEARCH_API_BASE_URL = "https://www.googleapis.com/customsearch/v1"

# --- API Quotas and Limits ---
MAX_RESULTS_PER_REQUEST = 10 # Max 10 results per single API call from Google CSE API
DEFAULT_MAX_TOTAL_RESULTS = 20 # Default total results desired across all pages
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5 

class GoogleSearchAPIError(Exception):
    """Custom exception for Google Search API errors."""
    pass

def _make_single_search_request(query, start_index, num_results):
    """
    Internal helper to make a single request to the Google Custom Search API.
    Handles authentication, parameters, and basic retries for transient errors.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise GoogleSearchAPIError(
            "Google API Key (GOOGLE_API_KEY) or Custom Search Engine ID (GOOGLE_CSE_ID) "
            "environment variables are not set. Please set them or provide valid defaults."
        )

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results, 
        "start": start_index 
    }

    retries = 0
    while retries < MAX_RETRIES:
        try:
            logger.info(f"Attempt {retries + 1}/{MAX_RETRIES}: Fetching results for '{query}' (start={start_index}, num={num_results})")
            response = requests.get(SEARCH_API_BASE_URL, params=params, timeout=15) # 15-second timeout
            response.raise_for_status() # Raise HTTPError for 4xx/5xx responses
            
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            error_code = http_err.response.status_code
            error_details = http_err.response.text
            logger.error(f"HTTP Error {error_code} during Google Search: {error_details}")

            if error_code == 400: # Bad Request (e.g., invalid parameter)
                raise GoogleSearchAPIError(f"Bad Request (400): {error_details}")
            elif error_code == 403: # Forbidden (e.g., API key invalid, quota exceeded, or key restrictions)
                logger.warning(f"Quota exceeded or Forbidden (403). Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            elif error_code == 429: # Too Many Requests (Rate Limiting)
                logger.warning(f"Rate limited (429). Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            elif error_code >= 500: # Server Errors
                logger.warning(f"Server error ({error_code}). Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                raise GoogleSearchAPIError(f"Unhandled HTTP error ({error_code}): {error_details}") from http_err
        
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection Error during Google Search: {conn_err}. Retrying...")
            time.sleep(RETRY_DELAY_SECONDS)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout during Google Search for query: '{query}'. Retrying...")
            time.sleep(RETRY_DELAY_SECONDS)
        except json.JSONDecodeError:
            logger.error("Error decoding JSON response from Google Search API. Response was not valid JSON.")
            raise GoogleSearchAPIError("Invalid JSON response from API.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred during Google Search request: {e}")
            raise GoogleSearchAPIError(f"Unexpected error: {e}")

        retries += 1
    raise GoogleSearchAPIError(f"Failed to complete search request for '{query}' after {MAX_RETRIES} retries.")


def get_google_blog_posts(query, max_results=DEFAULT_MAX_TOTAL_RESULTS):
    """
    Searches Google for blog posts related to perfume pairing/best practices.
    Designed for production use with error handling and pagination.

    Args:
        query (str): The base search query (e.g., "best perfume pairs").
        max_results (int): The maximum total number of results to fetch.

    Returns:
        list: A list of dictionaries, each containing 'title', 'link', 'snippet',
              representing relevant blog posts. Returns empty list on error or no results.
    """
    all_blog_posts = []
    current_start_index = 1
    
    # Refine the query to target blog posts
    refined_query = f"{query} blog | review | guide | tips"
    logger.info(f"Refined search query for blog posts: '{refined_query}'")

    while len(all_blog_posts) < max_results:
        num_to_fetch_this_page = min(MAX_RESULTS_PER_REQUEST, max_results - len(all_blog_posts))
        
        if num_to_fetch_this_page <= 0:
            break

        try:
            search_response = _make_single_search_request(refined_query, current_start_index, num_to_fetch_this_page)

            if 'items' in search_response:
                for item in search_response['items']:
                    # Simple filter to prefer blog-like content (can be refined with more advanced URL/title parsing)
                    # This aims to exclude pure product pages, categories, etc.
                    if any(ext in item.get('link', '').lower() for ext in ['.html', '.php', '.asp', '.htm', '.org']) and \
                       not any(key_word in item.get('link', '').lower() for key_word in ['/category/', '/tag/', '/author/', '/shop/', '/product/', '/collection/', '/buy/']):
                        all_blog_posts.append({
                            "title": item.get('title', 'N/A'),
                            "link": item.get('link', 'N/A'),
                            "snippet": item.get('snippet', 'N/A'),
                            "source_domain": item.get('displayLink', 'N/A') # Get the clean domain
                        })
                
                next_page_start_index = None
                if 'queries' in search_response and 'nextPage' in search_response['queries']:
                    next_page_start_index = search_response['queries']['nextPage'][0]['startIndex']
                
                if next_page_start_index and next_page_start_index > current_start_index:
                    current_start_index = next_page_start_index
                else:
                    logger.info(f"No more pages indicated for query: '{refined_query}'.")
                    break 
            else:
                logger.info(f"No search results 'items' found for '{refined_query}' starting at index {current_start_index}.")
                break 

        except GoogleSearchAPIError as e:
            logger.error(f"Critical error during blog post search for '{query}': {e}. Stopping.")
            break 
    
    logger.info(f"Finished blog post search for '{query}'. Retrieved {len(all_blog_posts)} blog posts.")
    return all_blog_posts

# --- Example Usage for Testing ---
if __name__ == "__main__":
    print("--- Running Google Search for Perfume Blog Posts ---")
    print("WARNING: Using hardcoded API Key and CSE ID for testing. Set environment variables for production!")
    print("To use environment variables (recommended), uncomment the 'export' lines at the top of the script and run them in your terminal before execution.")
    print("-" * 60)

    # Test Queries specific to perfume pairing and best practices
    test_queries = [
        "best perfume layering combinations blog",
        "perfume pairing guide for couples",
        "how to pick a signature scent blog",
        "perfume etiquette tips and tricks",
        "top 10 perfume blog reviews",
        "fragrance blending ideas",
        "perfume pairing with outfits blog"
    ]

    for query in test_queries:
        print(f"\n--- Searching for blog posts: \"{query}\" ---")
        try:
            # Fetch up to 5 blog posts for each test query
            blog_posts = get_google_blog_posts(query, max_results=5) 

            if blog_posts:
                print(f"Found {len(blog_posts)} relevant blog posts:")
                for i, post in enumerate(blog_posts):
                    print(f"  {i+1}. Title: {post['title']}")
                    print(f"     Link: {post['link']}")
                    print(f"     Source: {post['source_domain']}")
                    print(f"     Snippet: {post['snippet'][:250]}...") # Limit snippet length
                    print("-" * 20)
            else:
                print("No blog posts found for this query.")
        except GoogleSearchAPIError as e:
            print(f"Error during search: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        time.sleep(2) # Small delay to be polite to the API during testing
    
    print("\n--- Google Search for Blog Posts Test Complete ---")
    print("Review the output for relevant results and logs for any errors.")