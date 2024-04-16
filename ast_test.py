import ast
import json

class ConditionExtractor(ast.NodeVisitor):
    def __init__(self):
        self.conditions = []

    def visit_If(self, node):
        # This will visit any 'if' or 'elif' statements
        self.conditions.append(ast.unparse(node.test))
        # Continue processing the rest of the AST
        self.generic_visit(node)

    def visit_While(self, node):
        # This handles the condition in while loops
        self.conditions.append(ast.unparse(node.test))
        self.generic_visit(node)

def extract_conditions(source):
    tree = ast.parse(source)
    extractor = ConditionExtractor()
    extractor.visit(tree)
    return extractor.conditions

# Example usage
source_code = """
if x > 10 & x < 10:
    print("x is greater than 10")
elif x == 5:
    print("x is 5")
while x < 20:
    print("x is less than 20")
"""
conditions = extract_conditions(source_code)
print(json.dumps(conditions))  # Output the conditions as a JSON string