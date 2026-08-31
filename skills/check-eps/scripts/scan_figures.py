"""Flatten a LaTeX document and list every \\includegraphics with EPS-version info.

Output (tab-separated, one figure per line, in document order):
  FIG <texfile>:<line> <as-written> resolved=<path|NOT-FOUND> ext=<ext|none>
      eps=<path|none> fig_mtime=<iso|na> eps_mtime=<iso|na> eps_newer=<yes|no|na>
  WARNING ...
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
GRAPHICSPATH_RE = re.compile(r"\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}")
GPATH_ENTRY_RE = re.compile(r"\{([^}]*)\}")

# pdflatex's default search order for extensionless \includegraphics
DEFAULT_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".eps"]


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


def mtime_iso(path):
    return datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat(sep=" ", timespec="seconds")


class Scanner:
    def __init__(self, base):
        self.base = base  # compile dir: \input and figure paths resolve relative to it
        self.graphicspaths = []
        self.active = []  # files currently being processed, to break cycles

    def resolve_figure(self, target, texdir):
        dirs = [self.base, texdir] + [self.base / g for g in self.graphicspaths]
        has_ext = Path(target).suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps"}
        for d in dirs:
            cand = d / target
            if has_ext:
                if cand.exists():
                    return cand.resolve()
            else:
                for ext in DEFAULT_EXTS:
                    if cand.with_suffix(cand.suffix + ext).exists():
                        return cand.with_suffix(cand.suffix + ext).resolve()
        return None

    def report_figure(self, rel, lineno, target, texdir):
        resolved = self.resolve_figure(target, texdir)
        if resolved is None:
            print(f"FIG\t{rel}:{lineno}\t{target}\tresolved=NOT-FOUND\text=none\t"
                  f"eps=none\tfig_mtime=na\teps_mtime=na\teps_newer=na")
            return
        ext = resolved.suffix.lower()
        if ext == ".eps":
            print(f"FIG\t{rel}:{lineno}\t{target}\tresolved={resolved.as_posix()}\text=.eps\t"
                  f"eps=none\tfig_mtime={mtime_iso(resolved)}\teps_mtime=na\teps_newer=na")
            return
        eps = resolved.with_suffix(".eps")
        if eps.exists():
            newer = "yes" if eps.stat().st_mtime > resolved.stat().st_mtime else "no"
            print(f"FIG\t{rel}:{lineno}\t{target}\tresolved={resolved.as_posix()}\text={ext}\t"
                  f"eps={eps.as_posix()}\tfig_mtime={mtime_iso(resolved)}\t"
                  f"eps_mtime={mtime_iso(eps)}\teps_newer={newer}")
        else:
            print(f"FIG\t{rel}:{lineno}\t{target}\tresolved={resolved.as_posix()}\text={ext}\t"
                  f"eps=none\tfig_mtime={mtime_iso(resolved)}\teps_mtime=na\teps_newer=na")

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
            for m in GRAPHICSPATH_RE.finditer(line):
                for entry in GPATH_ENTRY_RE.finditer(m.group(1)):
                    if entry.group(1) not in self.graphicspaths:
                        self.graphicspaths.append(entry.group(1))
            events = []
            for m in GRAPHIC_RE.finditer(line):
                events.append((m.start(), "figure", m.group(1)))
            for m in INPUT_RE.finditer(line):
                events.append((m.start(), "input", m.group(1)))
            for _, kind, arg in sorted(events, key=lambda e: e[0]):
                if kind == "figure":
                    self.report_figure(rel, lineno, arg.strip(), path.parent)
                else:
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
