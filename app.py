import dash
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_html_components as html

import numpy as np
import dash_core_components as dcc
import plotly.graph_objs as go
from scipy import signal
from time import sleep
import os

app = dash.Dash()

app.scripts.config.serve_locally = True
# app.config['suppress_callback_exceptions'] = True

server = app.server

tabs = [
    {'label': 'Run #{}'.format(i), 'value': i} for i in range(1, 2)
]

tab = 1

runs = {}

app.layout = html.Div(id='container', children=[
    # Function Generator Panel - Left
    html.Div([
        html.H2("Dash DAQ: Function Generator & Oscilloscope Control Panel",
                style={'marginLeft': '40px'}),
    ], className='banner', id='header'),

    html.Div([
        html.Div([
            html.Div([
                html.H3("POWER", id="power_title")
            ], className='Title'),
            html.Div([
                html.Div(
                    [
                        daq.PowerButton(
                            id='fnct_power',
                            on='true',
                            label="Function Generator",
                            labelPosition='bottom',
                            color="#447EFF"),
                    ],
                    className='six columns',
                    style={'margin-bottom': '15px'}),
                html.Div(
                    [
                        daq.PowerButton(
                            id='osc_power',
                            on='true',
                            label="Oscilloscope",
                            labelPosition='bottom',
                            color="#447EFF")
                    ],
                    className='six columns',
                    style={'margin-bottom': '15px'}),
            ], style={'margin': '15px 0'})
        ], className='row power-settings-tab'),
        html.Div([
            html.Div(
                [html.H3("FUNCTION", id="function_title")],
                className='Title'),
            html.Div([
                daq.Knob(
                    value=1E6,
                    id="frequency_input",
                    label="Frequency (Hz)",
                    labelPosition="bottom",
                    size=75,
                    color="#447EFF",
                    scale={'interval': 1E5},
                    max=2.5E6,
                    min=1E5,
                    className='four columns'
                ),
                daq.Knob(
                    value=1,
                    id="amplitude_input",
                    label="Amplitude (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color="#447EFF",
                    max=10,
                    className='four columns'
                ),
                daq.Knob(
                    value=0,
                    id="offset_input",
                    label="Offset (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color="#447EFF",
                    max=10,
                    className='four columns'
                )], style={'marginLeft': '20%', 'textAlign': 'center'}),
            html.Div([
                daq.LEDDisplay(
                    id='frequency_display',
                    size=10, value=1E6,
                    label="Frequency (Hz)",
                    labelPosition="bottom",
                    color="#447EFF",
                    style={'marginBottom': '30px'},
                    className='four columns'),
                daq.LEDDisplay(
                    id='amplitude_display',
                    size=10,
                    value=1,
                    label="Amplitude (mV)",
                    labelPosition="bottom",
                    color="#447EFF",
                    className='four columns'),
                daq.LEDDisplay(
                    id='offset_display',
                    size=10,
                    value=10,
                    label="Offset (mV)",
                    labelPosition="bottom",
                    color="#447EFF",
                    className='four columns'),
            ], style={'marginLeft': '20%', 'textAlign': 'center'}),
            dcc.RadioItems(
                id='function_type',
                options=[
                    {'label': 'Sine', 'value': 'SIN'},
                    {'label': 'Square', 'value': 'SQUARE'},
                    {'label': 'Ramp', 'value': 'RAMP'},
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
        daq.ToggleSwitch(
            id='theme_toggle',
            label=["Light","Dark"],
            color="#2a3f5f",
            value=False,
            style={'width': '60%', 'margin': '0px auto'}
        ),
        daq.ColorPicker(
            id="color_picker",
            label="Color Picker",
            value=dict(hex="#447EFF"),
            size=164,
            theme={'dark': True}
        ),
    ], className='four columns left-panel'),

    # Oscillator Panel - Right
    html.Div([
        html.Div([html.H3("GRAPH", id="graph_title")], className='Title'),
        dcc.Tabs(
            tabs=tabs,
            value=1,
            id='tabs',
            style={'backgroundColor': '#447EFF', 'height': '80%'},
        ),

        html.Div([
            html.Div([
                         html.Div([
                            html.Div(id="graph_info", style = {'textAlign': 'center', 'fontSize': '16px', 'padding': '0px 5px', 'lineHeight': '20px', 'border': '2px solid #447EFF'}),
                         ], className="row graph-param"),
                ], className="six columns"),
            html.Button('+',
                        id='new_tab',
                        type='submit',
                        style={'height': '20px', 'width': '20px',
                               'padding': '2px', 'lineHeight': '10px',
                               'float': 'right'}),
        ], className='row oscope-info', style={'margin': '15px'}),
        html.Hr(),
        dcc.Graph(
            id='oscope',
            figure=dict(
                data=[dict(x=np.linspace(-0.000045, 0.000045, 1e3),
                           y=[0] * len(np.linspace(-0.000045, 0.000045, 1e3)),
                           marker={'color': '#2a3f5f'})],
                layout=go.Layout(
                    xaxis={'title': 's', 'color': '#506784', 'titlefont': dict(
                        family='Dosis',
                        size=15,
                    )},
                    yaxis={'title': 'Voltage (V)', 'color': '#506784', 'titlefont': dict(
                        family='Dosis',
                        size=15,
                    ), 'autorange': False, 'range': [-10, 10]},
                    margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                    plot_bgcolor='#F3F6FA',
                )
            ),
            config={'displayModeBar': True,
                    'modeBarButtonsToRemove': ['pan2d',
                                               'zoomIn2d',
                                               'zoomOut2d',
                                               'autoScale2d',
                                               'hoverClosestCartesian',
                                               'hoverCompareCartesian']}
        )
    ], className='seven columns right-panel')
])


# Callbacks for dark theme toggle
@app.callback(Output('frequency_input', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_frequency_input(value):
    return dict(dark = value)


@app.callback(Output('amplitude_input', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_amplitude_input(value):
    return dict(dark = value)


@app.callback(Output('offset_input', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_offset_input(value):
    return dict(dark = value)


@app.callback(Output('frequency_display', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_frequency_display(value):
    return dict(dark = value)


@app.callback(Output('amplitude_display', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_amplitude_display(value):
    return dict(dark = value)


@app.callback(Output('offset_display', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_offset_display(value):
    return dict(dark = value)


@app.callback(Output('color_picker', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_color_picker(value):
    return dict(dark = value)


@app.callback(Output('theme_toggle', 'theme'),
              [Input('theme_toggle', 'value')])
def dark_toggle(value):
    return dict(dark = value)


# Callbacks for color picker
@app.callback(Output('frequency_input', 'color'),
              [Input('color_picker', 'value')])
def color_frequency_input(color):
    return color['hex']


@app.callback(Output('amplitude_input', 'color'),
              [Input('color_picker', 'value')])
def color_amplitude_input(color):
    return color['hex']


@app.callback(Output('offset_input', 'color'),
              [Input('color_picker', 'value')])
def color_offset_input(color):
    return color['hex']


@app.callback(Output('frequency_display', 'color'),
              [Input('color_picker', 'value')])
def color_frequency_display(color):
    return color['hex']


@app.callback(Output('amplitude_display', 'color'),
              [Input('color_picker', 'value')])
def color_amplitude_display(color):
    return color['hex']


@app.callback(Output('offset_display', 'color'),
              [Input('color_picker', 'value')])
def color_offset_display(color):
    return color['hex']


@app.callback(Output('graph_info', 'style'),
              [Input('color_picker', 'value')])
def color_tabs_background(color):
    return {'textAlign': 'center', 'border': "2px solid " + color['hex']}


@app.callback(Output('tabs', 'style'),
              [Input('color_picker', 'value')])
def color_tabs_background(color):
    return {'backgroundColor': color['hex']}


@app.callback(Output('power_title', 'style'),
              [Input('color_picker', 'value')])
def color_power_title(color):
    return {'color': color['hex']}


@app.callback(Output('function_title', 'style'),
              [Input('color_picker', 'value')])
def color_function_title(color):
    return {'color': color['hex']}


@app.callback(Output('graph_title', 'style'),
              [Input('color_picker', 'value')])
def color_graph_title(color):
    return {'color': color['hex']}


@app.callback(Output('fnct_power', 'color'),
              [Input('color_picker', 'value')])
def color_fnct_power(color):
    return color['hex']


@app.callback(Output('osc_power', 'color'),
              [Input('color_picker', 'value')])
def color_osc_power(color):
    return color['hex']


@app.callback(Output('header', 'style'),
              [Input('color_picker', 'value')])
def color_banner(color):
    return {'backgroundColor': color['hex']}


# Callbacks for knob inputs
@app.callback(Output('amplitude_display', 'value'),
              [Input('amplitude_input', 'value')],)
def update_amplitude_display(value):
    return value


@app.callback(Output('frequency_display', 'value'),
              [Input('frequency_input', 'value')],)
def update_frequency_display(value):
    return value


@app.callback(Output('offset_display', 'value'),
              [Input('offset_input', 'value')])
def update_offset_display(value):
    return value


# Callbacks graph and graph info
@app.callback(Output('graph_info', 'children'),
              [Input('oscope', 'figure'),
               Input('tabs', 'value')])
def update_wave(_, value):
    if '' + str(value) in runs:
        return (runs['' + str(value)][1])
    return "-"


@app.callback(Output('oscope', 'figure'),
              [Input('tabs', 'value'),
               Input('frequency_input', 'value'),
               Input('function_type', 'value'),
               Input('amplitude_input', 'value'),
               Input('offset_input', 'value'),
               Input('osc_power', 'on'),
               Input('fnct_power', 'on')])
def update_output(value, frequency, wave, amplitude, offset, osc_on, fnct_on):
    global tab
    time = np.linspace(-0.000045, 0.000045, 1e3)
    zero = dict(
        data=[dict(x=time, y=[0] * len(time), marker={'color': '#2a3f5f'})],
        layout=go.Layout(
            xaxis={'title': 's', 'color': '#506784', 'titlefont': dict(
                family='Dosis',
                size=15,
            )},
            yaxis={'title': 'Voltage (V)', 'color': '#506784', 'titlefont': dict(
                family='Dosis',
                size=15,
            )},
            margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
            plot_bgcolor='#F3F6FA',
        )
    )

    if not osc_on:
        return dict(
            data=[],
            layout=go.Layout(
                xaxis={'title': 's', 'color': '#506784', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'showticklabels': False, 'ticks': '', 'zeroline': False},
                yaxis={'title': 'Voltage (V)', 'color': '#506784', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'showticklabels': False, 'zeroline': False},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='#506784',
            )
        )

    if not fnct_on:
        return zero

    if tab is not value:
        if '' + str(value) in runs:
            tab = value
            return runs['' + str(value)][0]
        tab = value
        return zero

    else:
        if wave == 'SIN':
            y = [float(offset) +
                 (float(amplitude) *
                  np.sin(np.radians(2.0 * np.pi * float(frequency) * t)))
                 for t in time]

        elif wave == 'SQUARE':
            y = [float(offset) +
                 float(amplitude) *
                 (signal.square(2.0 * np.pi * float(frequency)/10 * t))
                 for t in time]

        elif wave == 'RAMP':
            y = float(amplitude) * \
                (np.abs(signal.sawtooth(2*np.pi * float(frequency)/10 * time)))
            y = float(offset) + 2*y - float(amplitude)

        figure = dict(
            data=[dict(x=time, y=y, marker={'color': '#2a3f5f'})],
            layout=go.Layout(
                xaxis={'title': 's', 'color': '#506784', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                )},
                yaxis={'title': 'Voltage (V)', 'color': '#506784', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'autorange': False, 'range': [-10, 10]},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='#F3F6FA',
            )
        )

        runs['' + str(value)] = figure, str(wave) + " | " + str(frequency) +  \
             "Hz" + " | " + str(amplitude) + "mV" + " | " + str(offset) + "mV"

        # wait to update the runs variable
        sleep(0.10)

        return figure


@app.callback(Output('tabs', 'tabs'),
              [Input('new_tab', 'n_clicks')])
def new_tabs(n_clicks):
    if n_clicks is not None:
        tabs.append({'label': 'Run #' + str(tabs[-1]['value'] + 1),
                     'value': int(tabs[-1]['value']) + 1})
        return tabs
    return tabs


external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                "https://cdn.rawgit.com/samisahn/dash-app-stylesheets/2ce724f9/dash-tektronix-350.css",
                "https://fonts.googleapis.com/css?family=Dosis"]

for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

if __name__ == '__main__':
    app.run_server(port=8000, debug=True)
