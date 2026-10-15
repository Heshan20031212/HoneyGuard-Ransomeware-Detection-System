"""
TC04 — Rapid Mass Modification
Modifies multiple synthetic files rapidly within 2 seconds.
Expected Result: High-frequency indicator triggers and detection latency is recorded.
"""

from honeyguard.analytics.benchmark import BenchmarkSuite


def test_tc04_scenario():
    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc04_mass_modification(trial=1)
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "FILES_MODIFIED":
            assert m["val"] >= 10.0


if __name__ == "__main__":
    test_tc04_scenario()
    print("TC04 PASSED: Rapid mass modification detected.")
