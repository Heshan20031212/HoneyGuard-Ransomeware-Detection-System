"""
TC06 — Controlled Encryption-Like Simulation + Decoy Hit
Simulates encryption by writing high-entropy bytes and targeting a canary token.
Expected Result: Composite Risk Score >= 70, High-Risk Alert raised, Containment triggered!
"""

from honeyguard.analytics.benchmark import BenchmarkSuite
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.database.repositories import DirectoryRepository
from honeyguard.utils.paths import get_demo_workspace


def test_tc06_scenario():
    ws = get_demo_workspace() / "Finance"
    dir_id = DirectoryRepository.add_directory(str(ws), "Finance Demo", True)
    decoys = DecoyRegistry.list_decoys()
    if not decoys:
        DecoyRegistry.deploy_default_canary_pack(dir_id, "Finance")
        decoys = DecoyRegistry.list_decoys()

    suite = BenchmarkSuite(trials_per_scenario=1)
    res = suite.run_tc06_encryption_simulation(trial=1, decoy_record=decoys[0])
    assert res["result"] == "PASS"

    scores = [m["val"] for m in res["measurements"] if m["name"] == "RISK_SCORE"]
    assert len(scores) == 1
    assert scores[0] >= 70.0


if __name__ == "__main__":
    test_tc06_scenario()
    print("TC06 PASSED: Controlled encryption simulated, high-risk alert & containment verified.")
