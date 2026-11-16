import contextlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET
from cluecraft.puzzle import analyze, clues, parse_art, patterns, runs, validate
from cluecraft.cli import main
from cluecraft.svg import render


class PuzzleTests(unittest.TestCase):
    def test_runs_and_empty_lines(self):
        self.assertEqual(runs([1, 1, 0, 1, 0, 1, 1]), [2, 1, 2])
        self.assertEqual(runs([0, 0]), [])
        self.assertEqual(patterns(4, []), [(0, 0, 0, 0)])

    def test_pattern_generator_matches_brute_force(self):
        for size in range(1, 8):
            grouped = {}
            for line in itertools.product((0, 1), repeat=size):
                grouped.setdefault(tuple(runs(line)), set()).add(line)
            for clue, expected in grouped.items():
                self.assertEqual(set(patterns(size, clue)), expected)

    def test_unique_filled_and_empty_puzzles(self):
        for art in ("###\n###", "...\n..."):
            grid = parse_art(art)
            result = analyze(clues(grid))
            self.assertEqual(result.status, "unique")
            self.assertEqual(result.first_solution, grid)

    def test_ambiguous_diagonal(self):
        result = analyze(clues(parse_art("#.\n.#")))
        self.assertEqual((result.status, result.solutions_found), ("multiple", 2))

    def test_budget_does_not_claim_unique(self):
        result = analyze(clues(parse_art("#.\n.#")), max_nodes=1)
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.nodes, 1)

    def test_unsatisfiable_but_equal_totals(self):
        puzzle = {"version": 1, "rows": [[2], []], "columns": [[2], []]}
        self.assertEqual(analyze(puzzle).status, "unsatisfiable")

    def test_all_two_by_three_puzzles_against_enumeration(self):
        groups = {}
        for bits in itertools.product((0, 1), repeat=6):
            grid = [list(bits[:3]), list(bits[3:])]
            puzzle = clues(grid)
            key = json.dumps(puzzle, sort_keys=True)
            groups.setdefault(key, []).append(grid)
        for key, grids in groups.items():
            result = analyze(json.loads(key))
            self.assertEqual(result.status, "unique" if len(grids) == 1 else "multiple")
            self.assertIn(result.first_solution, grids)

    def test_invalid_art_and_clues(self):
        for art in ("", "##\n#", "x.", "#" * 26):
            with self.assertRaises(ValueError):
                parse_art(art)
        for puzzle in ({"version": 1, "rows": [[0]], "columns": [[]]},
                       {"version": 1, "rows": [[1]], "columns": [[]]},
                       {"version": 1, "rows": [[2]], "columns": [[1]]}):
            with self.assertRaises(ValueError):
                validate(puzzle)

    def test_art_rejects_surrounding_spaces_and_tabs(self):
        for art in (" #", "# ", "\t#", "#\t", "\n #\n", "\n# \n"):
            with self.subTest(art=art), self.assertRaises(ValueError):
                parse_art(art)
        for art in ("#\n", "\n#\n", "#\r\n", "\r\n#\r\n"):
            with self.subTest(art=art):
                self.assertEqual(parse_art(art), [[1]])

    def test_cli_rejects_art_with_surrounding_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory) / "art.txt"
            output = Path(directory) / "output"
            art.write_text(" #\n", encoding="utf-8")
            for command in ("build", "render"):
                with self.subTest(command=command):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
                        main([command, str(art), "-o", str(output)])
                    self.assertEqual(error.exception.code, 2)
                    self.assertIn("using only #", stderr.getvalue())
                    self.assertFalse(output.exists())

    def test_blank_puzzle_svg_does_not_reveal_solution(self):
        grid = parse_art("###\n###")
        ns = {"s": "http://www.w3.org/2000/svg"}
        blank = ET.fromstring(render(clues(grid)))
        answer = ET.fromstring(render(clues(grid), grid))
        self.assertEqual(len(blank.findall("s:rect[@fill='#21333d']", ns)), 0)
        self.assertEqual(len(answer.findall("s:rect[@fill='#21333d']", ns)), 6)

    def test_art_rejects_nonstandard_line_separators(self):
        for separator in ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            for art in ("#" + separator + "#", "#" + separator):
                with self.subTest(art=art), self.assertRaises(ValueError):
                    parse_art(art)
        for separator in ("\n", "\r\n", "\r"):
            with self.subTest(separator=separator):
                self.assertEqual(parse_art(separator + "#" + separator + "." + separator), [[1], [0]])

    def test_cli_rejects_nonstandard_line_separators(self):
        with tempfile.TemporaryDirectory() as directory:
            art, output = Path(directory) / "art.txt", Path(directory) / "output"
            for separator in ("\v", "\u2028"):
                art.write_text("#" + separator + "#", encoding="utf-8")
                for command in ("build", "render"):
                    with self.subTest(separator=separator, command=command):
                        stderr = io.StringIO()
                        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
                            main([command, str(art), "-o", str(output)])
                        self.assertEqual(error.exception.code, 2)
                        self.assertIn("using only #", stderr.getvalue())
                        self.assertFalse(output.exists())

    def test_cli_build_analyze_and_output_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            art, output = Path(directory) / "art.txt", Path(directory) / "clues.json"
            art.write_text("###\n###")
            args = ["build", str(art), "-o", str(output)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(main(["analyze", str(output)]), 0)
            self.assertEqual(json.loads(stream.getvalue())["status"], "unique")
            before = output.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(args)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
