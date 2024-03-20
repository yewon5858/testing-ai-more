from flask_restful import Api
from flask import Flask

from documentation import Documentation
from examplerequest import Example_Request
from singleexpressionconverter import Single_Expression_Converter
from multiexpressionconverter import Multi_Expression_Converter
from loggermodifyer import LoggerDeletionInteraction

def build_mcdc_api(app: Flask):
    api = Api(app)   

def add_requests_to_path(api: Api): 
    ##Adding to Path
    api.add_resource(Documentation, '/Documentation')
    api.add_resource(Example_Request, '/ExampleRequest')
    api.add_resource(Single_Expression_Converter, '/AnlayseExp')
    api.add_resource(Multi_Expression_Converter, '/AnlayseMultiExp')
    api.add_resource(LoggerDeletionInteraction, '/delete/logs')