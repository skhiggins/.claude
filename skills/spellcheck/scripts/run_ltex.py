"""Run the bundled LTeX+ CLI on a root .tex file and everything it \input/\includes, recursively."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from glob import glob
from pathlib import Path

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
HAS_WORDS_RE = re.compile(r"[A-Za-z]{2,}")


def strip_comments(text):
    out = []
    for line in text.splitlines():
        i = 0
        while True:
            j = line.find("%", i)
            if j == -1:
                out.append(line)
                break
            if j > 0 and line[j - 1] == "\\":
                i = j + 1
                continue
            out.append(line[:j])
            break
    return "\n".join(out)


def collect(root):
    root = Path(root).resolve()
    base = root.parent  # LaTeX resolves \input relative to the compile dir
    seen, ordered, missing = set(), [], []
    stack = [root]
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        ordered.append(f)
        try:
            text = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            print(f"WARNING: could not read {f}: {e}", file=sys.stderr)
            continue
        for m in INPUT_RE.finditer(text):
            rel = m.group(1).strip()
            if not rel.lower().endswith(".tex"):
                rel += ".tex"
            cand = base / rel
            if not cand.exists() and (f.parent / rel).exists():
                cand = f.parent / rel
            if cand.exists():
                stack.append(cand.resolve())
            else:
                missing.append((str(f), rel))
    return ordered, missing


def build_client_config(start_dir):
    settings = None
    for p in [start_dir, *start_dir.parents]:
        c = p / ".vscode" / "settings.json"
        if c.exists():
            settings = c
            break
    cfg = {}
    if settings:
        try:
            data = json.loads(settings.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            print(f"WARNING: could not parse {settings}: {e}", file=sys.stderr)
            data = {}
        for key, value in data.items():
            if not key.startswith("ltex."):
                continue
            parts = key.split(".")[1:]  # "ltex.dictionary.en-US" -> ["dictionary", "en-US"]
            node = cfg
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
    return cfg, settings


def find_cli():
    hits = sorted(
        glob(
            str(
                Path.home()
                / ".vscode"
                / "extensions"
                / "ltex-plus.vscode-ltex-plus-*"
                / "lib"
                / "ltex-ls-plus-*"
                / "bin"
                / "ltex-cli-plus.bat"
            )
        )
    )
    if not hits:
        sys.exit(
            "ERROR: ltex-cli-plus.bat not found under ~/.vscode/extensions. "
            "Is the LTeX+ VSCode extension installed?"
        )
    cli = Path(hits[-1])
    jdks = sorted(cli.parent.parent.glob("jdk-*"))
    return cli, (jdks[-1] if jdks else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="root .tex file")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        sys.exit(f"ERROR: {root} not found")

    files, missing = collect(root)
    # Files with no 2+ letter words (e.g., generated number snippets) cannot
    # have spelling errors; skipping them keeps command lines short.
    checkable = [
        f
        for f in files
        if HAS_WORDS_RE.search(strip_comments(f.read_text(encoding="utf-8", errors="replace")))
    ]

    print(f"Included files found: {len(files)} (checkable: {len(checkable)}, "
          f"skipped {len(files) - len(checkable)} with no words)")
    for src, rel in missing:
        print(f"WARNING: {src} includes {rel}, which was not found")

    cfg, settings = build_client_config(root.parent)
    print(f"Dictionary source: {settings if settings else 'none found'}")
    cli, jdk = find_cli()

    env = os.environ.copy()
    if jdk:
        env["JAVA_HOME"] = str(jdk)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(cfg, tmp)
        cfg_path = tmp.name

    # cmd.exe limits command lines to ~8191 chars, so chunk the file list.
    rel_files = [os.path.relpath(f, root.parent) for f in checkable]
    chunks, current, length = [], [], 0
    for rf in rel_files:
        if current and length + len(rf) > 6000:
            chunks.append(current)
            current, length = [], 0
        current.append(rf)
        length += len(rf) + 3
    if current:
        chunks.append(current)

    exit_code = 0
    for i, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            print(f"--- chunk {i} of {len(chunks)} ---")
        proc = subprocess.run(
            ["cmd", "/c", str(cli), f"--client-configuration={cfg_path}", *chunk],
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
            cwd=str(root.parent),
        )
        sys.stdout.write(proc.stdout)
        # Exit code 3 just means issues were found.
        if proc.returncode not in (0, 3):
            sys.stderr.write(proc.stderr)
            print(f"ERROR: ltex-cli exited with code {proc.returncode}", file=sys.stderr)
            exit_code = 1
        elif proc.returncode == 3:
            exit_code = max(exit_code, 0)

    os.unlink(cfg_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
