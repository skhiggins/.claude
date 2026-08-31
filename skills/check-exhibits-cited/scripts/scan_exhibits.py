"""Flatten a LaTeX document in document order and list exhibit labels and references.

Output (tab-separated, one event per line, in document order):
  LABEL <label> <figure|table|none> <file>:<line> appendix=<yes|no>
  REF   <label> <file>:<line> in_float=<yes|no> appendix=<yes|no>
  WARNING ...
"""

import argparse
import re
import sys
from pathlib import Path

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
BEGIN_RE = re.compile(r"\\begin\s*\{([A-Za-z*]+)\}")
END_RE = re.compile(r"\\end\s*\{([A-Za-z*]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|vref|fref|cref|Cref|cpageref)\*?\s*\{([^}]+)\}")
APPENDIX_RE = re.compile(r"\\appendix\b|\\begin\s*\{appendices\}")
MACRO_DEF_RE = re.compile(r"\\(?:let|def|newcommand|renewcommand|providecommand)\b")

FLOAT_TYPES = {
    "figure": "figure",
    "figure*": "figure",
    "sidewaysfigure": "figure",
    "landscapefigure": "figure",
    "table": "table",
    "table*": "table",
    "sidewaystable": "table",
    "landscapetable": "table",
    "longtable": "table",
}


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
        self.env_stack = []
        self.appendix = False
        self.active = []  # files currently being processed, to break cycles

    def float_type(self):
        for env in reversed(self.env_stack):
            if env in FLOAT_TYPES:
                return FLOAT_TYPES[env]
        return "none"

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
            for m in BEGIN_RE.finditer(line):
                events.append((m.start(), "begin", m.group(1)))
            for m in END_RE.finditer(line):
                events.append((m.start(), "end", m.group(1)))
            for m in LABEL_RE.finditer(line):
                events.append((m.start(), "label", m.group(1)))
            for m in REF_RE.finditer(line):
                events.append((m.start(), "ref", m.group(1)))
            for m in INPUT_RE.finditer(line):
                events.append((m.start(), "input", m.group(1)))
            if APPENDIX_RE.search(line) and not MACRO_DEF_RE.search(line):
                events.append((APPENDIX_RE.search(line).start(), "appendix", ""))
            for _, kind, arg in sorted(events, key=lambda e: e[0]):
                app = "yes" if self.appendix else "no"
                if kind == "begin":
                    self.env_stack.append(arg)
                    if arg == "appendices":
                        self.appendix = True
                elif kind == "end":
                    if arg in self.env_stack:
                        while self.env_stack and self.env_stack[-1] != arg:
                            self.env_stack.pop()
                        if self.env_stack:
                            self.env_stack.pop()
                elif kind == "appendix":
                    self.appendix = True
                elif kind == "label":
                    print(f"LABEL\t{arg.strip()}\t{self.float_type()}\t{rel}:{lineno}\tappendix={app}")
                elif kind == "ref":
                    in_float = "yes" if self.float_type() != "none" else "no"
                    for label in arg.split(","):
                        print(f"REF\t{label.strip()}\t{rel}:{lineno}\tin_float={in_float}\tappendix={app}")
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
