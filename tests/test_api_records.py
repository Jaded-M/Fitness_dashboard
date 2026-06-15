from __future__ import annotations

import unittest

from api.services.records import epley_1rm, record_board, top_set


class RecordServiceTests(unittest.TestCase):
    def test_top_set_prefers_structured_sets(self):
        row = {
            "weight": 80,
            "reps": 24,
            "set_data": [
                {"weight": 80, "reps": 8},
                {"weight": 85, "reps": 5},
            ],
        }
        self.assertEqual(top_set(row), (85.0, 5))

    def test_record_board_uses_best_estimated_one_rep_max(self):
        workouts = [
            {
                "date": "2026-06-01",
                "exercise": "Bench Press",
                "set_data": [{"weight": 80, "reps": 8}],
            },
            {
                "date": "2026-06-08",
                "exercise": "Bench Press",
                "set_data": [{"weight": 87.5, "reps": 3}],
            },
        ]
        records = record_board(workouts)
        self.assertEqual(records[0]["exercise"], "Bench Press")
        self.assertEqual(records[0]["weight"], 80.0)
        self.assertEqual(records[0]["estimated_1rm"], round(epley_1rm(80, 8), 1))


if __name__ == "__main__":
    unittest.main()
