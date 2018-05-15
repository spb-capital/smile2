import dash
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_html_components as html

import numpy as np
import dash_core_components as dcc
import plotly.graph_objs as go
from scipy import signal


app = dash.Dash()

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

server = app.server

tabs = [
    {'label': 'Run #{}'.format(i), 'value': i} for i in range(1, 2)
]

tab = 1

runs = {}

app.layout = html.Div(id='container', children=[
    # LEFT SIDE
    html.Div([
        html.H2("Dash DAQ: Function Generator & Oscilloscope Control Panel", style={'marginLeft': '40px'}),
    ], className='banner'),

    html.Div([
        html.Div([
            html.Div([
                html.H3("POWER")
            ], className='Title'),
            html.Div([
                html.Div([daq.PowerButton(id='fnct_power', on='true', label="Function Generator", labelPosition='bottom')], className='six columns', style={'margin-bottom': '15px'}),
                html.Div([daq.PowerButton(id='osc_power', on='true', label="Oscilloscope", labelPosition='bottom')], className='six columns', style={'margin-bottom': '15px'}),
            ], style={'margin': '15px 0'})
        ], className='row power-settings-tab'),
        html.Div([
            html.Div([
                html.H3("FUNCTION")
            ], className='Title'),
            html.Div([
                daq.Knob(
                    value=1E6,
                    id="frequency_input",
                    label="Frequency (Hz)",
                    labelPosition="bottom",
                    size=75,
                    color='rgb(68, 126, 255)',
                    # add custom ticks
                    scale={'interval': 1E5, 'custom': {'2.5E6': {'label': '2.5E6', 'style': {'color': 'red'}}}},
                    max=2.5E6,
                    min=1E5
                ),
                daq.Knob(
                    value=1,
                    id="amplitude_input",
                    label="Amplitude (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color='rgb(68, 126, 255)',
                    max=10,
                ),
                daq.Knob(
                    value=0,
                    id="offset_input",
                    label="Offset (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color='rgb(68, 126, 255)',
                    max=10,
                )],
                     style={'margin': '0 auto',
                            'display': 'flex',
                            'width': '80%',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                           }),
            # fix updates
            html.Div(id="hidden-freq", style={'display': 'none'}),
            html.Div(id="hidden-ampl", style={'display': 'none'}),
            html.Div(id="hidden-off", style={'display': 'none'}),
            #
            html.Div([
                daq.PrecisionInput(id='freq', size=75, precision=4, value=1E6, min=1E5, max=2.5E6, label="Frequency (Hz)", labelPosition="bottom"),
                daq.PrecisionInput(id='ampl', size=75, precision=4, value=1, min=0.5, max=10, label="Amplitude (mV)", labelPosition="bottom"),
                daq.PrecisionInput(id='off', size=75, precision=4, value=0, min=0, max=10, label="Offset (mV)", labelPosition="bottom"),
            ], style={'margin': '0 auto',
                      'display': 'flex',
                      'width': '80%',
                      'alignItems': 'center',
                      'justifyContent': 'space-between'
                     }),
            dcc.RadioItems(
                id='function_type',
                options=[
                    {'label': 'Sine', 'value': 'SIN'},
                    {'label': 'Square', 'value': 'SQUARE'},
                    {'label': 'Ramp', 'value': 'RAMP'},
                    # {'label': 'Pulse', 'value': 'PULSE'},
                ],
                value='SIN',
                labelStyle={'display': 'inline-block'},
                style={'margin': '30px auto 0px auto',
                       'display': 'flex',
                       'width': '80%',
                       'alignItems': 'center',
                       'justifyContent': 'space-between'}
                )
            ], className='row power-settings-tab'),
        html.Hr(),
        # html.Button('Update', id='setting_submit', type = 'submit'),
    ], className='four columns left-tab'),


    # RIGHT SIDE
    html.Div([
        html.Div([html.H3("GRAPH"),], className='Title'),
        dcc.Tabs(
            tabs=tabs,
            value=1,
            id='tabs',
            style={'backgroundColor': '#119DFF', 'height': '80%'},
        ),

        html.Div([
            # html.Div([daq.Indicator(id="fnct_indicator", label="FNCT", labelPosition = "bottom",)], className="one columns"),
            # html.Div([daq.Indicator(id="osc_indicator", label="OSC", labelPosition = "bottom")], className="one columns"),
            html.Div([html.Div("NO DATA", id="details", style={'textAlign': 'center', 'fontSize': '10px', 'padding': '0px 5px', 'lineHeight': '20px', 'border': '2px solid rgb(240, 240, 240)'})], className="four columns"),
            html.Div(id="curr_info"),
            html.Button('-', id='del_tab', type='submit', style={'height': '20px', 'width': '20px', 'padding': '0px', 'lineHeight': '10px', 'float': 'right', 'margin-left': '10px'}),
            html.Button('+', id='new_tab', type='submit', style={'height': '20px', 'width': '20px', 'padding': '0px', 'lineHeight': '10px', 'float': 'right'}),
        ], className='row graph-info', style={'margin': '15px'}),
        html.Hr(),
        dcc.Graph(
            id='oscope',
            figure=dict(
                data=[dict(x=np.linspace(-0.000045, 0.000045, 1e3), y=[0] * len(np.linspace(-0.000045, 0.000045, 1e3)), marker={'color': 'rgb(68, 126, 255)'})],
                layout=go.Layout(
                    xaxis={'type': 'linear', 'title': 's', 'titlefont': dict(
                        family='Dosis',
                        size=15,
                    )},
                    yaxis={'title': 'Voltage (V)', 'titlefont': dict(
                        family='Dosis',
                        size=15,
                    )},
                    margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                    plot_bgcolor='rgb(240, 240, 240)',
                )
            ),
            config={'displayModeBar': False}
        )
    ], className='seven columns graph'),
])

