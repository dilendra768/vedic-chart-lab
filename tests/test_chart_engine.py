import pytest
from chart_engine import divisional_sign, sign_index, degree_in_sign

def test_longitude_helpers():
    assert sign_index(0) == 0
    assert sign_index(359.9) == 11
    assert degree_in_sign(35.5) == pytest.approx(5.5)

def test_d1_keeps_rashi_sign():
    assert divisional_sign(45.0, 1) == 1

def test_d9_first_part_aries_is_aries():
    assert divisional_sign(1.0, 9) == 0

def test_d9_first_part_taurus_starts_capricorn():
    assert divisional_sign(31.0, 9) == 9

def test_d30_odd_sign_segments():
    assert divisional_sign(2.0, 30) == 0
    assert divisional_sign(7.0, 30) == 10

def test_invalid_division_fallback_is_deterministic():
    assert divisional_sign(42.0, 5) == divisional_sign(42.0, 5)
