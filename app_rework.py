import dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash_daq import DarkThemeProvider
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True
server = app.server

font_color = {'dark': '#ffffff', 'light': "#222"}
background_color = {'dark': '#2a3f5f', 'light': '#ffffff'}
title_color = {'dark': '#ffffff', 'light': '#447EFF'}

theme = {
    'dark': False,
    'primary': '#447EFF',
    'secondary': '#D3D3D3',
    'detail': '#D3D3D3'
}


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


def power_setting_div():
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


def function_setting_div():
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
                                        power_setting_div(),
                                        function_setting_div()
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
        dcc.Store(id='runs', data={})
    ]
)


# Callback to update theme layout
@app.callback(
    Output("dark-theme-components", 'children'),
    [Input("toggleTheme", 'value'), Input("color-picker", "value")]
)
def turn_dark(turn_dark, color_pick):
    if turn_dark:
        theme.update(dark=True)
    else:
        theme.update(dark=False)

    if color_pick is not None:
        theme.update(primary=color_pick['hex'])

    return DarkThemeProvider(
        theme=theme,
        children=[
            power_setting_div(),
            function_setting_div()
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


if __name__ == '__main__':
    app.run_server(port=8051, debug=True, dev_tools_hot_reload=False)
