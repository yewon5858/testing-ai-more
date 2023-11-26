# -*- coding: utf-8 -*-
# apt-get install gcc
# apt-get install make
# apt-get install libgmp3-dev
# pip install pysmt
# pysmt-install --check
# pysmt-install --msat
from pysmt.shortcuts import Symbol, LE, GE, LT, GT, Int, And, Equals, Plus, Solver, serialize, Not
from pysmt.typing import INT, BOOL
from pysmt.parsing import parse
from pathsearch import run_one_pathsearch, LongestMayMerge
from pyeda.boolalg.bdd import expr2bdd
from pyeda.boolalg.expr import expr
from random import Random
import string
import sys
import ast
import copy
from paquetes.ayuda_setta.cSolver import oSolver

def solve(eq, reuse_h, rng, path_to_test = None):
    """type: (str, callable, Random) -> list"""

    def cast(uniq_test):
        # type: (list) -> iter
        # unique_tests = [{a0: 0, a1: 0}, {a0: 1, a1: 1}, ...]
        # test = {a0: 0, a1: 0} --> a0: pyeda.BDDNode

        # Convert a0 (pyeda.BDDNode) to (pysmt.FNode) via string
        new_uniq_test = []
        for test in uniq_test:
            new_test = dict()
            for key, value in test.items():
                new_test[str(key)] = value
                # yield new_test
                new_uniq_test.append(new_test)

        # new_uniq_tests = [{"a0": 0, "a1": 0}, {"a0": 1, "a1": 1}, ...]
        return new_uniq_test

    def preprocess(test, decrypt_dict):
        # type: (dict, dict) -> iter
        # test = {a0: 0, a1: 0}
        # decrypt_dict = {"a0": (1 <= h), "a1": (h <= 10)}
        # new_test = {Not(1 <= h), Not(h <= 10)}

        print("Test {0}".format(test))
        
        print("Decrypt {0}".format(decrypt_dict))
        new_test = []
        for key, val in test.items():
            if val:
                new_test.append(decrypt_dict[key])
                # yield decrypt_dict[key]
            else:
                continue
                #new_test.append(Not(decrypt_dict[key]))
                # yield Not(decrypt_dict[key])

        print("New Test {0}".format(new_test))
        return new_test

    def sat_solve(test, variables):
        # type: (iter, iter) -> dict
        # test = iter of pysmt.fnode.FNode = [1 <= h, h >= 10, ...]
        solution = dict()
        with Solver(logic="QF_LIA") as solver:
            for atom in test:
                solver.add_assertion(atom)
                # atom_vars = atom.get_free_variables()
            solver_solve = solver.solve()
            if not solver_solve:
                print("Domain is not SAT!!!")
                return 'UNSAT'
                #exit()
            if solver_solve:
                for v in variables:
                    solution[v] = solver.get_value(v)
                    # print("{0} = {1}".format(v, solution[v]))
            else:
                print("No solution found")
        print("Solution: {0}\n".format(solution))
        # solution = {h: 10, ....}
        return solution

    # Replacement of integer expressions in equation by boolean expressions:
    # Before:
    #   equation = (1 <= h) & (10 >= h)
    # After:
    #   equation = a0 & a1

    # Equation
    # equation = "(1 <= h) & (10 >= h)".lower()
    # formula = (1 <= h) & (10 >= h)
    equation = eq.lower()

    # Declare variables
    variables = [Symbol(s, INT) for s in string.ascii_lowercase] # ['a', 'b', 'c', ...]
    formula = parse(equation)
    # Replace atoms by symbolic variables.
    # E.g.:
    #  - "(1 <= h)" by "a0"
    #  - "(10 >= h)" by "a1"

    atoms = list(formula.get_atoms())
    bool_variables = set(Symbol("a" + str(i), BOOL) for (i, a) in enumerate(atoms))

    # Encrypt
    # formula           = (1 <= h) & (h <= 10)
    # abstract_formula  = a0 & a1
    encrypt_dict = dict(zip(atoms, bool_variables))
    abstract_formula = formula.substitute(encrypt_dict)

    # Convert formula to BDD (pyeda) format
    f = expr(abstract_formula.serialize())
    f = expr2bdd(f)

    # Call to SETTA method / Compute the test case
    # allKeys, plot_data, t_list = run_experiment((maxRounds, rngRounds), hs, tcasii.tcas, tcasii.tcas_num_cond, run_one_pathsearch)
    test_case_pairs, num_test_cases, uniq_test = run_one_pathsearch(f, reuse_h, rng)

    # Decrypt
    # abstract_formula  = a0 & a1
    # fp           = (1 <= h) & (h <= 10)
    decrypt_dict = dict(zip(bool_variables, atoms))
    decrypt_dict = {str(key): value for key, value in decrypt_dict.items()}

    # Map atoms to tests
    # unique_tests = [{a0: 0, a1: 0}, {a0: 1, a1: 1}, ...]
    uniq_test = cast(uniq_test)
    solutions = []
    for test in uniq_test:
        # test = {"a0": 0, "a1": 0}
        test = preprocess(test, decrypt_dict)
            
        if path_to_test != None:
            print("test: ", test, " path_to_test: ", path_to_test)
        
        # test = {Not(1 <= h), Not(h <= 10)}
        sol = sat_solve(test, formula.get_free_variables())
        if (sol == 'UNSAT'):
            return []
        solutions.append(sol)

    return solutions


