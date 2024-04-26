import sys
from random import Random

from mcdc_test_generator.mcdc_testcase.bdd_engine.path_search import LongestMayMerge, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser
from mcdc_testcase.generator import solve

if __name__ == '__main__':

    if len(sys.argv) > 1 :
        eq = sys.argv[1]
    else:
        print("Argumento no valido")
        sys.exit(1)

    reuse_h = LongestMayMerge
    rng = Random(100)

    result = solve(eq, reuse_h, rng)
    print(result)