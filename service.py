from threading import Thread
from client import Client
from db import DB
import time

class Service:
    IDS = list(range(1,7))
    NUM_OF_INDEXES = len(IDS)

    def __init__(self, interval=1, timeout=5):
        self.client = Client(timeout=timeout)
        try:
            self.db = DB()
        except Exception as e:
            print(e)
            exit()
        self.row = [None] * self.NUM_OF_INDEXES
        self.interval = interval
        self.should_run = True

    def intrrupt(self):
        self.should_run = False

    def get_mesurment_for_patient(self, patient_id):
        return self.client.get_mesurment_for_patient(patient_id)

    def run(self):
        while self.should_run:
            for index, patient_id in enumerate(self.IDS):
                try:
                    self.row[index] = self.get_mesurment_for_patient(patient_id)
                except Exception as e:
                    print(e)
                    continue
            time.sleep(self.interval)