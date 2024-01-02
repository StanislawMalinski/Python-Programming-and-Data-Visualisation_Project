from flask import render_template

def get_patient_table(patient_ids):
    table = "<table>"
    table += "<tr>"
    table += "<th>Patient ID</th>"
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