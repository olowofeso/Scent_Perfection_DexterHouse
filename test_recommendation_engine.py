import unittest
from recommendation_engine import match_perfumes

class TestRecommendationEngine(unittest.TestCase):

    def setUp(self):
        """Set up mock perfume notes database for use in tests."""
        self.perfumes_db = {
            "Perfume A": {"top": ["Bergamot", "Lemon"], "middle": ["Rose", "Jasmine"], "base": ["Cedar", "Musk", "Amber"]},
            "Perfume B": {"top": ["Lemon", "Orange"], "middle": ["Jasmine", "Lily"], "base": ["Musk", "Vanilla", "Sandalwood"]},
            "Perfume C": {"top": ["Apple", "Mint"], "middle": ["Lavender", "Spice"], "base": ["Cedar", "Vetiver"]},
            "Perfume D": {"top": ["Bergamot"], "middle": ["Rose"], "base": ["Cedar", "Amber"]}, # High similarity to A
            "Perfume E": {"top": ["Grapefruit"], "middle": ["Peony"], "base": ["Patchouli"]}, # No similarity to A
            "Perfume F_NoBase": {"top": ["Mint"], "middle": ["Waterlily"], "base": []},
            "Perfume G_NoBase": {"top": ["Apple"], "middle": ["Spice"], "base": []}
        }

    def test_match_with_some_overlap(self):
        notes1 = self.perfumes_db["Perfume A"]
        notes2 = self.perfumes_db["Perfume B"]
        result = match_perfumes(notes1, notes2)

        self.assertEqual(result['base_note_score'], 1)
        self.assertIn("musk", result['shared_base_notes'])
        self.assertIn("lemon", result['shared_top_notes'])
        self.assertIn("jasmine", result['shared_middle_notes'])
        # Compatibility score: 1 (base) + 0.25 (top) + 0.25 (middle) = 1.5
        self.assertAlmostEqual(result['compatibility_score'], 1.5)

    def test_match_with_high_overlap(self):
        notes1 = self.perfumes_db["Perfume A"]
        notes_d = self.perfumes_db["Perfume D"] # Perfume D has high similarity to A
        result = match_perfumes(notes1, notes_d)

        self.assertEqual(result['base_note_score'], 2)
        self.assertIn("cedar", result['shared_base_notes'])
        self.assertIn("amber", result['shared_base_notes'])
        self.assertIn("bergamot", result['shared_top_notes'])
        self.assertIn("rose", result['shared_middle_notes'])
        # Compatibility score: 2 (base) + 0.25 (top) + 0.25 (middle) = 2.5
        self.assertAlmostEqual(result['compatibility_score'], 2.5)

    def test_match_with_no_overlap(self):
        notes1 = self.perfumes_db["Perfume A"]
        notes_e = self.perfumes_db["Perfume E"] # Perfume E has no similarity to A
        result = match_perfumes(notes1, notes_e)

        self.assertEqual(result['base_note_score'], 0)
        self.assertEqual(len(result['shared_base_notes']), 0)
        self.assertEqual(len(result['shared_top_notes']), 0)
        self.assertEqual(len(result['shared_middle_notes']), 0)
        self.assertAlmostEqual(result['compatibility_score'], 0.0)

    def test_one_perfume_no_base_notes(self):
        notes1 = self.perfumes_db["Perfume A"]
        notes_f_no_base = self.perfumes_db["Perfume F_NoBase"]
        result = match_perfumes(notes1, notes_f_no_base)

        self.assertEqual(result['base_note_score'], 0)
        self.assertAlmostEqual(result['compatibility_score'], 0.0) # Assuming no shared top/middle either

    def test_both_perfumes_no_base_notes(self):
        notes_f_no_base = self.perfumes_db["Perfume F_NoBase"]
        notes_g_no_base = self.perfumes_db["Perfume G_NoBase"] # Assuming G also has no overlap with F
        result = match_perfumes(notes_f_no_base, notes_g_no_base)

        self.assertEqual(result['base_note_score'], 0)
        # Example: Perfume F: {"top": ["Mint"], "middle": ["Waterlily"], "base": []}
        # Perfume G: {"top": ["Apple"], "middle": ["Spice"], "base": []}
        # No overlap in top or middle either for this specific example.
        self.assertAlmostEqual(result['compatibility_score'], 0.0)

    def test_empty_notes_dictionary_one_perfume(self):
        notes1 = self.perfumes_db["Perfume A"]
        result = match_perfumes(notes1, {}) # Second perfume has empty notes

        self.assertEqual(result['base_note_score'], 0)
        self.assertEqual(len(result['shared_base_notes']), 0)
        self.assertEqual(len(result['shared_top_notes']), 0)
        self.assertEqual(len(result['shared_middle_notes']), 0)
        self.assertAlmostEqual(result['compatibility_score'], 0.0)

    def test_empty_notes_dictionary_both_perfumes(self):
        result = match_perfumes({}, {}) # Both perfumes have empty notes

        self.assertEqual(result['base_note_score'], 0)
        self.assertAlmostEqual(result['compatibility_score'], 0.0)

    def test_case_insensitivity_in_notes(self):
        notes_x = {"top": ["Bergamot"], "middle": ["ROSE"], "base": ["Cedar", "musk"]}
        notes_y = {"top": ["bergamot", "Lemon"], "middle": ["Rose", "Jasmine"], "base": ["Musk", "Amber"]}
        result = match_perfumes(notes_x, notes_y)

        self.assertEqual(result['base_note_score'], 1)
        self.assertIn("musk", result['shared_base_notes'])
        self.assertIn("bergamot", result['shared_top_notes'])
        self.assertIn("rose", result['shared_middle_notes'])
        self.assertAlmostEqual(result['compatibility_score'], 1.5) # 1 (base) + 0.25 (top) + 0.25 (middle)

    def test_partial_shared_notes_different_categories(self):
        # Perfume P: Top: A, B; Middle: C, D; Base: E, F
        # Perfume Q: Top: A; Middle: X; Base: E, Y
        notes_p = {"top": ["A", "B"], "middle": ["C", "D"], "base": ["E", "F"]}
        notes_q = {"top": ["A"], "middle": ["X"], "base": ["E", "Y"]}
        result = match_perfumes(notes_p, notes_q)

        self.assertEqual(result['base_note_score'], 1) # Shared "E"
        self.assertIn("e", result['shared_base_notes'])
        self.assertEqual(len(result['shared_middle_notes']), 0)
        self.assertIn("a", result['shared_top_notes'])
        self.assertAlmostEqual(result['compatibility_score'], 1.25) # 1 (base) + 0.25 (top)

if __name__ == '__main__':
    unittest.main()
