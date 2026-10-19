"""Nonogram clues, bounded exhaustive search, and strict document validation."""
from dataclasses import dataclass
from itertools import groupby


def runs(line):
    return [sum(1 for _ in cells) for value, cells in groupby(line) if value]


def parse_art(text):
    lines = text.strip().splitlines()
    if not lines or not 1 <= len(lines) <= 25 or not 1 <= len(lines[0]) <= 25:
        raise ValueError("art must be 1–25 rows and 1–25 columns")
    if any(len(line) != len(lines[0]) or any(c not in ".#" for c in line) for line in lines):
        raise ValueError("art must be rectangular, using only # (filled) and . (empty)")
    return [[int(c == "#") for c in line] for line in lines]


def clues(grid):
    return {"version": 1, "rows": [runs(row) for row in grid],
            "columns": [runs(column) for column in zip(*grid)]}


def validate(puzzle):
    if not isinstance(puzzle, dict) or type(puzzle.get("version")) is not int or puzzle["version"] != 1:
        raise ValueError("expected a version 1 puzzle object")
    rows, columns = puzzle.get("rows"), puzzle.get("columns")
    if not isinstance(rows, list) or not isinstance(columns, list) or not (
        1 <= len(rows) <= 25 and 1 <= len(columns) <= 25
    ):
        raise ValueError("puzzle must have 1–25 rows and columns")
    for lines, size in ((rows, len(columns)), (columns, len(rows))):
        for line in lines:
            if not isinstance(line, list) or any(type(n) is not int or n < 1 for n in line):
                raise ValueError("clues must be lists of positive integers; use [] for an empty line")
            if sum(line) + max(0, len(line) - 1) > size:
                raise ValueError("clues do not fit their line")
    if sum(map(sum, rows)) != sum(map(sum, columns)):
        raise ValueError("row and column clues disagree on the number of filled cells")
    return puzzle


class SearchLimit(ValueError):
    pass


def patterns(size, clue, limit=10000):
    """Generate all legal line fillings, refusing excessive domain sizes."""
    result = []

    def place(index, prefix):
        if len(result) >= limit:
            raise SearchLimit("line pattern limit reached; uniqueness is unknown")
        if index == len(clue):
            result.append(tuple(prefix + [0] * (size - len(prefix))))
            return
        remaining = sum(clue[index:]) + len(clue) - index - 1
        for start in range(len(prefix), size - remaining + 1):
            filled = prefix + [0] * (start - len(prefix)) + [1] * clue[index]
            place(index + 1, filled + ([0] if index + 1 < len(clue) else []))

    place(0, [])
    return result


@dataclass(frozen=True)
class Analysis:
    status: str
    solutions_found: int
    nodes: int
    first_solution: list | None


def analyze(puzzle, max_nodes=100000):
    """Stop at two solutions or a node budget. Never equate timeout with unique."""
    validate(puzzle)
    if type(max_nodes) is not int or max_nodes < 1:
        raise ValueError("max_nodes must be a positive integer")
    height, width = len(puzzle["rows"]), len(puzzle["columns"])
    try:
        row_options = [patterns(width, line) for line in puzzle["rows"]]
        col_options = [patterns(height, line) for line in puzzle["columns"]]
    except SearchLimit:
        return Analysis("unknown", 0, 0, None)
    found, nodes, stopped = [], 0, False

    def visit(board, columns):
        nonlocal nodes, stopped
        if len(found) >= 2 or stopped:
            return
        y = len(board)
        if y == height:
            found.append([list(row) for row in board])
            return
        for candidate in row_options[y]:
            if nodes >= max_nodes:
                stopped = True
                return
            nodes += 1
            narrowed = [[line for line in choices if line[y] == candidate[x]]
                        for x, choices in enumerate(columns)]
            if all(narrowed):
                visit(board + [candidate], narrowed)
            if len(found) >= 2 or stopped:
                return

    visit([], col_options)
    status = "multiple" if len(found) >= 2 else (
        "unknown" if stopped else "unique" if found else "unsatisfiable"
    )
    return Analysis(status, len(found), nodes, found[0] if found else None)
