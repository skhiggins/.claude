import sys
from pathlib import Path


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


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python pdf_to_txt.py input.pdf [output.txt]", file=sys.stderr)
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    if not pdf_path.is_file():
        print(f"error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.with_suffix(".txt")

    try:
        pages = extract_pymupdf(pdf_path)
    except ImportError:
        try:
            pages = extract_pypdf(pdf_path)
        except ImportError:
            print("error: neither pymupdf nor pypdf is installed", file=sys.stderr)
            sys.exit(1)

    parts = []
    for i, text in enumerate(pages, 1):
        parts.append(f"\n===== [page {i} of {len(pages)}] =====\n")
        parts.append(text)
    content = "".join(parts)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    n_lines = content.count("\n") + 1
    print(f"Wrote {out_path}")
    print(f"pages: {len(pages)}, lines: {n_lines}, characters: {len(content)}")


if __name__ == "__main__":
    main()
