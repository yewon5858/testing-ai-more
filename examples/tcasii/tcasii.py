# The decisions considered here are the Traffic Alert and Collision Avoidance System (TCAS II) benchmarks used in avionics.
# The were presented in [https://doi.org/10.1002/qre.1934, https://link.springer.com/chapter/10.1007/978-3-319-99130-6_9, https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=286420,https://dl.acm.org/doi/pdf/10.1145/3167132.3167335 ]


from pyeda.boolalg.bdd import bddvar, expr2bdd, bdd2expr, BinaryDecisionDiagram, BDDZERO, BDDONE
from pyeda.inter import *

# Logging configuration
import logging
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


a, b, c, d, e, f, g, h, i, j, k, l, m, n = map(bddvar, 'abcdefghijklmn')
D1 = a & (~b | ~c) & d | e
D2 = ~(a & b) & ((d & ~e & ~f) | (~d & e & ~f) | ~d & ~e & ~f) & (
        (a & c & (d | e) & h) | (a & (d | e) & ~h) | (b & (e | f)))
D3 = ~(c & d) & (~e & f & ~g & ~a & (b & c | ~b & d))
D4 = a & c & (d | e) & h | a & (d | e) & ~h | b & (e | f)
D5 = ~e & f & ~g & ~a & (b & c | ~b & d)
D6 = (~a & b | a & ~b) & ~(c & d) & ~(g & h) & ((a & c | b & d) & e & (f & g | ~f & h))
D7 = (a & c | b & d) & e & (f & g | ~f & h)
D8 = (a & ((c | d | e) & g | a & f | c & (f | g | h | i)) | (a | b) & (c | d | e) & i) & ~(a & b) & ~(c & d) & ~(
        c & e) & ~(d & e) & ~(f & g) & ~(f & h) & ~(f & i) & ~(g & h) & ~(h & i)
D9 = a & (~b | ~c | b & c & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k)) | f
D10 = a & ((c | d | e) & g | a & f | c & (f | g | h | i)) & (a | b) & (c | d | e) & i
D11 = (~a & b | a & ~b) & ~(c & d) & ~(g & h) & ~(j & k) & (a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k))
D12 = (a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k)) & (a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k))
D13 = (~a & b | a & ~b) & ~(c & d) & (f & ~g & ~h | ~f & g & ~h | ~f & ~g & ~h) & (~(j & k)) & (
        (a & c | b & d) & e & (f | (i & (g & j | h & k))))
D14 = (a & c | b & d) & e & (f | (i & (g & j | h & k)))
D15 = (a & (~d | ~e | d & e & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k)) | ~(
        ~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k) & (b | c & ~m | f)) & (
              a & ~b & ~c | ~a & b & ~c | ~a & ~b & c)
D16 = a | b | c | ~c & ~d & e & f & ~g & ~h | i & (j | k) & l
D17 = a & (~d | ~e | d & e & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & ~k)) | ~(
        f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k) & (b | c & ~m | f)
D18 = a & ~b & ~c & ~d & ~e & f & (g | ~g & (h | i)) & ~(j & k | ~j & l | m)
D19 = a & ~b & ~c & (~f & (g | ~f & (h | i))) | f & (g | ~g & (h | i) & ~d & ~e) & ~(j & k | ~j & l & ~m)
D20 = a & ~b & ~c & (~f & (g | ~g & (h | i))) & (~e & ~n | d) | ~n & (j & k | ~j & l & ~m)


