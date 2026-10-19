from xml.etree import ElementTree as ET
from .puzzle import validate

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def render(puzzle, solution=None):
    validate(puzzle)
    rows, cols = puzzle["rows"], puzzle["columns"]
    cell = 7
    left = max(1, max(map(len, rows))) * cell + 10
    top = max(1, max(map(len, cols))) * cell + 24
    width, height = max(160, left + len(cols) * cell + 10), top + len(rows) * cell + 25
    root = ET.Element(f"{{{NS}}}svg", {"width": f"{width}mm", "height": f"{height}mm",
        "viewBox": f"0 0 {width} {height}", "font-family": "sans-serif",
        "role": "img", "aria-labelledby": "title"})

    def add(tag, **attrs):
        return ET.SubElement(root, f"{{{NS}}}{tag}", {k: str(v) for k, v in attrs.items()})

    add("title", id="title").text = "Cluecraft nonogram " + ("answer key" if solution is not None else "puzzle")
    add("rect", width="100%", height="100%", fill="white")
    add("text", x=10, y=13, **{"font-size": 5, "font-weight": "bold"}).text = "CLUECRAFT / " + ("ANSWER KEY" if solution is not None else "NONOGRAM")
    for y, clue in enumerate(rows):
        for offset, value in enumerate(reversed(clue or [0])):
            add("text", x=left - (offset + .5) * cell, y=top + (y + .7) * cell,
                **{"font-size": 3.4, "text-anchor": "middle"}).text = str(value)
    for x, clue in enumerate(cols):
        for offset, value in enumerate(reversed(clue or [0])):
            add("text", x=left + (x + .5) * cell, y=top - (offset + .3) * cell,
                **{"font-size": 3.4, "text-anchor": "middle"}).text = str(value)
    for y in range(len(rows)):
        for x in range(len(cols)):
            add("rect", x=left + x * cell, y=top + y * cell, width=cell, height=cell,
                fill="#21333d" if solution is not None and solution[y][x] else "white",
                stroke="#999", **{"stroke-width": .2})
    for x in range(0, len(cols) + 1, 5):
        add("line", x1=left + x * cell, x2=left + x * cell, y1=top, y2=top + len(rows) * cell,
            stroke="#21333d", **{"stroke-width": .5})
    for y in range(0, len(rows) + 1, 5):
        add("line", x1=left, x2=left + len(cols) * cell, y1=top + y * cell, y2=top + y * cell,
            stroke="#21333d", **{"stroke-width": .5})
    add("text", x=10, y=height - 13, **{"font-size": 3}).text = "Numbers show consecutive filled runs. Separate runs with at least one empty cell."
    add("text", x=10, y=height - 7, **{"font-size": 3}).text = "0 means an empty line. Check uniqueness with the analyze command before sharing."
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
