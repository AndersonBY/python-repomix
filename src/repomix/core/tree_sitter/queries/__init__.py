"""Tree-sitter queries for different programming languages."""

from .query_python import query_python
from .query_javascript import query_javascript
from .query_typescript import query_typescript
from .query_go import query_go
from .query_java import query_java
from .query_c import query_c
from .query_cpp import query_cpp
from .query_csharp import query_csharp
from .query_rust import query_rust
from .query_ruby import query_ruby
from .query_php import query_php
from .query_swift import query_swift
from .query_css import query_css

__all__ = [
    "query_python",
    "query_javascript",
    "query_typescript",
    "query_go",
    "query_java",
    "query_c",
    "query_cpp",
    "query_csharp",
    "query_rust",
    "query_ruby",
    "query_php",
    "query_swift",
    "query_css",
]
