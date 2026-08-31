"""Rename LaTeX labels and all references to them, atomically per label.

Usage:
    python apply_renames.py SPEC.json

SPEC.json format:
    {"files": ["abs/or/rel/path.tex", ...],
     "renames": {"old_label": "new_label", ...}}

Only occurrences inside \\label/\\ref/\\eqref/\\pageref/\\autoref/\\cref/\\Cref/\\vref
with an exact brace-delimited match, plus \\hyperref[...] with an exact
bracket-delimited match, are replaced (commented occurrences too, so
that commented-out blocks stay consistent if restored). Line endings preserved.
"""
import json
import re
import sys

CMD = r"\\(?:label|ref|eqref|pageref|autoref|cref|Cref|vref)\{"

with open(sys.argv[1], encoding="utf-8") as f:
    spec = json.load(f)

for path in spec["files"]:
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    total = 0
    for old, new in spec["renames"].items():
        pat = re.compile("(" + CMD + ")" + re.escape(old) + r"\}")
        text, n = pat.subn(lambda m: m.group(1) + new + "}", text)
        hyp = re.compile(r"(\\hyperref\[)" + re.escape(old) + r"\]")
        text, n2 = hyp.subn(lambda m: m.group(1) + new + "]", text)
        n += n2
        if n:
            print(f"{path}: {old} -> {new}  x{n}")
            total += n
    if total:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    print(f"{path}: {total} replacements")
