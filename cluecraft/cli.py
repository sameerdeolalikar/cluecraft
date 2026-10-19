import argparse
from dataclasses import asdict
import json
from pathlib import Path
from .puzzle import analyze, clues, parse_art
from .svg import render


def main(argv=None):
    parser = argparse.ArgumentParser(description="Turn ASCII pixel art into nonogram clues and printable puzzles.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="convert #/. text into clue JSON")
    export = commands.add_parser("render", help="create a printable puzzle or answer key from #/. text")
    export.add_argument("--solution", action="store_true", help="include the original filled cells")
    check = commands.add_parser("analyze", help="check clue JSON for uniqueness within a search budget")
    check.add_argument("--max-nodes", type=int, default=100000)
    for command in (build, export, check):
        command.add_argument("input", type=Path)
    for command in (build, export):
        command.add_argument("--output", "-o", type=Path, required=True)
        command.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > 100000:
            raise ValueError("input exceeds 100 KB")
        source = args.input.read_text(encoding="utf-8")
        if args.command == "analyze":
            result = analyze(json.loads(source), args.max_nodes)
            print(json.dumps(asdict(result), indent=2))
            return 0
        grid = parse_art(source)
        puzzle = clues(grid)
        output = json.dumps(puzzle, indent=2) + "\n" if args.command == "build" else render(
            puzzle, grid if args.solution else None
        )
        with args.output.open("w" if args.force else "x", encoding="utf-8") as stream:
            stream.write(output)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"cluecraft: {exc}\n")
    print(f"Created {args.output}.")
    return 0
