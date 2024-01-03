from threading import Thread
from client import Client
from db import DB
import time

class Service:
    IDS = list(range(1,7))
    NUM_OF_INDEXES = len(IDS)

    def __init__(self, interval=1, timeout=5):
        self.timeout = timeout
        self.client = Client(timeout=self.timeout)
        self.row = [None] * self.NUM_OF_INDEXES
        self.interval = interval


    def intrrupt(self):
        self.should_run = False

    def get_mesurment_for_patient(self, patient_id):
        return self.client.get_mesurment_for_patient(patient_id)

    def run(self, callback=lambda x: None):
        
        self.should_run = True

        Thread(name="Service-Thread", target=self._run, args=(callback,)).start()

    def _run(self, callback):
        start = time.time()
        try:
            self.db = DB()
        except Exception as e:
            print(e)
            exit()
        while self.should_run:
            for index, patient_id in enumerate(self.IDS):
                try:
                    self.row[index] = self.get_mesurment_for_patient(patient_id)
                    self.db.insert(patient_id, self.row[index])
                    callback(self.row)
                    print("Patient {} updated".format(patient_id))
                except Exception as e:
                    print("Patient {} failed to update".format(patient_id))
                    print(e)
                    continue
            time.sleep(self.interval)
        self.close()
        
    def close(self):
        self.db.close()