"""
A Simplified Markdown compiler developed in Python. This module
implements a parser which then calls the given backend.

Copyright 2026 Márcio Santos
"""

from functools import singledispatchmethod
from io import StringIO
import re
from enum import Enum
from typing import TextIO

from markdown_backend import MarkdownBackend
from markdown_list import (
    MarkdownList,
    ListItem,
    ListItemInnerElem,
    ListItemBlock,
    ListItemHeading
)
from utils import count_consec, matches, rewind_one_line

__all__ = [
    'MarkdownCompiler',
    'CompilationError'
]

class CompilationError(Exception):
    """
    A generic compilation error. This could be due to invalid Markdown
    or some other problem.
    """
#:

class MarkdownCompiler:
    """
    Implements a Simplified Markdown parser and compiler. Please refer to
    the `compile` method documentation.
    """

    INLINE_TITLE_MARKER = '!'
    INLINE_HEADING_MARKER = '#'
    INLINE_ULIST_MARKER = '-' # [-*]

    BLANK_LINE = re.compile('[ \t\n\r]*')
    UNINDENT_HEADING_LINE = re.compile(fr'\s?{INLINE_HEADING_MARKER}{"{1,6}"}(\s+.*)?')
    INDENT_HEADING_LINE = re.compile(fr'\s{"{2,}"}{INLINE_HEADING_MARKER}{"{1,6}"}(\s+.*)?')
    UNINDENT_TEXT_LINE = re.compile(r'\s?\S.*')
    INDENT_TEXT_LINE = re.compile(r'\s{2,}\S.*')
    LIST_ITEM_LINE = re.compile(fr'\s{"{,3}"}{INLINE_ULIST_MARKER}(\s+.*)?')
    TITLE_LINE = re.compile(fr'{INLINE_TITLE_MARKER}.*\S.*{INLINE_TITLE_MARKER}')

    def __init__(self, backend: MarkdownBackend):
        self._backend = backend
    #:

    def compile(self, in_: TextIO | str):
        """
        This method is the main interface for the compiler. It implements
        a State Machine (SM) where parsing and code generation is done
        in one go. Except for lists, as soon a Markdown element is
        recognized, code is generated for it. This SM handles paragraphs,
        blank lines, top-level headers and starts the state machine related
        to lists.

        We use a finite state machine to implement the Markdown parser.
        This finite state machine can be represented by a state diagram
        using, for example, the UML state diagram graphical notation.
        """
        if isinstance(in_, str):
            in_ = StringIO(in_)
        #:

        backend = self._backend
        title = self._read_title(in_)
        backend.open_document(title)

        CompilerState = Enum('CompilerState', 'OUTSIDE INSIDE_PAR NEW_LIST')
        state = CompilerState.OUTSIDE

        while line := in_.readline():   # we can't use for loop here because
            line = line[:-1]            # we want to be able to rewind in
            
            if state is CompilerState.OUTSIDE and self._is_heading_line(line):
                self._new_heading(line)
            #:
            elif state is CompilerState.OUTSIDE and matches(self.LIST_ITEM_LINE, line):
                rewind_one_line(in_, line)
                self._compile_list(in_)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.OUTSIDE and self._is_text_line(line):
                backend.open_par()
                backend.new_par_line(line)
                state = CompilerState.INSIDE_PAR
            #:
            elif state is CompilerState.INSIDE_PAR and matches(self.BLANK_LINE, line):
                backend.close_par()
                state = CompilerState.OUTSIDE
            #:
            elif state is CompilerState.INSIDE_PAR and self._is_heading_line(line):
                backend.close_par()
                self._new_heading(line)
                state = CompilerState.OUTSIDE
            #:
            elif state is CompilerState.INSIDE_PAR and matches(self.LIST_ITEM_LINE, line):
                backend.close_par()
                rewind_one_line(in_, line)
                self._compile_list(in_)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.INSIDE_PAR and self._is_text_line(line):
                backend.new_par_line(line)
            #:
            elif state is CompilerState.NEW_LIST and matches(self.UNINDENT_HEADING_LINE, line):
                self._new_heading(line)
                state = CompilerState.OUTSIDE
            #:
            elif state is CompilerState.NEW_LIST and matches(self.UNINDENT_TEXT_LINE, line):
                backend.open_par()
                backend.new_par_line(line)
                state = CompilerState.INSIDE_PAR
            #:
            else:
                assert state is CompilerState.OUTSIDE and matches(self.BLANK_LINE, line), \
                        f"Unknown line \'{line}\' for state {state}"
            #:
        #:

        backend.close_document()
    #:

    def _new_heading(self, line_with_markers: str):
        backend = self._backend
        text, level = self._parse_heading(line_with_markers)
        backend.open_heading(level)
        backend.new_text_line(text)
        backend.close_heading(level)
    #:

    def _parse_heading(self, line_with_markers: str) -> tuple[str, int]:
        line_with_markers = line_with_markers.lstrip()
        count = count_consec(line_with_markers, self.INLINE_HEADING_MARKER)
        assert count > 0, 'No heading markers found'
        text = line_with_markers[count:].strip()
        return text, count
    #:

    def _is_heading_line(self, line: str) -> bool:
        return (
            matches(self.UNINDENT_HEADING_LINE, line)
            or matches(self.INDENT_HEADING_LINE, line)
        )
    #:

    def _is_text_line(self, line: str) -> bool:
        return (
            matches(self.UNINDENT_TEXT_LINE, line)
            or matches(self.INDENT_TEXT_LINE, line)
        )
    #:

    def _read_title(self, in_: TextIO) -> str:
        first_line = in_.readline()[:-1]
        second_line = in_.readline()
        if matches(self.TITLE_LINE, first_line) and matches(self.BLANK_LINE, second_line):
            return first_line[1:-1].strip()
        #:
        in_.seek(0)
        return ''
    #:

    def _compile_list(self, in_: TextIO):
        line = in_.readline()[:-1]
        assert matches(self.LIST_ITEM_LINE, line), \
            f'First line not a list item line: |{line}|'
        
        mkd_list = MarkdownList()
        curr_list_item = mkd_list.add_new_list_item(
            self._new_list_item_inner_elem(line)
        )
        
        ListState = Enum('ListState', 'LIST_ITEM MAY_END')
        state = ListState.LIST_ITEM

        while line := in_.readline():
            line = line[:-1]

            if matches(self.UNINDENT_HEADING_LINE, line):
                # End of list: rewind the reader and terminate the SM.
                # An unidented heading terminates the list regardless of
                # the current state.
                rewind_one_line(in_, line)
                break
            #:
            elif state is ListState.LIST_ITEM and matches(self.LIST_ITEM_LINE, line):
                curr_list_item = mkd_list.add_new_list_item(
                    self._new_list_item_inner_elem(line)
                )
            #:
            elif state is ListState.LIST_ITEM and matches(self.INDENT_HEADING_LINE, line):
                curr_list_item.append(self._new_list_item_heading(line))
            #:
            elif state is ListState.LIST_ITEM and self._is_text_line(line):
                curr_list_item.add_text_line(line)
            #:
            elif state is ListState.LIST_ITEM and matches(self.BLANK_LINE, line):
                state = ListState.MAY_END
            #:
            elif state is ListState.MAY_END and matches(self.LIST_ITEM_LINE, line):
                curr_list_item = mkd_list.add_new_list_item(
                    self._new_list_item_inner_elem(line)
                )
                mkd_list.with_paragraphs = True
                state = ListState.LIST_ITEM
            #:
            elif state is ListState.MAY_END and matches(self.INDENT_HEADING_LINE, line):
                curr_list_item.append(self._new_list_item_heading(line))
                mkd_list.with_paragraphs = True
                state = ListState.LIST_ITEM
            #:
            elif state is ListState.MAY_END and matches(self.INDENT_TEXT_LINE, line):
                curr_list_item.append(ListItemBlock(line))
                mkd_list.with_paragraphs = True
                state = ListState.LIST_ITEM
            #:
            elif state is ListState.MAY_END and matches(self.UNINDENT_TEXT_LINE, line):
                # End of list: rewind the TextIO and terminates the SM
                rewind_one_line(in_, line)
                break
            #:
            else:
                assert state is ListState.MAY_END and matches(self.BLANK_LINE, line), \
                    f"Unknown line \'{line}\' for state {state}"
            #:
        #:

        self._compile_markdown_list(mkd_list)
        # self.__dump_markdown_list(mkd_list)
    #:

    def _new_list_item_inner_elem(self, initial_line: str) -> ListItemInnerElem:
        line = initial_line.strip()[1:]     # remove list marker
        if self._is_heading_line(line):
            return self._new_list_item_heading(line)
        #:
        return ListItemBlock(line)
    #:

    def _new_list_item_heading(self, line_with_markers: str) -> ListItemHeading:
        line, level = self._parse_heading(line_with_markers)
        return ListItemHeading(line, level)
    #:

    def _compile_markdown_list(self, mkd_list: MarkdownList):
        backend = self._backend
        backend.open_list()
        for list_item in mkd_list:
            self._compile_list_item(list_item, mkd_list.with_paragraphs)
        #:
        backend.close_list()
    #:

    def _compile_list_item(self, list_item: ListItem, with_paragraphs: bool):
        backend = self._backend
        backend.open_list_item()
        for inner_elem in list_item:
            self._compile_list_item_inner_elem(inner_elem, with_paragraphs)
        #:
        backend.close_list_item()
    #:

    @singledispatchmethod
    def _compile_list_item_inner_elem(self, elem, *_, **__):
        raise NotImplementedError(f"Unknown inner elem '{elem}' of type {type(elem)}")
    #:

    @_compile_list_item_inner_elem.register
    def _(self, block: ListItemBlock, with_paragraphs: bool):
        backend = self._backend
        if with_paragraphs:
            backend.open_par()
            backend.new_par_line(str(block))
            backend.close_par()
        #:
        else:
            backend.new_par_line(str(block))
    #:

    @_compile_list_item_inner_elem.register
    def _(self, heading: ListItemHeading, *_):
        backend = self._backend
        backend.open_heading(heading.level)
        backend.new_text_line(str(heading))
        backend.close_heading(heading.level)
    #:

    def __dump_markdown_mist(self, mkd_list: MarkdownList):
        print("MARKDOWN LIST")
        for list_item in mkd_list:
            print("LIST ITEM")
            for inner_elem in list_item:
                print(repr(inner_elem))
            #:
        #:
    #:
#:
