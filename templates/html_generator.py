from flask import render_template
from io import BytesIO
import base64

def get_patient_table(patient_ids):
    table = "<table>"
    table += "<tr>"
    table += "<th>Patients</th>"
    for id in patient_ids:
        table += "<th><a href=\"/patient/" + str(id) + "\">"
        table += str(id) + "</a></th>"
    table += "</tr>"
    table += "</table>"
    return table

def get_patient_table_mesurments(row):
    return render_template('live_figure1.html', **row)

def get_patient_details(patient):
    return render_template('patient_details.html', **patient)

def get_image_from_figure(fig):
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    header = f'<img src="data:image/png;base64,{plot_url}">'
    return header.format(plot_url=plot_url)