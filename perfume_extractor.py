import re
from thefuzz import process, fuzz

# A placeholder list of known perfumes. This should ideally be managed externally or expanded.
KNOWN_PERFUMES = [
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

def extract_perfume_names(query: str, known_perfumes: list[str] = None, threshold: int = 80) -> list[str]:
    """
    Extracts perfume names from a query using fuzzy matching against a list of known perfumes.

    Args:
        query (str): The user's query string.
        known_perfumes (list[str], optional): A list of known perfume names.
                                             Defaults to KNOWN_PERFUMES.
        threshold (int, optional): The minimum confidence score (0-100) for a match.
                                   Defaults to 80.

    Returns:
        list[str]: A list of extracted perfume names found in the query.
    """
    if known_perfumes is None:
        known_perfumes = KNOWN_PERFUMES

    extracted_names = []

    possible_matches = process.extractBests(query, known_perfumes, scorer=fuzz.token_set_ratio, score_cutoff=threshold, limit=None)

    for name, score in possible_matches:
        name_words = set(w.lower() for w in name.split())
        query_words = set(w.lower() for w in query.split())

        if not name_words:
            continue

        common_words = name_words.intersection(query_words)

        if len(name_words) <= 2:
            if len(common_words) == len(name_words):
                if name not in extracted_names:
                    extracted_names.append(name)
        elif len(common_words) / len(name_words) >= 0.6:
            if name not in extracted_names:
                extracted_names.append(name)
        elif score > 90 and len(common_words) / len(name_words) >= 0.4:
             if name not in extracted_names:
                extracted_names.append(name)

    final_list = []
    for name in extracted_names:
        if name not in final_list:
            final_list.append(name)

    return final_list

if __name__ == '__main__':
    test_queries = [
        "What are the notes in Dior Sauvage?",
        "Tell me about YSL Black Opium and also Lattafa Eclaire.",
        "I'm looking for a fragrance similar to By the Fireplace.",
        "Recommend a perfume by Chanel.",
        "Is Creed Aventus good?",
        "Notes for Sauvage by Dior",
        "compare Dior Sauvage with MYSLF Eau de Parfum",
        "what about Tom Ford's Tobacco Vanille perfume?",
        "bkdj Dior fdjlkj",
        "I want a perfume like Sauvage",
        "layer By the Fireplace with Tobacco Vanille",
        "Give me notes for lattafa perfumes eclaire",
        "What is eclaire by lattafa like?",
        "ysl myslf"
    ]

    print("--- Default KNOWN_PERFUMES Test ---")
    for t_query in test_queries:
        names = extract_perfume_names(t_query)
        print(f"Query: \"{t_query}\" -> Extracted: {names}")

    print("\n--- Test with Custom List and Threshold ---")
    custom_perfumes = ["My Special Perfume", "Another Scent", "Chanel Coco Mademoiselle"]
    test_q_custom1 = "Tell me about My Special Perfume and also Chanel Coco Mademoiselle"
    names_custom1 = extract_perfume_names(test_q_custom1, known_perfumes=custom_perfumes, threshold=85)
    print(f"Query: \"{test_q_custom1}\" -> Extracted: {names_custom1}")

    test_q_custom2 = "I want coco mademoiselle by chanel"
    names_custom2 = extract_perfume_names(test_q_custom2, known_perfumes=custom_perfumes, threshold=80)
    print(f"Query: \"{test_q_custom2}\" -> Extracted: {names_custom2}")

    specific_known_list = ["Yves Saint Laurent MYSLF Eau de Parfum", "YSL MYSLF", "Dior Sauvage"]
    test_q_edge = "I like ysl myslf but not the old one"
    names_edge = extract_perfume_names(test_q_edge, known_perfumes=specific_known_list, threshold=75)
    print(f"Query: \"{test_q_edge}\" -> Extracted: {names_edge}")

    test_q_short_vs_long = "Sauvage"
    names_short_vs_long = extract_perfume_names(test_q_short_vs_long, known_perfumes=specific_known_list, threshold=70)
    print(f"Query: \"{test_q_short_vs_long}\" -> Extracted: {names_short_vs_long}")
