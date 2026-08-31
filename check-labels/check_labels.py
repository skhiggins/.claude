"""Audit \\label prefixes and \\ref/\\eqref usage in a LaTeX paper and its response doc.

Usage:
    python check_labels.py [MAIN_TEX] [RESPONSE_TEX]

Defaults are the current paper's main file and response doc. Scans the full
recursive \\input/\\include closure of each. Report-only: never edits files.
"""
import os
import re
import sys

DEFAULT_MAIN = r"c:\Dropbox\FinancialInclusion\iZettle_fee\paper\BehavioralFirmsProfitableOpportunities.tex"
DEFAULT_RESP = r"c:\Dropbox\FinancialInclusion\iZettle_fee\paper\RR_Response_ECMA\r_BehavioralFirmsProfitableOpportunities.tex"

MAIN = os.path.normpath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAIN
RESP = os.path.normpath(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_RESP
ROOT = os.path.dirname(os.path.dirname(MAIN)) or "."


def strip_comments(line):
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == '\\' and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == '%':
            break
        out.append(c)
        i += 1
    return ''.join(out)


def load(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return [strip_comments(l) for l in f.read().splitlines()]


INPUT_RE = re.compile(r'\\(?:input|include)\{([^}]+)\}')


def closure(main):
    seen, order, stack = set(), [], [main]
    while stack:
        p = os.path.normpath(stack.pop(0))
        if not os.path.exists(p) and os.path.exists(p + '.tex'):
            p = p + '.tex'
        key = os.path.normcase(p)
        if key in seen:
            continue
        if not os.path.exists(p):
            print(f"MISSING INPUT FILE: {p}", file=sys.stderr)
            continue
        seen.add(key)
        order.append(p)
        base = os.path.dirname(p)
        for line in load(p):
            for m in INPUT_RE.finditer(line):
                stack.append(os.path.join(base, m.group(1)))
    return order


MATH_ENVS = {'equation', 'align', 'gather', 'multline', 'eqnarray', 'alignat'}
CLASS_OF_ENV = {e: 'e' for e in MATH_ENVS}
CLASS_OF_ENV.update({e: 'p' for e in ('prediction', 'proposition', 'corollary', 'lemma')})
CLASS_OF_ENV.update({e: 'OTHER:' + e for e in ('theorem', 'assumption', 'definition', 'remark')})
CLASS_OF_ENV.update({e: 'fig' for e in ('figure', 'sidewaysfigure', 'subfigure')})
CLASS_OF_ENV.update({e: 'tab' for e in ('table', 'sidewaystable', 'threeparttable', 'longtable')})
CLASS_OF_ENV['algorithm'] = 'alg'

EXPECT = {'e': ('e:',), 'p': ('p:',), 's': ('s:',), 'a': ('a:',), 'ss': ('ss:',),
          'fig': ('fig:',), 'tab': ('tab:',), 'fn': ('fn:',), 'alg': ('alg:',)}
# The response doc labels its own sections ec: (editor comment) / rc:N_M (referee comment)
RESP_EXPECT = dict(EXPECT, s=('s:', 'ec:', 'rc:'), ss=('ss:', 'ec:', 'rc:'))

TOK_RE = re.compile(
    r'\\begin\{([A-Za-z*]+)\}|\\end\{([A-Za-z*]+)\}|\\label\{([^}]*)\}'
    r'|\\(ref|eqref|pageref|autoref|cref|Cref|vref)\{([^}]*)\}'
    r'|\\(section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\{|\\footnote\{|\\appendix\b'
    r'|\\hyperref\[([^\]]*)\]')


def is_results_file(p):
    return '/results/' in p.replace('\\', '/').lower()


def rel(p):
    try:
        return os.path.relpath(p, ROOT).replace('\\', '/')
    except ValueError:
        return p


def analyze(files):
    labels = {}  # name -> [(file, line, class, in_results_file)]
    refs = []    # (file, line, cmd, name, in_results_file)
    for path in files:
        lines = load(path)
        text = '\n'.join(lines)
        offs, pos = [], 0
        for l in lines:
            offs.append(pos)
            pos += len(l) + 1

        def lineno(p):
            lo, hi = 0, len(offs) - 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if offs[mid] <= p:
                    lo = mid
                else:
                    hi = mid - 1
            return lo + 1

        def macro_spans(pattern):
            spans = []
            for m in re.finditer(pattern, text):
                depth, i = 1, m.end()
                while i < len(text) and depth:
                    if text[i] == '\\':
                        i += 2
                        continue
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                    i += 1
                spans.append((m.end(), i))
            return spans

        fn_spans = macro_spans(r'\\footnote\s*\{')
        # \cut{...} and \cutrr{...} discard their argument: content inside never renders
        cut_spans = macro_spans(r'\\cut(?:rr)?\s*\{')

        def in_cut(p):
            return any(a <= p < b for a, b in cut_spans)

        env_stack = []
        last_sec = None
        in_appendix = 'appendix' in os.path.basename(path).lower()
        res = is_results_file(path)
        for m in TOK_RE.finditer(text):
            if m.group(0) == '\\appendix':
                in_appendix = True
            elif m.group(1):
                env_stack.append(m.group(1).rstrip('*'))
            elif m.group(2):
                e = m.group(2).rstrip('*')
                for j in range(len(env_stack) - 1, -1, -1):
                    if env_stack[j] == e:
                        del env_stack[j]
                        break
            elif m.group(6):
                last_sec = {'section': 'a' if in_appendix else 's',
                            'subsection': 'ss', 'subsubsection': 'sss'}[m.group(6)]
            elif m.group(3) is not None:
                name = m.group(3).strip()
                cls = None
                for j in range(len(env_stack) - 1, -1, -1):
                    if env_stack[j] in CLASS_OF_ENV:
                        cls = CLASS_OF_ENV[env_stack[j]]
                        break
                if cls is None:
                    p0 = m.start()
                    if any(a <= p0 < b for a, b in fn_spans):
                        cls = 'fn'
                    else:
                        cls = last_sec or '???'
                labels.setdefault(name, []).append(
                    (path, lineno(m.start()), cls, res, in_cut(m.start())))
            elif m.group(4):
                refs.append((path, lineno(m.start()), m.group(4), m.group(5).strip(),
                             res, in_cut(m.start())))
            elif m.group(7) is not None:
                refs.append((path, lineno(m.start()), 'hyperref', m.group(7).strip(),
                             res, in_cut(m.start())))
    return labels, refs


def report(labels, refs, docname, ext_labels=None, extra_refs=(), expect=EXPECT):
    print(f"\n#### {docname} ####")

    def tags(res, cut):
        return ("  [AUTO-GEN FILE]" if res else "") + ("  [IN CUT TEXT]" if cut else "")

    print("\n-- DUPLICATE DEFINITIONS (outside cut text) --")
    for name, defs in sorted(labels.items()):
        live = [d for d in defs if not d[4]]
        if len(live) > 1:
            print(f"  {name}: " + "; ".join(f"{rel(f)}:{ln}" for f, ln, c, r, cu in live))

    print("\n-- PREFIX VIOLATIONS --")
    for name, defs in sorted(labels.items()):
        for f, ln, cls, res, cut in defs:
            exp = expect.get(cls)
            if exp is None:
                print(f"  [UNCLASSIFIED: {cls}] {name}  @ {rel(f)}:{ln}{tags(res, cut)}")
            elif not any(name.startswith(p) for p in exp):
                print(f"  {name}  class={cls} expected prefix {'/'.join(exp)}  @ {rel(f)}:{ln}{tags(res, cut)}")

    # a label "renders" if at least one definition sits outside cut text
    live_defined = {n for n, d in labels.items() if any(not cu for _, _, _, _, cu in d)}
    ext_live = {n for n, d in (ext_labels or {}).items() if any(not cu for _, _, _, _, cu in d)}
    all_live = live_defined | ext_live
    eq_labels = {n for n, d in list(labels.items()) + list((ext_labels or {}).items())
                 if any(c == 'e' for _, _, c, _, _ in d)}

    print("\n-- BROKEN REFS (rendered ref, label undefined or only in cut text) --")
    for f, ln, cmd, name, res, cut in refs:
        if not cut and name not in all_live:
            print(f"  \\{cmd}{{{name}}}  @ {rel(f)}:{ln}{tags(res, cut)}")
    print("\n-- REFS INSIDE CUT TEXT TO CUT/MISSING LABELS (info, not rendered) --")
    for f, ln, cmd, name, res, cut in refs:
        if cut and name not in all_live:
            print(f"  \\{cmd}{{{name}}}  @ {rel(f)}:{ln}")

    print("\n-- EQREF DISCIPLINE --")
    for f, ln, cmd, name, res, cut in refs:
        if name in eq_labels and cmd not in ('eqref', 'pageref', 'hyperref'):
            print(f"  \\{cmd}{{{name}}} should be \\eqref  @ {rel(f)}:{ln}{tags(res, cut)}")
        elif name not in eq_labels and name in (set(labels) | set(ext_labels or ())) and cmd == 'eqref':
            print(f"  \\eqref{{{name}}} should be \\ref  @ {rel(f)}:{ln}{tags(res, cut)}")

    print("\n-- UNREFERENCED LABELS (info; counting refs anywhere incl. cut text) --")
    refd = {r[3] for r in refs} | {r[3] for r in extra_refs}
    for name in sorted(labels):
        if name not in refd:
            f, ln = labels[name][0][0], labels[name][0][1]
            cu = all(d[4] for d in labels[name])
            print(f"  {name}  @ {rel(f)}:{ln}" + ("  [IN CUT TEXT]" if cu else ""))
    print(f"\nTOTALS: {sum(len(v) for v in labels.values())} label defs, {len(refs)} refs")


paper_files = closure(MAIN)
resp_files = closure(RESP) if os.path.exists(RESP) else []

print("== PAPER CLOSURE ==")
for p in paper_files:
    print(' ', rel(p))
print("== RESPONSE CLOSURE ==")
for p in resp_files:
    print(' ', rel(p))

pl, pr = analyze(paper_files)
rl, rr = analyze(resp_files) if resp_files else ({}, [])

report(pl, pr, "PAPER", extra_refs=rr)
if resp_files:
    report(rl, rr, "RESPONSE DOC", ext_labels=pl, expect=RESP_EXPECT)
