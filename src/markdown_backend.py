"""
In here we define a generic backend interface for the Markdown compiler
to use.

Copyright 2026 Márcio Santos
"""

from abc import ABC, abstractmethod

__all__ = ['MarkdownBackend']

class MarkdownBackend(ABC):
    @abstractmethod
    def open_document(self, title = ''):
        pass
    #:

    @abstractmethod
    def close_document(self):
        pass
    #:

    @abstractmethod
    def open_heading(self, level: int):
        pass
    #:

    @abstractmethod
    def close_heading(self, level: int):
        pass
    #:

    @abstractmethod
    def new_text_line(self, line: str):
        pass
    #:

    @abstractmethod
    def open_par(self):
        pass
    #:

    @abstractmethod
    def close_par(self):
        pass
    #:

    @abstractmethod
    def new_par_line(self, line: str):
        pass
    #:

    @abstractmethod
    def open_list(self, unordered_list = True):
        pass
    #:

    @abstractmethod
    def close_list(self, unordered_list = True):
        pass
    #:

    @abstractmethod
    def open_list_item(self):
        pass
    #:

    @abstractmethod
    def close_list_item(self):
        pass
    #:

    @abstractmethod
    def open_bold(self, text: str) -> str:
        pass
    #:

    @abstractmethod
    def close_bold(self, text: str) -> str:
        pass
    #:

    @abstractmethod
    def open_italic(self, text: str) -> str:
        pass
    #:

    @abstractmethod
    def close_italic(self, text: str) -> str:
        pass
    #:

    @abstractmethod
    def new_link(self, text: str, url: str, title: str) -> str:
        pass
    #:

    @abstractmethod
    def new_image(self, text: str, url: str, title: str) -> str:
        pass
    #:
#:
