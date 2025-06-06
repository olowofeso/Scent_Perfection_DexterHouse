def match_perfumes(perfume1_notes: dict, perfume2_notes: dict) -> dict:
    """
    Calculates a compatibility score for two perfumes based on shared base notes
    and also considers shared notes in top and middle.

    Args:
        perfume1_notes (dict): Notes for the first perfume, e.g.,
                                 {'top': ['Bergamot'], 'middle': ['Rose'], 'base': ['Cedar', 'Musk']}.
        perfume2_notes (dict): Notes for the second perfume, similar structure.

    Returns:
        dict: A dictionary containing the base_note_score, shared_base_notes,
              shared_top_notes, shared_middle_notes, and an overall compatibility_score.
              Example: {
                  'base_note_score': 1,
                  'shared_base_notes': ['Cedar'],
                  'shared_top_notes': [],
                  'shared_middle_notes': ['Rose'],
                  'compatibility_score': 1.5 # Example: base_score + 0.5 * other_shared
              }
    """
    if not isinstance(perfume1_notes, dict) or not isinstance(perfume2_notes, dict):
        raise ValueError("Perfume notes must be provided as dictionaries.")

    p1_base_notes = set(note.lower() for note in perfume1_notes.get('base', []))
    p2_base_notes = set(note.lower() for note in perfume2_notes.get('base', []))

    p1_top_notes = set(note.lower() for note in perfume1_notes.get('top', []))
    p2_top_notes = set(note.lower() for note in perfume2_notes.get('top', []))

    p1_middle_notes = set(note.lower() for note in perfume1_notes.get('middle', []))
    p2_middle_notes = set(note.lower() for note in perfume2_notes.get('middle', []))

    shared_base = list(p1_base_notes.intersection(p2_base_notes))
    base_score = len(shared_base)

    shared_top = list(p1_top_notes.intersection(p2_top_notes))
    shared_middle = list(p1_middle_notes.intersection(p2_middle_notes))

    # Basic compatibility score: prioritize base notes, add some weight for other shared notes
    compatibility_score = float(base_score)
    if shared_top:
        compatibility_score += 0.25 * len(shared_top)
    if shared_middle:
        compatibility_score += 0.25 * len(shared_middle)

    return {
        'base_note_score': base_score,
        'shared_base_notes': shared_base,
        'shared_top_notes': shared_top,
        'shared_middle_notes': shared_middle,
        'compatibility_score': compatibility_score
    }

