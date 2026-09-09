"""Expand a root .tex file and everything it \\input/\\include/\\subfile's (recursively, in
document order) into one comment-stripped text file with `path:line:` prefixes, so the
whole compiled prose can be read sequentially for typos.

Usage:
    python collect_tex.py ROOT.tex [--out FILE] [--include-generated]
                          [--drop-macros cut,cutrr] [--project-root DIR]

- Comments are stripped (a line's text after the first unescaped `%`); lines left blank
  are dropped. Original line numbers are preserved in the prefixes.
- Text inside the macros named by --drop-macros (default: cut,cutrr — macros this
  project defines as empty, so their argument never compiles) is removed, braces
  balanced, newlines kept so line numbers stay correct.
- Included files that live under a directory named results/, tables/, figures/, or
  numbers/ are treated as script-generated and skipped (listed in the summary) unless
  --include-generated is given.
- Includes are resolved relative to the root file's directory first (how LaTeX resolves
  them at compile time), then relative to the including file's directory.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
PROSE_RE = re.compile(r"[A-Za-z]{2,}\s+[A-Za-z]{2,}\s+[A-Za-z]{2,}")
GENERATED_DIRS = {"results", "tables", "figures", "numbers"}


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


def drop_macros(text, names):
    """Remove \\name{...} (balanced braces) for each name, keeping newlines inside the span."""
    if not names:
        return text
    pattern = re.compile(r"\\(?:" + "|".join(re.escape(n) for n in names) + r")\s*\{")
    out, pos = [], 0
    while True:
        m = pattern.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        out.append(text[pos:m.start()])
        depth, k = 1, m.end()
        while k < len(text) and depth:
            c = text[k]
            if c == "\\":
                k += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            k += 1
        out.append("\n" * text[m.start():k].count("\n"))
        pos = k
    return "".join(out)


def is_generated(path):
    return any(part.lower() in GENERATED_DIRS for part in path.parts[:-1])


def rel(path, project_root):
    try:
        return path.resolve().relative_to(project_root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def expand(path, base, project_root, macros, include_generated, seen, out, summary):
    path = path.resolve()
    if path in seen:
        summary["repeated"].append(rel(path, project_root))
        return
    seen.add(path)
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        summary["unreadable"].append((rel(path, project_root), str(e)))
        return
    stripped = "\n".join(strip_comment(l) for l in raw.splitlines())
    stripped = drop_macros(stripped, macros)
    name = rel(path, project_root)
    if path != root_path(summary) and not PROSE_RE.search(stripped):
        summary["no_prose"].append(name)
        return
    entry = [name, 0]
    summary["files"].append(entry)  # appended before recursing so the list is in document order
    out.append(f"==== FILE: {name} ====")
    for n, line in enumerate(stripped.splitlines(), 1):
        if line.strip():
            out.append(f"{name}:{n}: {line.rstrip()}")
            entry[1] += 1
        for m in INPUT_RE.finditer(line):
            target = m.group(1).strip()
            if "#" in target:
                continue  # macro definition such as \input{../results/numbers/#1.tex}, not a real include
            if not target.lower().endswith(".tex"):
                target += ".tex"
            cand = base / target
            if not cand.exists() and (path.parent / target).exists():
                cand = path.parent / target
            if not cand.exists():
                summary["missing"].append((name, n, target))
                continue
            if is_generated(cand) and not include_generated:
                summary["generated"].append(rel(cand, project_root))
                continue
            before = len(summary["files"])
            expand(cand, base, project_root, macros, include_generated, seen, out, summary)
            if len(summary["files"]) > before:
                out.append(f"==== BACK TO: {name} ====")


def root_path(summary):
    return summary["root"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out", help="output text file (default: <project>/.claude/typos_source_<timestamp>.txt)")
    ap.add_argument("--include-generated", action="store_true")
    ap.add_argument("--drop-macros", default="cut,cutrr", help="comma-separated macro names whose argument is not compiled")
    ap.add_argument("--project-root", default=".", help="paths in the output are made relative to this directory")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        sys.exit(f"ERROR: {root} not found")
    project_root = Path(args.project_root).resolve()
    macros = [m.strip() for m in args.drop_macros.split(",") if m.strip()]
    out_path = Path(args.out) if args.out else project_root / ".claude" / f"typos_source_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out = []
    summary = {"root": root.resolve(), "files": [], "generated": [], "no_prose": [], "missing": [], "unreadable": [], "repeated": []}
    expand(root, root.resolve().parent, project_root, macros, args.include_generated, set(), out, summary)
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    total = sum(k for _, k in summary["files"])
    print(f"Wrote {out_path} ({total} non-blank lines)")
    print("Files included (in document order):")
    for name, kept in summary["files"]:
        print(f"  {name}: {kept} lines")
    if summary["generated"]:
        print("Skipped as script-generated (typos there must be fixed in the generating script):")
        for g in sorted(set(summary["generated"])):
            print(f"  {g}")
    if summary["no_prose"]:
        print("Skipped as containing no prose (e.g., figure/number wrappers):")
        for g in sorted(set(summary["no_prose"])):
            print(f"  {g}")
    if summary["missing"]:
        print("WARNING: includes not found:")
        for src, n, t in summary["missing"]:
            print(f"  {src}:{n} -> {t}")
    if summary["unreadable"]:
        for name, err in summary["unreadable"]:
            print(f"WARNING: could not read {name}: {err}")
    if summary["repeated"]:
        print("Note: files included more than once were expanded only the first time: " + ", ".join(sorted(set(summary["repeated"]))))


if __name__ == "__main__":
    main()
