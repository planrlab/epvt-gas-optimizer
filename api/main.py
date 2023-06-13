'''
Created on June 12, 2023

@author: Arnab Mukherjee
'''
from api.optimize_gas import optimize
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# sys.path.append("../..")


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    '''
    Root to get information about the CFG Generator Microservice 
    '''
    return jsonify({'module': 'gas-optimizer',
                    'routes': [
                        {'method': 'POST',
                            'path': '/optimize',
                            'body': {
                                'source': "type:String"
                            },
                            'response_type': 'text/json',
                            'response_schema': {'original-code': 'type:String',
                                                'optimized-code': "type:String",
                                                'gas-saved': "type:Integer"},
                            'description': 'Returns the Optimized source code along with the gas saved.'
                         }
                    ]
                    })


@ app.route('/optimize', methods=['POST'])
def cfg_svg():
    '''
    Route to get the SVG representation
    '''
    body = json.loads(request.data)
    # print(body)
    optimized_code, gas_saved = optimize(body['source'])

    return jsonify({'original-code': body['source'], 'optimized-code': optimized_code, 'gas-saved': gas_saved})


# app.run(host='0.0.0.0')
if __name__ == "__main__":
    print("Starting Server....")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
