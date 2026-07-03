import tree_sitter_java
import tree_sitter_cpp
from tree_sitter import Language, Parser

# Supported languages mapping
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "cpp",
}

# Load grammars
JAVA_LANGUAGE = Language(tree_sitter_java.language())
CPP_LANGUAGE = Language(tree_sitter_cpp.language())

LANGUAGE_MAP = {
    "java": JAVA_LANGUAGE,
    "cpp": CPP_LANGUAGE,
}


def get_language(filename: str) -> str:
    """Detect language from file extension."""
    for ext, lang in SUPPORTED_EXTENSIONS.items():
        if filename.endswith(ext):
            return lang
    return None


def get_token_sequence(source: str, language: str) -> list:
    """
    Parses source code using tree-sitter and returns
    a flat list of node type names (token sequence).
    """
    if language == "python":
        # Fall back to built-in ast module for Python
        import ast
        from app.parser.ast_parser import normalize_ast, parse_code
        tree = normalize_ast(parse_code(source))
        import ast as ast_module
        return [type(node).__name__ for node in ast_module.walk(tree)]

    lang_obj = LANGUAGE_MAP.get(language)
    if not lang_obj:
        raise ValueError(f"Unsupported language: {language}")

    parser = Parser(lang_obj)
    tree = parser.parse(bytes(source, "utf-8"))

    tokens = []
    def walk(node):
        tokens.append(node.type)
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return tokens


def compute_multilang_similarity(source1: str, source2: str, language: str) -> dict:
    """
    Computes similarity between two code snippets of the same language.
    """
    import difflib

    try:
        tokens1 = get_token_sequence(source1, language)
        tokens2 = get_token_sequence(source2, language)
    except Exception as e:
        return {"error": str(e)}

    token_similarity = difflib.SequenceMatcher(None, tokens1, tokens2).ratio()
    string_similarity = difflib.SequenceMatcher(None, source1, source2).ratio()
    combined_score = (token_similarity + string_similarity) / 2

    return {
        "language": language,
        "string_similarity": round(string_similarity * 100, 2),
        "token_similarity": round(token_similarity * 100, 2),
        "combined_score": round(combined_score * 100, 2),
    }