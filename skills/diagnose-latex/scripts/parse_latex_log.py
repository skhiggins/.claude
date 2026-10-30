"""Summarize a LaTeX .log (and optional .blg) for diagnosing a failed compile.

Usage:
    python parse_latex_log.py <jobname>.log [--blg <jobname>.blg] [--max-errors N]

Prints, in plain text:
  - run status: whether the run finished, produced output, or stopped early
  - every error, in order, with the file it occurred in (from -file-line-error
    output, or else from TeX's open-file stack, which is heuristic), the source
    line number from the "l.<n>" context line, and the context TeX printed
  - a summary of the warnings that matter for diagnosis (undefined references
    and citations, multiply defined labels, rerun requests)
  - biber/bibtex errors and warnings, if a .blg is given

Handles both error formats: classic "! Message" and "-file-line-error"
("./file.tex:123: Message"), which LaTeX Workshop's tools use.
"""

import argparse
import os
import re
import sys

MAX_PRINT_LINE = 79  # TeX Live default; log lines are hard-wrapped at this width

FILE_EXT = (r"tex|sty|cls|cfg|def|clo|fd|bbl|aux|out|toc|lof|lot|ldf|ltx|lbx|bbx|"
            r"cbx|dbx|bcf|tikz|pgf|dict|mkii|code\.tex|w18|nav|snm|vrb|ind|gls")
OPEN_FILE_RE = re.compile(r"\((\"?[^\s()\"]+?\.(?:" + FILE_EXT + r")\"?)(?=[\s()]|$)")
# The optional "c:" prefix matters on Windows: LaTeX Workshop passes absolute paths,
# so errors read "c:/Dropbox/.../file.tex:294: ...", and the path may contain spaces.
FILE_LINE_ERR_RE = re.compile(r"^((?:[A-Za-z]:)?[^:\s][^:]*?\.(?:" + FILE_EXT + r")):(\d+): (.*)$")
# Loose pattern for the sanity check: any line that looks like "<something>:<n>: <msg>"
LOOSE_FILE_LINE_RE = re.compile(r"^\S.*?:\d+: \S")
CONTEXT_LINE_RE = re.compile(r"^l\.(\d+) ?(.*)$")


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def unwrap(lines):
    """Join lines that TeX hard-wrapped at max_print_line characters."""
    out = []
    buf = ""
    for line in lines:
        buf += line
        if len(line) == MAX_PRINT_LINE:
            continue
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return out


def track_files(lines):
    """Return, for each line index, the innermost file TeX had open (heuristic)."""
    stack = []
    current = []
    for line in lines:
        current.append(stack[-1] if stack else None)
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "(":
                m = OPEN_FILE_RE.match(line, i)
                if m:
                    stack.append(m.group(1).strip('"'))
                    i = m.end()
                    continue
                stack.append(None)  # a non-file parenthesis; keep the stack balanced
            elif ch == ")":
                if stack:
                    stack.pop()
            i += 1
    return current


def find_context(lines, start, limit=20):
    """Find the l.<n> context line after an error and the continuation line."""
    for j in range(start + 1, min(start + 1 + limit, len(lines))):
        m = CONTEXT_LINE_RE.match(lines[j])
        if m:
            cont = lines[j + 1].strip() if j + 1 < len(lines) else ""
            return int(m.group(1)), m.group(2), cont, j
        if j > start + 1 and (lines[j].startswith("! ") or FILE_LINE_ERR_RE.match(lines[j])):
            break
    return None, None, None, None


