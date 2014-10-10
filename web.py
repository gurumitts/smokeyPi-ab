from flask import Flask, send_file, request
from flask import render_template
from data_store import DataStore
import json

app = Flask(__name__)



@app.route('/')
def index(name=None):
    db = DataStore()
    temps = db.get_temps(0)
    return render_template('index.html', temps=temps)

@app.route('/temps/<idx>')
def temps(idx=0):
    db = DataStore()
    temps = db.get_temps(idx)
    return temps



if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')