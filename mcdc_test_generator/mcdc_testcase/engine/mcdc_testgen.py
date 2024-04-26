from multiprocessing import Pool, Manager
from math import factorial
from random import randint, seed, Random
import sys
import time

from itertools import permutations, repeat, product, chain, tee
from sortedcontainers import SortedList

from pyeda.boolalg.bdd import expr2bdd, bdd2expr, _iter_all_paths, _path2point, BDDNode, BDDNODEZERO, BDDNODEONE, \
    BDDVariable, BinaryDecisionDiagram
from pyeda.boolalg.expr import expr
from pyeda.inter import bddvars

from mcdc_testcase.engine.mcdc_helpers import *
from mcdc_testcase.engine import logger


# noinspection PyUnreachableCode
def no_mechanism(_f, _h):
    assert False, "MP maybe not initialized correctly?"
    exit(1)


# MP: Things that need to be synced.
# We use `None` to provoke a type-error if we ever get this wrong.
# See `init_globals()`.
# How many rounds:
maxRounds = None
rngRounds = None
mechanism = no_mechanism


def path_via_node(fr, vc, to, conditions):
    # type: (BDDNode, BDDNode, BDDNode, iter) -> list
    # list of paths from the root to terminal node via intermediate node vc

    # temp_list_of_paths = list(_iter_all_paths(fr, to))
    # list_of_paths = [path for path in temp_list_of_paths if vc in path]

    list_of_paths = [uniformize(_path2point(path), conditions)
                     for path in _iter_all_paths(fr, to) if vc in path]
    return list_of_paths


def equal(bddnode, condition):
    # type: (BDDNode, BDDVariable) -> bool
    return bddnode.root == condition.uniqid


