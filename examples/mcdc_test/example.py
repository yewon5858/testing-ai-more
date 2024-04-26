from random import Random

from mcdc_testcase.bdd_engine.path_search import LongestMayMerge, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser
from mcdc_testcase.generator.generator import solve

if __name__ == '__main__':
    reuse_heuristics = [LongestMayMerge, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser]
    reuse_heuristic = reuse_heuristics[0]
    a: int
    b: int

    # La condición que se desea estudiar es eq.
    eq = "(a > 10) & (b < 9)"

    rng = Random(100)

    result = solve(eq, reuse_heuristic, rng)
    print(result)

# (x > 0) & (y < 10)

# (x = 0) & (y = 0)

# (x >= 0) & (y >= 0) & (x + y <= 100)

# (w >= x) & (x = y) & (y >= z)

# ((x > 0) & (y < 0)) & ((x < 0) & (y > 0))
