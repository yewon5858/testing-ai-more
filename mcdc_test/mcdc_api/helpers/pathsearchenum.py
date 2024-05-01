from enum import Enum
from mcdc_testcase.bdd_engine.path_search import LongestMayMerge, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser

class MyEnum(Enum):
    LONGEST_MAY_MERGE = LongestMayMerge
    LONGEST_PATH = LongestPath
    LONGEST_BOOL = LongestBool
    LONGEST_BOOL_MAY = LongestBoolMay
    BETTER_SIZE = BetterSize
    RANDOM_REUSER = RandomReuser
    
enum_map = {
    'LongestMayMerge': MyEnum.LONGEST_MAY_MERGE,
    'LongestPath': MyEnum.LONGEST_PATH,
    'LongestBool': MyEnum.LONGEST_BOOL,
    'LongestBoolMay': MyEnum.LONGEST_BOOL_MAY,
    'BetterSize': MyEnum.BETTER_SIZE,
    'RandomReuser': MyEnum.RANDOM_REUSER
}
