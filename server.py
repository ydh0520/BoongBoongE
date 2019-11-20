from flask import Flask,render_template,request
from random import *
import json
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    test_index = randint(1,31)
    return render_template('test.html',index= test_index,data = get_data_index(test_index-1))

@app.route('/info')
def inof():
    return "info"

@app.route('/result',methods=['GET','POST'])
def result():
    id = request.args.get('id')
    sentence = request.args.get('sentence')
    return get_data_index(3)

def get_data_index(index):
    with open('static/data/data.json') as data_file:
        data =json.load(data_file)
    return data["data"][index]




if __name__ == '__main__':
    app.run()