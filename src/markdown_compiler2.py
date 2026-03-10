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
    INLINE_ULIST_MARKER = '[-*]'
    INLINE_OLIST_MARKER = r'\d+\.?'
    INLINE_APATTERN_MARKER = r'\*'
    INLINE_UPATTERN_MARKER = '_'

    BLANK_LINE = re.compile('[ \t\n\r]*')
    UNINDENT_HEADING_LINE = re.compile(fr'\s?{INLINE_HEADING_MARKER}{"{1,6}"}(\s+.*)?')
    INDENT_HEADING_LINE = re.compile(fr'\s{"{2,}"}{INLINE_HEADING_MARKER}{"{1,6}"}(\s+.*)?')
    UNINDENT_TEXT_LINE = re.compile(r'\s?\S.*')
    INDENT_TEXT_LINE = re.compile(r'\s{2,}\S.*')
    ULIST_ITEM_LINE = re.compile(fr'\s{"{,3}"}{INLINE_ULIST_MARKER}(\s+.*)?')
    OLIST_ITEM_LINE = re.compile(fr'\s{"{,3}"}{INLINE_OLIST_MARKER}(\s+.*)?')
    TITLE_LINE = re.compile(fr'{INLINE_TITLE_MARKER}.*\S.*{INLINE_TITLE_MARKER}')

    BOLD_A_PATTERN = re.compile(
        fr'(?<!{INLINE_APATTERN_MARKER}){INLINE_APATTERN_MARKER}{"{2}"}'
        fr'(?!\s)(.+?)(?<!\s){INLINE_APATTERN_MARKER}{"{2}"}'
        fr'(?!{INLINE_APATTERN_MARKER})'
    )
    BOLD_U_PATTERN = re.compile(
        fr'(?<![a-zA-Z0-9{INLINE_UPATTERN_MARKER}]){INLINE_UPATTERN_MARKER}{"{2}"}(?!\s)'
        fr'(.+?)(?<!\s){INLINE_UPATTERN_MARKER}{"{2}"}'
        fr'(?![a-zA-Z0-9{INLINE_UPATTERN_MARKER}])'
    )
    ITALIC_A_PATTERN = re.compile(
        fr'(?<!{INLINE_APATTERN_MARKER}){INLINE_APATTERN_MARKER}(?!\s)'
        fr'(.+?)(?<!\s){INLINE_APATTERN_MARKER}'
        fr'(?!{INLINE_APATTERN_MARKER})'
    )
    ITALIC_U_PATTERN = re.compile(
        fr'(?<![a-zA-Z0-9{INLINE_UPATTERN_MARKER}]){INLINE_UPATTERN_MARKER}(?!\s)'
        fr'(.+?)(?<!\s){INLINE_UPATTERN_MARKER}'
        fr'(?![a-zA-Z0-9{INLINE_UPATTERN_MARKER}])'
    )
    LINK_PATTERN = re.compile(r'(?<!\!)\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)')
    IMAGE_PATTERN = re.compile(r'\!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)')

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
            elif state is CompilerState.OUTSIDE and matches(self.ULIST_ITEM_LINE, line):
                rewind_one_line(in_, line)
                self._compile_list(in_, True)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.OUTSIDE and matches(self.OLIST_ITEM_LINE, line):
                rewind_one_line(in_, line)
                self._compile_list(in_, False)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.OUTSIDE and self._is_text_line(line):
                backend.open_par()
                line = self._compile_inline(line)
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
            elif state is CompilerState.INSIDE_PAR and matches(self.ULIST_ITEM_LINE, line):
                backend.close_par()
                rewind_one_line(in_, line)
                self._compile_list(in_, True)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.INSIDE_PAR and matches(self.OLIST_ITEM_LINE, line):
                backend.close_par()
                rewind_one_line(in_, line)
                self._compile_list(in_, False)
                state = CompilerState.NEW_LIST
            #:
            elif state is CompilerState.INSIDE_PAR and self._is_text_line(line):
                line = self._compile_inline(line)
                backend.new_par_line(line)
            #:
            elif state is CompilerState.NEW_LIST and matches(self.UNINDENT_HEADING_LINE, line):
                self._new_heading(line)
                state = CompilerState.OUTSIDE
            #:
            elif state is CompilerState.NEW_LIST and matches(self.UNINDENT_TEXT_LINE, line):
                backend.open_par()
                line = self._compile_inline(line)
                backend.new_par_line(line)
                state = CompilerState.INSIDE_PAR
            #:
            elif state is CompilerState.NEW_LIST and matches(self.ULIST_ITEM_LINE, line):
                rewind_one_line(in_, line)
                self._compile_list(in_, True)
            #:
            elif state is CompilerState.NEW_LIST and matches(self.OLIST_ITEM_LINE, line):
                rewind_one_line(in_, line)
                self._compile_list(in_, False)
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
        text = self._compile_inline(text)
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

    def _compile_list(self, in_: TextIO, unordered_list: bool):
        line = in_.readline()[:-1]

        if unordered_list:
            assert matches(self.ULIST_ITEM_LINE, line), \
                f'First line not a list item line: |{line}|'
        else:
            assert matches(self.OLIST_ITEM_LINE, line), \
                f'First line not a list item line: |{line}|'
        
        mkd_list = MarkdownList()
        curr_list_item = mkd_list.add_new_list_item(
            self._new_list_item_inner_elem(line, unordered_list)
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
            elif state is ListState.LIST_ITEM and matches(self.ULIST_ITEM_LINE, line):
                if unordered_list:
                    curr_list_item = mkd_list.add_new_list_item(
                        self._new_list_item_inner_elem(line, unordered_list)
                    )
                #:
                else:
                    rewind_one_line(in_, line)
                    break
                #:
            #:
            elif state is ListState.LIST_ITEM and matches(self.OLIST_ITEM_LINE, line):
                if unordered_list:
                    rewind_one_line(in_, line)
                    break
                #:
                else:
                    curr_list_item = mkd_list.add_new_list_item(
                        self._new_list_item_inner_elem(line, unordered_list)
                    )
                #:
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
            elif state is ListState.MAY_END and matches(self.ULIST_ITEM_LINE, line):
                if unordered_list:
                    curr_list_item = mkd_list.add_new_list_item(
                        self._new_list_item_inner_elem(line, unordered_list)
                    )
                    mkd_list.with_paragraphs = True
                    state = ListState.LIST_ITEM
                #:
                else:
                    rewind_one_line(in_, line)
                    break
                #:
            #:
            elif state is ListState.MAY_END and matches(self.OLIST_ITEM_LINE, line):
                if unordered_list:
                    rewind_one_line(in_, line)
                    break
                #:
                else:
                    curr_list_item = mkd_list.add_new_list_item(
                        self._new_list_item_inner_elem(line, unordered_list)
                    )
                    mkd_list.with_paragraphs = True
                    state = ListState.LIST_ITEM
                #:
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

        self._compile_markdown_list(mkd_list, unordered_list)
        # self.__dump_markdown_list(mkd_list)
    #:

    def _new_list_item_inner_elem(self, initial_line: str, unordered_list: bool) -> ListItemInnerElem:
        if unordered_list:
            line = initial_line.strip()[1:]     # remove list marker
        #:
        else:
            line = initial_line.strip()
            line = line[line.find(' '):]
        #:
        if self._is_heading_line(line):
            return self._new_list_item_heading(line)
        #:
        line = self._compile_inline(line)
        return ListItemBlock(line)
    #:

    def _new_list_item_heading(self, line_with_markers: str) -> ListItemHeading:
        line, level = self._parse_heading(line_with_markers)
        line = self._compile_inline(line)
        return ListItemHeading(line, level)
    #:

    def _compile_markdown_list(self, mkd_list: MarkdownList, unordered_list: bool):
        backend = self._backend
        backend.open_list(unordered_list)
        for list_item in mkd_list:
            self._compile_list_item(list_item, mkd_list.with_paragraphs)
        #:
        backend.close_list(unordered_list)
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

    def __dump_markdown_list(self, mkd_list: MarkdownList):
        print("MARKDOWN LIST")
        for list_item in mkd_list:
            print("LIST ITEM")
            for inner_elem in list_item:
                print(repr(inner_elem))
            #:
        #:
    #:

    def _compile_inline(self, line: str) -> str:
        result = self._handle_media(line)
        result = self._handle_bold(result)
        result = self._handle_italic(result)
        return result
    #:

    def _handle_bold(self, line: str) -> str:
        backend = self._backend
        result = self._apply_style(line, self.BOLD_A_PATTERN, backend.open_bold, backend.close_bold)
        return self._apply_style(result, self.BOLD_U_PATTERN, backend.open_bold, backend.close_bold)
    #:

    def _handle_italic(self, line: str) -> str:
        backend = self._backend
        result = self._apply_style(line, self.ITALIC_A_PATTERN, backend.open_italic, backend.close_italic)
        return self._apply_style(result, self.ITALIC_U_PATTERN, backend.open_italic, backend.close_italic)
    #:

    def _handle_media(self, line: str) -> str:
        backend = self._backend
        result = self._apply_media(line, self.IMAGE_PATTERN, backend.new_image)
        return self._apply_media(result, self.LINK_PATTERN, backend.new_link)
    #:

    def _apply_style(self, line: str, re_pattern, open_func, close_func) -> str:
        parts = re_pattern.split(line)
        if len(parts) > 1:
            for i in range(1,len(parts), 2):
                parts[i] = close_func(open_func(parts[i]))
            #:
        #:
        return "".join(parts)
    #:

    def _apply_media(self, line: str, re_pattern, new_func) -> str:
        parts = re_pattern.split(line)
        if len(parts) > 1:
            for i in range(1,len(parts), 4):
                if parts[i+2] is None:
                    parts[i+2] = ''
                #:
                parts[i] = new_func(parts[i].strip(), parts[i+1].strip(), parts[i+2])
                parts[i+1] = ''
                parts[i+2] = ''
            #:
        #:
        return "".join(parts)
    #:
#:
