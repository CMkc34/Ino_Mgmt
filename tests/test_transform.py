"""Tests for pipelines/transform.py.

Each test gives a function a small, fixed input and checks the result
against a value worked out by hand.

TODO (owner, sprint 1): add tests for compute_trend_metrics
(acceptance criterion AC-1.5: at least one test per transform function).
"""

import pytest

from pipelines.transform import compound_annual_growth_rate


def test_growth_rate_doubling_in_one_year_is_100_percent():
    assert compound_annual_growth_rate(100, 200, years=1) == pytest.approx(1.0)


def test_growth_rate_doubling_in_five_years():
    # 2 ** (1/5) - 1 = 0.1487
    assert compound_annual_growth_rate(100, 200, years=5) == pytest.approx(0.1487, abs=1e-4)


def test_growth_rate_is_negative_when_the_value_shrinks():
    assert compound_annual_growth_rate(200, 100, years=1) == pytest.approx(-0.5)


def test_growth_rate_rejects_a_zero_start_value():
    with pytest.raises(ValueError):
        compound_annual_growth_rate(0, 100, years=5)


def test_growth_rate_rejects_zero_years():
    with pytest.raises(ValueError):
        compound_annual_growth_rate(100, 200, years=0)
