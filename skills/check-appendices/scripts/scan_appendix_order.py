"""Flatten a LaTeX document and map appendix sections, their labels, and all references.

Output (tab-separated, in document order):
  APPENDIX <idx> <file>:<line> <title>          -- a \\section in the appendix part
  LABEL <label> in=<idx|main> <file>:<line>     -- every \\label, attributed to the
                                                   appendix section it appears in
  REF <label> loc=<idx|main> <file>:<line>      -- every reference; loc is where the
                                                   reference itself sits
  WARNING ...
"""

import argparse
import re
import sys
from pathlib import Path

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|vref|fref|cref|Cref|cpageref)\*?\s*\{([^}]+)\}")
SECTION_RE = re.compile(r"\\section\s*\*?\s*\{([^}]*)\}")
APPENDIX_RE = re.compile(r"\\appendix\b|\\begin\s*\{appendices\}")
MACRO_DEF_RE = re.compile(r"\\(?:let|def|newcommand|renewcommand|providecommand)\b")


def strip_comment(line):
    i = 0
    while True:
        j = line.find("%", i)
        if j == -1:
            return line
        if j > 0 and line[j - 1] == "\\":
            i = j + 1
            continue
        return line[:j]


class Scanner:
    def __init__(self, base):
        self.base = base  # compile dir: \input paths resolve relative to it
        self.appendix = False
        self.app_idx = 0  # 0 = main text (or appendix front matter before first \section)
        self.active = []  # files currently being processed, to break cycles

    def loc(self):
        return str(self.app_idx) if self.appendix and self.app_idx > 0 else "main"

    def process(self, path):
        path = path.resolve()
        if path in self.active:
            print(f"WARNING\tcircular include of {path}, skipped")
            return
        self.active.append(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"WARNING\tcould not read {path}: {e}")
            self.active.pop()
            return
        rel = path.as_posix()
        for lineno, raw in enumerate(text.splitlines(), 1):
            line = strip_comment(raw)
            events = []
            for m in SECTION_RE.finditer(line):
                events.append((m.start(), "section", m.group(1)))
            for m in LABEL_RE.finditer(line):
                events.append((m.start(), "label", m.group(1)))
            for m in REF_RE.finditer(line):
                events.append((m.start(), "ref", m.group(1)))
            for m in INPUT_RE.finditer(line):
                events.append((m.start(), "input", m.group(1)))
            if APPENDIX_RE.search(line) and not MACRO_DEF_RE.search(line):
                events.append((APPENDIX_RE.search(line).start(), "appendix", ""))
            for _, kind, arg in sorted(events, key=lambda e: e[0]):
                if kind == "appendix":
                    self.appendix = True
                elif kind == "section":
                    if self.appendix:
                        self.app_idx += 1
                        print(f"APPENDIX\t{self.app_idx}\t{rel}:{lineno}\t{arg.strip()}")
                elif kind == "label":
                    print(f"LABEL\t{arg.strip()}\tin={self.loc()}\t{rel}:{lineno}")
                elif kind == "ref":
                    for label in arg.split(","):
                        print(f"REF\t{label.strip()}\tloc={self.loc()}\t{rel}:{lineno}")
                elif kind == "input":
                    target = arg.strip()
                    if not target.lower().endswith(".tex"):
                        target += ".tex"
                    cand = self.base / target
                    if not cand.exists() and (path.parent / target).exists():
                        cand = path.parent / target
                    if cand.exists():
                        self.process(cand)
                    else:
                        print(f"WARNING\t{rel}:{lineno} includes {target}, which was not found")
        self.active.pop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="root .tex file (the file that is compiled)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        sys.exit(f"ERROR: {root} not found")
    Scanner(root.parent).process(root)


if __name__ == "__main__":
    main()