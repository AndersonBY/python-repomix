"""Tree-sitter query for Ruby code analysis."""

# Ruby tree-sitter query for extracting key code elements
query_ruby = """
; Comments
(comment) @comment

; Require statements
(call
  method: (identifier) @_method
  arguments: (argument_list
    (string) @name.reference.module)
  (#match? @_method "^(require|require_relative|load)$")) @definition.import

; Class definitions
(class
  name: (constant) @name.definition.class) @definition.class

; Module definitions
(module
  name: (constant) @name.definition.module) @definition.module

; Method definitions
(method
  name: (identifier) @name.definition.method) @definition.method

(singleton_method
  name: (identifier) @name.definition.method) @definition.method

; Constant assignments
(assignment
  left: (constant) @name.definition.constant) @definition.constant
"""
