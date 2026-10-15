"""
TC05 — Repeated Rename / Extension Changes
Changes extensions of synthetic files to .locked.
Expected Result: Extension change indicator triggers and suspicious behaviour is detected.
"""

from honeyguard.analytics.benchmark import BenchmarkSuite


def test_tc05_scenario():
    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc05_repeated_rename(trial=1)
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "FILES_RENAMED":
            assert m["val"] >= 8.0


if __name__ == "__main__":
    test_tc05_scenario()
    print("TC05 PASSED: Repeated rename and extension changes detected.")
