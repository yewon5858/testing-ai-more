import json
from pyeda.boolalg.expr import expr, exprvar

def eval_pyeda(eq: str, test: dict) -> int:

    # a = exprvar("a")
    # b = exprvar("b")
    # ...
    for var in test.keys():
        exec(f"{var} = exprvar('{var}')")

    f = expr(eq)

    # Devuelve 0/1 (False/True) en función del resultado de la evaluación
    return f.restrict(data)

def eval_python(eq: str, test: dict) -> bool:

    # Todo: es un poco chapucero, pero lo mas rapido es reemplazar los simbolos &|! de pyeda por and, or y not en python
    eq = eq.replace("&", "and")
    eq = eq.replace("|", "or")
    eq = eq.replace("!", "not")

    for var, val in test.items():
        exec(f"{var} = {val}")

    # Devuelve False/True en función del resultado de la evaluación
    return eval(eq)


if __name__ == '__main__':
    # Lectura de la solucion proporcionada por pymcdc/llm
    formato_1 = '{"a": 1, "b": 0}'
    data = json.loads(formato_1)

    formato_2 = "[{'a': 1, 'b': 2}]"
    data = eval(formato_2)

    # La condición que se desea estudiar es eq.
    eq1 = "(a > 10) & (b < 9)"

    # En el caso de usar pyeda, la ecuación tiene que estar en formato booleano
    eq2 = "a & b"
    for test in data:
        eval_python(eq1, test)
        eval_pyeda(eq2, test)

