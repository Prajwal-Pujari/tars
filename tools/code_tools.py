import os
import logging
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_rust as tsrust
import tree_sitter_go as tsgo
from tree_sitter import Language, Parser

logger = logging.getLogger(__name__)

# Load languages
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())
RUST_LANGUAGE = Language(tsrust.language())
GO_LANGUAGE = Language(tsgo.language())

def get_parser(extension):
    parser = Parser()
    if extension == ".py":
        parser.language = PY_LANGUAGE
    elif extension in [".js", ".jsx"]:
        parser.language = JS_LANGUAGE
    elif extension in [".ts", ".tsx"]:
        parser.language = JS_LANGUAGE  # Fallback
    elif extension == ".rs":
        parser.language = RUST_LANGUAGE
    elif extension == ".go":
        parser.language = GO_LANGUAGE
    else:
        return None
    return parser

def parse_code(file_path):
    """Parse source code into an AST."""
    ext = os.path.splitext(file_path)[1]
    parser = get_parser(ext)
    if not parser:
        logger.warning(f"No tree-sitter parser for {ext}")
        return None
    
    try:
        with open(file_path, "rb") as f:
            src = f.read()
        tree = parser.parse(src)
        return tree
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return None
