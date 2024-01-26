import requests
from db import DB 

BASE_URL = 'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{index}'


class Client:
    COLUMN_NAME = ['birthdate', 'disabled', 'id', 'lastname', 'firstname', 'trace_name', 'anL1', 'anL2', 'anL3', 'anR1', 'anR2', 'anR3', 'R1', 'R2', 'R3', 'L1', 'L2', 'L3', 'time-stamp']
    def __init__(self, timeout=5):
        self.timeout = timeout

    def get_mesurment_for_patient(self, index):
        response = requests.get(BASE_URL.format(index=index), timeout=self.timeout)
        return self._get_dict(response.json())
    
    def _get_dict(self, row):
        return dict(zip(self.COLUMN_NAME, self._get_row(row)))

    def _get_row(self, el):
        return [el["birthdate"],
            el["disabled"],
            el["id"],
            el["lastname"],
            el["firstname"],
            el["trace"]["name"]] + [s["anomaly"] for s in el["trace"]["sensors"]] + [s["value"] for s in el["trace"]["sensors"]] + [DateTime.now().strftime("%Y-%m-%d %H:%M:%S")]
        
