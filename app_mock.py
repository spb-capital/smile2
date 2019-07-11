import dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash_daq import DarkThemeProvider
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate

import numpy as np
import plotly.graph_objs as go
from scipy import signal
from time import sleep

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True
server = app.server

font_color = {'dark': '#ffffff', 'light': "#222"}
background_color = {'dark': '#2a3f5f', 'light': '#ffffff'}
title_color = {'dark': '#ffffff', 'light': '#447EFF'}
axis_color = {'dark': '#EBF0F8', 'light': '#506784'}
marker_color = {'dark': '#f2f5fa', 'light': '#2a3f5f'}

theme = {
    'dark': False,
    'primary': '#447EFF',
    'secondary': '#D3D3D3',
    'detail': '#D3D3D3'
}

tab = '1'


def header():
    return html.Div(
        id='header',
        className='banner',
        style={'backgroundColor': '#447EEF'},
        children=[
            html.H2(
                "Dash DAQ: Function Generator & Oscilloscope Control Panel",
                style={
                    'color': 'white',
                    'marginLeft': '40px',
                    'display': 'inline-block',
                    'text-align': 'center'
                }
            ),
            html.Img(
                src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/" +
                    "excel/dash-daq/dash-daq-logo-by-plotly-stripe+copy.png",
                style={
                    'position': 'relative',
                    'float': 'right',
                    'right': '10px',
                    'height': '75px'
                }
            )
        ]
    )


def Knobs():
    return html.Div([
        daq.Knob(
            value=1000000,
            id="frequency-input",
            label="Frequency (Hz)",
            labelPosition="bottom",
            size=75,
            color=theme['primary'],
            scale={'interval': 100000},
            max=2500000,
            min=100000,
            className='four columns'
        ),
        daq.Knob(
            value=1,
            id="amplitude-input",
            label="Amplitude (mV)",
            labelPosition="bottom",
            size=75,
            scale={'labelInterval': 10},
            color=theme['primary'],
            max=10,
            min=0,
            className='four columns'
        ),
        daq.Knob(
            value=0,
            id="offset-input",
            label="Offset (mV)",
            labelPosition="bottom",
            size=75,
            scale={'labelInterval': 10},
            color=theme['primary'],
            max=10,
            min=0,
            className='four columns'
        )
    ],
        style={'marginLeft': '20%', 'textAlign': 'center'})


def led_displays():
    return html.Div([
        daq.LEDDisplay(
            id='frequency-display',
            size=10, value=1E6,
            label="Frequency (Hz)",
            labelPosition="bottom",
            color=theme['primary'],
            style={'marginBottom': '30px'},
            className='four columns'),
        daq.LEDDisplay(
            id='amplitude-display',
            size=10,
            value=1,
            label="Amplitude (mV)",
            labelPosition="bottom",
            color=theme['primary'],
            className='four columns'),
        daq.LEDDisplay(
            id='offset-display',
            size=10,
            value=10,
            label="Offset (mV)",
            labelPosition="bottom",
            color=theme['primary'],
            className='four columns'),
    ], style={'marginLeft': '20%', 'textAlign': 'center'})


