import sys

def eval_python(eq: str, test: dict) -> bool:

    # Todo: reemplazar los simbolos &|! de pyeda por and, or y not en python
    eq = eq.replace("&", "and")
    eq = eq.replace("|", "or")
    eq = eq.replace("!", "not")
    eq = eq.replace("=", "==")

    for var, val in test.items():
        exec(f"{var} = {val}")

    # Devuelve False/True en función del resultado de la evaluación
    return eval(eq)

def comprob_valores_diferentes_nueva(variables: set, listT: list, listaF: list) -> bool:
    exists_pair_for_var = dict.fromkeys(variables, False)
    for var in variables:
        for testT in listT:
            # Tests que hacen falsa la expresion booleana. El valor de la variable var debe cambiar.
            test_to_false_with_diff_var_value = [testF for testF in listaF if testT[var] != testF[var]]
            # Para algun test que hace cierta la expresion booleana, existe algun test que la falsea en el que var
            # cambia de valor numerico
            exists_pair_for_var[var] = exists_pair_for_var[var] or (len(test_to_false_with_diff_var_value) > 0)

    print(f"ListT: {listT}")
    print(f"ListF: {listaF}")
    print(f"exists_pair_for_var: {exists_pair_for_var}")
    # Toda varible de la expresion booleana tiene una pareja de casos de prueba (T, F)
    return all(exists_pair_for_var)

def comprob_valores_diferentes(listT: list, listaF: list) -> bool:
    for testT in listT:
        for var in testT:
            encontrado = False
            for testF in listaF:
                if testT[var] != testF[var]:
                    encontrado = True
                    break  # Si encontramos un valor diferente para esta var, pasamos a la siguiente var
            if not encontrado:
                # Si no encontramos ningún valor diferente para esta var, devolvemos False
                return False
    return True


if __name__ == '__main__':
    if len(sys.argv) > 2:
        eq = sys.argv[1]
        testList = sys.argv[2]
    else:
        print("Argumento no valido")
        sys.exit(1)

    #"[{'a': 1, 'b': 2}]" formato lista de tests
    data = eval(testList)

    # La condición que se desea estudiar es eq.
    # El formato de la condición
    # eq = "(a > 10) & (b < 9)"

    # Casos de prueba que hacen cierta o falsa la formula booleana
    trueList = []
    falseList = []

    # Conjunto de todas las variables
    variables = set()

    for test in data:
        variables.update(test.keys())
        #print(eval_python(eq,test)) print de la evaluacion de eq para cada test
        if eval_python(eq, test):
            trueList.append(test) #lista de tests True
        else:
            falseList.append(test) #lista de tests False

    nTests = len(data)
    nVar = len(variables)
    nTestsAdecuado: bool = (nVar + 1 <= nTests <= 2 * nVar)

    print("Cumple con MC/DC: " + str(comprob_valores_diferentes_nueva(variables, trueList, falseList) and nTestsAdecuado))