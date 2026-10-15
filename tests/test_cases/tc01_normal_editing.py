"""
TC01 — Normal Document Editing (Benign Scenario)
Performs normal user file editing in protected workspace.
Expected Result: No high-risk ransomware alert (False Positive = 0).
"""

import time
from honeyguard.analytics.benchmark import BenchmarkSuite


def test_tc01_scenario():
    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc01_normal_editing(trial=1)
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "FALSE_POSITIVE":
            assert m["val"] == 0.0


if __name__ == "__main__":
    test_tc01_scenario()
    print("TC01 PASSED: Normal editing generated zero false alerts.")
