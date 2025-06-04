# scrape.py
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

async def scrape_fragrantica_notes_async(perfume_name: str):
    """
    Asynchronously scrapes perfume notes from Fragrantica.
    Args:
        perfume_name (str): The name of the perfume to search for.
    Returns:
        dict: A dictionary with "top", "middle", "base" notes, or None if scraping fails or notes not found.
              Example: {"top": ["note1", "note2"], "middle": ["note3"], "base": ["note4"]}
    """
    if not perfume_name:
        print("Perfume name cannot be empty.")
        return None

    # Sanitize perfume_name for URL and search (basic)
    search_query = perfume_name.lower().replace(" ", "+")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Consider headless=False for debugging
        page = await browser.new_page()
        
        try:
            # Step 1: Search for the perfume on Fragrantica
            # Using a direct search URL pattern if available, or a more general search
            # This URL navigates to the search results page
            search_url = f"https://www.fragrantica.com/search/?query={search_query}"
            print(f"Navigating to search URL: {search_url}")
            await page.goto(search_url, wait_until="networkidle", timeout=60000)

            # Look for the first search result link that directly matches the perfume name or is most relevant.
            # This often involves inspecting the HTML structure of Fragrantica's search results.
            # The selector needs to be robust. Example: a link within a list of results.
            # This selector targets links within grid cells that are specifically for perfumes.
            
            # More specific selector based on typical Fragrantica structure for search results:
            # It looks for an 'a' tag within a 'div' that has a class 'cell-perfume'.
            # This is an example; actual class names might change and need verification.
            perfume_link_selector = "div.cell.cell-perfume a" # Common pattern
            
            # Attempt to find a direct link. We might need to be more sophisticated here,
            # e.g., by checking text content if multiple links match.
            link_element = page.locator(perfume_link_selector).first
            
            href = await link_element.get_attribute("href")
            if not href:
                print(f"No perfume link found for '{perfume_name}' on search results page.")
                await browser.close()
                return None

            perfume_page_url = page.urljoin(href) # Ensure it's an absolute URL
            print(f"Found perfume page link: {perfume_page_url}")

            # Step 2: Navigate to the perfume's page
            print(f"Navigating to perfume page: {perfume_page_url}")
            await page.goto(perfume_page_url, wait_until="networkidle", timeout=60000)
            
            # Step 3: Extract notes from the perfume's page
            # The notes are usually in a specific structured element.
            # This selector targets the typical notes pyramid structure.
            # It looks for <p> tags within a <div> that has a specific itemprop attribute,
            # or a class that indicates it's the notes accord pyramid.
            # Selector based on Fragrantica's common structure for notes pyramid:
            # Looks for a div with class 'accord-box' then specific paragraphs for note groups.
            # This is highly dependent on Fragrantica's current HTML structure.

            # Wait for the notes section to be present
            notes_pyramid_selector = "div[itemprop='description'] > div:nth-of-type(1) > p" # A common pattern for notes
            try:
                await page.wait_for_selector(notes_pyramid_selector, timeout=10000)
            except Exception as e:
                print(f"Notes pyramid selector not found or timed out: {e}")
                # Fallback: Try to get whatever HTML is available for debugging or alternative parsing
                page_content_for_debug = await page.content()
                # print(f"Page content for debugging notes section:\n{page_content_for_debug[:2000]}") # Print first 2k chars
                await browser.close()
                return None

            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            # --- New Notes Extraction Logic ---
            notes_data = {"top": [], "middle": [], "base": []}
            
            # Fragrantica often uses a structure like:
            # <div itemprop="description">
            #   <div> <!-- This div contains the notes pyramid -->
            #     <p><strong>Top notes are:</strong> <a>Note1</a>, <a>Note2</a>.</p>
            #     <p><strong>Middle notes are:</strong> <a>Note3</a>, <a>Note4</a>.</p>
            #     <p><strong>Base notes are:</strong> <a>Note5</a>, <a>Note6</a>.</p>
            #   </div>
            #   ... other divs for description etc.
            # </div>
            # Or sometimes, notes are within divs with class like 'cell small-12 text-center' for each group.
            
            description_div = soup.find("div", itemprop="description")
            if not description_div:
                print("Could not find the main description itemprop div.")
                await browser.close()
                return None

            # The notes pyramid is usually the first child div within the description_div
            notes_pyramid_container = description_div.find("div", recursive=False)
            if not notes_pyramid_container:
                print("Could not find the notes pyramid container within itemprop description.")
                await browser.close()
                return None

            note_paragraphs = notes_pyramid_container.find_all("p")

            if not note_paragraphs:
                print("No paragraphs found in notes pyramid container. Trying alternative structure...")
                # Alternative structure: Check for divs directly holding notes (less common for pyramid)
                # This is a simplified fallback, might need specific selectors if this path is common
                # For example: divs with class like 'notesgroup' or similar
                # For now, if <p> tags aren't there, assume failure for this structure.
                await browser.close()
                return None


            for p_tag in note_paragraphs:
                category_text = p_tag.find("strong")
                if not category_text:
                    continue # Paragraph might not be a notes category

                category_name_full = category_text.get_text(strip=True).lower()

                current_category_key = None
                if "top notes" in category_name_full:
                    current_category_key = "top"
                elif "middle notes" in category_name_full or "heart notes" in category_name_full:
                    current_category_key = "middle"
                elif "base notes" in category_name_full:
                    current_category_key = "base"

                if current_category_key:
                    note_links = p_tag.find_all("a")
                    if not note_links: # Sometimes notes are just text, not links
                        # Extract text after "<strong>Top notes are:</strong>" and split by comma
                        # This is a bit fragile and depends on consistent punctuation.
                        raw_text = p_tag.text.replace(category_text.text, "").strip(" .")
                        notes_in_p = [note.strip() for note in raw_text.split(',') if note.strip()]
                        notes_data[current_category_key].extend(notes_in_p)
                    else:
                        for link in note_links:
                            note_name = link.get_text(strip=True)
                            if note_name:
                                notes_data[current_category_key].append(note_name)

            # Validate if any notes were found
            if not any(notes_data.values()):
                print(f"No notes extracted. HTML structure might have changed. Content of notes container: \n{notes_pyramid_container.prettify()}")
                await browser.close()
                return None

            print(f"Successfully scraped notes for {perfume_name}: {notes_data}")
            return notes_data

        except Exception as e:
            print(f"An error occurred during scraping {perfume_name}: {e}")
            # Optionally, capture a screenshot for debugging if Playwright is configured for it
            # await page.screenshot(path=f"error_{perfume_name.replace(' ', '_')}.png")
            return None
        finally:
            await browser.close()

