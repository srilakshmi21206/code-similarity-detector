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

print("Code 1 normalized:")
print(get_normalized_dump(code1))
print()
print("Code 2 normalized:")
print(get_normalized_dump(code2))
print()
print("Are they identical?", get_normalized_dump(code1) == get_normalized_dump(code2))