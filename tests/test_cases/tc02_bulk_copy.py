"""
TC02 — Normal Bulk Copying (Benign Scenario)
Copies multiple legitimate files into workspace.
Expected Result: No ransomware classification.
"""

from honeyguard.analytics.benchmark import BenchmarkSuite


def test_tc02_scenario():
    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc02_bulk_copying(trial=1)
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "FALSE_POSITIVE":
            assert m["val"] == 0.0


if __name__ == "__main__":
    test_tc02_scenario()
    print("TC02 PASSED: Bulk copying completed without ransomware alert.")
