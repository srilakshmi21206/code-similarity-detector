from app.parser.ast_parser import get_normalized_dump

code1 = """
def add(a, b):
    result = a + b
    return result
"""

code2 = """
def add(x, y):
    total = x + y
    return total
"""

code_with_print = """
def greet(name):
    print(name)
"""

code_with_len = """
def greet(name):
    len(name)
"""


def test_renamed_variables_produce_identical_normalized_dump():
    """Renaming variables/functions shouldn't change the normalized AST."""
    assert get_normalized_dump(code1) == get_normalized_dump(code2)


def test_normalized_dump_is_a_non_empty_string():
    dump = get_normalized_dump(code1)
    assert isinstance(dump, str)
    assert len(dump) > 0


def test_builtin_names_are_preserved_not_normalized():
    """
    Regression test: built-in function names like print/len should
    remain literally 'print' / 'len' in the normalized dump, rather
    than being replaced with a generic VARn placeholder.
    """
    dump_print = get_normalized_dump(code_with_print)
    dump_len = get_normalized_dump(code_with_len)
    assert "print" in dump_print
    assert "len" in dump_len
    assert dump_print != dump_len