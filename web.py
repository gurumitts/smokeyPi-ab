from flask import Flask
from flask import render_template, request
import math
from data_store import DataStore

app = Flask(__name__)

temp_range = 60

@app.route('/')
def index(name=None):
    db = DataStore()
    settings = db.get_settings()
    db.shutdown()
    min_temp = math.floor(settings['target_temp'] - temp_range/2)
    max_temp = math.ceil(settings['target_temp'] + temp_range/2)
    return render_template('index.html', min_temp=min_temp, max_temp=max_temp, **settings)

@app.route('/history')
def history(name=None):
    db = DataStore()
    settings = db.get_settings()
    db.shutdown()
    tr = request.args.get('tr')
    if tr is None:
        tr = 8
    min_temp = math.floor(settings['target_temp'] - temp_range/2)
    max_temp = math.ceil(settings['target_temp'] + temp_range/2)
    return render_template('history.html', tr=tr, min_temp=min_temp, max_temp=max_temp, **settings)

@app.route('/temps/<idx>')
def temps(idx=0):
    db = DataStore()
    temps = db.get_temps(idx)
    db.shutdown()
    return temps

@app.route('/settings', methods=['POST'])
def settings():
    settings = request.get_json()
    db = DataStore()
    print 'Saving new settings: ' % settings
    db.save_settings(settings)
    return "ok"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')