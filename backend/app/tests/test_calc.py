import pytest
from app.engines.amortization import equal_payment_schedule
from app.modules.interest_only import interest_only_schedule

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_io_first_k_periods_interest_only():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    assert s["interest_only_months"] == 12
    first = s["rows"][:12]
    # 前 K 期：月供 == 利息，本金为零，余额不变
    for row in first:
        assert row["principal"] == 0.0
        assert row["payment"] == row["interest"] == 2916.67
        assert row["balance"] == 1_000_000.0
        assert row["segment"] == "interest_only"
    assert s["monthly_payment_interest_only"] == 2916.67

def test_io_second_segment_recomputes_equal_payment():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    rest = s["rows"][12:]
    assert len(rest) == 348
    # 第二段：剩余本金按等额本息，共 348 期
    expect = equal_payment_schedule(1_000_000, 3.5, 348)
    assert s["monthly_payment_amortizing"] == expect["monthly_payment"]
    assert all(r["segment"] == "amortizing" for r in rest)
    assert all(r["principal"] > 0 for r in rest)
    assert rest[-1]["balance"] == 0.0

def test_io_two_segment_payments_distinct():
    s = interest_only_schedule(1_000_000, 3.5, 360, 12)
    assert s["monthly_payment_interest_only"] < s["monthly_payment_amortizing"]
    assert s["segments"][0]["periods"] == 12
    assert s["segments"][1]["periods"] == 348
    assert s["total_payment"] == round(sum(r["payment"] for r in s["rows"]), 2)
    # 利息合计 = 只息段利息 + 第二段等额本息利息（沿用基础引擎的未取整累计口径）
    r = 3.5 / 12.0 / 100.0
    rest = equal_payment_schedule(1_000_000, 3.5, 348)
    assert s["total_interest"] == round(12 * 1_000_000 * r + rest["total_interest"], 2)

def test_io_invalid_k():
    with pytest.raises(ValueError):
        interest_only_schedule(100, 3, 360, 0)
    with pytest.raises(ValueError):
        interest_only_schedule(100, 3, 360, 360)
