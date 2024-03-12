#https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
from flask import Flask, jsonify
from random import Random
import mcdc_test
app = Flask(__name__)

@app.route('/hellotomcdc', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, to the MC/DC test generator!'}, 
                   {'content': 'We will provide you here with the API specifications'},
                   {'documentation': 'XY'})    

@app.route('/generateexamples', methods=['GET'])
def generateexamples():
    reuse_h = mcdc_test.pathsearch.LongestMayMerge
    eq = '(a > 10) & (b < 9)'
    rng = Random(100)

    result = mcdc_test.setta_extension_minimal.solve(eq, reuse_h, rng)
    return jsonify({"expression": eq},
                   {"solution": result})

if __name__ == '__main__':
    app.run(debug=True)