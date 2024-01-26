from dash import dcc, html, Input, Output, callback, Dash, State
import dash_bootstrap_components as dbc
import dash
import plotly.express as px
from service import Service
from templates.html_generator import get_image_from_figure

app = Dash(__name__)
ser = Service()

def getTable(row):
    anomaly = row["anL1"] == 1
    style = {"border": "1px solid black", "width": "50px"}
    style["background"] = "red" if anomaly else "white"
    el = html.Table([
        html.Tr([
            html.Th("Sensors:"),
            html.Td("L1", style=style),
            html.Td("L2", style=style),
            html.Td("L3", style=style),
            html.Td("R1", style=style),
            html.Td("R2", style=style),
            html.Td("R3", style=style),
        ]),
        html.Tr([
            html.Th("Values:"),
            html.Td(row["L1"], style=style),
            html.Td(row["L2"], style=style),
            html.Td(row["L3"], style=style),
            html.Td(row["R1"], style=style),
            html.Td(row["R2"], style=style),
            html.Td(row["R3"], style=style),
        ])
    ])
    return [el]

def getPatientDetails(row):
    el = html.Div([
        html.H4("Patient details:"),
        html.P(f"Patient ID: {row['id']}"),
        html.P(f"Firstname: {row['firstname']}"),
        html.P(f"Lastname: {row['lastname']}"),
        html.P(f"Birthdate: {row['birthdate']}"),
        html.P(f"Trace name: {row['trace_name']}")
    ])
    return [el]

def getFeetImage(row):
    el = html.Div([
        html.Img(src="/static/feet.jpg")
    ])


app.layout = html.Div(
    children=[
        dcc.Store(id='memory'),
        html.H1("PPDV project"),
        html.H2("Patient ID:"),
        dcc.Dropdown(ser.IDS, id='patient_id', value='1'),
        dbc.Row([
            dbc.Col([
                html.H3("Patient details:"),
                html.Div(id='patient-details', children=[])], style={'width': '50%'}),
            dbc.Col([html.Div(id='table', children=[])], style={'width': '50%'})
        ], style={'display': 'flex'}),
        dbc.Row([
            dbc.Col([
                html.H3("Right leg:"),
                dcc.Graph(id='graph-right', figure={})], style={'width': '50%'}),
            dbc.Col([
                html.H3("Left leg:"),
                dcc.Graph(id='graph-left', figure={})], style={'width': '50%'}),
        ],style={'display': 'flex'}),

        html.Button('start', id='start'),
        html.Button('stop', id='stop'),
        html.Div(id='feet-image', children=[])
    ]
)


@app.callback([
    Output(component_id='graph-right', component_property='figure'),
    Output(component_id='graph-left', component_property='figure'),
    Output('memory', 'data'),
    Output('patient-details', 'children'),
    Input(component_id='patient_id', component_property='value'),
    State('memory', 'data')
    ])
def update_graph(patient_id, data):
    data = data or {"left_wall": 0, "right_wall": 1}

    df = ser.get_df(patient_id)
    print(df)
    fig_r = px.line(df, x='time', y=["R1", "R2", "R3"],
                    range_x=[df.time.min(), df.time.max()], 
                    range_y=[0,1024],
                    height=400, width=400)

    fig_l = px.line(df, x='time', y=["L1", "L2", "L3"], 
                    range_x=[df.time.min(), df.time.max()], 
                    range_y=[0,1024],
                    height=400, width=400)
    
    patient_details = getPatientDetails(ser.get_mesurment_for_patient(patient_id))

    return fig_r, fig_l, data, patient_details


@app.callback([
    Output('table', 'children'),
    Output('feet-image', 'children'),
    Input('start', 'n_clicks'),
    Input('stop', 'n_clicks'),
    Input(component_id='patient_id', component_property='value'),
])
def table_controll(start, stop, patient_id):
    el = dash.ctx.triggered_id
    if el == 'start':
        ser.should_run = True
    elif el == 'stop':
        ser.should_run = False

    row = ser.get_row(patient_id)
    return getTable(row), getFeetImage(row)

def update_table(row):
    print(row)

if __name__ == "__main__":
    app.run_server(debug=True)
    ser.set_recive_callback(lambda x: update_table(x))