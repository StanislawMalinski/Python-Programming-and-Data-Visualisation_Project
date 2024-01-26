from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from service import Service
from threading import Thread
import time

from templates.html_generator import *

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
service = Service(socket=socketio)

is_running = True
global patient_id_global
patient_id_global = 1

@app.route('/', methods=['GET'])
def index():
    model = get_patient_table(service.IDS)
    return render_template('index.html', 
                           patient_selector=model)

@app.route('/patient/<int:patient_id>', methods=['GET'])
def patient(patient_id):
    global patient_id_global
    patient_id_global = patient_id
    service.intrrupt()
    model = service.get_mesurment_for_patient(patient_id)
    patient_selector = get_patient_table(service.IDS)
    patient_details = get_patient_details(model)
    patient_mesurmants = get_patient_table_mesurments(model)
    return render_template('patient.html', 
                           patient_selector=patient_selector,
                           patient_details=patient_details,
                           patient_mesurmants=patient_mesurmants,
                           id=patient_id)
                           #async_mode=socketio.async_mode)

@socketio.on('update_window_frame')
def update_window_frame(msg):
    
    service.set_window_frame(patient_id_global, int(msg)/100)

@socketio.on('upadate_window_offset')
def update_window_offset(msg):
    
    service.set_window_offset(patient_id_global, int(msg)/100)
            
@socketio.on('load_me_figure')
def get_figure(msg):
    
    fig = service.generate_figure_and_emit(patient_id_global)

@socketio.on('give_me_data')
def load_more_data(msg):
    service.intrrupt()
    service.set_alarm_callback(lambda x: socketio.emit('alarm', f"Patient {x} expirience anomaly."))
    service.set_recive_callback(lambda x: socketio.emit('new_data', x))
    service.run_one(patient_id_global)

@socketio.on('no_more_data')
def stop_data(msg):
    service.intrrupt()


if __name__ == '__main__':
    socketio.run(app, debug=True)
