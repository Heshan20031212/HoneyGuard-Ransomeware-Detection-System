"""
TC03 — Single Decoy Access
Touches or modifies a registered honeytoken canary file.
Expected Result: Suspicious event logged, Risk Score = 40 (remains below alert threshold 70).
"""

from honeyguard.analytics.benchmark import BenchmarkSuite
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.database.repositories import DirectoryRepository
from honeyguard.utils.paths import get_demo_workspace


def test_tc03_scenario():
    ws = get_demo_workspace() / "Finance"
    dir_id = DirectoryRepository.add_directory(str(ws), "Finance Demo", True)
    decoys = DecoyRegistry.list_decoys()
    if not decoys:
        DecoyRegistry.deploy_default_canary_pack(dir_id, "Finance")
        decoys = DecoyRegistry.list_decoys()

    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc03_decoy_access(trial=1, decoy_record=decoys[0])
    assert res["result"] == "PASS"
    for m in res["measurements"]:
        if m["name"] == "RISK_SCORE":
            assert m["val"] == 40.0
        elif m["name"] == "ALERT_TRIGGERED":
            assert m["val"] == 0.0


if __name__ == "__main__":
    test_tc03_scenario()
    print("TC03 PASSED: Canary touched, logged with score 40, below threshold 70.")
