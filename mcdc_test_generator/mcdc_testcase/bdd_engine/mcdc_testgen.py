from itertools import chain, tee

from pyeda.boolalg.bdd import (_iter_all_paths, _path2point, BDDNode, BDDNODEZERO, BDDNODEONE, BDDVariable,
                               BinaryDecisionDiagram)

from mcdc_testcase.bdd_engine.mcdc_helpers import *
from mcdc_testcase.bdd_engine import logger


def equal(bddnode, condition):
    # type: (BDDNode, BDDVariable) -> bool
    return bddnode.root == condition.uniqid


def path_via_node(fr, vc, to, conditions):
    # type: (BDDNode, BDDNode, BDDNode, iter) -> list
    # list of paths from the root to terminal node via intermediate node vc

    # temp_list_of_paths = list(_iter_all_paths(fr, to))
    # list_of_paths = [path for path in temp_list_of_paths if vc in path]

    list_of_paths = [uniformize(_path2point(path), conditions)
                     for path in _iter_all_paths(fr, to) if vc in path]
    return list_of_paths


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

            paths_to_zero: list
            paths_to_one: list

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


def paths_from_pair_is_reused(tcs, pair):
    # type: (dict, (dict, dict)) -> bool
    """Each path occurs only once, exactly for the pair we're looking at,
       hence sum of reuse is larger than 2 (1 each).
    """
    r0 = calc_reuse(pair[0], tcs)
    r1 = calc_reuse(pair[1], tcs)
    return r0 + r1 > 2
