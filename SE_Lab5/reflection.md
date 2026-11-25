# Reflection — Lab 5: Static Code Analysis

## 1. Which tool did you find most useful, and why?
For me Bandit was the most useful because it pointed straight at the dangerous lines (`os.system`, `eval`, MD5) and told me the severity and CWE, so I knew what to fix first. Pylint taught me the most about everyday code quality, and Flake8 was the quickest to clear.

## 2. Were there any false positives or warnings you disagreed with?
Mostly no. The hard-coded password warning (B105) was only rated low and the token was a demo value, but it was still a real habit worth fixing. The MD5 warning would be less serious if the hash were only a non-security checksum, but here it was used as an identifier, so I switched to SHA-256 anyway.

## 3. What did the tools miss?
The tools did not catch that the program printed a GPA of 4.35, which is impossible on a 4.0 scale, or that attendance mixes days and percentages. I only found the GPA bug by running the program and reading the output, so static analysis cannot replace running and testing the code.

## 4. How would you use static analysis in a real project?
I would run Flake8 and Pylint in a pre-commit hook and Bandit in a CI pipeline so every pull request is checked automatically. That way issues are caught early, before review, and the whole team follows the same style.

## What I learned
Fixing issues by severity worked well: security first, then bugs, then style. My Pylint score went from 5.71 to 10.00, Bandit went from 6 issues to 0 and Flake8 from 16 warnings to 0, while the program still runs and produces sensible output.
