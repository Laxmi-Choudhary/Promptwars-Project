import unittest
from app import calculate_risk

class TestApp(unittest.TestCase):

    def test_safe(self):
        _, status = calculate_risk(50, 5)
        assert status == "Safe"

    def test_critical(self):
        _, status = calculate_risk(300, 80)
        assert status == "Critical"

if __name__ == "__main__":
    unittest.main()