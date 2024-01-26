import datetime
from dash import dcc, html, Input, Output, callback, Dash, State
import dash_bootstrap_components as dbc
import dash
import plotly.express as px
from service import Service
from templates.html_generator import get_image_from_figure

app = Dash(__name__)
ser = Service(interval=0.1,timeout=5)
Lhead = ['L1', 'L2', 'L3']
Rhead = ['R1', 'R2', 'R3']

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
    scale = lambda x: "translate(-50%, -50%) scale(" + str(1 + int(row[x]) * 0.2 / 1023) + ")"
    el = html.Div([
        html.Div([
            html.Img(id="animated-image", src="/assets/feets.jpg", style={"height": "400px"}),
            html.Div([
                html.Label("L1"),
            ], id="L1", className="pulsing-circle", style={"transform":  scale("L1")}),
            html.Div([
                html.Label("L2"),
            ], id="L2", className="pulsing-circle", style={"transform":  scale("L2")}),
            html.Div([
                html.Label("L3"),
            ], id="L3", className="pulsing-circle", style={"transform":  scale("L3")}),
            html.Div([
                html.Label("R1"),
            ], id="R1", className="pulsing-circle", style={"transform":  scale("R1")}),
            html.Div([
                html.Label("R2"),
            ], id="R2", className="pulsing-circle", style={"transform":  scale("R2")}),
            html.Div([
                html.Label("R3"),
            ], id="R3", className="pulsing-circle", style={"transform":  scale("R3")}),
        ], id="animated-container")
    ])
    return [el]


app.layout = html.Div(
    children=[
        dcc.Store(id='memory'),
        html.H1("PPDV project"),
        html.H2("Patient ID:"),
        dcc.Dropdown(ser.IDS, id='patient_id', value='1'),
        dcc.Interval(id='interval', interval=500, n_intervals=0),
        dbc.Row([
            dbc.Col([
                html.Div(id='patient-details', children=[])], style={'width': '50%'}),
            dbc.Col([
                html.Div(id='table', children=[]),
                html.Div(id='time-stamp', children=[]),
                html.Button('replay', id='replay'),
                html.Button('reset', id='reset'),
                html.Button('connect', id='connect'),
                html.Button('stop', id='stop'),

                html.Button('prev', id='prev'),
                html.Button('next', id='next'),
                html.Br(),
                html.Label("Playback speed:"),
                dcc.Input(id='playback-speed', type='number', value=0.5, max=4, min=0.1, step=0.1)
                ], 
                style={'width': '50%'})

        ], style={'display': 'flex'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph-right', figure={})], style={'width': '33%'}),
            dbc.Col([
                dcc.Graph(id='graph-left', figure={})], style={'width': '33%'}),
            dbc.Col([
                html.Div(id='feet-image-container', children=[])], style={'width': '33%'}),
        ],style={'display': 'flex'}),
        
    ]
)


@app.callback([
    Output('graph-right', 'figure'),
    Output('graph-left', 'figure'),
    Output('patient-details', 'children'),
    Input('patient_id', 'value'),
    ])
def update_graph(patient_id):
    df = ser.get_df(patient_id)
    ser.replay_set_up(patient_id)
    fig_r = px.line(df, x='time', y=["R1", "R2", "R3"],
                    title='Right leg',
                    range_x=[df.time.min(), df.time.min()+60], 
                    range_y=[-10,1034],
                    height=400, width=400)

    fig_l = px.line(df, x='time', y=["L1", "L2", "L3"], 
                    title='Left leg',
                    
                    range_x=[df.time.min(), df.time.min()+60], 
                    range_y=[-10,1034],
                    height=400, width=400)

    fig_l['data'][0]['line']['color'] = '#0000ff'
    fig_l['data'][1]['line']['color'] = '#ff00ff'
    fig_l['data'][2]['line']['color'] = '#00ffff'

    fig_r['data'][0]['line']['color'] = '#0000ff'
    fig_r['data'][1]['line']['color'] = '#ff00ff'
    fig_r['data'][2]['line']['color'] = '#00ffff'

    lines = [fig_l['data'][x]['line']['color'] for x in range(3)]
    lines += [fig_r['data'][x]['line']['color'] for x in range(3)]
    df_left_an_x = df[df['anL1'] == True].index
    for h in Lhead:
        fig_l.add_trace(px.scatter(x=df_left_an_x, y=df[df['anL1'] == True][h], color_discrete_sequence=['red']).data[0])
    for h in Rhead:
        fig_r.add_trace(px.scatter(x=df_left_an_x, y=df[df['anL1'] == True][h], color_discrete_sequence=['red']).data[0])

    try: 
        patient_details = getPatientDetails(ser.get_mesurment_for_patient(patient_id))
    except:
        patient_details = getPatientDetails({"birthdate": "1997", "disabled": False, "id": 1, "lastname": "Kowalski", "firstname": "Jan", "trace_name": "test", "anL1": 0, "anL2": 0, "anL3": 0, "anR1": 0, "anR2": 0, "anR3": 0, "R1": 0, "R2": 0, "R3": 0, "L1": 0, "L2": 0, "L3": 0})
    return fig_r, fig_l, patient_details


@app.callback([
    Output('table', 'children'),
    Output('feet-image-container', 'children'),
    Output('memory', 'data'),
    Output('time-stamp', 'children'),
    Output('interval', 'interval'),

    Input('interval', 'n_intervals'),
    Input('replay', 'n_clicks'),
    Input('connect', 'n_clicks'),
    Input('reset', 'n_clicks'),
    Input('stop', 'n_clicks'),

    Input('prev', 'n_clicks'),
    Input('next', 'n_clicks'),
    Input('playback-speed', 'value'),

    Input('patient_id', 'value'),
    State('memory', 'data')
])
def table_controll(interval, replay, connect, reset, stop, prev, next, playback, patient_id, data):
    data = data or {"replay": "stopped", "row-time-stamp": None}
    el = dash.ctx.triggered_id
    if el == 'replay':
        data["replay"] = "playing"
    elif el == 'stop':
        ser.should_run = False
        data["replay"] = "stopped"
    elif el == 'reset':
        data["replay"] = "stopped"
    elif el == 'connect':
        ser.should_run = True
        data["replay"] = "connect"
    elif el == 'prev':
        data["replay"] = "stopped"
        ser.replay_prev()
    elif el == 'next':
        ser.replay_next()
        data["replay"] = "stopped"
    row = None

    if el != 'playback-speed':
        try:
            if data["replay"] == "stopped":
                row = ser.replay_row()
            elif data["replay"] == "reset":
                row = ser.replay_reset()
            elif data["replay"] == "playing":
                row = ser.replay_next()
            elif data["replay"] == "connect":
                row = ser.get_row(patient_id)
        except:
            row = {'birthdate': '1997', 'disabled': False, 'id': 1, 'lastname': 'Kowalski', 'firstname': 'Jan', 'trace_name': 'test', 'anL1': 0, 'anL2': 0, 'anL3': 0, 'anR1': 0, 'anR2': 0, 'anR3': 0, 'R1': 0, 'R2': 0, 'R3': 0, 'L1': 0, 'L2': 0, 'L3': 0}
    else:
        row = ser.replay_row()

    if "time-stamp" not in row.keys():
        row["time-stamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["row-time-stamp"] = row["time-stamp"]
    elif "time-stamp" not in row.keys() and data["replay"] == "stopped":
        row["time-stamp"] = data["row-time-stamp"]
    

    return getTable(row), getFeetImage(row), data, row["time-stamp"], playback * 1000


if __name__ == "__main__":
    app.run_server(debug=True)