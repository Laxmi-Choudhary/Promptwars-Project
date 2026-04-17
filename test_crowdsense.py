import unittest
from app import calculate_risk, decision_engine

class TestCrowdSense(unittest.TestCase):

    def test_safe_zone(self):
        score, status = calculate_risk(50, 5)
        self.assertEqual(status, "Safe")

    def test_moderate_zone(self):
        score, status = calculate_risk(120, 20)
        self.assertEqual(status, "Moderate")

    def test_critical_zone(self):
        score, status = calculate_risk(250, 80)
        self.assertEqual(status, "Critical")

    def test_decision_engine(self):
        row = {"Risk_Score": 85}
        self.assertEqual(decision_engine(row), "🔴 EMERGENCY")

if __name__ == "__main__":
    unittest.main()