import sqlite3,json, random, time

class DataStore:

    sample_size = 10

    def __init__(self):
        #print 'Preparing data store...'
        self.connection = sqlite3.connect('app.sqlite3.db')
        self.connection.row_factory = sqlite3.Row
        self.startup()
        #print 'data store is ready'

    def save_settings(self, enabled, target_temp):
        if enabled:
            params = ['1', target_temp]
        else:
            params = ['0', target_temp]
        cursor = self.connection.cursor()
        cursor.execute("""update settings set ENABLED = ?, TARGET_TEMP = ? where id = 1 ;""", params)
        self.connection.commit()
        cursor.close()

    def get_settings(self):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM settings WHERE id = 1""")
        r = cursor.fetchone()
        enable = r['ENABLED'] == 1
        target_temp = r['TARGET_TEMP']
        cursor.close()
        return enable, target_temp

    def get_heat_source_status(self):
        cursor = self.connection.cursor()
        cursor.execute("""select HEAT_SOURCE from settings where id = 1 ;""")
        r = cursor.fetchone()
        heat_source = r['HEAT_SOURCE']
        self.connection.commit()
        cursor.close()
        return heat_source

    def set_heat_source_status(self,status):
        cursor = self.connection.cursor()
        cursor.execute("""update settings set HEAT_SOURCE = ? where id = 1 ;""", [status])
        self.connection.commit()
        cursor.close()

    def add_temperature(self, current_temp):
        cursor = self.connection.cursor()
        cursor.execute("""INSERT INTO temperatures (temp) VALUES(?)""", [current_temp])
        self.connection.commit()
        cursor.close()

    def get_control_data(self):
        cursor = self.connection.cursor()
        cursor.execute("""select s.target_temp, s.heat_source, s.enabled,
            (select round(avg(t.temp),1) from temperatures t where t.id in
            (select id from temperatures ORDER BY dt DESC Limit %s))
            as avg_temp from settings s """ % self.sample_size)
        r = cursor.fetchone()
        control_data = {}
        control_data['enabled'] = r['enabled']
        control_data['heat_source'] = r['heat_source']
        control_data['target_temp'] = r['target_temp']
        control_data['avg_temp'] = r['avg_temp']

        cursor.close()
        return control_data

    def get_temps(self, start_idx):
        if start_idx is None:
            start_idx = 0
        cursor = self.connection.cursor()
        cursor.execute("""select t.id,datetime(t.dt,'localtime'),
            t.temp,s.heat_source,(select round(avg(t.temp),1) from temperatures t where t.id in
            (select id from temperatures ORDER BY dt DESC Limit %s)) as avg_temp
            from temperatures t,settings s where t.id > ?""" % self.sample_size, [start_idx])
        rows = cursor.fetchall()
        temps = []
        for row in rows:
            temps.append([row[0],row[1],row[2],row[3],row[4]])
        return json.dumps(temps)

    def shutdown(self):
        self.connection.close()

    def startup(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute('select count(*) from temperatures')
            #print cursor.fetchone()
        except Exception as e:
            print e.message
            print 'Required table not found... creating temperatures table...'
            cursor.execute("""create table temperatures(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT,
                DT DATETIME DEFAULT CURRENT_TIMESTAMP,
                TEMP REAL);""")
            print 'done!'
        finally:
            cursor.close()

        cursor = self.connection.cursor()
        try:
            cursor.execute('select count(*) from settings')
            cursor.fetchone()
        except Exception as e:
            print e.message
            print 'Required table not found... creating settings table...'
            cursor.execute("""create table settings(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT,
                ENABLED INTEGER,
                TARGET_TEMP REAL,
                HEAT_SOURCE TEXT);""")
            cursor.execute("""insert into settings (ENABLED, TARGET_TEMP, HEAT_SOURCE )
                values(?,?,?);""", ['0', '200', 'off'])
            print 'done!'
        finally:
            cursor.close()

if __name__ == '__main__':
    db = DataStore()

    print db.get_settings()
    db.save_settings(False,210)
    #print db.get_settings()
    print db.get_control_data()
    count = 1
    while count < 20000:
        db.add_temperature(205 + 12*random.random() )
        count += 1
        time.sleep(1)
        print db.get_control_data()

    print db.get_control_data()
    print db.get_temps(7)
