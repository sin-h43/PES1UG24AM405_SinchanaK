from hypothesis import given, settings, strategies as st
from mobile_data_plan import parse_plan, usage_average, payable_bill


# ---------------- required fuzz tests: random text / None must never crash ----------------
@given(st.text() | st.none())
def test_parse_plan_no_crash(s):
    try:
        parse_plan(s)
    except Exception as e:
        assert False, f"parse_plan crashed with {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_usage_average_no_crash(s):
    try:
        usage_average(s)
    except Exception as e:
        assert False, f"usage_average crashed with {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
    try:
        payable_bill(s)
    except Exception as e:
        assert False, f"payable_bill crashed with {type(e).__name__}: {e}"


# ---------------- smarter fuzzing: structured inputs that reach the real logic ----------------
# Text built from the characters these parsers care about (digits, separators, nan/inf letters)
tricky_text = st.text(alphabet="0123456789.,:|-+eE_ naif\t\n", max_size=30)
anything = st.one_of(st.none(), st.integers(), st.floats(), st.binary(),
                     st.lists(st.integers(), max_size=3))


@settings(max_examples=500, deadline=None)
@given(tricky_text | anything)
def test_all_functions_no_crash_on_tricky_input(s):
    for fn in (parse_plan, usage_average, payable_bill):
        try:
            fn(s)
        except Exception as e:
            assert False, f"{fn.__name__}({s!r}) crashed with {type(e).__name__}: {e}"


# ---------------- properties on valid input ----------------
@settings(max_examples=300, deadline=None)
@given(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu")), min_size=1, max_size=10),
       st.integers(0, 10_000))
def test_parse_plan_valid(plan, gb):
    assert parse_plan(f"  {plan} : {gb} ") == (plan.title(), float(gb))


@settings(max_examples=300, deadline=None)
@given(st.text(alphabet="0123456789. ", max_size=10), st.integers(0, 100))
def test_parse_plan_rejects_missing_or_extra_separator(a, b):
    assert parse_plan(f"{a}{b}") is None            # no ':'
    assert parse_plan(f"{a}:{b}:{b}") is None       # two ':'


@settings(max_examples=300, deadline=None)
@given(st.lists(st.integers(0, 10_000_000), min_size=1, max_size=50))
def test_usage_average_within_min_max(values):
    result = usage_average(",".join(map(str, values)))
    assert min(values) <= result <= max(values)
    assert abs(result - sum(values) / len(values)) <= 0.005 + 1e-9


@settings(max_examples=200, deadline=None)
@given(st.lists(st.integers(0, 1000), max_size=5), st.sampled_from(["", " ", "x", "-5", "1.5", "nan", "1_0"]))
def test_usage_average_rejects_bad_element(values, bad):
    csv = ",".join(map(str, values + [bad]))
    assert usage_average(csv) is None


@settings(max_examples=300, deadline=None)
@given(st.floats(0, 1_000_000), st.floats(0, 1_000_000))
def test_payable_bill_non_negative_and_bounded(bill, discount):
    result = payable_bill(f"{bill:.2f}|{discount:.2f}")
    assert result is not None
    assert 0 <= result <= float(f"{bill:.2f}") * 1.18 + 0.01


@settings(max_examples=200, deadline=None)
@given(st.floats(0, 1000), st.sampled_from(["nan", "inf", "-5", "1e3", "", "abc"]))
def test_payable_bill_rejects_bad_discount(bill, bad):
    assert payable_bill(f"{bill:.2f}|{bad}") is None


# ---------------- regression tests for bugs fuzzing found ----------------
def test_none_input():
    assert parse_plan(None) is None and usage_average(None) is None and payable_bill(None) is None

def test_missing_separator():
    assert parse_plan("standard") is None
    assert payable_bill("399") is None

def test_too_many_separators():
    assert parse_plan("a:b:5") is None
    assert payable_bill("1|2|3") is None

def test_empty_plan_name():
    assert parse_plan(":5") is None

def test_nan_and_inf_rejected():
    assert parse_plan("basic:nan") is None
    assert parse_plan("basic:inf") is None
    assert payable_bill("nan|0") is None
    assert payable_bill("100|inf") is None

def test_empty_usage_entries():
    assert usage_average("") is None
    assert usage_average("1,,3") is None
    assert usage_average("1,2,") is None

def test_negative_values_rejected():
    assert usage_average("-5,10") is None
    assert payable_bill("-100|0") is None
    assert payable_bill("100|-50") is None

def test_average_not_truncated():
    assert usage_average("300,451") == 375.5      # old code gave 375 (floor division)

def test_bill_example_and_floor_at_zero():
    assert payable_bill("399|50") == 420.82
    assert payable_bill("100|500") == 0.0

def test_huge_numbers_rejected():
    assert usage_average("9" * 5000) is None
    assert payable_bill("9" * 500 + "|0") is None
