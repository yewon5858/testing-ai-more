from flask import request, jsonify
from flask_restful import Resource,abort
from random import Random

from mcdc_testcase.generator.generator import solve
from random import Random

from mcdc_api.helpers.fnodeconverter import convert_fnode_to_string
from mcdc_api.helpers.pathsearchenum import enum_map
from mcdc_api.parser.baseparser import parser_base
import logging

logger = logging.getLogger(__name__)

##Single Expressions will be taken as an input
class Single_Expression_Converter(Resource):
    def __init__(self):
        self.parser_single_expression = parser_base.copy()
        self.parser_single_expression.add_argument('EXPRESSION', type=str, required=True)
        super(Single_Expression_Converter, self).__init__()
    
    ##For Documentation how to access the endpoint
    def get(self):
        result = [
            {'The body needs the following': {
                'PATHSEARCH': 'One of the following options: ' + str(enum_map.keys()), # Convert keys to string
                'RANDOM': 'Any positive integer',
                'EXPRESSION': 'A non-empty boolean expressions'
            }}, 
            {'Example': {
                'PATHSEARCH': 'LongestMayMerge',
                'RANDOM': '5',
                'EXPRESSION': 'a > 10'
            }}
        ]
        return jsonify(result) 
 
    def post(self):
        args = self.parser_single_expression.parse_args(strict=True)
        try:
            reuse_h = enum_map[args['PATHSEARCH']]
        except KeyError:
            logger.error("Invalid PATHSEARCH value: %s. From IP: %s", args['PATHSEARCH'], request.remote_addr)
            abort(400, message="Invalid PATHSEARCH value. The following options exist: " + ', '.join(enum_map.keys()))
        if args['RANDOM'] < 0 or type(args['RANDOM']) != int:
            logger.error("Invalid RANDOM value: %s. From IP: %s", args['RANDOM'], request.remote_addr)
            abort(400, message="RANDOM value must be non-negative")
        rng = Random(args['RANDOM'])
        eq = args['EXPRESSION']
        if (not eq):
            logger.error("Invalid EXPRESSION. No Expression provided. From IP: %s", request.remote_addr)
            abort(400, message="No expression was provided")
        try: 
            result = solve(eq, reuse_h.value, rng)
            output_ready = convert_fnode_to_string(result)
            return jsonify(output_ready)
        except Exception as ex:
            logger.critical("An unexpected error occurred. Exception: " + str(ex))
            abort(500, message="An unexpected error occurred. Please try again later.")
