import sys
from setta_extension_minimal import solve
from pathsearch import LongestMayMerge
from random import Random

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