from flask_restful import reqparse

parser_base = reqparse.RequestParser(bundle_errors=True)
parser_base.add_argument('PATHSEARCH', type=str, required=True)
parser_base.add_argument('RANDOM', type=int, required=True)