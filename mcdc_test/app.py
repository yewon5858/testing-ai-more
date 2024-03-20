from flask import Flask
from mcdc_api.apibuilder import build_mcdc_api

app = Flask(__name__)
build_mcdc_api(app)

if __name__ == '__main__':
    app.run(debug=True)