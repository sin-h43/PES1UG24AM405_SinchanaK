import pytest
from mobile_data_plan import overage_charge, recharge_allowed, validity_status


# ================= overage_charge =================
# plan not in INCLUDED_GB  (True / False)
def test_unknown_plan():
    with pytest.raises(ValueError, match="unknown plan"):
        overage_charge("gold", 1, False, False)

# data_gb < 0  (True / False)
def test_negative_usage():
    with pytest.raises(ValueError, match="invalid data usage"):
        overage_charge("basic", -1, False, False)

def test_zero_usage_is_valid():
    assert overage_charge("basic", 0, False, False) == 0

# is_loyal and plan != "premium"  (T / F-loyal False / F-premium)
def test_loyal_non_premium_gets_bonus_gb():
    assert overage_charge("basic", 3, False, True) == 0      # included 3

def test_not_loyal_no_bonus():
    assert overage_charge("basic", 3, False, False) == 15    # extra 1

def test_loyal_premium_no_bonus():
    assert overage_charge("premium", 11, False, True) == 15  # extra 1, no bonus

# extra <= 0  (True / False, boundary)
def test_within_included_data():
    assert overage_charge("standard", 3, False, False) == 0

def test_exactly_at_limit():
    assert overage_charge("standard", 5, False, False) == 0

# is_roaming  (True / False) with extra <= 10
def test_overage_non_roaming():
    assert overage_charge("standard", 8, False, False) == 45

def test_overage_roaming():
    assert overage_charge("basic", 5, True, False) == 120

# extra > 10  (True / False, boundary at 10 and 11)
def test_extra_exactly_10_no_surcharge():
    assert overage_charge("basic", 12, False, False) == 150  # 10 * 15

def test_extra_11_surcharge_non_roaming():
    assert overage_charge("basic", 13, False, False) == 275  # 11 * 25

def test_extra_11_surcharge_roaming():
    assert overage_charge("basic", 13, True, False) == 605   # 11 * 55


# ================= recharge_allowed =================
# is_kyc_pending True: amount <= 200 (T / F)
def test_kyc_pending_within_limit():
    assert recharge_allowed(200, 0, True) is True

def test_kyc_pending_over_limit():
    assert recharge_allowed(201, 0, True) is False

# is_kyc_pending False: amount > 2000 (T / F)
def test_amount_over_2000():
    assert recharge_allowed(2001, 0, False) is False

def test_amount_exactly_2000():
    assert recharge_allowed(2000, 0, False) is True

# pending_recharges <= 2 (T / F)
def test_recharge_allowed():
    assert recharge_allowed(500, 1, False) is True

def test_pending_at_limit():
    assert recharge_allowed(500, 2, False) is True

def test_pending_over_limit():
    assert recharge_allowed(500, 3, False) is False


# ================= validity_status =================
# is_prepaid (T / F) x has_addon (T / F)
def test_prepaid_no_addon_active_boundary():
    assert validity_status(0, True, False) == "active"       # cutoff 0

def test_postpaid_no_addon_active():
    assert validity_status(3, False, False) == "active"      # cutoff 3

def test_prepaid_addon_active():
    assert validity_status(2, True, True) == "active"        # cutoff 2

def test_postpaid_addon_active():
    assert validity_status(5, False, True) == "active"       # cutoff 5

# elif days_left >= cutoff - 15 (T / F)
def test_grace_upper():
    assert validity_status(-1, True, False) == "grace"

def test_grace_lower_boundary():
    assert validity_status(-15, True, False) == "grace"

def test_expired():
    assert validity_status(-16, True, False) == "expired"

def test_postpaid_addon_grace_and_expired():
    assert validity_status(4, False, True) == "grace"
    assert validity_status(-11, False, True) == "expired"    # cutoff-15 = -10
