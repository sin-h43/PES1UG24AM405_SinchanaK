import pytest
from mobile_data_plan import overage_charge, recharge_allowed, validity_status


# ---------- overage_charge ----------
def test_within_included_data():
    assert overage_charge("standard", 3, False, False) == 0

def test_unknown_plan():
    with pytest.raises(ValueError):
        overage_charge("gold", 1, False, False)

def test_negative_usage():
    with pytest.raises(ValueError):
        overage_charge("basic", -1, False, False)

def test_loyal_basic_extra_gb():
    # included 2 + 1 loyalty = 3 -> no extra
    assert overage_charge("basic", 3, False, True) == 0

def test_overage_non_roaming():
    # extra 3 * 15
    assert overage_charge("standard", 8, False, False) == 45

def test_overage_roaming():
    # extra 3 * 40
    assert overage_charge("basic", 5, True, False) == 120

def test_heavy_overage_non_roaming():
    # extra 12 * (15 + 10)
    assert overage_charge("basic", 14, False, False) == 300

def test_heavy_overage_roaming():
    # extra 12 * (40 + 10 + 5)
    assert overage_charge("basic", 14, True, False) == 660


# ---------- recharge_allowed ----------
def test_recharge_allowed():
    assert recharge_allowed(500, 1, False) is True

def test_recharge_kyc_pending_within_limit():
    assert recharge_allowed(150, 0, True) is True

def test_recharge_amount_too_high():
    assert recharge_allowed(2500, 0, False) is False

def test_recharge_too_many_pending():
    assert recharge_allowed(500, 3, False) is False


# ---------- validity_status ----------
def test_validity_active_prepaid():
    assert validity_status(5, True, False) == "active"

def test_validity_grace_postpaid_addon():
    # cutoff = 3 + 2 = 5, days_left 2 -> grace
    assert validity_status(2, False, True) == "grace"

def test_validity_expired():
    assert validity_status(-20, True, False) == "expired"
