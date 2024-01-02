from flask import Flask, render_template
from turbo_flask import Turbo
from service import Service
from threading import Thread
import time

from templates.html_generator import *

app = Flask(__name__)
#turbo = Turbo(app)
service = Service()

is_running = True

@app.route('/', methods=['GET'])
def index():
    model = get_patient_table(service.IDS)
    return render_template('index.html', 
                           patient_selector=model)

@app.route('/patient/<int:patient_id>', methods=['GET'])
def patient(patient_id):
    model = service.get_mesurment_for_patient(patient_id)
    patient_selector = get_patient_table(service.IDS)
    patient_details = get_patient_details(model)
    patient_mesurmants = get_patient_table_mesurments(model)
    return render_template('patient.html', 
                           patient_selector=patient_selector,
                           patient_details=patient_details,
                           patient_mesurmants=patient_mesurmants)
                        
def update_mesurments():
    row = service.row
    with app.app_context():
        while is_running:
            time.sleep(1)
            turbo.push(turbo.replace(render_template('live_figure1.html', row=row), 'live_figure1'))

if __name__ == '__main__':
    app.run(debug=True)

#service_thread = Thread(name="Service-Thread", target=service.run)
#update_thread = Thread(name="Update-Thread", target=update_mesurments)

#service_thread.start()
#update_thread.start()



