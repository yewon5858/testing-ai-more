from setta_extension_minimal import solve
from pathsearch import LongestMayMerge
from random import Random

if __name__ == '__main__':

    reuse_h = LongestMayMerge
    a = int
    b = int

# La condición que se desea estudiar es eq.
    eq = (a > 10) & (b < 9)
    
    
    
    
    rng = Random(100)

    result = solve(eq, reuse_h, rng)
    print(result)