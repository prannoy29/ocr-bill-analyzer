from flask import Flask,request,make_response,jsonify
import json
import text_selector
from werkzeug import secure_filename
import os
app=Flask(__name__)

@app.route('/test',methods=['POST'])
def return_data():
    # print(values)
    # json_obj=request.get_json()
    f = request.files['photo']
    f.save(secure_filename(f.filename))
    response=text_selector.test_function(f.filename)
    if os.path.exists(f.filename):
        os.remove(f.filename)
    return make_response(jsonify(response),200)

@app.route('/print',methods=['GET'])
def print_hello_world():
    print ('hello_world')


if __name__=="__main__":
    app.debug=False
    app.run('0.0.0.0')