from flask import Flask, request, jsonify

app = Flask(__name__)

from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:8889"}})

import ast
import astunparse

def foo(msg):
    #tokenizar el asunto
    tree = ast.parse(msg)
    expr = astunparse.unparse(tree)

    #print("AST: ", ast.dump(tree))
    res = {}
    childs = ast.walk(tree)
    i=0
    for node in ast.walk(tree):
        #print("NODE: ", i, " ", node)
        #print(node.__dict__)
        #print(node.__dict__.keys())
        i+=1
        for x in ast.iter_child_nodes(node):
            #print(x)
            if type(x) == ast.Expr:
                continue
                #print(ast.walk(x))
            elif type(x) == ast.Compare:
                comp = astunparse.unparse(x).replace("\n", '')
                token = '___expname'+str(len(res.keys())) 
                res[token] = comp
                expr = expr.replace(comp, token)

            elif type(x) == ast.BoolOp:
                #handleBool(x)
                continue
    print(res, expr)
    return res, expr

def handleBool(x):
    res = []
    band = False
    bor = False
    i=0
    for a in ast.iter_child_nodes(x):
        #and, or
        print("bol ", a)
        if(type(a) == ast.And):
            band = True
            continue
        else:
            res.append(a)

    if(band):
        handleAnd(res)
    return res

def handleAnd(res):
    print(res)
    for i in res:
        if(type(i) == ast.Name):
            #We are in at and and the variable is a boolean...
            continue
        elif(type(i) == ast.Compare):
            #We need to tokenize the expression, only if both members are names
            print("aaa ", i.left, i)