# D2 = "~(a & b) & ((d & ~e & ~f) | (~d & e & ~f) | ~d & ~e & ~f) & ((a & c & (d | e) & h) | (a & (d | e) & ~h) | (b & (e | f)))"
# D4 = "a & c & (d | e) & h | a & (d | e) & ~h | b & (e | f)"
# D6 = "(~a & b | a & ~b) & ~(c & d) & ~(g & h) & ((a & c | b & d) & e & (f & g | ~f & h))"
# D8 = "(a & ((c | d | e) & g | a & f | c & (f | g | h | i)) | (a | b) & (c | d | e) & i) & ~(a & b) & ~(c & d)& ~(c & e) & ~(d & e) & ~(f & g) & ~(f & h) & ~(f & i) & ~(g & h) & ~(h & i)"
# D9 = "a & (~b | ~c | b & c & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k)) | f"
# D11 = "(~a & b | a & ~b) & ~(c&d) & ~(g&h) & ~(j & k)&(a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k))"
# D12 = "(a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k)) & (a & c | b & d) & e & (i | ~g & ~k | ~j & (~h | ~k))"
# D13 = "(~a & b | a & ~b) & ~(c & d) & (f & ~g & ~h | ~f & g & ~h | ~f & ~g & ~h) & (~(j & k)) & ((a & c | b & d) & e & (f | (i & (g & j | h & k))))"
# D15 = "(a & (~d | ~e | d & e & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & k)) | ~(~f & g & h & ~i | ~g & h & i)& ~(~f & g & l & k | ~g & ~i & k) & (b | c & ~m | f)) & (a & ~b & ~c | ~a & b & ~c | ~a & ~b & c)"
# D17 = "a & (~d | ~e | d & e & ~(~f & g & h & ~i | ~g & h & i) & ~(~f & g & l & k | ~g & ~i & ~k)) | ~(f & g & h & ~i | ~g & h & i) & ~( ~f & g & l & k | ~g & ~i & k) & (b | c & ~m | f)"

def makeLarge(f):
    l = len(f.inputs)
    vars = list(f.inputs)
    X = bddvars('X', l)
    Y = bddvars('Y', l)
    Z = bddvars('Z', l)
    fx = f.compose({vars[i]: X[i] for i in range(l)})
    # fy = f.compose({vars[i]: Y[i] for i in range(l)})
    # fz = f.compose({vars[i]: Z[i] for i in range(l)})
    Dlarge = f & fx  # & fy & fz
    return Dlarge


# TODO: example for "larger" formula
# These take too long with sorting:
# tcas = [makeLarge(D15), makeLarge(D17), makeLarge(D19), makeLarge(D20)]
tcas = [D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20]
# tcas_dict = {expr2bdd(expr(D_i)): D_i for D_i in tcas}
# tcas_dict_ordered = SortedDict({D_i: expr2bdd(expr(D_i)) for D_i in tcas})

tcas1 = [D2, D8, D9, D13, D15, D17, D19]  # failed the first test
tcas2 = [D6, D11, D19]  # passed with Order : d, e, f, g, h, i, j, k, l, m, n, a, b, c = map(bddvar, 'defghijklmnabc')
tcas3 = [D11, D12, D13]  # passed with Order : i, j, k, l, m, n, a, b, c, d, e, f, g, h = map(bddvar, 'ijklmnabcdefgh')
tcas4 = [D4, D6, D9,
         D11]  # passed with Order : f, i, j, k, l, m, n, a, b, c, d, e, g, h = map(bddvar, 'fijklmnabcdegh') and In general 7 failed, 13 passed in 0.75s
tcas5 = [D4, D9, D12]  # passed with Order : a, d, c, e, i, j, b, f, g, m, n, k, h, l = map(bddvar, 'adceijbfgmnkhl')
tcas6 = [D15, D17]  #

tcas_names = ["D" + str(i) for i in range(1, 21)]
tcas_num_cond = [5, 7, 7, 7, 7, 8, 8, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 14]
# tcas_dict_name = {ds_i: value for ds_i, value in zip(tcas_names,  tcas_num_cond)}
tcas_dict = dict(zip(tcas, tcas_num_cond))


def test_to_str(test):
    # type: (dict) -> str
    # print(sorted(test))
    # return "".join(str(c) for c in test.values())
    return "".join(str(test[c]) if test[c] is not None else '?' for c in sorted(test))

