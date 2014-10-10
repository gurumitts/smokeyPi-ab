import time
from ds18b20 import DS18B20
from apscheduler.schedulers.background import BackgroundScheduler
from data_store import DataStore

scheduler = BackgroundScheduler()

sensor = None

def get_db():
    db = DataStore()
    return db

def get_sensor():
    global sensor
    if sensor is None:
        print 'Loading Temperature Sensor'
        sensor = DS18B20()
    return sensor


def start_jobs():
    print 'Loading DB'
    get_db()
    print 'DB load complete'
    get_sensor()
    scheduler.start()
    scheduler.add_job(track,'interval', seconds=2)
    scheduler.add_job(control_power, 'interval', seconds=5)
    scheduler.print_jobs()

def track():
    current_temp = get_sensor().get_temperature(DS18B20.DEGREES_F)
    try:
        get_db().add_temperature(current_temp)
    except Exception as e:
        print e
        print e.message
    print current_temp

def control_power():
    last_temp = get_db().get_last_temp()
    print 'using %s to control power' % last_temp


if __name__ == '__main__':
    start_jobs()
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        scheduler.shutdown()
    print 'end'