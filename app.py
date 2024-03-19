import logging, os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort
from random import Random
from pysmt.shortcuts import serialize
from enum import Enum

from mcdc_test import * 
from mcdc_test.pathsearch import LongestMayMerge
# from mcdc_test.setta_extension_minimal import solve
# from mcdc_test.pathsearch import LongestMayMerge, LongestPath, LongestBool, LongestBoolMay, BetterSize, RandomReuser
from random import Random

app = Flask(__name__)
api = Api(app)

###Logging for more concrete informations
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)
logger = logging.getLogger(__name__)


#This method is needed as the solve function returns fnodes which can not be serialized to a json format
def convert_fnode_to_string(result):
    converted_list = []    
    for item in result:
        fnode_str_list = [serialize(fnode) for fnode in item.keys()]
        value_str_list = [serialize(fnode) for fnode in item.values()]
        new_dict = dict(zip(fnode_str_list, value_str_list))
        converted_list.append(new_dict)
    return converted_list

class Documentation(Resource):
    def get(self):
        return jsonify({'message': 'Hello, to the MC/DC test generator!'}, 
                    {'content': 'We will provide you here with the API specifications'},
                    {'documentation': 'XY'})    

class Example_Request(Resource):
    def get(self):
        try: 
            reuse_h = pathsearch.LongestMayMerge
            eq = '(a > 10) & (b < 9)'
            rng = Random(100)
            result = setta_extension_minimal.solve(eq, reuse_h, rng)
            converted_list = convert_fnode_to_string(result)
            return jsonify(converted_list)
        except Exception as ex:
            #TODO: Log here
            abort(500, message="An unexpected error occurred. Please try again later.")
            
class MyEnum(Enum):
    LONGEST_MAY_MERGE = pathsearch.LongestMayMerge
    LONGEST_PATH = pathsearch.LongestPath
    LONGEST_BOOL = pathsearch.LongestBool
    LONGEST_BOOL_MAY = pathsearch.LongestBoolMay
    BETTER_SIZE = pathsearch.BetterSize
    RANDOM_REUSER = pathsearch.RandomReuser
    
enum_map = {
    'LongestMayMerge': MyEnum.LONGEST_MAY_MERGE,
    'LongestPath': MyEnum.LONGEST_PATH,
    'LongestBool': MyEnum.LONGEST_BOOL,
    'LongestBoolMay': MyEnum.LONGEST_BOOL_MAY,
    'BetterSize': MyEnum.BETTER_SIZE,
    'RandomReuser': MyEnum.RANDOM_REUSER
}

parser_base = reqparse.RequestParser(bundle_errors=True)
parser_base.add_argument('PATHSEARCH', type=str, required=True)
parser_base.add_argument('RANDOM', type=int, required=True)


##Single Expressions will be taken as an input
class Single_Expression_Converter(Resource):
    def __init__(self):
        self.parser_single_expression = parser_base.copy()
        self.parser_single_expression.add_argument('EXPRESSION', type=str, required=True)
        super(Single_Expression_Converter, self).__init__()
    
    ##For Documentation how to access the endpoint
    def get(self):
        return jsonify({'message': 'Hello, to the MC/DC test generator!'})    
 
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
            result = setta_extension_minimal.solve(eq, reuse_h.value, rng)
            output_ready = convert_fnode_to_string(result)
            return jsonify(output_ready)
        except Exception as ex:
            logger.critical("An unexpected error occurred. Exception: " + str(ex))
            abort(500, message="An unexpected error occurred. Please try again later.")

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
                result = pathsearch.solve(eq, reuse_h.value, rng)
                output_ready = convert_fnode_to_string(result)
                final_result.append(output_ready)
            return jsonify(final_result)
        except Exception as ex:
            logger.critical("An unexpected error occurred. Exception: " + str(ex))
            abort(500, message="An unexpected error occurred. Please try again later.")
            
class LoggerDeletionInteraction(Resource):
    def get(self):
        try:
            with open("app.log", 'r') as file:
                log_content = file.read()
                return log_content
        except FileNotFoundError:
            return "Log file not found."
        except Exception as e:
            return f"Error reading log file: {str(e)}" 
        
    def delete(self):
        try:
            os.remove("app.log")
            return {"message": "File deleted successfully."}, 200
        except FileNotFoundError:
            abort(404, message=f"File \"app.log\" not found.")
        except Exception as e:
            abort(500, message=f"Failed to delete file \"app.log\". Error: {str(e)}")
         

    
api.add_resource(Documentation, '/Documentation')
api.add_resource(Example_Request, '/ExampleRequest')
api.add_resource(Single_Expression_Converter, '/ExpressionAnalysis')
api.add_resource(Multi_Expression_Converter, '/MultiExpressionAnalysis')
api.add_resource(LoggerDeletionInteraction, '/delete/logs')

if __name__ == '__main__':
    app.run(debug=True)