if __name__ == '__main__':
    print("--- Testing recommendation_engine.py ---")

    # Example perfume notes data (replace with actual data source in a real app)
    perfumes_db = {
        "Perfume A": {"top": ["Bergamot", "Lemon"], "middle": ["Rose", "Jasmine"], "base": ["Cedar", "Musk", "Amber"]},
        "Perfume B": {"top": ["Lemon", "Orange"], "middle": ["Jasmine", "Lily"], "base": ["Musk", "Vanilla", "Sandalwood"]},
        "Perfume C": {"top": ["Apple", "Mint"], "middle": ["Lavender", "Spice"], "base": ["Cedar", "Vetiver"]},
        "Perfume D": {"top": ["Bergamot"], "middle": ["Rose"], "base": ["Cedar", "Amber"]}, # High similarity to A
        "Perfume E": {"top": ["Grapefruit"], "middle": ["Peony"], "base": ["Patchouli"]} # No similarity to A
    }

    # Test case 1: Perfumes with some overlap
    notes1 = perfumes_db["Perfume A"]
    notes2 = perfumes_db["Perfume B"]
    match_ab = match_perfumes(notes1, notes2)
    print(f"\nMatch between Perfume A and Perfume B:")
    print(f"  Shared Base Notes: {match_ab['shared_base_notes']} (Score: {match_ab['base_note_score']})")
    print(f"  Shared Top Notes: {match_ab['shared_top_notes']}")
    print(f"  Shared Middle Notes: {match_ab['shared_middle_notes']}")
    print(f"  Overall Compatibility Score: {match_ab['compatibility_score']}")
    assert match_ab['base_note_score'] == 1
    assert "musk" in match_ab['shared_base_notes']
    assert "lemon" in match_ab['shared_top_notes']
    assert "jasmine" in match_ab['shared_middle_notes']

    # Test case 2: Perfumes with high overlap
    notes3 = perfumes_db["Perfume D"]
    match_ad = match_perfumes(notes1, notes3)
    print(f"\nMatch between Perfume A and Perfume D (High Similarity):")
    print(f"  Shared Base Notes: {match_ad['shared_base_notes']} (Score: {match_ad['base_note_score']})")
    print(f"  Shared Top Notes: {match_ad['shared_top_notes']}")
    print(f"  Shared Middle Notes: {match_ad['shared_middle_notes']}")
    print(f"  Overall Compatibility Score: {match_ad['compatibility_score']}")
    assert match_ad['base_note_score'] == 2
    assert "cedar" in match_ad['shared_base_notes'] and "amber" in match_ad['shared_base_notes']
    assert "bergamot" in match_ad['shared_top_notes']
    assert "rose" in match_ad['shared_middle_notes']

    # Test case 3: Perfumes with no overlap
    notes4 = perfumes_db["Perfume E"]
    match_ae = match_perfumes(notes1, notes4)
    print(f"\nMatch between Perfume A and Perfume E (No Similarity):")
    print(f"  Shared Base Notes: {match_ae['shared_base_notes']} (Score: {match_ae['base_note_score']})")
    print(f"  Overall Compatibility Score: {match_ae['compatibility_score']}")
    assert match_ae['base_note_score'] == 0
    assert match_ae['compatibility_score'] == 0

    # Test case 4: One perfume has no base notes
    notes_no_base = {"top": ["Mint"], "middle": ["Waterlily"], "base": []}
    match_a_nobase = match_perfumes(notes1, notes_no_base)
    print(f"\nMatch between Perfume A and Perfume with no base notes:")
    print(f"  Shared Base Notes: {match_a_nobase['shared_base_notes']} (Score: {match_a_nobase['base_note_score']})")
    print(f"  Overall Compatibility Score: {match_a_nobase['compatibility_score']}")
    assert match_a_nobase['base_note_score'] == 0

    # Test case 5: Both perfumes have no base notes
    match_nobase_nobase = match_perfumes(notes_no_base, {"top": ["Apple"], "middle": ["Spice"], "base": []})
    print(f"\nMatch between two perfumes with no base notes:")
    print(f"  Shared Base Notes: {match_nobase_nobase['shared_base_notes']} (Score: {match_nobase_nobase['base_note_score']})")
    print(f"  Overall Compatibility Score: {match_nobase_nobase['compatibility_score']}")
    assert match_nobase_nobase['base_note_score'] == 0
    assert match_nobase_nobase['compatibility_score'] == 0

    # Test case 6: Empty notes dictionary for one perfume
    try:
        match_perfumes(notes1, {})
    except ValueError:
        print("\nSuccessfully caught ValueError for empty notes dict - test passed conceptually, but real test would be more specific if not using asserts for this.")
        pass # This is expected if we enforce structure, but current code is flexible.

    # Test with one perfume's notes completely empty
    match_empty_notes1 = match_perfumes(perfumes_db["Perfume A"], {})
    print(f"\nMatch with Perfume A and Empty Notes Profile:")
    print(f"  Result: {match_empty_notes1}")
    assert match_empty_notes1['base_note_score'] == 0
    assert match_empty_notes1['compatibility_score'] == 0

    match_empty_notes2 = match_perfumes({}, perfumes_db["Perfume A"])
    print(f"\nMatch with Empty Notes Profile and Perfume A:")
    print(f"  Result: {match_empty_notes2}")
    assert match_empty_notes2['base_note_score'] == 0
    assert match_empty_notes2['compatibility_score'] == 0

    match_both_empty = match_perfumes({}, {})
    print(f"\nMatch with two Empty Notes Profiles:")
    print(f"  Result: {match_both_empty}")
    assert match_both_empty['base_note_score'] == 0
    assert match_both_empty['compatibility_score'] == 0

    print("\n--- recommendation_engine.py tests completed ---")