@app.route('/json', methods=['POST'])
def handle_post_request():
    json_data = request.json
        # Decodificar el objeto JSON
    # Obtener el valor del campo "mensaje"
    #if ('maxRounds' in json_data.keys()): maxRounds = int(json_data['maxRounds'])
    #if ('rngRounds' in json_data.keys()): rngRounds = int(json_data['rngRounds'])
    
    msg = json_data['expression']

    token_dict, expr_tokenized = foo(msg)

    parsed_msg = expr_tokenized.replace(" and ", " & ").replace(" or ", " | ").replace("not ", "~").replace("==", "=")
    
    print("parsed msg: ", parsed_msg)
    f = expr2bdd(expr(parsed_msg))
    hs = [LongestMayMerge]#, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser]

    import random as rng
    test_case_pairs, num_test_cases, uniq_test = run_one_pathsearch(f, hs[0], rng)

    #print("ntests: ", num_test_cases, "\ntest_case_pairs tests: ", test_case_pairs)

    #print("ntests: ", num_test_cases, "\nuniq tests: ", uniq_test)

    print(str(uniq_test).replace(": 1", " = true").replace(": 0", " = false"))
    uniq_test_detokenized = []
    
    for index, test in enumerate(uniq_test):
        #Añadimos un diccionario vacio
        uniq_test_detokenized.append({})
        exp_to_solve = ""
        for k in test.keys():
            if str(k) in token_dict.keys():
                print("test: ", test)
                uniq_test_detokenized[index][token_dict[str(k)]] = test[k]
                if test[k] == 0 : math_exp = "!"+str(token_dict[str(k)])
                else: math_exp = str(token_dict[str(k)])
                
                math_exp = str(token_dict[str(k)]) + " : " + str(test[k])
                exp_to_solve = str(token_dict[str(k)])

            else:
                uniq_test_detokenized[index][k] = test[k]
            
            print("exp to solve: ", exp_to_solve)

            sat_solution = no_duplicates(solve(exp_to_solve, hs[0], rng, math_exp))


    cs = oSolver()
    uniq_test = []
    for test in uniq_test_detokenized:
        print("test... ")
        expr_dict = {}
        for exp in test:
            #fooo = parse(exp)
            #print(exp.get_atoms(), exp.get_free_variables())

            expr_tree = ast.parse(str(exp))

            for child in ast.iter_child_nodes(expr_tree):
                #If it is a numeric expression...
                if type(child) == ast.Expr and type(child.value) == ast.Compare:
                    comparisson = child.value
                    if(type(comparisson.left) == ast.Name and type(comparisson.comparators[0]) == ast.Name ):
                        cs.addVariable(comparisson.left.id)
                        cs.addVariable(comparisson.comparators[0].id)
                    
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(Equals(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(Not(Equals(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(LT(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(LE(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(GT(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(GE(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))


                    elif(type(comparisson.left) == ast.Constant and type(comparisson.comparators[0]) == ast.Name ):
                        #cs.addVariable(comparisson.left.id)
                        cs.addVariable(comparisson.comparators[0].id)
                    
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(Equals(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(Not(Equals(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(LT(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(LE(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(GT(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(GE(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))

                    elif(type(comparisson.left) == ast.Name and type(comparisson.comparators[0]) == ast.Constant ):
                        cs.addVariable(comparisson.left.id)
                        #cs.addVariable(comparisson.comparators[0].id)
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(Equals(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(Not(Equals(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(LT(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(LE(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(GT(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(GE(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))

                    elif(type(comparisson.left) == ast.Constant and type(comparisson.comparators[0]) == ast.Constant ):
                        #cs.addVariable(comparisson.left.id)
                        #cs.addVariable(comparisson.comparators[0].id)
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(Equals(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(Not(Equals(Int(comparisson.left.value), Int(comparisson.comparators[0].value))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(LT(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(LE(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(GT(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(GE(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                else:
                    #If it is not we asume it is a boolean
                    expr_dict[exp] = test[exp] == 1
                    print("exp: ", exp, " val: ", test[exp])

        
        numeric_results = cs.solve()
        for i in numeric_results:
            expr_dict[i] = numeric_results[i]

        print(numeric_results)
        uniq_test.append(expr_dict)

    #uniq_test = no_duplicates(uniq_test)
    print(uniq_test_detokenized)
    print(uniq_test)

    return jsonify({'test_cases': str(uniq_test).replace(":", " =")})

@app.route('/json_pairs', methods=['POST'])
def handle_post_request2():
    json_data = request.json
        # Decodificar el objeto JSON
    print(json_data)
    # Obtener el valor del campo "mensaje"
    if (json_data.hasKey('maxRounds')): maxRounds = int(json_data['maxRounds'])
    if (json_data.hasKey('rngRounds')): rngRounds = int(json_data['rngRounds'])

    msg = json_data['expression']

    parsed_msg = msg.replace(" and ", " & ").replace(" or ", " | ").replace("not ", "~")
    
    print(parsed_msg)
    f = expr2bdd(expr(parsed_msg))
    hs = [LongestMayMerge]#, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser]

    import random as rng
    test_case_pairs, num_test_cases, uniq_test = run_one_pathsearch(f, hs[0], rng)

    print("ntests: ", num_test_cases, "\nuniq tests: ", uniq_test)

    """
    print("test case pairs: ", test_case_pairs)

    print(json_data)

    pathsearch_api(maxRounds, rngRounds)
    """

    return jsonify({'test_cases': str(test_case_pairs).replace(": 1", " = true").replace(": 0", " = false")})

def no_duplicates(s):
    r = []
    for i in s:
        if i not in r:
            r.append(i)
    return r

def remove_not_numeric(exp):
    return exp

if __name__ == '__main__':
    import random as rng
    hs = [LongestMayMerge]#, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser]

    #equation = "a <= b & (b <= a)"
    
    #s = no_duplicates(solve(equation, hs[0], rng))

    #foo("(a + 1 * 1) > 0 and b")
    

    """
    parsed_msg = equation.replace(" and ", " & ").replace(" or ", " | ").replace("not ", "~")
    
    print(parsed_msg)
    f = expr2bdd(expr(parsed_msg))
    
    test_case_pairs, num_test_cases, uniq_test = run_one_pathsearch(f, hs[0], rng)
    print(uniq_test)
    """
    app.run()


