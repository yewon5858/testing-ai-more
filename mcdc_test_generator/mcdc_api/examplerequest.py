from flask import jsonify
from flask_restful import Resource, abort
from random import Random

from mcdc_testcase.generator.generator import solve
from mcdc_testcase.bdd_engine.path_search import LongestMayMerge
from mcdc_api.helpers.fnodeconverter import convert_fnode_to_string
from random import Random

class Example_Request(Resource):
    def get(self):
        try: 
            reuse_h = LongestMayMerge
            eq = '(a > 10) and (b < 9)' # and --> &
            rng = Random(100)
            result = solve(eq, reuse_h, rng)
            converted_list = convert_fnode_to_string(result)
            return jsonify(converted_list)
        except Exception as ex:
            #TODO: Log here
            abort(500, message="An unexpected error occurred. Please try again later.")