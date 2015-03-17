import time
from ds18b20 import DS18B20
from apscheduler.schedulers.background import BackgroundScheduler
import RPi.GPIO as GPIO
import sys
from data_store import DataStore

scheduler = BackgroundScheduler()

sensor = None
heat_source_pin = 16

print GPIO.VERSION
GPIO.setmode(GPIO.BOARD)
GPIO.setup(heat_source_pin, GPIO.OUT)

def get_db():
    db = DataStore()
    return db

def get_sensor():
    global sensor
    if sensor is None:
        print 'Loading Temperature Sensor'
        sensor = DS18B20()
    return sensor

def set_heat_source(switch):
    GPIO.output(heat_source_pin, switch)

def heat_source_on():
    set_heat_source(True)

def heat_source_off():
    set_heat_source(False)

def start_jobs(target_temp):
    print 'Loading DB'
    db = get_db()
    db.save_settings({'enabled': False, 'target_temp': target_temp, 'sample_size': 20, 'tolerance': 5})
    db.shutdown()
    print 'DB load complete'
    get_sensor()
    print 'Sensor load complete'
    print 'Starting control with target temp = %s' % target_temp
    scheduler.start()
    scheduler.add_job(track,'interval', seconds=2)
    scheduler.add_job(control_power, 'interval', seconds=5)
    scheduler.print_jobs()

def track():
    current_temp = get_sensor().get_temperature(DS18B20.DEGREES_F)
    try:
        db = get_db()
        db.add_temperature(current_temp)
        db.shutdown()
    except Exception as e:
        print e
        print e.message
    print current_temp

def control_power():
    try:
        db = get_db()
        control_data = db.get_control_data()
        print 'using %s to control power' % control_data
        target_temp = control_data['target_temp']
        enabled = control_data['enabled']
        heat_source = control_data['heat_source']
        avg_temp = control_data['avg_temp']
        tolerance = control_data['tolerance']
        sample_size = control_data['sample_size']
        temp = control_data['temp']
        if avg_temp is None:
            avg_temp = 1
        if enabled is 0:
            heat_source_off()
            db.set_heat_source_status('off')
            print 'disabled turning off heat'
        else:
            if temp < target_temp and avg_temp - tolerance < target_temp:
                heat_source_on()
                db.set_heat_source_status('on')
                print 'heat is on'
            else:
                heat_source_off()
                db.set_heat_source_status('off')
                print 'heat is off'
        db.shutdown()
    except Exception as e:
        print e
        print e.message


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_temp = sys.argv[1]
        start_jobs(target_temp)
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        heat_source_off()
        GPIO.cleanup()
    print 'end'