@app.callback(Output('hidden-ampl', 'children'),
              [Input('amplitude_input', 'value')])
def update_hidden_ampl(value):
    return str(value)

@app.callback(Output('ampl', 'value'),
              [Input('hidden-ampl', 'children')],)
def update_amplPI(value):
    return float(value)

@app.callback(Output('hidden-freq', 'children'),
              [Input('frequency_input', 'value')])
def update_hidden_freq(value):
    return str(value)

@app.callback(Output('freq', 'value'),
              [Input('hidden-freq', 'children')],)
def update_freqPI(value):
    return float(value)

@app.callback(Output('hidden-off', 'children'),
              [Input('offset_input', 'value')])
def update_hidden_off(value):
    return str(value)

@app.callback(Output('off', 'value'),
              [Input('hidden-off', 'children')],)
def update_offPI(value):
    return float(value)

@app.callback(Output('details', 'children'),
              [Input('oscope', 'figure'),
               Input('tabs', 'value')])
def update_details(_, value):
    if '' + str(value) in runs:
        return runs['' + str(value)][1]
    return "NO DATA"

@app.callback(Output('oscope', 'figure'),
              [Input('tabs', 'value'),
               Input('frequency_input', 'value'),
               Input('function_type', 'value'),
               Input('amplitude_input', 'value'),
               Input('offset_input', 'value'),
               Input('osc_power', 'on'),
               Input('fnct_power', 'on')])
def update_output(value, frequency, wave, amplitude, offset, osc_on, fnct_power):
    global tab

    time = np.linspace(-0.000045, 0.000045, 1e3)
    zero = dict(
        data=[dict(x=time, y=[0] * len(time), marker={'color': 'rgb(68, 126, 255)'})],
        layout=go.Layout(
            xaxis={'type': 'linear', 'title': 's', 'titlefont': dict(
                family='Dosis',
                size=15,
            )},
            yaxis={'title': 'Voltage (V)', 'titlefont': dict(
                family='Dosis',
                size=15,
            )},
            margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
            plot_bgcolor='rgb(240, 240, 240)',
        )
    )

    if not osc_on:
        return dict(
            data=[],
            layout=go.Layout(
                xaxis={'type': 'linear', 'title': 's', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'showticklabels': False, 'ticks': '', 'zeroline': False},
                yaxis={'title': 'Voltage (V)', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'showticklabels': False, 'zeroline': False},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='rgb(0, 0, 0)',
            )
        )

    # check
    if not fnct_power:
        return zero

    # if n_clicks is not None:
    if tab is not value:
        if '' + str(value) in runs:
            tab = value
            return runs['' + str(value)][0]
        tab = value
        return zero

    else:
        if wave == 'SIN':
            y = [float(offset) + (float(amplitude) * np.sin(np.radians(2.0 * np.pi * float(frequency) * t))) for t in time]

        elif wave == 'SQUARE':
            y = [float(offset) + float(amplitude) *(signal.square(2.0 * np.pi * float(frequency)/10 * t)) for t in time]

        elif wave == 'RAMP':
            y = float(amplitude) * (np.abs(signal.sawtooth(2 * np.pi * float(frequency)/10 * time)))
            y = float(offset) + 2*y - float(amplitude)

        figure = dict(
            data=[dict(x=time, y=y, marker={'color': 'rgb(68, 126, 255)'})],
            layout=go.Layout(
                xaxis={'type': 'linear', 'title': 's', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                )},
                yaxis={'title': 'Voltage (V)', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                )},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='rgb(240, 240, 240)',
            )
        )

        runs['' + str(value)] = figure, str(wave) + "      " + str(frequency) +  " Hz" + "      " + str(amplitude) + "mV"

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

@app.callback(Output('tabs', 'tabs'),
              [Input('new_tab', 'n_clicks')])
def new_tabs(n_clicks):
    if n_clicks is not None:
        tabs.append({'label': 'Run #' + str(tabs[-1]['value'] + 1), 'value': int(tabs[-1]['value']) + 1})
        return tabs
    return tabs

external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                "https://cdn.rawgit.com/samisahn/dash-app-stylesheets/09e3a2ee/dash-tektronix-350.css",
                "https://fonts.googleapis.com/css?family=Dosis"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(port=8000, debug=True)
