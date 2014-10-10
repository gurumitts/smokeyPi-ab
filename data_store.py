import sqlite3,json

class DataStore:

    def __init__(self):
        #print 'Preparing data store...'
        self.connection = sqlite3.connect('app.sqlite3.db')
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        try:
            cursor.execute('select count(*) from temperatures')
            #print cursor.fetchone()
        except Exception as e:
            print e.message
            print 'Required table not found... initializing the repository'
            cursor.execute("""create table temperatures(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT,
                DT DATETIME DEFAULT CURRENT_TIMESTAMP,
                TEMP REAL);""")
        finally:
            cursor.close()
        #print 'data store is ready'


    def add_temperature(self, current_temp):
        cursor = self.connection.cursor()
        cursor.execute("""INSERT INTO temperatures (temp) VALUES(?)""", [current_temp])
        self.connection.commit()
        cursor.close()

    def get_last_temp(self):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM temperatures WHERE id = (SELECT MAX(id) FROM temperatures)""")
        r = cursor.fetchone()
        last_temp = 0
        if r is not None:
            last_temp = r['temp']
        cursor.close()
        return last_temp

    def get_temps(self, start_idx):
        if start_idx is None:
            start_idx = 0
        cursor = self.connection.cursor()
        cursor.execute("""select id,datetime(dt,'localtime'),temp from temperatures where id = ?""",[start_idx])
        rows = cursor.fetchall()
        temps = []
        for row in rows:
            temps.append([row[0],row[1],row[2]])
        return json.dumps(temps)

    def shutdown(self):
        self.connection.close()


if __name__ == '__main__':
    db = DataStore()
    db.add_temperature(78.9)
    db.add_temperature(78.1)
    db.add_temperature(78.2)
    db.add_temperature(78.3)
    db.add_temperature(78.4)
    print db.get_last_temp()
    print db.get_temps(7)
