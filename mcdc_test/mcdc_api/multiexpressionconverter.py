from flask import request, jsonify
from flask_restful import Resource, abort
from random import Random

from mcdc_test.setta_extension_minimal import solve
from random import Random

from helpers.fnodeconverter import convert_fnode_to_string
from helpers.pathsearchenum import enum_map


##Multiple Expressions will be taken as an input --> Reduce RoundTrips
class Multi_Expression_Converter(Resource):
    def __init__(self):
        self.parser_multi_expression = parser_base.copy()
        self.parser_multi_expression.add_argument('EXPRESSION', action='append', type=str, required=True) ###convert this to list input
        super(Multi_Expression_Converter, self).__init__()
    
        ##For Documentation how to access the endpoint
    def get(self):
        return jsonify({
            'The body needs the following': {
                'PATHSEARCH': 'One of the following options: ' + str(enum_map.keys()), # Convert keys to string
                'RANDOM': 'Any positive integer',
                'EXPRESSION': 'A non-empty list of boolean expressions'
            }})   
        
    def post(self):
        args = self.parser_multi_expression.parse_args(strict=True)
        try:
            reuse_h = enum_map[args['PATHSEARCH']]
        except KeyError:
            logger.error("Invalid PATHSEARCH value: %s. From IP: %s", args['PATHSEARCH'], request.remote_addr)
            print(type(', '.join(enum_map.keys())))
            #abort(400, message="Invalid PATHSEARCH value. The following options exist: " + ', '.join(enum_map.keys()))
        if args['RANDOM'] < 0 or type(args['RANDOM']) != int:
            logger.error("Invalid RANDOM value: %s. From IP: %s", args['RANDOM'], request.remote_addr)
            abort(400, message="RANDOM value must be non-negative")
        rng = Random(args['RANDOM'])
        eqs = args['EXPRESSION']
        if (not eqs or len(eqs) == 0):
            logger.error("Invalid EXPRESSION. No Expression provided. From IP: %s", request.remote_addr)
            abort(400, message="No expression was provided")
        try:
            final_result:list = []
            for eq in eqs:
                result = solve(eq, reuse_h.value, rng)
                output_ready = convert_fnode_to_string(result)
                final_result.append(output_ready)
            return jsonify(final_result)
        except Exception as ex:
            logger.critical("An unexpected error occurred. Exception: " + str(ex))
            abort(500, message="An unexpected error occurred. Please try again later.")