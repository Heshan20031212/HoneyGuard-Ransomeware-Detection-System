"""
Unit Tests: Weighted Risk Engine & Threshold Evaluation
Formula: Risk Score = Honeytoken (40) + Activity (25) + Rename (20) + Entropy (18)
"""

from honeyguard.detection.risk_engine import RiskEngine


def test_risk_score_calculation():
    engine = RiskEngine(
        honeytoken_weight=40,
        file_activity_weight=25,
        rename_extension_weight=20,
        entropy_weight=18,
        threshold=70
    )

    # 1. Only Honeytoken interaction -> 40 (MEDIUM, not alert)
    res1 = engine.evaluate_risk({"honeytoken_interaction": True})
    assert res1["risk_score"] == 40
    assert res1["risk_level"] == "MEDIUM"
    assert res1["is_alert"] is False

    # 2. Honeytoken + High Frequency -> 40 + 25 = 65 (MEDIUM, not alert)
    res2 = engine.evaluate_risk({
        "honeytoken_interaction": True,
        "high_frequency_file_activity": True
    })
    assert res2["risk_score"] == 65
    assert res2["is_alert"] is False

    # 3. Honeytoken + High Frequency + Extension Change -> 40 + 25 + 20 = 85 (HIGH, ALERT)
    res3 = engine.evaluate_risk({
        "honeytoken_interaction": True,
        "high_frequency_file_activity": True,
        "rename_extension_change": True
    })
    assert res3["risk_score"] == 85
    assert res3["risk_level"] == "HIGH"
    assert res3["is_alert"] is True

    # 4. All 4 indicators -> 40 + 25 + 20 + 18 = 103 (CRITICAL, ALERT)
    res4 = engine.evaluate_risk({
        "honeytoken_interaction": True,
        "high_frequency_file_activity": True,
        "rename_extension_change": True,
        "content_entropy_change": True
    })
    assert res4["risk_score"] == 103
    assert res4["risk_level"] == "CRITICAL"
    assert res4["is_alert"] is True