def radioitem():
    return dcc.RadioItems(
        id='function-type',
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


def power_setting_div(cur_input, cur_tab):
    return html.Div(
        className='row power-settings-tab',
        children=[
            html.Div(
                className='Title',
                children=html.H3("Power", id='power-title', style={'color': theme['primary']})),
            html.Div(
                # power-controllers
                [
                    html.Div(
                        [
                            daq.PowerButton(
                                id='function-generator',
                                on=True,
                                label="Function Generator",
                                labelPosition='bottom',
                                color=theme['primary']),
                        ],
                        className='six columns',
                        style={'margin-bottom': '15px'}),
                    html.Div(
                        [
                            daq.PowerButton(
                                id='oscilloscope',
                                on=True,
                                label="Oscilloscope",
                                labelPosition='bottom',
                                color=theme['primary'])
                        ],
                        className='six columns',
                        style={'margin-bottom': '15px'}),
                ],
                style={'margin': '15px 0'}
            )
        ]
    )


def function_setting_div(cur_input, cur_tab):
    return html.Div(
        className='row power-settings-tab',
        children=[
            html.Div(
                className='Title',
                style={'color': theme['primary']},
                children=html.H3("Function", id='function-title')),
            # Knobs
            Knobs(),
            # LED Displays
            led_displays(),
            # # RadioItems
            radioitem()
        ]
    )


app.layout = html.Div(
    id='main-page',
    className='container',
    children=[
        # toggle
        html.Div(
            id='toggleDiv',
            style={
                'width': 'fit-content',
                'margin': '0 auto'
            },
            children=[
                daq.ToggleSwitch(
                    id='toggleTheme',
                    style={
                        'position': 'absolute',
                        'transform': 'translate(-50%, 20%)',
                        'z-index': '9999'
                    },
                    size=30,
                    value=False
                )
            ]
        ),
        # header
        header(),

        html.Div(
            children=html.Div(
                children=[
                    # Setting panel - left
                    html.Div(
                        className='five columns left-panel',
                        children=[
                            html.Div(
                                id='dark-theme-components',
                                children=DarkThemeProvider(
                                    theme=theme,
                                    children=[
                                        power_setting_div(None, '1'),
                                        function_setting_div(None, "1")
                                    ]
                                )
                            ),

                            daq.ColorPicker(
                                id="color-picker",
                                label="Color Picker",
                                value=dict(hex="#447EFF"),
                                size=164,
                                style={'marginTop': '20px'}
                            )
                        ]
                    ),
                    # Oscillator Panel - Right
                    html.Div(
                        className='seven columns right-panel',
                        children=[
                            html.Div([html.H3("Graph", id="graph-title")], style={'color': theme['primary']},
                                     className='Title'),

                            dcc.Tabs(
                                id='tabs',
                                children=[dcc.Tab(
                                    label='Run #1',
                                    value='1'
                                )],
                                value='1',
                                className='oscillator-tabs'
                            ),

                            html.Div(
                                className='row oscope-info',
                                children=[
                                    html.Div([
                                        html.Div([
                                            html.Div(
                                                id="graph-info",
                                                children="-",
                                                style={
                                                    'border': '1px solid' + theme['primary']}),
                                        ], className="row graph-param"),
                                    ], className="six columns"),
                                    html.Button(
                                        '+',
                                        id='new-tab',
                                        n_clicks=0,
                                        type='submit',
                                        style={'height': '20px', 'width': '20px',
                                               'padding': '2px', 'lineHeight': '10px',
                                               'float': 'right'})

                                ]
                            ),
                            html.Hr(),
                            dcc.Graph(id='oscope-graph', figure={})
                        ]
                    )
                ]
            )
        ),
        dcc.Store(id='tab-number', data=1),
        dcc.Store(id='runs', data={}),

        dcc.Store(id='control-inputs', data={}  # {tabs_number: {value1:x, value2:x}
                  )
    ]
)

# {'tab-1': {'func_on': True, 'osco': True,...},
# 'tab-2': {...},
# 'tab-3': ... }

# # update control values
# @app.callback(
#     Output("control-inputs", "data"),
#     [Input( controls...)],
#     [State("tabs', "value")]
# )
#
# # Update figure
# @app.callback(
#     Output(figure)
#     Input'control-input',
#     Input("tab", 'value')
# )


# Callback to update theme layout
@app.callback(
    Output("dark-theme-components", 'children'),
    [Input("toggleTheme", 'value'), Input("color-picker", "value")],
    [State("control-inputs", 'data'), State('tabs', 'value')]
)
def turn_dark(turn_dark, color_pick, cur_inputs, cur_tab_value):
    theme.update(dark=turn_dark)

    if color_pick is not None:
        theme.update(primary=color_pick['hex'])

    return DarkThemeProvider(
        theme=theme,
        children=[
            power_setting_div(cur_inputs, cur_tab_value),
            function_setting_div(cur_inputs, cur_tab_value)
        ]
    )


# Update colors upon color-picker changes
@app.callback(
    [
        Output('power-title', 'style'),
        Output('function-title', 'style'),
        Output('graph-title', 'style'),
        Output('graph-info', 'style'),
        Output('tabs', 'style'),
        Output('header', 'style'),
    ],
    [Input('color-picker', 'value')])
def color_update(color):
    return list({'color': color['hex']} for _ in range(3)) + [
        {'border': ("1px solid " + color['hex']), 'color': color['hex']}] + list(
        {'backgroundColor': color['hex']} for _ in range(2))


# Callback updating backgrounds
@app.callback(
    Output('main-page', 'style'),
    [Input("toggleTheme", 'value')]
)
def update_background(turn_dark):
    if turn_dark:
        return {'backgroundColor': background_color['dark'], 'color': font_color['dark']}
    else:
        return {'backgroundColor': background_color['light'], 'color': font_color['light']}


# Callbacks for knob inputs
@app.callback(Output('frequency-display', 'value'),
              [Input('frequency-input', 'value')], )
def update_frequency_display(value):
    return value


@app.callback(Output('amplitude-display', 'value'),
              [Input('amplitude-input', 'value')], )
def update_amplitude_display(value):
    return value


@app.callback(Output('offset-display', 'value'),
              [Input('offset-input', 'value')])
def update_offset_display(value):
    return value


@app.callback(
    Output('tab-number', 'data'),
    [Input("new-tab", 'n_clicks')],
    [State("tab-number", 'data')]
)
def update_total_tab_number(n_clicks, cur_total_tab):
    if n_clicks:
        return cur_total_tab + 1
    return cur_total_tab


# Update tabs
@app.callback(
    Output('tabs', 'children'),
    [Input('tab-number', 'data')]
)
def update_tabs(total_tab_number):
    return list(dcc.Tab(
        label='Run #{}'.format(i),
        value='{}'.format(i)
    ) for i in range(1, total_tab_number + 1))


# Make figure and save to running stats
@app.callback(
    [Output('oscope-graph', 'figure'), Output('runs', 'data')],
    [
        Input('tabs', 'value'),

        Input('frequency-input', 'value'),
        Input('function-type', 'value'),
        Input('amplitude-input', 'value'),
        Input('offset-input', 'value'),
        Input('oscilloscope', 'on'),
        Input('function-generator', 'on')
    ],
    [State("toggleTheme", "value"), State("runs", 'data'), State('oscope-graph', 'figure')]
)
def update_figure(sel_tab, frequency, wave, amplitude, offset, osc_on, fnct_on, theme, cur_runs, cur_fig):
    global axis_color, marker_color
    global tab
    theme_select = 'dark' if theme else 'light'
    axis = axis_color[theme_select]
    marker = marker_color[theme_select]
    time = np.linspace(-0.000045, 0.000045, 1000)
    base_figure = dict(
        data=[dict(x=time, y=[0] * len(time), marker={'color': marker})],
        layout=dict(xaxis=dict(title='s',
                               color=axis,
                               titlefont=dict(family='Dosis', size=13)),
                    yaxis=dict(title='Voltage (mV)',
                               color=axis,
                               range=[-10, 10],
                               titlefont=dict(family='Dosis', size=13)),
                    margin={'l': 40, 'b': 40, 't': 20, 'r': 50},
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)')
    )
    if not osc_on:
        base_figure.update(data=[])
        base_figure['layout']['xaxis'].update(showticklabels=False, showline=False, zeroline=False)
        base_figure['layout']['yaxis'].update(showticklabels=False, showline=False, zeroline=False)
        return base_figure, cur_runs

    if not fnct_on:
        return base_figure, cur_runs

    # todo: share figures bw themes when theme is toggled, problem: if toggletheme, input is fired again, so figure is updated
    # need to re-wire controller inputs in darktheme editor

    if tab is not sel_tab:
        if sel_tab in cur_runs:
            tab = sel_tab
            figure = cur_runs[sel_tab][0]
            figure['data'][0]['marker']['color'] = marker
            figure['layout']['xaxis']['color'] = figure['layout']['yaxis']['color'] = axis
            return figure, cur_runs
        tab = sel_tab
        return base_figure, cur_runs

    else:
        if wave == 'SIN':
            y = [float(offset) +
                 (float(amplitude) *
                  np.sin(np.radians(2.0 * np.pi * float(frequency) * t)))
                 for t in time]

        elif wave == 'SQUARE':
            y = [float(offset) +
                 float(amplitude) *
                 (signal.square(2.0 * np.pi * float(frequency) / 10 * t))
                 for t in time]

        elif wave == 'RAMP':
            y = float(amplitude) * \
                (np.abs(signal.sawtooth(2 * np.pi * float(frequency) / 10 * time)))
            y = float(offset) + 2 * y - float(amplitude)

        base_figure['data'][0].update(y=y)

        cur_runs[sel_tab] = base_figure, str(wave) + " | " + str(frequency) + \
                          "Hz" + " | " + str(amplitude) + "mV" + " | " + str(offset) + "mV"

        # wait to update the runs variable
        sleep(0.10)

        return base_figure, cur_runs


# Update graph-info
@app.callback(
    Output('graph-info', 'children'),
    [
        Input('tabs', 'value'),
        Input('runs', 'data')
    ]
)
def update_info(value, cur_runs):
    if value in cur_runs:
        return cur_runs[value][1]
    return "-"


if __name__ == '__main__':
    app.run_server(port=8051, debug=True, dev_tools_hot_reload=False)
