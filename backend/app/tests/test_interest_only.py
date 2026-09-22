import json
import os
import tempfile
from pathlib import Path

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="mortgage-test-")

import pytest
from app.engines.amortization import equal_payment_schedule, interest_only_schedule
from app.modules import interest_only as interest_only_module
from app.seed import init_db
from app.services.mortgage_service import MortgageService


def test_first_k_periods_interest_only():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    for row in s["rows"][:12]:
        assert row["principal"] == 0.0
        assert row["payment"] == row["interest"]
        assert row["balance"] == 1_000_000.0
        assert row["segment"] == "interest_only"


def test_after_k_equal_payment_on_remaining():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    ref = equal_payment_schedule(1_000_000, 3.5, 348)
    assert s["monthly_payment_after"] == ref["monthly_payment"]
    assert s["rows"][12]["payment"] == ref["rows"][0]["payment"]
    assert s["rows"][12]["segment"] == "equal_payment"
    assert s["rows"][-1]["balance"] == 0.0


def test_two_segment_payments_and_totals():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    assert s["monthly_payment_io"] == round(1_000_000 * 3.5 / 1200, 2)
    expected_interest = round(12 * 1_000_000 * 3.5 / 1200 + equal_payment_schedule(1_000_000, 3.5, 348)["total_interest"], 2)
    assert s["total_interest"] == expected_interest
    assert len(s["rows"]) == 360


def test_zero_rate_interest_only():
    s = interest_only_schedule(120000, 0, 24, 6)
    assert s["monthly_payment_io"] == 0.0
    assert s["monthly_payment_after"] == round(120000 / 18, 2)
    assert s["rows"][-1]["balance"] == 0.0


def test_invalid_k_rejected():
    for bad in (0, -1, 360, 400):
        with pytest.raises(ValueError):
            interest_only_schedule(1_000_000, 3.5, 360, bad)
    with pytest.raises(ValueError):
        interest_only_module.validate_k(None, 360)


@pytest.fixture()
def svc():
    init_db()
    with MortgageService() as s:
        yield s


def test_service_interest_only_response(svc):
    out = svc.schedule(1_000_000, 3.5, 360, None, False, 12, True, 12)
    assert out["interest_only"] is True
    assert out["interest_only_months"] == 12
    assert out["monthly_payment_io"] == 2916.67
    assert out["monthly_payment_after"] == equal_payment_schedule(1_000_000, 3.5, 348)["monthly_payment"]
    assert out["run_id"] is None
    assert len(out["preview"]) == 12
    assert out["preview"][0]["segment"] == "interest_only"


def test_service_persist_false_writes_nothing(svc):
    before = len(svc.history(1000))
    svc.schedule(1_000_000, 3.5, 360, None, False, 12, True, 12)
    assert len(svc.history(1000)) == before


def test_service_persist_snapshot_immune_to_rule_change(svc):
    rule = svc.create_interest_only_rule("只息12期", 12, True)
    out = svc.schedule(1_000_000, 3.5, 360, None, True, 12, True, rule["interest_only_months"])
    assert out["run_id"]
    svc.update_interest_only_rule(rule["id"], "只息24期", 24, True)
    stored = [h for h in svc.history(1000) if h["id"] == out["run_id"]][0]
    payload = json.loads(stored["input_json"])
    result = json.loads(stored["result_json"])
    assert payload["interest_only_months"] == 12
    assert result["interest_only_months"] == 12
    assert result["monthly_payment_io"] == out["monthly_payment_io"]
    assert result["monthly_payment_after"] == out["monthly_payment_after"]


def test_service_rules_crud_and_disable(svc):
    rule = svc.create_interest_only_rule("只息6期", 6, True)
    assert rule["enabled"] is True
    updated = svc.update_interest_only_rule(rule["id"], "只息9期", 9, True)
    assert updated["interest_only_months"] == 9 and updated["name"] == "只息9期"
    disabled = svc.set_interest_only_rule_enabled(rule["id"], False)
    assert disabled["enabled"] is False
    assert svc.set_interest_only_rule_enabled(99999, False) is None
    ids = [r["id"] for r in svc.list_interest_only_rules()]
    assert rule["id"] in ids


def test_service_invalid_k_raises(svc):
    with pytest.raises(ValueError):
        svc.schedule(1_000_000, 3.5, 360, None, False, 12, True, 360)
    with pytest.raises(ValueError):
        svc.schedule(1_000_000, 3.5, 360, None, False, 12, True, None)


def test_service_unchecked_unchanged(svc):
    out = svc.schedule(1_000_000, 3.5, 360, None, False)
    assert "interest_only" not in out
    assert out["monthly_payment"] == 4490.45
