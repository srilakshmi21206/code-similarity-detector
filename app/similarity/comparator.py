import ast
import difflib
from app.parser.ast_parser import parse_code, normalize_ast


def ast_to_token_sequence(tree: ast.AST) -> list:
    """
    Walks the AST and produces a flat list of node type names.
    This is more robust than comparing raw string dumps because it
    ignores minor structural noise and focuses on the shape of the code.
    """
    tokens = []
    for node in ast.walk(tree):
        tokens.append(type(node).__name__)
    return tokens


def compute_similarity(source1: str, source2: str) -> dict:
    """
    Compares two pieces of Python source code and returns similarity scores.
    Returns a dict with both a string-based score and a token-based score.
    """
    try:
        tree1 = normalize_ast(parse_code(source1))
        tree2 = normalize_ast(parse_code(source2))
    except SyntaxError as e:
        return {"error": f"Syntax error in code: {str(e)}"}

    # Approach 1: raw normalized string comparison
    dump1 = ast.dump(tree1)
    dump2 = ast.dump(tree2)
    string_similarity = difflib.SequenceMatcher(None, dump1, dump2).ratio()

    # Approach 2: token sequence comparison (structure-focused)
    tokens1 = ast_to_token_sequence(tree1)
    tokens2 = ast_to_token_sequence(tree2)
    token_similarity = difflib.SequenceMatcher(None, tokens1, tokens2).ratio()

    # Combined score: average of both approaches
    combined_score = (string_similarity + token_similarity) / 2

    return {
        "string_similarity": round(string_similarity * 100, 2),
        "token_similarity": round(token_similarity * 100, 2),
        "combined_score": round(combined_score * 100, 2),
    }