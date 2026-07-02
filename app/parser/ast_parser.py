import ast

class Normalizer(ast.NodeTransformer):
    """
    Walks the AST and replaces variable/function names with generic placeholders
    so that renaming variables doesn't defeat similarity detection.
    """
    def __init__(self):
        self.name_map = {}
        self.counter = 0

    def _get_placeholder(self, original_name):
        if original_name not in self.name_map:
            self.counter += 1
            self.name_map[original_name] = f"VAR{self.counter}"
        return self.name_map[original_name]

    def visit_Name(self, node):
        node.id = self._get_placeholder(node.id)
        return node

    def visit_FunctionDef(self, node):
        node.name = self._get_placeholder(node.name)
        self.generic_visit(node)
        return node

    def visit_arg(self, node):
        node.arg = self._get_placeholder(node.arg)
        return node


def parse_code(source: str) -> ast.AST:
    """Parses Python source code into an AST."""
    return ast.parse(source)


def normalize_ast(tree: ast.AST) -> ast.AST:
    """Returns a normalized version of the AST with generic variable names."""
    normalizer = Normalizer()
    return normalizer.visit(tree)


def get_normalized_dump(source: str) -> str:
    """Convenience function: source code -> normalized AST string representation."""
    tree = parse_code(source)
    normalized = normalize_ast(tree)
    return ast.dump(normalized)