def scrape_fragrantica_notes(perfume_name: str):
    """
    Synchronous wrapper for the async scraping function.
    This is what app.py will call.
    """
    print(f"Initiating scrape for: {perfume_name}")
    try:
        # asyncio.get_event_loop() might cause issues in some environments (e.g. Flask with some WSGI servers)
        # or if an event loop is already running.
        # Using asyncio.run() is generally safer for calling async code from sync.
        result = asyncio.run(scrape_fragrantica_notes_async(perfume_name))
        if result:
            print(f"Scraping successful for {perfume_name}.")
        else:
            print(f"Scraping failed or no notes found for {perfume_name}.")
        return result
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # This can happen if Flask is already running in an async context (e.g., with `async_mode='asgi'`)
            # Or if called from a Jupyter notebook with an active loop.
            # A more robust solution might involve checking `asyncio.get_running_loop()`
            # and deciding how to schedule the async task.
            # For now, try creating a new event loop for this specific task if possible,
            # but this is tricky and can lead to other issues.
            # A better long-term solution is to ensure the calling environment
            # and the scraping function are compatible (e.g., Flask app runs async).
            print(f"RuntimeError: {e}. Consider running Flask in an async-compatible way or restructuring calls.")
            # Fallback: This is a simplistic way to handle it, might not always work.
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
            # result = loop.run_until_complete(scrape_fragrantica_notes_async(perfume_name))
            # loop.close()
            # return result
            # For now, re-raise or return None as this indicates a deeper integration issue.
            print("Cannot currently run async scrape from this synchronous context due to existing event loop.")
            return None # Or re-raise the exception
        else:
            raise e # Re-raise other RuntimeErrors
    except Exception as e:
        print(f"An unexpected error occurred in synchronous wrapper for {perfume_name}: {e}")
        return None


if __name__ == '__main__':
    # --- Example Usage (for testing scrape.py directly) ---
    # Test with a known perfume
    example_perfume = "Dior Sauvage" # A popular perfume, likely to be found
    print(f"\n--- Testing direct scrape for: {example_perfume} ---")

    # Using the synchronous wrapper as it would be called by app.py
    scraped_data = scrape_fragrantica_notes(example_perfume)

    if scraped_data:
        print(f"\nScraped notes for {example_perfume}:")
        print(json.dumps(scraped_data, indent=2))
    else:
        print(f"\nCould not scrape notes for {example_perfume}.")

    print("\n--- Testing with a potentially problematic name (e.g., non-existent or very generic) ---")
    example_perfume_nonexistent = "Celestial Whisper of the Nonexistent Flower"
    scraped_data_nonexistent = scrape_fragrantica_notes(example_perfume_nonexistent)
    if scraped_data_nonexistent:
        print(f"\nScraped notes for {example_perfume_nonexistent}:") # Should ideally not find this
        print(json.dumps(scraped_data_nonexistent, indent=2))
    else:
        print(f"\nCould not scrape notes for {example_perfume_nonexistent} (as expected).")

    print("\n--- Testing with an empty name ---")
    scraped_data_empty = scrape_fragrantica_notes("")
    if scraped_data_empty:
        print(f"\nScraped notes for empty name:") # Should not happen
        print(json.dumps(scraped_data_empty, indent=2))
    else:
        print(f"\nCould not scrape notes for empty name (as expected).")
