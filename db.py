import sqlite3
from datetime import datetime

innitialize = '''
    CREATE TABLE IF NOT EXISTS HISTORY(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        anL1 INTEGER,
        anL2 INTEGER, 
        anL3 INTEGER,
        anR1 INTEGER,
        anR2 INTEGER,
        anR3 INTEGER,
        R1 INTEGER,
        R2 INTEGER,
        R3 INTEGER,
        L1 INTEGER,
        L2 INTEGER, 
        L3 INTEGER,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

insert = '''
            INSERT INTO HISTORY(patient_id, anL1, anL2, anL3, anR1, anR2, anR3, R1, R2, R3, L1, L2, L3)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''

select = '''
            SELECT * FROM HISTORY 
                WHERE patient_id = ?
                ORDER BY time DESC
        '''

clean = '''
            DELETE FROM HISTORY
                WHERE time < datetime('now', '-10 minutes')
        '''

select_anomaly = '''
            SELECT trace FROM HISTORY
                WHERE patient_id = ?
                AND (anL1 = 1 OR anL2 = 1 OR anL3 = 1 OR anR1 = 1 OR anR2 = 1 OR anR3 = 1)
                ORDER BY time DESC
            '''

connection = "data_base/history.db"

class DB:
    COLUMN_NAME = [ 'id', 'patient_id', 'anL1', 'anL2', 'anL3', 'anR1', 'anR2', 'anR3', 'R1', 'R2', 'R3', 'L1', 'L2', 'L3', 'time']
    REF_DATE = datetime.strptime("1997-01-01 00:00:00" ,"%Y-%m-%d %H:%M:%S")
    def __init__(self):
        self.db_context = sqlite3.connect(connection)
        self.cursor = self.db_context.cursor()

        self.cursor.execute(innitialize)
        self.db_context.commit()
    

    def insert(self, id, dict):
        self.cursor.execute(insert, (id, dict["anL1"], dict["anL2"], dict["anL3"], dict["anR1"], dict["anR2"], dict["anR3"], dict["R1"], dict["R2"], dict["R3"], dict["L1"], dict["L2"], dict["L3"]))
        self.db_context.commit()

    def get(self, id):
        self.cursor.execute(select, (id,))
        records = self.cursor.fetchall()
        m = self._to_seconds(records[-1][-1])
        for index, record in enumerate(records):
            record = list(record)
            record[-1] = self._to_seconds(record[-1]) - m
            records[index] = tuple(record)
        return records

    def close(self):
        #self.cursor.execute(clean)
        #self.db_context.commit()
        self.db_context.close()

    def _to_seconds(self, time):
        time = datetime.strptime(time ,"%Y-%m-%d %H:%M:%S")
        return (time - self.REF_DATE).total_seconds()

if __name__ == "__main__":
    db = DB()
    print(db.get(1))
    db.close()