import sqlite3

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
                    AND time > datetime('now', '-10 minutes')
                ORDER BY time DESC
        '''

clean = '''
            DELETE FROM HISTORY
                WHERE time < datetime('now', '-10 minutes')
        '''

connection = "data_base/history.db"

class DB:
    def __init__(self):
        self.db_context = sqlite3.connect(connection)
        self.cursor = self.db_context.cursor()

        self.cursor.execute(innitialize)
        self.db_context.commit()
    

    def insert(self, dict):
        self.cursor.execute(insert, (dict["id"], dict["anL1"], dict["anL2"], dict["anL3"], dict["anR1"], dict["anR2"], dict["anR3"], dict["R1"], dict["R2"], dict["R3"], dict["L1"], dict["L2"], dict["L3"]))
        self.db_context.commit()

    def get(self, id):
        self.cursor.execute(select, (id))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.execute(clean)
        self.db_context.commit()
        self.db_context.close()
