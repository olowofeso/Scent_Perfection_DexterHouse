# gsearch.py
import os
from googleapiclient.discovery import build
from google.auth.exceptions import DefaultCredentialsError
from dotenv import load_dotenv

# Attempt to import database components
# These will be fully available when called from app.py's context
try:
    from app import db  # db instance from Flask app
    from database_setup import Article
except ImportError:
    # This allows the script to be imported and parts of it run (like variable setup)
    # without Flask context, but database operations will fail if db is None.
    db = None
    Article = None
    print("Warning: gsearch.py running standalone or Flask app context not available. DB operations will be skipped.")


# Load environment variables from .env file
load_dotenv()

# --- Constants for Google Search API ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID") # Custom Search Engine ID

# --- Initialize Google Search Service ---
google_search_service = None
credentials_error_occurred = False

if GOOGLE_API_KEY and GOOGLE_CSE_ID:
    try:
        google_search_service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Error initializing Google Search service: {e}")
        google_search_service = None
else:
    print("Google API Key or CSE ID is missing. Google search functionality will be disabled.")
    credentials_error_occurred = True


def get_google_blog_posts(query: str, num_results: int = 5):
    """
    Searches for blog posts related to a query using Google Custom Search API
    and stores new unique articles in the database.

    Args:
        query (str): The search query.
        num_results (int): The number of search results to return.

    Returns:
        list: A list of search result dictionaries.
    """
    if credentials_error_occurred or not google_search_service:
        print("Google Search API is not configured. Cannot fetch articles.")
        return []

    if not query:
        print("Search query cannot be empty.")
        return []

    refined_query = f"{query} perfume review OR fragrance blog OR perfume forum"

    try:
        print(f"Executing Google Custom Search for: '{refined_query}' (requesting {num_results} results)")
        result = google_search_service.cse().list(
            q=refined_query,
            cx=GOOGLE_CSE_ID,
            num=num_results,
        ).execute()

        items = result.get('items', [])
        
        if not items:
            print(f"No Google search results found for '{refined_query}'.")
            return []

        search_results_for_return = []
        new_articles_added_count = 0

        for item in items:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")

            search_results_for_return.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })

            # --- Database Integration: Store new articles ---
            if db and Article: # Check if db and Article model are available
                try:
                    # Check if an article with this URL already exists
                    existing_article = db.session.query(Article).filter_by(source_url=link).first()
                    if not existing_article:
                        new_article = Article(
                            title=title,
                            source_url=link,
                            content=snippet # Storing snippet as content for now
                        )
                        db.session.add(new_article)
                        new_articles_added_count += 1
                    else:
                        print(f"Article with URL '{link}' already exists. Skipping.")
                except Exception as db_error:
                    print(f"Database error while trying to add article '{title}': {db_error}")
                    # Optionally, db.session.rollback() if a transaction is problematic
            # --- End Database Integration ---

        if db and Article and new_articles_added_count > 0:
            try:
                db.session.commit()
                print(f"Successfully added {new_articles_added_count} new articles to the database.")
            except Exception as commit_error:
                print(f"Database commit error: {commit_error}")
                db.session.rollback() # Rollback in case of commit error

        print(f"Found {len(search_results_for_return)} results from Google Custom Search.")
        return search_results_for_return

    except DefaultCredentialsError:
        print("Google API credentials error. Ensure GOOGLE_APPLICATION_CREDENTIALS env var is set or gcloud login.")
        return []
    except Exception as e:
        print(f"An error occurred with Google Custom Search: {e}")
        # Handle specific HTTP errors as before for better diagnostics
        if "HttpError 403" in str(e) and "disabled_key" in str(e):
            print("ERROR: Google API key disabled.")
        elif "HttpError 403" in str(e) and "forbidden" in str(e):
            print("ERROR: Google API key invalid or no permissions for Custom Search API.")
        elif "HttpError 400" in str(e) and "invalid_parameter" in str(e) and "cx" in str(e):
             print("ERROR: Custom Search Engine ID (cx) invalid.")
        return []


if __name__ == '__main__':
    print("Testing Google Custom Search for blog posts...")

    if credentials_error_occurred or not google_search_service:
        print("\nSkipping gsearch.py tests: Google Search API not configured (API_KEY/CSE_ID missing or invalid).")
    elif not db or not Article:
        print("\nSkipping gsearch.py tests: Database components (db, Article) not available in standalone mode.")
        print("To test database integration, run this functionality through the Flask app.")
        # Optionally, could still run a non-DB test:
        # print("\n--- Running non-DB search test ---")
        # results_no_db = get_google_blog_posts("test query without db", num_results=1)
        # if results_no_db:
        #     print(f"Found {len(results_no_db)} result(s) (DB operations skipped).")
        # else:
        #     print("No results found (DB operations skipped).")
    else:
        # This block will likely not run successfully in standalone `python gsearch.py`
        # because `db` won't be initialized with a Flask app context.
        # It's here for completeness if the environment could somehow provide `db`.
        print("\nAttempting test with (potentially non-functional) DB operations in standalone mode:")

        # Clean up dummy articles if they exist from a previous failed run (for testing only)
        # This is tricky in standalone. For true testing, a dedicated test DB and setup is needed.
        # For now, we'll just proceed. If app.py runs this, it will use the app's DB context.

        test_queries = [
            "Dior Sauvage review blog",
            "best summer fragrances for men forum",
            "Chanel No 5 detailed analysis"
        ]

        for t_query in test_queries:
            print(f"\n--- Searching for: '{t_query}' (expecting DB ops if in Flask context) ---")
            results = get_google_blog_posts(t_query, num_results=2) # Request few results for testing
            if results:
                for i, res in enumerate(results):
                    print(f"  Result {i+1}: Title: {res['title']}")
            else:
                print(f"  No results found for '{t_query}'.")
        
        # Example: Query the DB to see if articles were added (again, needs app context)
        # try:
        #     all_articles_in_db = db.session.query(Article).all()
        #     print(f"\nTotal articles in DB after tests: {len(all_articles_in_db)}")
        #     for art_entry in all_articles_in_db:
        #         print(f"  - DB: {art_entry.title} ({art_entry.source_url})")
        # except Exception as e:
        #     print(f"Could not query articles from DB in standalone: {e}")