#!/bin/bash
# find_pages.sh <pdf> <string...>
# Print the 1-based PDF page number(s) whose rendered text contains the given
# fixed string (not a regex). Choose short plain-text phrases (3-8 words) free
# of math, macros, and words that pdftotext may merge across hyphenated line
# breaks. Requires pdftotext on PATH.
#
# Example:
#   bash find_pages.sh paper.pdf "prior to taking logs"
pdf="$1"
shift
str="$*"
if [ -z "$pdf" ] || [ -z "$str" ]; then
  echo "Usage: find_pages.sh <pdf> <string...>" >&2
  exit 2
fi
pdftotext -q "$pdf" - | awk -v s="$str" 'BEGIN{RS="\f"} index($0, s){print NR}'
