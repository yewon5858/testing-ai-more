import ast
import astunparse


def collect_variables(a):
    if type(a) is ast.Module:
        return [v for s in a.body for v in collect_variables(s)]
    elif type(a) is ast.FunctionDef:
        vs = [v for s in a.body for v in collect_variables(s)]
        return [a.name] + vs
    elif type(a) is ast.Assign:
        vs = [v for s in a.targets for v in collect_variables(s)]
        return vs + collect_variables(a.value)
    elif type(a) is ast.Return:
        return collect_variables(a.value)
    elif type(a) is ast.Name:
        return [a.id]
    elif type(a) is ast.BinOp:
        return collect_variables(a.left) + collect_variables(a.right)
    else:
        print(type(a))  # Display trees not captured by cases above.
        return []



# print(ast.dump(ast.parse('1 <= a < 10', mode='eval'), indent=4))
# Expression(
#     body=Compare(
#         left=Constant(value=1),
#         ops=[
#             LtE(),
#             Lt()],
#         comparators=[
#             Name(id='a', ctx=Load()),
#             Constant(value=10)]))


class ComparisonTransformer(ast.NodeTransformer):
    def __init__(self):
        self.encrypt = dict()

    def _identifier(self, node: ast.Compare) -> str:
        id_list = [n.id for n in node.comparators + [node.left] if isinstance(n, ast.Name)]
        print(f"id_list = {id_list}")
        id_node = "".join(id_list)
        return id_node + str(len(self.encrypt))

    def _datatype(self, node: ast.Compare) -> type:
        data_type = None
        for comparator in node.comparators:
            if isinstance(comparator, ast.Constant):
                data_type = type(comparator.value)
        return data_type

    def visit_Compare(self, node):
        comparison = astunparse.unparse(node)

        id_name = self._identifier(node)

        print(f"id: {id_name}")
        transformation = ast.parse(id_name)

        data_type = self._datatype(node)

        self.encrypt[id_name] = (comparison, data_type)

        print("Comparison: {0}".format(comparison))
        print("Transformed: {0}".format(astunparse.unparse(transformation)))
        print("Encrypt: {0}".format(self.encrypt))
        return transformation


# print(ast.dump(ast.parse('x or y', mode='eval'), indent=4))
# Expression(
#     body=BoolOp(
#         op=Or(),
#         values=[
#             Name(id='x', ctx=Load()),
#             Name(id='y', ctx=Load())]))

class DisplayBoolOpVariables(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()

    def visit_Name(self, node):
        print(node.id)
        self.generic_visit(node)
    def visit_BoolOp(self, node):
        variables = [var.id for var in node.values if isinstance(var, ast.Name)]
        self.variables = self.variables.union(variables)
    #     print("node: {0}".format(astunparse.unparse(node)))
    #     comparators = []
    #     print(node.values)
    #     for value in node.values:
    #         print("value: {0}".format(astunparse.unparse(value)))
    #         if isinstance(value, ast.Compare):
    #             print("comparison: {0}".format(astunparse.unparse(value)))
    #             modified_compare = self.modify_comparison(value)
    #             comparators.append(modified_compare)
    #         else:
    #             print(type(value.values))
    #             transformed_value = self.generic_visit(value)
    #             print("transformed_value: {0}".format(astunparse.unparse(transformed_value)))
    #             comparators.append(transformed_value)
    #
    #         node.values = comparators
    #     return node

    # def modify_comparison(self, compare_node):
    #     print("Comparison: {0}".format(astunparse.unparse(compare_node)))
    #     if (len(compare_node.ops) == 1 and isinstance(compare_node.ops[0], (ast.Lt, ast.Gt, ast.LtE, ast.GtE))
    #             and isinstance(compare_node.comparators[0], ast.Num)):
    #         return compare_node.left
    #     return compare_node


if __name__ == "__main__":
    # Código de ejemplo
    code = "(a < 10) and (b > 10) or c"

    # Analiza el código fuente
    tree = ast.parse(code)

    # Crea una instancia del transformador
    transformer = ComparisonTransformer()

    # Aplica el transformador al árbol
    transformed_tree = transformer.visit(tree)

    # Revierte el árbol modificado a código fuente
    modified_code = astunparse.unparse(transformed_tree)

    print(modified_code)
    print(transformer.encrypt)
