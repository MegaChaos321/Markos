"""
In this module we define an LaTeX Backend which will be an alternative backend
for the Markos project.

Copyright 2026 Márcio Santos
"""

from typing import TextIO
from io import StringIO
from typing_extensions import override

from markdown_backend import MarkdownBackend

__all__ = ['LaTeXBackend']

class LaTeXBackend(MarkdownBackend):
    def __init__(self, out: TextIO):
        self._storage = out
        self._out = StringIO()
    #:

    def close(self):
        self._storage.write(self._out.getvalue())
        self._out.close()
    #:

    @override
    def open_document(self, title=''):
        out = self._out
        out.write(r"""\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{graphicx}
""")
        if title:
            out.write(fr'\hypersetup{{pdftitle={{{title}}}}}' + '\n')
            out.write(fr'\title{{{title}}}' + '\n')
            out.write(fr'\date{{}}' + '\n')
        #:
        out.write(r'\begin{document}' + '\n')
        if title:
            out.write(fr'\maketitle' + '\n')
        #:
    #:

    @override
    def close_document(self):
        self._out.write(r'\end{document}' + '\n')
    #:

    @override
    def open_heading(self, level: int):
        if level == 1:
            self._out.write(fr'\section*{{')
        #:
        elif level == 2:
            self._out.write(fr'\subsection*{{')
        #:
        else:
            self._out.write(fr'\subsubsection*{{')
        #:
    #:

    @override
    def close_heading(self, level: int):
        self._out.write(f'}}' + '\n')
    #:

    @override
    def new_text_line(self, line: str):
        safe_line = self._escape_latex(line)
        self._out.write(safe_line)
    #:

    @override
    def open_par(self):
        self._out.write(f'')
    #:

    @override
    def close_par(self):
        self._out.write(f'\n\n')
    #:

    @override
    def new_par_line(self, line: str):
        self.new_text_line(line)
    #:

    @override
    def open_list(self, unordered_list = True):
        if unordered_list:
            self._out.write(r'\begin{itemize}' + '\n')
        #:
        else:
            self._out.write(r'\begin{enumerate}' + '\n')
        #:
    #:

    @override
    def close_list(self, unordered_list = True):
        if unordered_list:
            self._out.write(r'\end{itemize}' + '\n')
        #:
        else:
            self._out.write(r'\end{enumerate}' + '\n')
        #:
    #:

    @override
    def open_list_item(self):
        self._out.write(fr'\item ')
    #:

    @override
    def close_list_item(self):
        self._out.write(f'\n')
    #:

    @override
    def open_bold(self, text: str) -> str:
        return fr'\textbf{{{text}'
    #:

    @override
    def close_bold(self, text: str) -> str:
        return fr'{text}}}'
    #:

    @override
    def open_italic(self, text: str) -> str:
        return fr'\textit{{{text}'
    #:

    @override
    def close_italic(self, text: str) -> str:
        return fr'{text}}}'
    #:

    @override
    def new_link(self, text: str, url: str, title: str) -> str:
        return fr'\href{{{url}}}{{{text}}}'
    #:

    @override
    def new_image(self, text: str, url: str, title: str) -> str:
        latex_img = fr"""\begin{{figure}}[h!]
  \centering
  \includegraphics[draft, width=\textwidth]{{{url}}}
"""
        if text:
            latex_img += fr'  \caption{{{text}}}' + '\n'
        #:
        return latex_img + fr"\end{{figure}}" + '\n'
    #:

    @override
    def escape_raw_text(self, text: str) -> str:
        result = text.replace('\\', '___BACKSLASH___')
        result = result.replace('{', r'\{')
        result = result.replace('}', r'\}')
        result = result.replace('___BACKSLASH___', r'\textbackslash{}')
        return result
    #:

    def _escape_latex(self, text: str) -> str:
        replacements = [
            ('%', r'\%'), ('$', r'\$'), ('&', r'\&'), 
            ('_', r'\_'), ('#', r'\#')
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        #:
        return text
    #:
#:
