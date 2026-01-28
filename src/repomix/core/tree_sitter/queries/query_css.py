"""Tree-sitter query for CSS code analysis."""

# CSS tree-sitter query for extracting key code elements
query_css = """
; Comments
(comment) @comment

; Import statements
(import_statement) @definition.import

; Rule sets
(rule_set
  (selectors) @name.definition.selector) @definition.rule

; Media queries
(media_statement) @definition.media

; Keyframes
(keyframes_statement
  name: (keyframes_name) @name.definition.keyframes) @definition.keyframes

; Font-face
(at_rule
  (at_keyword) @_keyword
  (#eq? @_keyword "@font-face")) @definition.fontface
"""
