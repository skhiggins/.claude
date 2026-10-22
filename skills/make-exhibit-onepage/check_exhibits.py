"""Batch note-fit checker for /make-exhibit-onepage (all-exhibits mode).

Usage: python check_exhibits.py <root.tex> <root.pdf> [tex_file ...]

For every \begin{table}/\begin{figure} in the given tex files (comments
stripped), extracts the caption title and the width knob, locates the caption's
page in the PDF (via pdftotext), and classifies the exhibit's note-fit status:

  FITS       caption page also contains a significance line after the caption
  SPILL?     no significance line after the caption on its page, but the next
             page shows one before any new caption -- likely spilled note
  NO-NOTE?   no significance line found on either page (figure without stars,
             or notes inside the float) -- needs a manual check
  NOT-FOUND  caption text not found in the PDF (macro-heavy caption; check
             manually)

The classification is a screening pass: verify SPILL?/NO-NOTE? rows manually
(two exhibits can share a page, notes can end without stars, etc.).
"""
import re
import subprocess
import sys


def strip_comments(line):
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def plain(text):
    """Normalize a caption to pdftotext-like plain text."""
    text = re.sub(r"\\(new|added|emph|textbf|textit|short)\s*\{", "", text)
    text = re.sub(r"\\makequote\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = text.replace("~", " ").replace("{", "").replace("}", "")
    text = text.replace("$", "").replace("\\%", "%")
    return re.sub(r"\s+", " ", text).strip()


def extract_exhibits(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        raw_lines = f.readlines()
    lines = [strip_comments(l) for l in raw_lines]
    exhibits = []
    i = 0
    n = len(lines)
    while i < n:
        m = re.search(r"\\begin\{(table|figure)\}", lines[i])
        if not m:
            i += 1
            continue
        env = m.group(1)
        start = i
        body = []
        j = i
        while j < n and ("\\end{%s}" % env) not in lines[j]:
            body.append(lines[j])
            j += 1
        if j < n:
            body.append(lines[j])
        block = "\n".join(body)
        cm = re.search(r"\\caption\*?\s*\{", block)
        caption = ""
        if cm:
            depth = 1
            k = cm.end()
            while k < len(block) and depth > 0:
                if block[k] == "\\" and k + 1 < len(block):
                    k += 2
                    continue
                if block[k] == "{":
                    depth += 1
                elif block[k] == "}":
                    depth -= 1
                k += 1
            caption = plain(block[cm.end():k - 1])
        wm = re.search(r"max width\s*=\s*([0-9.]+)\\textwidth", block)
        gm = re.search(r"includegraphics\[[^\]]*width\s*=\s*([0-9.]+)\s*\\textwidth",
                       block)
        width = wm.group(1) if wm else (gm.group(1) if gm else "none")
        knob = "adjustbox" if wm else ("includegraphics" if gm else "none")
        minipage = "minipage" in block
        exhibits.append({
            "file": path, "line": start + 1, "env": env,
            "caption": caption, "width": width, "knob": knob,
            "minipage": minipage,
        })
        i = j + 1
    return exhibits


def pdf_pages(pdf):
    txt = subprocess.run(["pdftotext", "-q", pdf, "-"],
                         capture_output=True, text=True).stdout
    return txt.split("\f")


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


STARS = re.compile(r"p\s*<\s*(0?\.01|\.01)")
CAPTION_HEAD = re.compile(r"(table|figure)\s+[A-Z]?\.?\d+[.:]", re.I)


def classify(ex, pages):
    cap = norm(ex["caption"])[:45]
    if len(cap) < 8:
        return "NOT-FOUND", -1
    hits = [p for p, text in enumerate(pages) if cap in norm(text)]
    if not hits:
        return "NOT-FOUND", -1
    page = hits[0]
    text = norm(pages[page])
    after = text[text.index(cap) + len(cap):]
    if STARS.search(after):
        return "FITS", page + 1
    if page + 1 < len(pages):
        nxt = pages[page + 1]
        headm = CAPTION_HEAD.search(nxt)
        head = nxt[:headm.start()] if headm else nxt
        if STARS.search(norm(head)):
            return "SPILL?", page + 1
    return "NO-NOTE?", page + 1


def main():
    root_tex, pdf = sys.argv[1], sys.argv[2]
    files = sys.argv[3:] or [root_tex]
    pages = pdf_pages(pdf)
    for f in files:
        for ex in extract_exhibits(f):
            status, page = classify(ex, pages)
            print("\t".join([
                status, "p%s" % page, ex["env"],
                "%s:%s" % (ex["file"], ex["line"]),
                "w=%s(%s)%s" % (ex["width"], ex["knob"],
                                 ",minipage" if ex["minipage"] else ""),
                ex["caption"][:60],
            ]))


if __name__ == "__main__":
    main()
