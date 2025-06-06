import requests
from bs4 import BeautifulSoup, NavigableString # Import NavigableString
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import re
from thefuzz import process, fuzz

import undetected_chromedriver as uc

def scrape_fragrantica_notes(perfume_name: str, interactive: bool = True):
    """
    Searches for a perfume on Fragrantica and scrapes its scent notes.
    This function initializes and quits its own WebDriver.

    Args:
        perfume_name (str): The name of the perfume to search for.
        interactive (bool): If True, prompts user to choose from suggestions.
                            If False, tries to pick the best match automatically.
    """
    fragrantica_url = "https://www.fragrantica.com/"
    notes = {}

    print("DEBUG: Initializing undetected_chromedriver for Fragrantica...")
    driver = None
    try:
        options_uc = uc.ChromeOptions()
        # options_uc.add_argument('--headless') # Uncomment for headless mode in production
        options_uc.add_argument('--disable-gpu')
        options_uc.add_argument('--window-size=1920,1080')
        options_uc.add_argument('--no-sandbox')
        options_uc.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options_uc)
        
        driver.get(fragrantica_url)
        print("DEBUG: Browser opened with undetected_chromedriver. Navigating to Fragrantica homepage.")
        time.sleep(5) # Give it a bit more time for initial page load and scripts

    except WebDriverException as e:
        print(f"ERROR: WebDriver initialization failed: {e}")
        print("INFO: Please ensure Chrome browser is installed.")
        if driver: driver.quit()
        return {}
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during WebDriver initialization: {e}")
        if driver: driver.quit()
        return {}

    try:
        search_input_locator = (By.CLASS_NAME, 'super-search')
        print("DEBUG: Waiting for search input element to be present on the main page...")
        search_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(search_input_locator)
        )
        print("DEBUG: Search input element found.")

        print(f"DEBUG: Typing '{perfume_name}' into search bar character by character...")
        for char in perfume_name:
            search_input.send_keys(char)
            time.sleep(0.05) # 50ms delay
        
        time.sleep(1.5) # Give the website a moment to process the full input and generate suggestions

        print("DEBUG: Waiting for search suggestions dropdown to appear...")
        suggestions_container_locator = (By.CSS_SELECTOR, 'span.aa-dropdown-menu') 
        
        try:
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(suggestions_container_locator)
            )
            print("DEBUG: Search suggestions dropdown appeared.")
            
            suggestion_links_locator = (By.CSS_SELECTOR, 'span.aa-dropdown-menu .aa-dataset-perfumes a[href*="/perfume/"]')
            
            print("DEBUG: Collecting suggestion links from perfume dataset...")
            all_suggestion_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(suggestion_links_locator)
            )

            if not all_suggestion_elements:
                print("WARNING: No suggestion links found within the perfume dataset of the dropdown after typing. This may mean no results.")
                return {}

            unique_suggestions = {}
            for elem in all_suggestion_elements:
                link_text = elem.text.strip()
                if link_text and link_text not in unique_suggestions:
                    unique_suggestions[link_text] = elem
                if len(unique_suggestions) >= 10:
                    break

            if not unique_suggestions:
                print("WARNING: No valid unique suggestions found in the dropdown's perfume dataset.")
                return {}
            
            suggestion_list = list(unique_suggestions.keys())
            chosen_perfume_name = None
            relevant_link_element = None

            if interactive:
                print("\n--- Found multiple perfumes. Please select one: ---")
                for i, text in enumerate(suggestion_list):
                    print(f"{i+1}. {text}")
                print("---------------------------------------------------")

                chosen_index = -1
                while True:
                    try:
                        choice = input("Enter the number of your choice (1-{}): ".format(len(suggestion_list))).strip()
                        chosen_index = int(choice) - 1
                        if 0 <= chosen_index < len(suggestion_list):
                            break
                        else:
                            print("Invalid choice. Please enter a number within the range.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                chosen_perfume_name = suggestion_list[chosen_index]
                relevant_link_element = unique_suggestions[chosen_perfume_name]
                print(f"DEBUG: User chose: '{chosen_perfume_name}'.")
            else: # Non-interactive mode
                print(f"DEBUG: Non-interactive mode. Trying to find best match for '{perfume_name}' among suggestions: {suggestion_list}")
                # Use process.extractOne to find the best match from the suggestion texts
                # We use the original perfume_name (the search query) to compare against the suggestions from Fragrantica
                best_match_tuple = process.extractOne(perfume_name, suggestion_list, scorer=fuzz.ratio) # fuzz.token_set_ratio might be better

                if best_match_tuple:
                    extracted_name, score = best_match_tuple
                    print(f"DEBUG: Best match in suggestions: '{extracted_name}' with score {score}")
                    if score >= 85: # Adjusted threshold for auto-selection based on Fragrantica's own search results
                        chosen_perfume_name = extracted_name
                        relevant_link_element = unique_suggestions[chosen_perfume_name]
                        print(f"DEBUG: Automatically selected '{chosen_perfume_name}' (Score: {score}).")
                    else:
                        print(f"DEBUG: No high-confidence single match found (best was '{extracted_name}' with score {score}). Aborting non-interactive selection.")
                        return {} # Cannot proceed without a clear choice
                else:
                    print("DEBUG: process.extractOne returned no match from suggestions. Aborting.")
                    return {}
            
            if not chosen_perfume_name or not relevant_link_element:
                print("DEBUG: Could not determine a perfume to proceed with from suggestions. Aborting.")
                return {}

            print(f"DEBUG: Proceeding with '{chosen_perfume_name}'. Clicking link...")
            driver.execute_script("arguments[0].click();", relevant_link_element) 
            print("DEBUG: Chosen suggestion clicked. Waiting for perfume page to load...")

        except TimeoutException:
            print("ERROR: Search suggestions dropdown or its contents did not appear within 15s. This might indicate no results or a changed structure.")
            print(f"INFO: Current URL: {driver.current_url}")
            try:
                print(f"INFO: Page source head at timeout: \n{driver.page_source[:500]}...")
            except:
                print("INFO: Could not retrieve page source at timeout (driver might be unresponsive).")
            return {}
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while handling search suggestions: {e}")
            print(f"INFO: Current URL: {driver.current_url}")
            try:
                print(f"INFO: Page source head at error: \n{driver.page_source[:500]}...")
            except:
                print("INFO: Could not retrieve page source at error.")
            return {}
        
        page_loaded_successfully = False
        try:
            print("DEBUG: Trying to detect perfume page by URL match...")
            WebDriverWait(driver, 15).until(EC.url_matches(r'fragrantica\.com/perfume/\S+-\d+\.html'))
            print(f"DEBUG: URL matches perfume page pattern: {driver.current_url}")
            page_loaded_successfully = True
        except TimeoutException:
            print("DEBUG: URL did not match perfume page pattern within 15s after click.")
            pass

        if not page_loaded_successfully:
            try:
                print("DEBUG: Trying to detect perfume page by 'h1[itemprop=\"name\"]' presence...")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[itemprop="name"]')))
                print("DEBUG: Found 'h1[itemprop=\"name\"]'. Directly landed on perfume page.")
                page_loaded_successfully = True
            except TimeoutException:
                print("DEBUG: 'h1[itemprop=\"name\"]' not found within 10s after click.")
                pass

        if not page_loaded_successfully:
            try:
                print("DEBUG: Trying to detect perfume page by '#toptop' ID presence...")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'toptop')))
                print("DEBUG: Found '#toptop' ID. Directly landed on perfume page.")
                page_loaded_successfully = True
            except TimeoutException:
                print("DEBUG: '#toptop' ID not found within 10s after click.")
                pass

        if not page_loaded_successfully:
            print("ERROR: After clicking suggestion, still could not confirm direct perfume page loaded.")
            print(f"INFO: Current URL: {driver.current_url}")
            try:
                print(f"INFO: Current page source head: \n{driver.page_source[:500]}...")
            except:
                print("INFO: Could not retrieve page source at error.")
            return {}

        perfume_page_url = driver.current_url
        print(f"DEBUG: Confirmed final URL for scraping is: {perfume_page_url}")

        if not re.search(r'fragrantica\.com/perfume/\S+-\d+\.html', perfume_page_url):
            print(f"ERROR: Navigated to unexpected final URL after suggestion click: {perfume_page_url}. Expected a perfume page.")
            return {}

        print("DEBUG: Perfume page confirmed and loaded. Starting to scrape notes...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        time.sleep(1) # Give the page a moment to fully render after parsing initial HTML

        # --- REVISED NOTE EXTRACTION LOGIC leveraging the provided images ---
        notes_root_element = None

        # Attempt 1: Prioritize the 'pyramid' ID as seen in the images
        notes_root_element = soup.find('div', id='pyramid')
        
        # Attempt 2: Fallback to the specific CSS selector from the last debug session
        if not notes_root_element:
            print("DEBUG: Could not find notes section by 'id=pyramid'. Trying JS Path CSS selector.")
            notes_root_element = soup.select_one('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(5)')
        
        # Attempt 3: Fallback to the generic style-based search
        if not notes_root_element:
            print("DEBUG: Could not find notes section by JS Path CSS selector. Falling back to style-based search.")
            notes_root_element = soup.find('div', style=lambda value: value and 'display: flex; flex-direction: column' in value and 'background: white;' in value)
            if not notes_root_element:
                print("DEBUG: Also could not find notes section using style-based search. Trying 'notes-pyramid' class as final fallback.")
                notes_root_element = soup.find('div', class_='notes-pyramid') # Old class
                if not notes_root_element:
                    print("DEBUG: All attempts to find the notes root container failed.")
                    return {}
        
        # If we successfully found a root element, now look for the h4 tags within it.
        # We need to be flexible because the H4 text itself might be wrapped in <b>.
        notes = {}
        all_h4_tags = notes_root_element.find_all('h4')

        h4_note_sections = []
        for h4_tag in all_h4_tags:
            # Get the text content, stripping any whitespace and making it lowercase for robust comparison.
            # This handles <b> tags within the h4.
            h4_text = h4_tag.get_text(strip=True).lower()
            if 'top notes' in h4_text or 'middle notes' in h4_text or 'base notes' in h4_text:
                h4_note_sections.append(h4_tag)

        if not h4_note_sections:
            print("DEBUG: No 'Top Notes', 'Middle Notes', or 'Base Notes' headings found within the notes root section (after text content filtering).")
            return {}

        for h4_tag in h4_note_sections:
            # Extract section name: "top", "middle", or "base"
            section_name = h4_tag.get_text(strip=True).replace(' Notes', '').lower()
            
            # Find the div that contains the actual note links.
            # This loop iterates through siblings to find the first div that *actually* contains 'a' tags pointing to notes.
            notes_list_container = None
            current_sibling = h4_tag.find_next_sibling()
            while current_sibling:
                # Check if it's a div and if it contains any 'a' tags with '/notes/' href
                if current_sibling.name == 'div' and current_sibling.find('a', href=re.compile(r'/notes/')):
                    notes_list_container = current_sibling
                    break
                current_sibling = current_sibling.find_next_sibling()
            
            if notes_list_container:
                # Find all 'a' tags that represent individual notes within this container.
                individual_notes_links = notes_list_container.find_all('a', href=re.compile(r'/notes/'))
                
                if individual_notes_links:
                    extracted_notes = []
                    for note_link in individual_notes_links:
                        # Extract the href attribute
                        href = note_link.get('href')
                        note_text = ""
                        if href:
                            # Use regex to extract the note name from the URL path
                            match = re.search(r'/notes/([^/]+)-\d+\.html', href)
                            if match:
                                # Replace hyphens with spaces and capitalize each word
                                note_text = match.group(1).replace('-', ' ').title()
                            else:
                                # Fallback if the regex doesn't match the expected pattern
                                # This might happen if the URL structure changes slightly or is a more general note page
                                note_text = href.split('/')[-1].replace('.html', '').replace('-', ' ').title()
                                
                        if note_text: 
                            extracted_notes.append(note_text)
                        else:
                            print(f"DEBUG: Could not extract text from href for note link: {note_link}")
                    
                    if extracted_notes:
                        notes[section_name] = extracted_notes
                        print(f"DEBUG: Scraped {len(extracted_notes)} notes for '{section_name}'.")
                    else:
                        print(f"DEBUG: No individual note links with text found for '{section_name}' in the identified list container (after robust extraction).")
                else:
                    print(f"DEBUG: No individual note links found for '{section_name}' in the identified list container.")
            else:
                print(f"DEBUG: No suitable notes list container div found after h4 for '{section_name}'.")
        
        if not notes:
            print("WARNING: No scent notes found on the page after all parsing attempts.")
        else:
            print(f"DEBUG: Successfully extracted notes: {notes.keys()}")

    except TimeoutException:
        print(f"ERROR: Operation timed out for '{perfume_name}'. This usually means an element wasn't found in time.")
        print(f"INFO: Current URL at timeout: {driver.current_url}")
        try:
            print(f"INFO: Page source head at timeout: \n{driver.page_source[:500]}...")
        except:
            print("INFO: Could not retrieve page source at timeout (driver might be unresponsive).")
    except NoSuchElementException:
        print(f"ERROR: A required element was not found for '{perfume_name}'. Website structure might have changed.")
        print(f"INFO: Current URL at error: {driver.current_url}")
        try:
            print(f"INFO: Page source head at error: \n{driver.page_source[:500]}...")
        except:
            print("INFO: Could not retrieve page source at error.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during scraping for '{perfume_name}': {e}")
        print(f"INFO: Current URL at error: {driver.current_url}")
        try:
            print(f"INFO: Page source head at error: \n{driver.page_source[:500]}...")
        except:
            print("INFO: Could not retrieve page source at error.")
    finally:
        if driver:
            driver.quit()
            print("DEBUG: Browser closed.")

    return notes

if __name__ == "__main__":
    known_perfumes = [
        "Yves Saint Laurent MYSLF Eau de Parfum",
        "Lattafa Perfumes Eclaire",
        "Maison Martin Margiela By the Fireplace",
        "Dior Sauvage",
        "Chanel No. 5",
        "Versace Dylan Blue",
        "Giorgio Armani Acqua di Gio",
        "Creed Aventus",
        "Baccarat Rouge 540",
        "Tom Ford Tobacco Vanille",
        "Jo Malone Wood Sage & Sea Salt",
        "Givenchy Irresistible",
        "Givenchy L'Interdit",
        "Prada Paradoxe",
        "Viktor & Rolf Flowerbomb",
        "Mugler Alien",
        "Gucci Bloom",
        "Burberry Her",
        "YSL Black Opium",
        "Carolina Herrera Good Girl",
        "Afnan Supremacy Not Only Intense"
    ]

    # --- Test Non-Interactive Mode ---
    print("\n--- Testing Non-Interactive Mode ---")
    # Using a name that is likely to be a unique and strong first result on Fragrantica
    # Note: Fragrantica search can be finicky; this might need adjustment.
    non_interactive_test_perfume = "Dior Sauvage Eau de Parfum"
    print(f"Attempting to scrape '{non_interactive_test_perfume}' non-interactively...")
    # First, let's see if our internal fuzzy match corrects it to something in KNOWN_PERFUMES
    # This part simulates the pre-scraping name correction that might happen in a full app
    best_match_non_interactive_tuple = process.extractOne(non_interactive_test_perfume, known_perfumes, scorer=fuzz.ratio)
    final_search_name_non_interactive = non_interactive_test_perfume
    if best_match_non_interactive_tuple:
        name, score = best_match_non_interactive_tuple
        if score >= 85: # Using a slightly higher threshold for auto-correction before search
            print(f"DEBUG: Pre-search correction: '{non_interactive_test_perfume}' to '{name}' (Score: {score})")
            final_search_name_non_interactive = name
        else:
            print(f"DEBUG: Pre-search: No strong correction for '{non_interactive_test_perfume}' (Best: {name}, Score: {score}). Using original/typed name.")

    notes_non_interactive = scrape_fragrantica_notes(final_search_name_non_interactive, interactive=False)
    if notes_non_interactive:
        print(f"\n--- Scent Notes for {final_search_name_non_interactive.title()} (Non-Interactive) ---")
        for section, note_list in notes_non_interactive.items():
            print(f"{section.title()} Notes: {', '.join(note_list)}")
        print("-" * 30)
    else:
        print(f"Could not retrieve notes for '{final_search_name_non_interactive}' in non-interactive mode.")
    print("--- Non-Interactive Test Complete ---\n")

    # --- Interactive Mode (existing loop) ---
    print("\n--- Testing Interactive Mode ---")
    while True:
        user_input = input("Enter the perfume name (e.g., 'By the Fireplace', 'Sauvage'), or 'quit' to exit: ").strip()
        if user_input.lower() == 'quit':
            break
        if not user_input:
            print("Perfume name cannot be empty. Please try again.")
            continue

        # Fuzzy matching against known_perfumes list (pre-correction)
        best_match_tuple = process.extractOne(user_input, known_perfumes, scorer=fuzz.ratio)
        corrected_perfume_name = user_input # Default to user input
        
        if best_match_tuple:
            best_match_name, score = best_match_tuple
            if score >= 80: # Threshold for suggesting or auto-correcting
                print(f"Suggestion based on internal list: Did you mean '{best_match_name}'? (Confidence: {score}%)")
                if score >= 95: # Higher score for auto-correction
                    print(f"Auto-correcting to '{best_match_name}' for search.")
                    corrected_perfume_name = best_match_name
                else:
                    confirm = input("Enter 'y' to use suggestion, or 'n' to search for your original query: ").strip().lower()
                    if confirm == 'y':
                        corrected_perfume_name = best_match_name
                    else:
                        print(f"Searching for original query: '{user_input}'")
            else:
                print(f"No close match found in internal list for '{user_input}'. Searching with original query.")
        else:
            print(f"No matches in known perfumes. Searching with original query: '{user_input}'")

        print(f"\n--- Initiating interactive search for: {corrected_perfume_name} ---")
        # Pass interactive=True for the interactive part of the test
        scent_notes = scrape_fragrantica_notes(corrected_perfume_name, interactive=True)

        if scent_notes:
            print(f"\n--- Scent Notes for {corrected_perfume_name.title()} (Interactive) ---")
            if 'top' in scent_notes: # Ensure keys exist before accessing
                print(f"Top Notes: {', '.join(scent_notes['top'])}")
            if 'middle' in scent_notes:
                print(f"Middle Notes: {', '.join(scent_notes['middle'])}")
            if 'base' in scent_notes:
                print(f"Base Notes: {', '.join(scent_notes['base'])}")
            print("-" * (len(corrected_perfume_name) + 30))
        else:
            print(f"Could not retrieve scent notes for '{corrected_perfume_name}' in interactive mode.")
        print("\n")
    print("--- Interactive Test Complete ---")