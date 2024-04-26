# -*- coding: utf-8 -*-
# apt-get install gcc
# apt-get install make
# apt-get install libgmp3-dev
# pip install pysmt
# pysmt-install --check
# pysmt-install --msat

from mcdc_testcase.engine.path_search import run_one_pathsearch
from pyeda.boolalg.bdd import expr2bdd
from pyeda.boolalg.expr import expr
from random import Random
import string

from pysmt.parsing import parse
from pysmt.typing import INT, BOOL
from pysmt.shortcuts import Symbol, Not, Solver

def solve(eq, reuse_h, rng, path_to_test = None):
    # type: (str, callable, Random, _) -> list

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
            if val == 1:
                new_test.append(decrypt_dict[key])
            else:
                # val == 0
                new_test.append(Not(decrypt_dict[key]))

        print(f"Test {new_test} fullfils {test}")
        return new_test

    def sat_solve(test, variables):
        # type: (iter, iter) -> dict
        # test = iter of pysmt.fnode.FNode = [1 <= h, h >= 10, ...]
        solution = dict()
        with Solver(logic="QF_LIA") as solver:
            for atom in test:
                print(f"Adding assertion {atom} from {test}")
                solver.add_assertion(atom)
                # atom_vars = atom.get_free_variables()
            solver_solve = solver.solve()
            print(f"Solving {test} with {solver_solve}")
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
    # Let's assume that all the variables are Integers and are named with with alphabet letters
    int_variables = [Symbol(s, INT) for s in string.ascii_lowercase]  # ['a', 'b', 'c', ...]
    formula = parse(equation)

    # Replace atoms by symbolic variables.
    # E.g.:
    #  - "(1 <= h)" by "a0"
    #  - "(10 >= h)" by "a1"

    atoms = list(formula.get_atoms())
    print(f"Numerical atoms: {atoms}")

    # Encrypt
    # formula           = (1 <= h) & (h <= 10)
    # abstract_formula  = a0 & a1
    bool_variables = set(Symbol("a" + str(i), BOOL) for (i, a) in enumerate(atoms))
    encrypt_dict = dict(zip(atoms, bool_variables))
    abstract_formula = formula.substitute(encrypt_dict)
    print(f"Boolean atoms: {abstract_formula.get_atoms()}")

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
    print(f"Decrypt dictionary: {decrypt_dict}")
    print(f"Boolean test cases: {uniq_test}")

    solutions = []
    for test in uniq_test:
        # test = {"a0": 0, "a1": 0}
        # print(f"Decrypting {test}")
        test = preprocess(test, decrypt_dict)
        # print(f"Into {test}")

        if path_to_test is not None:
            print("test: ", test, " path_to_test: ", path_to_test)
        
        # test = {Not(1 <= h), Not(h <= 10)}
        sol = sat_solve(test, formula.get_free_variables())
        if sol == 'UNSAT':
            return []
        solutions.append(sol)

    return solutions