def satisfy_mcdc(f, heuristic):
    # type: (BinaryDecisionDiagram, callable) -> (dict, int, list)

    def select_paths_bdd(f):
        # type: (BinaryDecisionDiagram) -> dict

        # set that will store the paths selected from the BDD in tuple format,
        # i.e., psi = set(elem_1, elem_2,...)
        # where:
        # elem_1 != elem_2, and
        # elem_i = (bddnode_1, bddnode_2, ....)
        # psi = set()

        # Dictionary that translates a path in tuple format:
        # path = (bddnode_1, ..., bddnode_n)
        # into:
        # path = {a: 1, ..., c: None}
        # The use of a dictionary guarantees singleton references to the same path, which is useful when instantiating
        # None values in the path (e.g., c: None) and the path is shared by several case of studies
        tuple_2_dict = dict()

        # test_case is a dictionary of pairs
        test_case = dict()

        # Format:
        # test_case[cond] = (path_zero, path_one)
        # where:
        # c is the condition, and
        # path_zero/path_one go to terminal node 0/1 in the BDD respectively

        root = f.node
        bdd_nodes = list(f.dfs_preorder())

        # TODO: could be adjustable.
        conditions = sorted(f.support, key=lambda c: c.uniqid)
        for c in conditions:
            logger.debug("\n")
            logger.debug("current variable: {0}".format(c))
            logger.debug("______________________________________")

            paths_to_zero = []
            paths_to_one = []

            c_nodes = [node for node in bdd_nodes if equal(node, c)]
            # TODO: Could be interesting to make the following loop a generator.
            # for vc in c_nodes:
            #     # Paths to terminal nodes that are sorted by length
            #     # Note: Search for the shortest paths_to_zero & paths_to_one for all c_nodes
            #     # If several paths have the same length, then choose the one with highest reuse factor
            #     # Paths start from the root node in the BDD, and they must explicitly cross node vc (which has cond c)
            #     paths_to_zero += path_via_node(root, vc, BDDNODEZERO, conditions)
            #     paths_to_one += path_via_node(root, vc, BDDNODEONE, conditions)

            # WARNING: iterators are exhausted once they are read
            paths_to_zero, paths_to_zero_log = tee(
                chain.from_iterable(path_via_node(root, vc, BDDNODEZERO, conditions) for vc in c_nodes))
            paths_to_one, paths_to_one_log = tee(
                chain.from_iterable(path_via_node(root, vc, BDDNODEONE, conditions) for vc in c_nodes))

            logger.debug("paths_to_zero:\t{0}".format(paths_to_zero_log))
            logger.debug("paths_to_one:\t{0}".format(paths_to_one_log))

            # paths_to_zero = {P0, P1}, and
            # paths_to_one = {P2, P3} with
            # P0 = (bddnode_1, ..., bddnode_n),
            # P1 = (bddnode_1, ..., bddnode_m), and n != m

            logger.debug("sorting...")
            fcp_list = heuristic(test_case, c, paths_to_zero, paths_to_one)
            logger.debug("# paths differing in condition {0}: {1}\n".format(c, len(fcp_list)))
            # logger.debug(list(fcp_list))

            if len(fcp_list) == 0:
                print("Warning: suspecting masking(?)")
                assert False
            else:
                # Choose the first pair = (path_zero, path_one) that satisfy the restrictions, if any
                (path_zero, path_one) = fcp_list[0]

                # Assign test cases path_zero and path_one to condition c
                p0, p1 = Path(dict(path_zero)), Path(dict(path_one))
                # TODO: seems to be missing a merge here; needs a variation on
                #  p0 = merge(p0,p1), p1 = merge(p1,p0)
                test_case[c] = (p0, p1)
                logger.debug("test_case[{0}] = ({1})".format(c, test_case[c]))

                # continue with the next condition

        # TODO: If code breaks, indent code until here

        # test_case[a] = ({a: 0, b: None, c: 0}, {a: 1, b: 1, c: None})
        # test_case[b] = ({a: 1, b: 0, c: 0}, {a: 1, b: 1, c: None})
        # test_case[c] = ({a: 0, b: None, c: 0}, {a: 0, b: None, c: 1})

        return test_case

    # First loop
    # Select pair of paths p0/p1 from the BDD
    # test_case, tuple_2_dict = select_paths_bdd(self)

    test_case = select_paths_bdd(f)

    # psi = compact_truth_table(test_case, tuple_2_dict)
    # psi[p0] = {a, c}, where tuple_2_dict(p0) = {a: 0, b: None, c: 0}
    # psi[p1] = {b},    where tuple_2_dict(p1) = {a: 1, b: 1, c: None}

    # Second loop
    # Instantiate '?' for each path in test_case
    test_case = instantiate(test_case)
    replace_final_question_marks(test_case)
    uniq_test = unique_tests(test_case)
    # TODO: num_test_cases is kind of redundant
    num_test_cases = len(uniq_test)
    return test_case, num_test_cases, uniq_test


def init_globals(_runs, _tcas, _tcas_num_cond, _mechanism):
    # type: (int, dict, int, callable) -> None
    # https://stackoverflow.com/a/28862472/60462
    global maxRounds
    global tcas
    global tcas_num_cond
    global mechanism
    maxRounds = _runs
    sys.setrecursionlimit(1500)  # Required e.g. for makeLarge(D15)
    tcas = list(map(lambda x: expr2bdd(expr(x)), _tcas))
    tcas_num_cond = _tcas_num_cond
    mechanism = _mechanism


def sample_one(l):
    # type: (int) -> list
    have = []
    while len(have) < l:
        j = randint(0, l - 1)
        if j not in have:
            have.append(j)
    return have


def gen_perm(l):
    # type: (int) -> list
    global maxRounds
    return gen_perm_max(maxRounds, l)


def gen_perm_max(maxRounds, l):
    # type: (int, int) -> list
    # If you're asking for more rounds than we have permutations,
    #   we'll give them all to you.
    if maxRounds >= factorial(l):
        # Still hating MP with a vengeance. Force deep eval.
        return list(map(lambda p: list(p), permutations(range(l))))
    # Otherwise, we'll sample sloppily:
    perms = []
    for _ in range(maxRounds):
        # `append`/` += [i]` seems to be the efficient choice here.
        perms.append(sample_one(l))  # ignore duplicates for now XXX
    return perms


