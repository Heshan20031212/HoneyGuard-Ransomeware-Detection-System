"""
TC07 — Benign High-I/O Workload
Performs rapid read/write operations on normal temporary files without touching decoys.
Expected Result: False-Positive Rate = 0.0%.
"""

from honeyguard.analytics.benchmark import BenchmarkSuite


def test_tc07_scenario():
    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc07_benign_high_io(trial=1)
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "FALSE_POSITIVE":
            assert m["val"] == 0.0


if __name__ == "__main__":
    test_tc07_scenario()
    print("TC07 PASSED: High-I/O benign workload generated zero false positives.")
