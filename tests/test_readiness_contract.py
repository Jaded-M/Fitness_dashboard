from __future__ import annotations

import unittest
from datetime import date

import pandas as pd

from core.readiness_engine import ReadinessInputs, calculate_readiness


class ReadinessContractTests(unittest.TestCase):
    def test_empty_snapshot_returns_mobile_contract_fields(self):
        report = calculate_readiness(
            ReadinessInputs(
                workouts=pd.DataFrame(),
                food=pd.DataFrame(),
                steps=pd.DataFrame(),
                checkins=pd.DataFrame(),
                today=date(2026, 6, 13),
            )
        )

        required = {
            "score",
            "label",
            "training_load_score",
            "recovery_score",
            "activity_score",
            "nutrition_score",
            "subjective_score",
            "recommended_split",
            "key_action",
            "warnings",
            "insights",
            "muscle_status",
        }
        self.assertTrue(required.issubset(report))
        self.assertGreaterEqual(report["score"], 0)
        self.assertLessEqual(report["score"], 100)


if __name__ == "__main__":
    unittest.main()