def parse_log(path, max_errors):
    text = read_text(path)
    raw_lines = text.splitlines()
    lines = unwrap(raw_lines)
    files = track_files(lines)

    status = []
    if any(l.startswith("Output written on") for l in lines):
        out = next(l for l in lines if l.startswith("Output written on"))
        status.append(out.strip())
    if any("No pages of output" in l for l in lines):
        status.append("No pages of output.")
    for marker in ("Emergency stop", "Fatal error occurred", "==> Fatal error",
                   "TeX capacity exceeded", "Runaway argument?", "Runaway definition?",
                   "File ended while scanning", "job aborted"):
        hits = [i for i, l in enumerate(lines) if marker in l]
        if hits:
            status.append(f"'{marker}' at log line {hits[0] + 1}")
    finished = any(l.startswith("Here is how much of TeX's memory you used") for l in lines)
    if not finished:
        status.append("Log has no 'Here is how much of TeX's memory you used' block: "
                      "the run was interrupted or the log is from a run still in progress.")

    errors = []
    for i, line in enumerate(lines):
        msg = fname = None
        lineno = None
        m = FILE_LINE_ERR_RE.match(line)
        if m:
            fname, lineno, msg = m.group(1), int(m.group(2)), m.group(3)
        elif line.startswith("! "):
            msg = line[2:]
            fname = files[i]
        else:
            continue
        ctx_no, ctx_before, ctx_after, _ = find_context(lines, i)
        if lineno is None:
            lineno = ctx_no
        detail = []
        for j in range(i + 1, min(i + 8, len(lines))):
            if CONTEXT_LINE_RE.match(lines[j]) or lines[j].startswith("! ") or FILE_LINE_ERR_RE.match(lines[j]):
                break
            if lines[j].strip():
                detail.append(lines[j].rstrip())
        errors.append({
            "log_line": i + 1, "message": msg.strip(), "file": fname,
            "line": lineno, "context_before": ctx_before, "context_after": ctx_after,
            "detail": detail[:5],
            "attribution": "file-line-error" if m else "open-file stack (heuristic)",
        })

    undefined_refs = sorted(set(re.findall(r"Reference `([^']+)' on page \d+ undefined", text)))
    undefined_cites = sorted(set(re.findall(r"Citation `([^']+)' on page \d+ undefined", text)
                                 + re.findall(r"Citation '([^']+)' on page \d+ undefined", text)))
    multiply = sorted(set(re.findall(r"Label `([^']+)' multiply defined", text)))
    rerun = [l.strip() for l in lines if re.search(r"Rerun to get|Please \(re\)run|Please rerun", l)]
    missing_files = sorted(set(re.findall(r"File `([^']+)' not found", text)))

    print(f"LOG: {os.path.abspath(path)}")
    print("== Run status ==")
    for s in status or ["(no status markers found)"]:
        print(f"  {s}")
    print(f"== Errors: {len(errors)} ==")
    for k, e in enumerate(errors[:max_errors], 1):
        loc = f"{e['file'] or '?'}:{e['line'] if e['line'] is not None else '?'}"
        print(f"[{k}] {e['message']}")
        print(f"    at {loc}   (log line {e['log_line']}; file from {e['attribution']})")
        if e["context_before"] is not None:
            print(f"    TeX context: l.{e['line']} {e['context_before']}")
            if e["context_after"]:
                print(f"                 {' ' * len(str(e['line']))}  {e['context_after']}")
        for d in e["detail"]:
            print(f"    | {d}")
    if len(errors) > max_errors:
        print(f"  ... {len(errors) - max_errors} more errors not shown (later errors are often "
              f"consequences of the first)")
    # Sanity check: lines that look like file-line-error output but were not parsed,
    # so a format the regexes miss cannot silently produce "Errors: 0"
    parsed = {e["log_line"] - 1 for e in errors}
    unparsed = [(i, l) for i, l in enumerate(lines)
                if i not in parsed and LOOSE_FILE_LINE_RE.match(l)
                and not l.startswith(("l.", "Package ", "LaTeX ", "Overfull", "Underfull"))]
    if unparsed:
        print(f"  WARNING: {len(unparsed)} log line(s) look like 'file:line: message' errors "
              f"but were not parsed; read them directly:")
        for i, l in unparsed[:10]:
            print(f"    log line {i + 1}: {l.strip()[:200]}")
    print("== Warnings relevant to diagnosis ==")
    print(f"  Missing files: {', '.join(missing_files) or 'none'}")
    print(f"  Undefined references ({len(undefined_refs)}): {', '.join(undefined_refs[:30]) or 'none'}")
    print(f"  Undefined citations ({len(undefined_cites)}): {', '.join(undefined_cites[:30]) or 'none'}")
    print(f"  Multiply defined labels ({len(multiply)}): {', '.join(multiply) or 'none'}")
    print(f"  Rerun requests: {len(rerun)}" + (f" (e.g. {rerun[0]})" if rerun else ""))
    return len(errors)


def parse_blg(path):
    print(f"== Bibliography log: {os.path.abspath(path)} ==")
    if not os.path.exists(path):
        print("  (no .blg file: biber/bibtex has not run since the build files were last cleaned)")
        return
    lines = read_text(path).splitlines()
    hits = [l.strip() for l in lines
            if re.search(r"\bERROR\b|\bWARN\b|I couldn't open|I found no|---line \d+ of file", l)]
    for h in hits[:40]:
        print(f"  {h}")
    if not hits:
        print("  no errors or warnings")


def scan_ctrl(paths):
    """Report lines containing control characters other than tab/newline."""
    bad = re.compile(r"[\x00-\x08\x0B\x0C\x0D\x0E-\x1F\x7F]")
    for p in paths:
        found = 0
        for n, line in enumerate(read_text(p).split("\n"), 1):
            line = line[:-1] if line.endswith("\r") else line
            for m in bad.finditer(line):
                found += 1
                print(f"{p}:{n}: control character 0x{ord(m.group()):02X} at column {m.start() + 1}: "
                      f"{line[max(0, m.start() - 30):m.start() + 30]!r}")
        if not found:
            print(f"{p}: no control characters")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?")
    ap.add_argument("--blg")
    ap.add_argument("--max-errors", type=int, default=10)
    ap.add_argument("--scan-ctrl", nargs="+", metavar="TEX",
                    help="instead of parsing a log, list control characters in these source files")
    a = ap.parse_args()
    if a.scan_ctrl:
        scan_ctrl(a.scan_ctrl)
        return
    if not a.log:
        ap.error("a log file is required unless --scan-ctrl is given")
    if not os.path.exists(a.log):
        print(f"NO LOG: {a.log} does not exist")
        sys.exit(2)
    parse_log(a.log, a.max_errors)
    if a.blg:
        parse_blg(a.blg)


if __name__ == "__main__":
    main()
