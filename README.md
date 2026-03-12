Markos
=============

**Markos** is a tool that implements a subset of the CommonMark
specification. CommonMark is an open-source specification of the
Markdown syntax with a JavaScript reference implementation:
[commonmark.js](https://github.com/commonmark/commonmark.js/).

The following is taken from commonmark.js GitHub page:

> CommonMark is a rationalized version of Markdown syntax,
> with a [spec][the spec] and BSD-licensed reference
> implementations in C and JavaScript.

>  [the spec]: http://spec.commonmark.org

> For more information, see <http://commonmark.org>.

**Markos** is implemented in Python and is suitable for a beginners 
course in Python programming.

Installing
----------

In the future you will be able install Markos using `pip`:

    pip install markos      # not yet available

Currently, Markos has the following dependencies:

- Beautiful Soup 4
- Docopt

Simplified Markdown
-------------------

Currently, Simplified Markdown (SM) is a subset of the CommonMark
Markdown specification with some added extensions.

The subset of Markdown contained in SM, and currently supported by
`markos` consists of:

TBD...

Simplified Markdown also adds the following extension to Markdown:

TBD...

Command line
------------

Markos parses Simplified Markdown from a specified file or from standard
input. The output is rendered either to a given output file or to standard
output. Command line syntax for calling Markos is:

```
    markos.py [-s STYLE_SHEET] [-p] [-l] [INPUT_FILE] [OUTPUT_FILE]
```

Use `markos --help` to get a summary of options. 

Implementation
---------------

This implementation follows a traditional **Frontend->Backend**
architecture. The **Frontend** parses Markdown code, calling the 
appropriate **Backend** to generate the output code. Currently there is
one backend that generates HTML, but further backends may be
implemented in the future. All backends must implement the 
`MarkdownBackend` interface. 

Instead of parsing Markdown into an AST (Abstract Syntax Tree) and then
rendering from that intermediate representation, markos directly 
translates the source text into the target language/format supported
by the chosen backend.
Using an AST would offer greater flexibility — for example, it would
make it easier to support custom transformations, multiple output 
formats, or backend-specific optimizations. However, the 
direct-rendering approach we adopted is significantly simpler to
implement and understand. It serves as an excellent,
beginner-friendly example of object-oriented programming principles
in action, making it particularly well-suited for educational purposes
and students learning software design.


MENCIONAR:
    - Orientado à linha
    - Expressões regulares
    - Máquina de estados
    - Interfaces / classes abstractas para backend

A note on security
------------------

The following note is adapted from commonmark.js and also applies to Markos: 

> The library does not attempt to sanitize link attributes or
> raw HTML. If you use this library in applications that accept
> untrusted user input, you should run the output through an HTML sanitizer 
> to protect against [XSS attacks](http://en.wikipedia.org/wiki/Cross-site_scripting).

Performance
-----------

TBD...

Authors
-------

Márcio Santos