# Def. as per paper
def calc_reuse(path, test_case_pairs):
    # type: (dict, dict) -> int
    # for p in test_case.values():
    #   print("reuse:\t{0}".format(p))
    # tcs = map(lambda p: (merge_Maybe(conditions,path,p[0]),merge_Maybe(conditions, path, p[1])), test_case.values())
    tcs = filter(lambda p: p[0] == path or p[1] == path, test_case_pairs.values())
    return len(list(tcs))


def calc_may_reuse(path, test_case_pairs):
    # type: (dict, dict) -> int
    tcs = filter(lambda p: merge_Maybe_except_c_bool(None, path, p[0]) is not None
                           or merge_Maybe_except_c_bool(None, path, p[1]) is not None, test_case_pairs.values())
    return len(list(tcs))


def hi_reuse_short_path(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return SortedList(paths, key=lambda path: (-calc_reuse(path[0], tcs) - calc_reuse(path[1], tcs),
                                               # highest reuse/shortest path
                                               size(path[0]) + size(path[1])))


def hi_reuse_long_path(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return SortedList(paths, key=lambda path: (-calc_reuse(path[0], tcs) - calc_reuse(path[1], tcs),
                                               # highest reuse/longest path
                                               -size(path[0]) - size(path[1])))


def hi_reuse_long_merged_path(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return SortedList(paths, key=lambda path: (-calc_may_reuse(path[0], tcs) - calc_may_reuse(path[1], tcs),
                                               # highest reuse/longest path
                                               -size(path[0]) - size(path[1])))


def h3(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    # Not "very good", e.g. can't find optimal solution in general, here D3:
    #    Num_Cond=7: min=8, |p|=5040, [(9, 5040)]
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return [paths.__next__()]


def h3s(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    # Try to improve over H3 by pre-sorting. Ideally, we'd want to build the product "diagonally".
    # Shortest path/highest reuse
    # Still "meh" (of course[*]) as in "does not find n+1 at all": Num_Cond=7: min=8, |p|=5040, [(9, 5040)]
    # Re: [*] "of course" -- or is it? Of course ORDER of solutions plays a role, since we're only
    #    taking the first one once we return results here!
    paths_to_zero = SortedList(paths_to_zero, key=lambda path: (size(path), -calc_reuse(path, tcs)))
    paths_to_one = SortedList(paths_to_one, key=lambda path: (size(path), -calc_reuse(path, tcs)))
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return [paths.__next__()]


def h3h(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    # highest reuse/shortest path
    # Still fails D3
    paths_to_zero = SortedList(paths_to_zero, key=lambda path: (-calc_reuse(path, tcs), size(path)))
    paths_to_one = SortedList(paths_to_one, key=lambda path: (-calc_reuse(path, tcs), size(path)))
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = ((path_zero, path_one) for (path_zero, path_one) in cartesian_product
             if xor(path_zero, path_one, c))
    return [paths.__next__()]


def h3hl(tcs, c, paths_to_zero, paths_to_one):
    # type: (dict, BDDVariable, list, list) -> list
    # highest reuse/longest path
    # Still fails D3
    paths_to_zero = SortedList(paths_to_zero, key=lambda path: (-calc_reuse(path, tcs), -size(path)))
    paths_to_one = SortedList(paths_to_one, key=lambda path: (-calc_reuse(path, tcs), -size(path)))
    cartesian_product = product(paths_to_zero, paths_to_one)

    # Choose path_zero and path_one that only differs on condition c
    paths = filter(lambda p: xor(p[0], p[1], c), cartesian_product)
    return [paths.__next__()]


def paths_from_pair_is_reused(tcs, pair):
    # type: (dict, (dict, dict)) -> bool
    """Each path occurs only once, exactly for the pair we're looking at,
       hence sum of reuse is larger than 2 (1 each).
    """
    r0 = calc_reuse(pair[0], tcs)
    r1 = calc_reuse(pair[1], tcs)
    return r0 + r1 > 2
