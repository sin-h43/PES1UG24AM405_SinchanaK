# Issues Found and Fixed — student_grade_system.py

Line numbers refer to the original file as analysed (re-check against your own report files).
Order: high and medium severity first.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Shell command built from input (Bandit B605, High) | Security | 53 | `os.system("echo ... " + filename)` passes `filename` to a shell, so a crafted name like `x; rm -rf ~` would run arbitrary commands. | Removed `os.system`; use `print()` for the message. |
| Weak MD5 hash (Bandit B324, High) | Security | 44 | `hashlib.md5` is broken and unsuitable for security use. | Switched to `hashlib.sha256`. |
| `eval()` on caller-supplied string (Bandit B307 / Pylint W0123, Medium) | Security | 40 | `eval(gpa_expr)` executes arbitrary Python code. | Removed `eval`; GPA is now `avg / scale` with a numeric `scale` parameter. |
| Insecure random for a PIN (Bandit B311, Low) | Security | 47 | `random.randint` is predictable and not meant for security values. | Use `secrets.randbelow` from the `secrets` module. |
| Hard-coded token, also printed (Bandit B105, Low) | Security | 56, 64 | Secret stored in source code and echoed to the console. | Read from env var `GRADE_PORTAL_TOKEN`; only print whether it is configured. |
| `try/except/pass` with bare `except` (Bandit B110, Pylint W0702, Flake8 E722) | Bug / Security | 22-25 | Hides every error (even a typo or Ctrl+C) and silently ignores unknown students. | Catch only `KeyError` and return `False`/`True` so callers know the outcome. |
| Mutable default argument (Pylint W0102) | Bug | 14 | `grade_list=[]` is created once and shared across calls, so the log grows across unrelated calls. | Default to `None`, create a new list inside the function. |
| Wrong GPA output (found by running the program) | Logic bug | 64 | `avg / 20.0` gave a GPA of 4.35, impossible on a 4.0 scale. | Use `avg / 25.0` (0-100 marks to 4.0 scale), rounded to 2 decimals; now prints 3.48. |
| Unused variables `grace_marks`, `avg_score` (Pylint W0612, Flake8 F841) | Code quality | 28, 39 | Dead code; `grace_marks` looks like an unfinished feature. | Removed `grace_marks`; `avg_score` is now actually used in the GPA calculation. |
| Unused import `json` (Pylint W0611, Flake8 F401) | Code quality | 6 | Import never used. | Removed. |
| File opened without `with` / encoding (Pylint R1732, W1514) | Code quality | 50-52 | File may stay open if `write` fails; encoding is platform-dependent. | `with open(filename, "w", encoding="utf-8")`. |
| Non-snake_case name `addGrade` (Pylint C0103) | Style | 14 | Violates PEP 8 naming. | Renamed to `add_grade` and updated the caller. |
| `== None` comparison (Pylint C0121, Flake8 E711) | Style | 29 | Should use identity check. | Use `is None`. |
| Redundant if/else returns (Pylint R1703, R1705) | Style | 32-35 | Can be one boolean return. | `return avg >= pass_threshold`. |
| `%` string formatting (Pylint C0209) | Style | 18 | Old style formatting. | Use an f-string. |
| Missing docstrings (Pylint C0116) | Style | 14-55 | No function documents its purpose. | Added one-line docstrings. |
| Blank-line spacing E302 / E305 | Formatting | 14-66 | Two blank lines required around top-level definitions. | Added; also wrapped `main()` in `if __name__ == "__main__":`. |
| Lines over 79 chars (Flake8 E501) | Formatting | 18, 31 | Line too long. | Shortened by using f-string and a local `student` variable. |

## Noted but not changed
- `record_attendance` adds days to a value that looks like a percentage (Bob goes 74 to 76), so the unit is inconsistent. This needs a design decision on whether attendance is stored as days or percent.
- `main()` was called at import time; now guarded with `if __name__ == "__main__":`.
