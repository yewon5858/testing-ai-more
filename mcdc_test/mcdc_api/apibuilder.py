from flask_restful import Api
from flask import Flask

from mcdc_api.documentation import Documentation
from mcdc_api.examplerequest import Example_Request
from mcdc_api.singleexpressionconverter import Single_Expression_Converter
from mcdc_api.multiexpressionconverter import Multi_Expression_Converter
from mcdc_api.loggermodifyer import LoggerDeletionInteraction

def build_mcdc_api(app: Flask):
    api = Api(app)   
    add_requests_to_path(api)

def add_requests_to_path(api: Api): 
    ##Adding to Path
    api.add_resource(Documentation, '/Documentation')
    api.add_resource(Example_Request, '/ExampleRequest')
    api.add_resource(Single_Expression_Converter, '/AnlayseExp')
    api.add_resource(Multi_Expression_Converter, '/AnlayseMultiExp')
    api.add_resource(LoggerDeletionInteraction, '/delete/logs')