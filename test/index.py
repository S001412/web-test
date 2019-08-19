from flask import Flask, request, Response  
import json
 
app = Flask(__name__)
 
@app.route('/')
def hello_world():  
    return Response(json.dumps({"welcome": "hello world!"}),  mimetype='application/json')
 
@app.route('/json', methods=['POST'])
def my_json():  
    print(request.headers)
    print(request.json)
    rt = {'info':'hello '+request.json['name']}
    return Response(json.dumps(rt),  mimetype='application/json')
 
if __name__ == '__main__':  
    app.run(debug=True)
