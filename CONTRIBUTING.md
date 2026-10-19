# Contributing

Use Python 3.11+, four-space indentation, and descriptive snake_case names. Run
`python3 -m unittest discover -s tests -v` before sending a pull request.

Keep solving independent of rendering and command-line I/O. For solver changes,
cross-check small grids against enumeration, exercise budget exhaustion, and
never report uniqueness without finishing the necessary search. Include a tiny
reproducible puzzle for a bug report. Distinguish human-solvable deductions from
backtracking results.

Keep commits focused with imperative subjects. Pull requests should describe the
problem, behavior, relevant issue, and validation. Use original puzzle designs;
do not copy commercial puzzle collections or include personal data or secrets.
Preserve any required third-party attribution and licenses.
