from flask import Flask
from mcdc_api.apibuilder import build_mcdc_api
from flask_cors import CORS

app = Flask(__name__)
build_mcdc_api(app)
#This prevents problems based on Cross-Origin Resource Sharing (CORS)
CORS(app) #https://flask-cors.readthedocs.io/en/latest/

if __name__ == '__main__':
    app.run(debug=True)