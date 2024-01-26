from threading import Thread
from client import Client
from db import DB
from math import floor
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from templates.html_generator import get_image_from_figure
import time
import pandas as pd

class Service:
    IDS = list(range(1,7))
    NUM_OF_INDEXES = len(IDS)

    def __init__(self,socket=None, interval=1, timeout=5):
        self.timeout = timeout
        self.client = Client(timeout=self.timeout)
        self.interval = interval
        self.socket = socket
        self.db = DB()

        self.window_offset = 0.1
        self.window_frame = 0


    def intrrupt(self):
        self.should_run = False

    def get_mesurment_for_patient(self, patient_id):
        return self.client.get_mesurment_for_patient(patient_id)

    def run_one(self, patient_id):
        self.should_run = True
        Thread(name="Service-Thread", target=self._run_one, args=(patient_id,)).start()

    def run(self):
        self.should_run = True
        Thread(name="Service-Thread", target=self._run).start()

    def get_row(self, patient_id):
        return self.get_mesurment_for_patient(patient_id)

    def _run(self):
        try:
            self.db = DB()
        except Exception as e:
            print(e)
            exit()
        row = [None] * self.NUM_OF_INDEXES
        while self.should_run:
            for index, patient_id in enumerate(self.IDS):
                try:
                    row[index] = self.get_mesurment_for_patient(patient_id)
                    self.db.insert(patient_id, row[index])
                    self.recive_callback(row)
                    print("Patient {} updated".format(patient_id))
                except Exception as e:
                    print("Patient {} failed to update".format(patient_id))
                    print(e)
                    continue
            time.sleep(self.interval)
        self.close()


    def _run_one(self, index):
        patient_id = index
        while self.should_run:
            try:
                row = self.get_mesurment_for_patient(patient_id)
                self.recive_callback(row)
                print("Patient {} updated".format(patient_id))
            except Exception:
                print("Patient {} failed to update".format(patient_id))
            time.sleep(self.interval)
        
    def close(self):
        self.db.close()

    def __del__(self):
        self.close()

    def getDB(self):
        try:
            db = DB()
        except Exception as e:
            print(e)
            exit()
        return db

    def get_df(self, id):
        db = self.getDB()
        rows = db.get(id)
        df = pd.DataFrame(rows, columns=db.COLUMN_NAME)
        df.index = df['time']
        df = df.drop(columns=['id', 'patient_id'])
        db.close()
        return df
    
    def set_alarm_callback(self, callback):
        self.alarm_callback = callback

    def set_recive_callback(self, callback):
        self.recive_callback = callback

    def set_window_frame(self, patient_id, frame):
        self.window_frame = frame
        self.generate_figure_and_emit(patient_id)

    def set_window_offset(self, patient_id, offset):
        self.window_offset = offset
        self.generate_figure_and_emit(patient_id)

    def generate_figure_and_emit(self, patient_id):
        fig = self.generate_figure(patient_id)
        html = get_image_from_figure(fig)
        self.socket.emit('update_activity_figure', html)

    def plot(self, df):
        print(df)
        fig, ax = plt.subplots(3,2, figsize=(10,10), dpi=100)
        for i, s in enumerate(['L1','R1', 'L2', 'R2', 'L3', 'R3']):
            ax[i // 2, i % 2].plot(df.index, df[s], label=s)
            ax[i // 2, i % 2].plot(df.index[df['an' + s] == True],
                                    df[s][df['an' + s] == True],  color='red', lw=2)
            ax[i // 2, i % 2].set_title(s)
        map(lambda x: x.ylim(0,1024), ax.flatten())
        plt.close()
        return fig

    def generate_figure(self, patient_id):
        df = self.get_df(patient_id)
        start = floor(self.window_offset * len(df))
        end = start + floor(self.window_frame * (len(df) - start))   
        df = df.iloc[start:end]
        return self.plot(df)

    def replay_set_up(self, patient_id):
        self.replay_index = 0
        self.replay_df = self.get_df(patient_id)
        return self.replay_df.iloc[self.replay_index]

    def replay_row(self):
        print(self.replay_index)
        return self.replay_df.iloc[self.replay_index]

    def replay_prev(self):
        if self.replay_index <= 0:
            self.replay_index = len(self.replay_df) - 1
        self.replay_index -= 1
        return self.replay_df.iloc[self.replay_index]

    def replay_next(self):
        if self.replay_index >= len(self.replay_df) - 1:
            self.replay_index = 0
        self.replay_index += 1
        return self.replay_df.iloc[self.replay_index - 1]
    
    def replay_reset(self):
        self.replay_index = 0
        return self.replay_df.iloc[self.replay_index]

if __name__ == "__main__":
    ser = Service()
    df = ser.generate_figure(1)
    print(df)
