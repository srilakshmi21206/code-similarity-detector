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

print("Original vs Renamed Copy (should be ~100%):")
print(compute_similarity(original, renamed_copy))
print()

print("Original vs Unrelated (should be low):")
print(compute_similarity(original, unrelated))