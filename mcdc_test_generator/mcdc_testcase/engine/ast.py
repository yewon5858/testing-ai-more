# -*- coding: utf-8 -*-
import ast
import random as rng

from pysmt.shortcuts import Symbol, LE, GE, LT, GT, Int, And, Equals, Plus, Solver, serialize, Not
from pysmt.typing import INT

from pyeda.boolalg.bdd import expr2bdd
from pyeda.boolalg.expr import expr

from pathsearch import run_one_pathsearch, LongestMayMerge
from sat_solver.cSolver import oSolver


def foo(msg):
    # tokenizar el asunto
    tree = ast.parse(msg)
    expr = ast.unparse(tree)

    # print("AST: ", ast.dump(tree))
    res = {}

    i = 0
    for node in ast.walk(tree):
        # print("NODE: ", i, " ", node)
        # print(node.__dict__)
        # print(node.__dict__.keys())
        i += 1
        for x in ast.iter_child_nodes(node):
            # print(x)
            if type(x) == ast.Expr:
                continue
                # print(ast.walk(x))
            elif type(x) == ast.Compare:
                comp = ast.unparse(x).replace("\n", '')
                token = '___expname' + str(len(res.keys()))
                res[token] = comp
                expr = expr.replace(comp, token)

            elif type(x) == ast.BoolOp:
                # handleBool(x)
                continue
    print(res, expr)
    return res, expr


def handleBool(x):
    res = []
    band = False
    bor = False
    i = 0
    for a in ast.iter_child_nodes(x):
        # and, or
        print("bol ", a)
        if (type(a) == ast.And):
            band = True
            continue
        else:
            res.append(a)

    if (band):
        handleAnd(res)
    return res


def handleAnd(res):
    print(res)
    for i in res:
        if (type(i) == ast.Name):
            # We are in at and and the variable is a boolean...
            continue
        elif (type(i) == ast.Compare):
            # We need to tokenize the expression, only if both members are names
            print("aaa ", i.left, i)


def handle_post_request(expression: str, token_dict: dict):
    parsed_msg = expression.replace(" and ", " & ").replace(" or ", " | ").replace("not ", "~").replace("==", "=")

    print("parsed msg: ", parsed_msg)
    f = expr2bdd(expr(parsed_msg))
    hs = [LongestMayMerge]  # , LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser]


    test_case_pairs, num_test_cases, uniq_test = run_one_pathsearch(f, hs[0], rng)

    # print("ntests: ", num_test_cases, "\ntest_case_pairs tests: ", test_case_pairs)

    # print("ntests: ", num_test_cases, "\nuniq tests: ", uniq_test)

    print(str(uniq_test).replace(": 1", " = true").replace(": 0", " = false"))
    uniq_test_detokenized = []

    for index, test in enumerate(uniq_test):
        # Añadimos un diccionario vacio
        uniq_test_detokenized.append({})
        exp_to_solve = ""
        for k in test.keys():
            if str(k) in token_dict.keys():
                print("test: ", test)
                uniq_test_detokenized[index][token_dict[str(k)]] = test[k]
                if test[k] == 0:
                    math_exp = "!" + str(token_dict[str(k)])
                else:
                    math_exp = str(token_dict[str(k)])

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
            # fooo = parse(exp)
            # print(exp.get_atoms(), exp.get_free_variables())

            expr_tree = ast.parse(str(exp))

            for child in ast.iter_child_nodes(expr_tree):
                # If it is a numeric expression...
                if type(child) == ast.Expr and type(child.value) == ast.Compare:
                    comparisson = child.value
                    if (type(comparisson.left) == ast.Name and type(comparisson.comparators[0]) == ast.Name):
                        cs.addVariable(comparisson.left.id)
                        cs.addVariable(comparisson.comparators[0].id)

                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(
                                Equals(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(Not(Equals(Symbol(comparisson.left.id, INT),
                                                        Symbol(comparisson.comparators[0].id, INT))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(
                                LT(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(
                                LE(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(
                                GT(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(
                                GE(Symbol(comparisson.left.id, INT), Symbol(comparisson.comparators[0].id, INT)))


                    elif (type(comparisson.left) == ast.Constant and type(comparisson.comparators[0]) == ast.Name):
                        # cs.addVariable(comparisson.left.id)
                        cs.addVariable(comparisson.comparators[0].id)

                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(
                                Equals(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(
                                Not(Equals(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(
                                LT(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(
                                LE(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(
                                GT(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(
                                GE(Int(comparisson.left.value), Symbol(comparisson.comparators[0].id, INT)))

                    elif (type(comparisson.left) == ast.Name and type(comparisson.comparators[0]) == ast.Constant):
                        cs.addVariable(comparisson.left.id)
                        # cs.addVariable(comparisson.comparators[0].id)
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(
                                Equals(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(
                                Not(Equals(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(
                                LT(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(
                                LE(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(
                                GT(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(
                                GE(Symbol(comparisson.left.id, INT), Int(comparisson.comparators[0].value)))

                    elif (type(comparisson.left) == ast.Constant and type(comparisson.comparators[0]) == ast.Constant):
                        # cs.addVariable(comparisson.left.id)
                        # cs.addVariable(comparisson.comparators[0].id)
                        if type(comparisson.ops[0]) == ast.Eq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.NotEq and test[exp] == 0):
                            cs.addConstraint(Equals(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.NotEq and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Eq and test[exp] == 0):
                            cs.addConstraint(
                                Not(Equals(Int(comparisson.left.value), Int(comparisson.comparators[0].value))))
                        elif type(comparisson.ops[0]) == ast.Lt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.GtE and test[exp] == 0):
                            cs.addConstraint(LT(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.LtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Gt and test[exp] == 0):
                            cs.addConstraint(LE(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.Gt and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.LtE and test[exp] == 0):
                            cs.addConstraint(GT(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                        elif type(comparisson.ops[0]) == ast.GtE and test[exp] == 1 or (
                                type(comparisson.ops[0]) == ast.Lt and test[exp] == 0):
                            cs.addConstraint(GE(Int(comparisson.left.value), Int(comparisson.comparators[0].value)))
                else:
                    # If it is not we asume it is a boolean
                    expr_dict[exp] = test[exp] == 1
                    print("exp: ", exp, " val: ", test[exp])

        numeric_results = cs.solve()
        for i in numeric_results:
            expr_dict[i] = numeric_results[i]

        print(numeric_results)
        uniq_test.append(expr_dict)

    # uniq_test = no_duplicates(uniq_test)
    print(uniq_test_detokenized)
    print(uniq_test)

    return {'test_cases': str(uniq_test).replace(":", " =")}



def no_duplicates(s):
    r = []
    for i in s:
        if i not in r:
            r.append(i)
    return r


def remove_not_numeric(exp):
    return exp
