from pysmt.shortcuts import *
from pysmt.typing import *
from pysmt.parsing import parse
from pysmt.fnode import FNode


class oSolver:
    def __init__(self):
        self.variables = []
        self.constraints = []
        self.solver = Solver(logic="QF_LIA")
        self.formula = And()

    def addVariable(self, var):
        var_symbol = Symbol(var, INT)
        if var_symbol not in self.variables: self.variables.append(var_symbol)
        #self.formula = self.formula.And(Equals(var, Int(0)))

    def addConstraint(self, c):
        self.formula = self.formula.And(c)
        self.constraints.append(str(c))

    def reset(self):
        self.formula = And()
        self.variables = []
        self.constraints = []
        self.solver = Solver(logic="QF_LIA")

    def solve(self):
        ret = {}
        for i in self.variables:
            print(i)
        
        print("formula: ", self.formula)

        self.solver.add_assertion(self.formula)

        for i in self.constraints:
            print(i)

        if self.solver.solve():
            for v in self.variables:
                print(f"{v} = {self.solver.get_value(v)}")
                ret[v]=self.solver.get_value(v)
        else:
            print("No solution found")
        self.reset()
        return ret
        

