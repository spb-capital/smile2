import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output, Event
import plotly.graph_objs as go
import dash
from scipy import signal
import dash_daq as daq

app = dash.Dash()

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

server = app.server

tabs = [
    {'label': 'Run #{}'.format(i), 'value': i} for i in range(1, 2)
]

tab = 1

runs = {}

app.layout = html.Div([

# LEFT SIDE
    html.Div([
        html.H2("Dash Instrumentation"),
    ], className='banner'),
    html.Div('', id = 'settings1'),
    html.Div('', id = 'settings2'),
    html.Div('', id = 'settings3'),
    html.Div([
        html.Div([
                html.Div([
                    html.H3("POWER")
                ], className='Title'),
                html.Div([
                    html.Div([daq.PowerButton(id = 'fnct_power', on = 'true', label = "FNCT", labelPosition = 'bottom')], className = 'six columns', style = {'margin-bottom': '15px'}),
                    html.Div([daq.PowerButton(id = 'osc_power', on = 'true', label = "OSC", labelPosition = 'bottom')], className = 'six columns', style = {'margin-bottom': '15px'}),
                ], style = {'margin': '15px 0'})
                ], className='row power-settings-tab'),
        html.Div([
                html.Div([
                    html.H3("FUNCTION")
                ], className = 'Title'),
                html.Div([
                    "Frequency (Hz)",
                    # daq.PrecisionInput(precision = 2, value = 10E5, style = {'float': 'right'}),
                    # dcc.Input(id='frequency_input', type='text', value = 10E5, style = {'float': 'right', 'textAlign': 'center'}),
                    daq.PrecisionInput(id = 'frequency_input', precision = 4, value = 1E6, min = 1E3, max = 2.5E6, size = 100, style = {'float': 'right'}),
                ], style = {'margin': '15px 0'}),
                html.Div([
                    "Amplitude (μm)",
                    daq.PrecisionInput(id = 'amplitude_input', precision = 4, value = 1, min = 0.5, max = 10, size = 100, style = {'float': 'right'}),
                ], style = {'margin': '20px 0'}),
                html.Div([
                    "Offset (μm)",
                    daq.PrecisionInput(id = 'offset_input', precision = 4, value = 0, min = 0.5, max = 10, size = 100, style = {'float': 'right'}),
                ], style = {'margin': '20px 0'}),
                dcc.RadioItems(
                    id = 'function_type',
                    options=[
                        {'label': 'Sine', 'value': 'SIN'},
                        {'label': 'Square', 'value': 'SQUARE'},
                        {'label': 'Ramp', 'value': 'RAMP'},
                        # {'label': 'Pulse', 'value': 'PULSE'},
                    ],
                    value='SIN',
                    labelStyle={'display': 'inline-block'},
                    style = {'margin': '0 auto',
                    'display': 'flex',
                    'width': '80%',
                    'alignItems': 'center',
                    'justifyContent': 'space-between'}
                )
            ], className='row power-settings-tab'),
        html.Hr(),
        html.Button('Update', id='setting_submit', type = 'submit'),
    ], className = 'four columns left-tab'),


# RIGHT SIDE
    html.Div([
        html.Div([html.H3("GRAPH"),], className = 'Title'),

        dcc.Tabs(
            tabs = tabs,
            value = 1,
            id = 'tabs',
            style={'backgroundColor': '#119DFF', 'height': '80%'},
        ),
        html.Div([
            html.Div([daq.Indicator(id="fnct_indicator")], className = "one columns"),
            html.Div([daq.Indicator(id="osc_indicator")], className = "one columns"),
            html.Button('-', id='del_tab', type = 'submit', style = {'height': '20px', 'width': '20px', 'padding': '0px', 'lineHeight': '10px', 'float': 'right', 'margin-left': '10px'}),
            html.Button('+', id='new_tab', type = 'submit', style = {'height': '20px', 'width': '20px', 'padding': '0px', 'lineHeight': '10px', 'float': 'right'}),

        ], className='row graph-info', style = {'margin': '15px'}),
        html.Div(id = 'tab-output'),
        dcc.Graph(
            id='oscope',
            figure=
            {
                'data': dict(
                        data = [dict(x = np.linspace(-0.000045, 0.000045, 1e5), y = [0] * len(np.linspace(-0.000045, 0.000045, 1e5)))],
                        layout =  go.Layout(
                            xaxis={'type': 'linear', 'title': 's'},
                            yaxis={'title': 'Voltage (V)'},
                            margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                            plot_bgcolor = 'rgb(240, 240, 240)',
                        )
                    ),
                'layout': go.Layout(
                    xaxis={'type': 'linear', 'title': 's'},
                    yaxis={'title': 'Voltage (V)'},
                    margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                    plot_bgcolor = 'rgb(240, 240, 240)',
                )
            }
        ),], className = 'seven columns graph'),
])

@app.callback(Output('tabs', 'tabs'),
            [Input('new_tab', 'n_clicks')])
def new_tabs(n_clicks):
    tabs.append({'label': 'Run #' + str(tabs[-1]['value'] + 1), 'value': int(tabs[-1]['value']) + 1})
    return tabs

@app.callback(Output('oscope', 'figure'),
            [Input('setting_submit', 'n_clicks'),
             Input('tabs', 'value')],
            [State('frequency_input', 'value'),
            State('function_type', 'value'),
            State('amplitude_input', 'value'),
            State('offset_input', 'value'),
             ])
def update_output(n_clicks, value, frequency, wave, amplitude, offset):
    global tab
    time = np.linspace(-0.000045, 0.000045, 1e5)
    zero = dict(
            data = [dict(x = time, y = [0] * len(time))],
            layout =  go.Layout(
                xaxis={'type': 'linear', 'title': 's'},
                yaxis={'title': 'Voltage (V)'},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor = 'rgb(240, 240, 240)',
            )
        )

    if n_clicks is not None:
        if tab is not value:
            if('' + str(value) in runs):
                tab = value
                return runs['' + str(value)]
            else:
                tab = value
                return zero

        else:
            if(wave == 'SIN'):
                y = [float(offset) + (float(amplitude) * np.sin(np.radians(2.0 * np.pi * float(frequency) * t))) for t in time]

            elif(wave == 'SQUARE'):
                y = [float(offset) + float(amplitude) *(signal.square(2.0 * np.pi * float(frequency)/10 * t)) for t in time]

            elif(wave == 'RAMP'):
                y = float(amplitude) * (np.abs(signal.sawtooth(2 * np.pi * float(frequency)/10 * time)))
                y = float(offset) + 2*y - float(amplitude)

            figure = dict(
                    data = [dict(x = time, y = y)],
                    layout =  go.Layout(
                        xaxis={'type': 'linear', 'title': 's'},
                        yaxis={'title': 'Voltage (V)'},
                        margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                        plot_bgcolor = 'rgb(240, 240, 240)',
                    )
                )

            runs['' + str(value)] = figure

            return figure


@app.callback(
    Output('fnct_indicator', 'value'),
    [Input('fnct_power', 'on')])
def fnct_indication(on):
    return on

@app.callback(
    Output('osc_indicator', 'value'),
    [Input('osc_power', 'on')])
def osc_indication(on):
    return on


external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                "https://rawgit.com/samisahn/dash-app-stylesheets/master/dash-instrumentation.css",
                "https://fonts.googleapis.com/css?family=Dosis"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(port = 8000, debug = True)
