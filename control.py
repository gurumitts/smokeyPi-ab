import time
from ds18b20 import DS18B20
from apscheduler.schedulers.background import BackgroundScheduler
import RPi.GPIO as GPIO
import sys
from data_store import DataStore

scheduler = BackgroundScheduler()

sensor = None
heat_source_pin = 16

heat_start = 0
heat_end = 0

print GPIO.VERSION
GPIO.setmode(GPIO.BOARD)
GPIO.setup(heat_source_pin, GPIO.OUT)

def current_time():
    return int(round(time.time() * 1000))

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


def heat_is_on():
    return GPIO.input(heat_source_pin)


def burst_heat(heat_duration, cool_duration):
    print 'starting burst..'
    now = current_time()
    if heat_is_on():
        print 'heat is already on %s %s %s' % (now, heat_start, heat_duration)
        if now > heat_start + heat_duration:
            print 'turning it off'
            heat_source_off()
        else:
            print 'leaving it on'
    else:
        print 'heat is off %s %s %s' % (now, heat_end, cool_duration)
        if now > heat_end + cool_duration:
            print 'cool done period ended, turing heat on'
            heat_source_on()
        else:
            print 'still cooling down'


def heat_source_on():
    global heat_start
    heat_start = current_time()
    set_heat_source(True)


def heat_source_off():
    global heat_end
    heat_end = current_time()
    set_heat_source(False)


def start_jobs(target_temp):
    print 'Loading DB'
    db = get_db()
    db.save_settings({'enabled': False, 'target_temp': target_temp,
                      'sample_size': 20, 'tolerance': 5, 'heat_duration': 30000, 'cool_duration':30000})
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
        slope = control_data['slope']
        heat_duration = control_data['heat_duration']
        cool_duration = control_data['cool_duration']
        if avg_temp is None:
            avg_temp = 1
        if enabled is 0:
            heat_source_off()
            db.set_heat_source_status('off')
            print 'disabled turning off heat'
        else:
            if temp > target_temp:
                if temp < target_temp + tolerance and slope < 0:
                    burst_heat(heat_duration, cool_duration)
                else:
                    heat_source_off()
            else:
                if temp > target_temp - tolerance and slope > 0:
                    heat_source_off()
                else:
                    burst_heat(heat_duration, cool_duration)
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