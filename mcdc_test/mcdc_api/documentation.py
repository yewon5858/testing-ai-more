from flask import jsonify
from flask_restful import Resource

class Documentation(Resource):
    def get(self):
        return jsonify({'message': 'Hello, to the MC/DC test generator!'}, 
                    {'content': 'We will provide you here with the API specifications'},
                    {'documentation': 'XY'})    