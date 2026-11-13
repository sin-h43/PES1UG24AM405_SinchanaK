import math
import re

MAX_GB = 10_000                 # sanity cap for plan data (GB)
MAX_DAILY_MB = 10_000_000       # sanity cap for one day's usage (MB)
MAX_AMOUNT = 1_000_000_000      # sanity cap for bill / discount

_NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?")   # plain ASCII decimal, no nan/inf/exponent/underscore
_INTEGER = re.compile(r"[0-9]+")


def _to_number(text, max_value):
    """Parse a plain non-negative decimal; return None if invalid, non-finite or too large."""
    text = text.strip()
    if not _NUMBER.fullmatch(text):
        return None
    value = float(text)
    if not math.isfinite(value) or value > max_value:
        return None
    return value


# Contract: these functions never raise on bad input - they return None instead.
def parse_plan(text):
    """'standard:5' -> ('Standard', 5.0); None if the input is invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    plan = parts[0].strip()
    gb = _to_number(parts[1], MAX_GB)
    if not plan or gb is None:
        return None
    return plan.title(), gb


def usage_average(usage_csv):
    """'300,450,800' -> 516.67 (average MB/day); None if the input is invalid."""
    if not isinstance(usage_csv, str):
        return None
    values = []
    for part in usage_csv.split(','):
        part = part.strip()
        if not _INTEGER.fullmatch(part) or len(part) > 12:
            return None
        value = int(part)
        if value > MAX_DAILY_MB:
            return None
        values.append(value)
    return round(sum(values) / len(values), 2)


def payable_bill(text):
    """'399|50' -> 420.82 (bill + 18% GST - discount, never negative); None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    bill = _to_number(parts[0], MAX_AMOUNT)
    discount = _to_number(parts[1], MAX_AMOUNT)
    if bill is None or discount is None:
        return None
    total = round(bill * 1.18 - discount, 2)
    if total <= 0:
        return 0.0
    return total


def main():
    print("==== Running parse_plan ====")
    user_input = input("Enter plan:data in GB (e.g. standard:5): ")
    result = parse_plan(user_input)
    print("Plan and Data:", result if result is not None
          else "Invalid input (expected plan:gb, e.g. standard:5)")

    print("\n==== Running usage_average ====")
    user_input = input("Enter daily usage in MB as CSV (e.g. 300,450,800): ")
    result = usage_average(user_input)
    print("Average Usage:", result if result is not None
          else "Invalid input (expected whole numbers separated by commas)")

    print("\n==== Running payable_bill ====")
    user_input = input("Enter bill|discount (e.g. 399|50): ")
    result = payable_bill(user_input)
    print("Payable Bill:", result if result is not None
          else "Invalid input (expected bill|discount as plain numbers)")


if __name__ == "__main__":
    main()
