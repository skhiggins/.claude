"""List or delete the build artifacts of a LaTeX root file.

Usage:
    python clean_tex_build.py <file>.tex                 # list only
    python clean_tex_build.py <file>.tex --delete        # delete known artifacts
    python clean_tex_build.py <file>.tex --delete --only <name> [<name> ...]
                                                         # delete exactly these
                                                         # <jobname>.* files

Matches every file in the tex file's folder named ``<jobname>.<something>``
(``<jobname>`` = file name without ``.tex``), never the ``.tex`` file itself.
Known build extensions are deleted with ``--delete``; others are reported as
REVIEW and left alone unless named with ``--only``.
"""

import argparse
import os
import sys

KNOWN = {
    ".aux", ".bbl", ".bcf", ".blg", ".brf", ".dvi", ".fdb_latexmk", ".figlist",
    ".fls", ".glg", ".glo", ".gls", ".idx", ".ilg", ".ind", ".ist", ".lof",
    ".log", ".lol", ".lot", ".makefile", ".nav", ".nlo", ".nls", ".out", ".pdf",
    ".ps", ".run.xml", ".snm", ".spl", ".synctex", ".synctex.gz",
    ".synctex(busy)", ".tdo", ".thm", ".toc", ".vrb", ".xdv",
    ".loa", ".lox", ".upa", ".upb", ".pyg", ".wrt", ".dpth", ".md5",
    ".auxlock", ".acn", ".acr", ".alg",
}


def fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--only", nargs="+", metavar="NAME",
                    help="delete exactly these file names (basenames), which "
                         "must match <jobname>.*; implies --delete")
    args = ap.parse_args()

    tex = args.tex.lstrip("@")
    if not tex.lower().endswith(".tex"):
        sys.exit(f"ERROR not a .tex file: {tex}")
    tex = os.path.abspath(tex)
    if not os.path.isfile(tex):
        sys.exit(f"ERROR file not found: {tex}")

    folder = os.path.dirname(tex)
    texname = os.path.basename(tex)
    jobname = texname[:-4]
    prefix = jobname + "."

    matches = []
    for name in sorted(os.listdir(folder)):
        if name == texname or not name.startswith(prefix):
            continue
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        ext = name[len(jobname):].lower()
        matches.append((name, path, ext, os.path.getsize(path)))

    if not matches:
        print("NONE")
        return

    delete = args.delete or bool(args.only)
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {m[0] for m in matches}
        if unknown:
            sys.exit("ERROR not <jobname>.* files in that folder: " + ", ".join(sorted(unknown)))
        targets = [m for m in matches if m[0] in wanted]
    else:
        targets = [m for m in matches if m[2] in KNOWN]

    if not delete:
        for name, path, ext, size in matches:
            tag = "DELETE" if ext in KNOWN else "REVIEW"
            kind = "known" if ext in KNOWN else "unknown"
            print(f"{tag} {path} {fmt_size(size)} {kind}")
        return

    for name, path, ext, size in targets:
        try:
            os.remove(path)
            print(f"DELETED {path}")
        except OSError as e:
            print(f"FAILED {path} {e.strerror or e}")
    if not args.only:
        for name, path, ext, size in matches:
            if ext not in KNOWN:
                print(f"REVIEW {path} {fmt_size(size)} unknown (kept)")


if __name__ == "__main__":
    main()
