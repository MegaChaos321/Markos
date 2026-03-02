"""
Common utilities for the whole Markdown project.

Copyright 2026 Márcio Santos
"""

import sys
import re
from typing import TextIO

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

__all__ = [
    'prettify_html',
    'rewind_one_line',
    'from_file_or_stdin',
    'to_file_or_stdout',
    'matches',
    'count_consec'
]

def prettify_html(html_code: str | TextIO, indent = 2) -> str:
    soup = BeautifulSoup(html_code, features = 'html.parser')
    return soup.prettify(formatter = HTMLFormatter(indent = indent)) # type: ignore
#:

def rewind_one_line(in_: TextIO, line: str):
    n_chars = len(line.encode()) + 1 # '+ 1' accounts for the removed '\n'
    in_.seek(in_.tell() - n_chars, 0)
#:

def from_file_or_stdin(file_path: str | None) -> TextIO:
    return open(file_path, 'rt', encoding='UTF-8') if file_path else sys.stdin
#:

def to_file_or_stdout(file_path: str | None) -> TextIO:
    return open(file_path, 'wt', encoding='UTF-8') if file_path else sys.stdout
#:

def matches(pattern: re.Pattern, line: str) -> bool:
    return bool(pattern.fullmatch(line))
#:

def count_consec(txt: str, char: str, start_pos: int = 0):
    count = 0
    for ch in txt[start_pos:]:
        if ch != char:
            break
        #:
        count += 1
    #:
    return count
#:
