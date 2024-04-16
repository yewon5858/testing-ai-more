from setta_extension_minimal import solve
from pathsearch import LongestMayMerge
from random import Random

if __name__ == '__main__':

    reuse_h = LongestMayMerge
    eq = '(a > 10) & (b < 9)'
    rng = Random(100)

    result = solve(eq, reuse_h, rng)
    print(result)

# (x > 0) & (y < 10)

# (x = 0) & (y = 0)

# (x >= 0) & (y >= 0) & (x + y <= 100)

# (w >= x) & (x = y) & (y >= z)

# ((x > 0) & (y < 0)) & ((x < 0) & (y > 0))
