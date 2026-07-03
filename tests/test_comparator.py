from app.similarity.comparator import compute_similarity

original = """
def add(a, b):
    result = a + b
    return result
"""

renamed_copy = """
def add(x, y):
    total = x + y
    return total
"""

unrelated = """
def greet(name):
    print("Hello " + name)
"""

calls_print = """
def add(a, b):
    print(a)
    return a + b
"""

calls_len = """
def add(a, b):
    len(a)
    return a + b
"""

invalid_syntax = "def broken(:\n    pass"


def test_renamed_copy_scores_near_100():
    """Same logic with renamed variables should score very close to 100%."""
    result = compute_similarity(original, renamed_copy)
    assert result["combined_score"] >= 95


def test_unrelated_code_scores_low():
    """Structurally different code should score noticeably lower."""
    result = compute_similarity(original, unrelated)
    assert result["combined_score"] < 90


def test_result_contains_expected_keys():
    result = compute_similarity(original, renamed_copy)
    assert "string_similarity" in result
    assert "token_similarity" in result
    assert "combined_score" in result


def test_different_builtin_calls_are_not_treated_as_identical():
    """
    Regression test: calling print() vs len() should NOT be normalized
    to the same placeholder. Before the fix, built-in names were being
    anonymized just like user variables, which inflated similarity
    between code that actually does different things.
    """
    result = compute_similarity(calls_print, calls_len)
    assert result["combined_score"] < 100


def test_syntax_error_returns_error_key():
    result = compute_similarity(original, invalid_syntax)
    assert "error" in result