import sys
from pyeda.boolalg.expr import expr, exprvar

def eval_python(eq: str, test: dict) -> bool:

    # Todo: reemplazar los simbolos &|! de pyeda por and, or y not en python
    eq = eq.replace("&", "and")
    eq = eq.replace("|", "or")
    eq = eq.replace("!", "not")

    for var, val in test.items():
        exec(f"{var} = {val}")

    # Devuelve False/True en función del resultado de la evaluación
    return eval(eq)

def eval_python_var(eq: str, test: dict) :

    # Todo: reemplazar los simbolos &|! de pyeda por and, or y not en python
    eq = eq.replace("&", "and")
    eq = eq.replace("|", "or")
    eq = eq.replace("!", "not")

    for var, val in test.items():
        exec(f"{var} = {val}")

    # Devuelve False/True en función del resultado de la evaluación
    return eval(eq)

def comprob_valores_diferentes(listT, listaF):
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

    if len(sys.argv) > 2 :
        eq = sys.argv[1]
        testList = sys.argv[2]
    else:
        print("Argumento no valido")
        sys.exit(1)

    #"[{'a': 1, 'b': 2}]" formato lista de tests
    data = eval(testList)

    # La condición que se desea estudiar es eq.
    #eq1 = "(a > 10) & (b < 9)" formato de la condición
    trueList = []
    falseList = []
    variables = set() #cjto de todas las variables

    for test in data:
        variables.update(test.keys())
        #print(eval_python(eq,test)) print de la evaluacion de eq para cada test
        if eval_python(eq, test):
            trueList.append(test) #lista de tests True
        else:
            falseList.append(test) #lista de tests False

    nTests = len(data)
    nVar = len(variables)
    nTestsAdecuado: bool

    if(nVar+1 <= nTests and nTests <= 2*nVar):
        nTestsAdecuado = True
    else:
        nTestsAdecuado = False

    print("Cumple con MC/DC: " + str(comprob_valores_diferentes(trueList, falseList) and nTestsAdecuado))