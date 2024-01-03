from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from matplotlib.figure import Figure
from service import Service
from threading import Thread
import time

from templates.html_generator import *

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
service = Service()

is_running = True
patient_id_global = 1

@app.route('/', methods=['GET'])
def index():
    model = get_patient_table(service.IDS)
    return render_template('index.html', 
                           patient_selector=model)

@app.route('/patient/<int:patient_id>', methods=['GET'])
def patient(patient_id):
    patient_id_global = patient_id
    model = service.get_mesurment_for_patient(patient_id)
    patient_selector = get_patient_table(service.IDS)
    patient_details = get_patient_details(model)
    patient_mesurmants = get_patient_table_mesurments(model)
    return render_template('patient.html', 
                           patient_selector=patient_selector,
                           patient_details=patient_details,
                           patient_mesurmants=patient_mesurmants,
                           id=patient_id,
                           async_mode=socketio.async_mode)
                        
@socketio.on('give_me_figure')
def figure():
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    socketio.emit("here_is_your_gigure", f"<img src='data:image/png;base64,{data}'/>")

@socketio.on('give_me_data')
def load_more_data(msg):
    service.run(lambda x: socketio.emit('new_data', x[patient_id_global]))

@socketio.on('no_more_data')
def stop_data(msg):
    service.intrrupt()

if __name__ == '__main__':
    socketio.run(app, debug=True)

#service_thread = Thread(name="Service-Thread", target=service.run)
#update_thread = Thread(name="Update-Thread", target=update_mesurments)

#service_thread.start()
#update_thread.start()



