"""Convert a PDF to a text file with page markers, reusing an earlier conversion when one exists.

usage: python pdf_to_txt.py input.pdf [output.txt] [--force]

Default output path (when output.txt is omitted): <project>/.claude/references/<name>.txt, where
<project> is the nearest folder above the PDF that contains a .claude folder (the user's home
folder does not count), or the current working directory if there is none, and <name> is the
PDF's path relative to <project> with separators and other non-filename characters replaced
by "_" (e.g., 2026/AEJApplied/PDF_Proof.pdf -> 2026_AEJApplied_PDF_Proof.txt). A PDF outside
<project> is named after its file name alone.

The first line of every output file records the source PDF and its SHA-256 hash:
    ===== [source: <pdf path>; sha256: <hash>] =====
Before converting, the script looks in the output folder for a .txt whose first line carries
the same hash (a previous run converted this same PDF, under any name). If it finds one, it
reports that file instead of converting again. A .txt at the exact output path without such
a line (written before this check existed) is reused when it is non-empty and newer than the
PDF. --force converts regardless.
"""

import hashlib
import re
import sys
from pathlib import Path

HEADER_RE = re.compile(r"^===== \[source: .*; sha256: ([0-9a-f]{64})\] =====$")
PAGE_RE = re.compile(r"===== \[page \d+ of (\d+)\] =====")


def extract_pymupdf(pdf_path: Path) -> list[str]:
    import fitz

    doc = fitz.open(pdf_path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return pages


def extract_pypdf(pdf_path: Path) -> list[str]:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    return [page.extract_text() or "" for page in reader.pages]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def header_hash(txt_path: Path) -> str | None:
    """Return the hash recorded on the first line of txt_path, or None if there is none."""
    try:
        with txt_path.open("r", encoding="utf-8", errors="replace") as f:
            first = f.readline().rstrip("\r\n")
    except OSError:
        return None
    m = HEADER_RE.match(first)
    return m.group(1) if m else None


def find_existing(pdf_path: Path, out_path: Path, digest: str) -> Path | None:
    """Return an existing conversion of pdf_path (under any name in the output folder), or None."""
    out_dir = out_path.parent
    if out_dir.is_dir():
        for cand in sorted(out_dir.glob("*.txt")):
            if header_hash(cand) == digest:
                return cand
    if (
        out_path.is_file()
        and out_path.stat().st_size > 0
        and header_hash(out_path) is None
        and out_path.stat().st_mtime >= pdf_path.stat().st_mtime
    ):
        return out_path
    return None


def project_root(pdf_path: Path) -> Path:
    """Nearest ancestor of pdf_path containing a .claude folder (home excluded), else the cwd."""
    home = Path.home().resolve()
    for ancestor in pdf_path.resolve().parents:
        if ancestor == home:
            break
        if (ancestor / ".claude").is_dir():
            return ancestor
    return Path.cwd().resolve()


def default_out_path(pdf_path: Path) -> Path:
    pdf_abs = pdf_path.resolve()
    root = project_root(pdf_path)
    try:
        stem = "_".join(pdf_abs.relative_to(root).with_suffix("").parts)
    except ValueError:  # PDF is not inside the project
        stem = pdf_abs.stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("_")
    return root / ".claude" / "references" / f"{stem}.txt"


def report(content: str) -> None:
    m = PAGE_RE.search(content)
    n_pages = int(m.group(1)) if m else 0
    n_lines = content.count("\n") + 1
    print(f"pages: {n_pages}, lines: {n_lines}, characters: {len(content)}")


def main() -> None:
    force = "--force" in sys.argv[1:]
    args = [a for a in sys.argv[1:] if a != "--force"]
    if not args:
        print("usage: python pdf_to_txt.py input.pdf [output.txt] [--force]", file=sys.stderr)
        sys.exit(1)
    pdf_path = Path(args[0])
    if not pdf_path.is_file():
        print(f"error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    out_path = Path(args[1]) if len(args) > 1 else default_out_path(pdf_path)
    digest = sha256_of(pdf_path)

    if not force:
        existing = find_existing(pdf_path, out_path, digest)
        if existing is not None:
            content = existing.read_text(encoding="utf-8", errors="replace")
            print("Already converted by a previous run; skipping conversion (pass --force to reconvert).")
            print(f"Existing file: {existing}")
            report(content)
            return

    try:
        pages = extract_pymupdf(pdf_path)
    except ImportError:
        try:
            pages = extract_pypdf(pdf_path)
        except ImportError:
            print("error: neither pymupdf nor pypdf is installed", file=sys.stderr)
            sys.exit(1)

    parts = [f"===== [source: {pdf_path.resolve()}; sha256: {digest}] =====\n"]
    for i, text in enumerate(pages, 1):
        parts.append(f"\n===== [page {i} of {len(pages)}] =====\n")
        parts.append(text)
    content = "".join(parts)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")
    report(content)


if __name__ == "__main__":
    main()
