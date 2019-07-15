appName <- Sys.getenv("DASH_APP_NAME")
if (appName != ""){
  pathPrefix <- sprintf("/%s/", appName)
  
  Sys.setenv(DASH_ROUTES_PATHNAME_PREFIX = pathPrefix,
             DASH_REQUESTS_PATHNAME_PREFIX = pathPrefix)
  setwd(sprintf("/app/apps/%s", appName))
}

library(dash)
library(dashDaq)
library(dashHtmlComponents)
library(dashCoreComponents)
library(magrittr)
library(rlang)

app <- Dash$new()
font_color <- list(dark='#ffffff', light='#222')
background_color <- list(dark='#2a3f5f', light='#ffffff')
axis_color <- list(dark='#EBF0F8', light='#506784')
marker_color <- list(dark='#f2f5fa', light='#2a3f5f')

theme <- list(
  dark=F,
  primary = '#447EFF',
  secondary = '#D3D3D3',
  detail = '#D3D3D3'
)

init_input <- list(list(
    function_generator = T,
    oscilloscope = T,
    frequency_input = 1E6,
    amplitude_input = 1,
    offset_input = 0,
    function_type = 'SIN'
  ))

header <- function(){
  return(htmlDiv(
    id='header',
    className='banner',
    style=list(backgroundColor='#6682C0'),
    children=list(
      htmlH2(
        "Dash DAQ: Function Generator & Oscilloscope Control Panel",
        style=list(
          color='white', 
          marginLeft='40px',
          display='inline-block',
          'text-align'='center'
          )),
      htmlImg(
        src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/excel/dash-daq/dash-daq-logo-by-plotly-stripe+copy.png",
        style=list(
          position='relative',
          float='right',
          right='10px',
          height='75px'
        )
        )
    )))
}

knobs <- function(cur_input, cur_tab){
  return(htmlDiv(list(
    ###FREQ INPUT
    daqKnob(
      value=cur_input[[cur_tab]][['frequency_input']],
      id='frequency-input',
      label='Frequency (Hz)',
      labelPosition='bottom',
      size=75,
      color=theme[['primary']],
      scale=list(interval=100000),
      max=2500000,
      min=100000,
      className='four columns'
    ),
    ###AMP INPUT
    daqKnob(
      value=cur_input[[cur_tab]][['amplitude_input']],
      id='amplitude-input',
      label='Amplitude (mV)',
      labelPosition='bottom',
      size=75,
      color=theme[['primary']],
      scale=list(labelInterval=10),
      max=10,
      min=0,
      className='four columns'
    ),
    ###OFFSET
    daqKnob(
      value=cur_input[[cur_tab]][['offset_input']],
      id='offset-input',
      label='Offset (mV)',
      labelPosition='bottom',
      size=75,
      color=theme[['primary']],
      scale=list(labelInterval=10),
      max=10,
      min=0,
      className='four columns'
    )
  ),
  style=list(marginLeft='20%', textAlign='center')))
}
led_displays <- function(cur_input, cur_tab){
  return(htmlDiv(list(
    daqLEDDisplay(
      id='frequency-display',
      size=10,
      value=cur_input[[cur_tab]][['frequency_input']],
      label="Frequency (Hz)",
      labelPosition="bottom",
      color=theme[['primary']],
      style=list(marginBottom= '30px'),
      className='four columns'),
    
    daqLEDDisplay(
      id='amplitude-display',
      size=10,
      value=cur_input[[cur_tab]][['amplitude_input']],
      label="Amplitude (mV)",
      labelPosition="bottom",
      color=theme[['primary']],
      className='four columns'),
    
    daqLEDDisplay(
      id='offset-display',
      size=10,
      value=cur_input[[cur_tab]][['offset_input']],
      label="Offset (mV)",
      labelPosition="bottom",
      color=theme[['primary']],
      className='four columns'),
    ), style=list(marginLeft = '20%', textAlign = 'center')))
}

radioitem <- function(cur_input, cur_tab){
  return(dccRadioItems(
    id='function-type',
    options=list(
      list(label= 'Sine', value= 'SIN'),
      list(label= 'Square', value= 'SQUARE'),
      list(label= 'Ramp', value= 'RAMP'),
      ),
    value=cur_input[[cur_tab]][['function_type']],
    labelStyle=list(display= 'inline-block'),
    style=list(
      margin= '30px auto 0px auto',
      display = 'flex',
      width = '80%',
      alignItems = 'center',
      justifyContent = 'space-between'
      )))
  }


power_setting_div <- function(cur_inputs, cur_tab){
  if(is.na(cur_inputs)||rlang::is_empty(cur_inputs)){
  cur_inputs = init_input
  }
return(htmlDiv(
  className='row power-settings-tab',
  children=list(
    htmlDiv(
      className='Title',
      children=htmlH3("Power", 
                      id='power-title', 
                      style=list(color=theme[['primary']]))),
    htmlDiv(
      # power-controllers
      list(
        htmlDiv(
            daqPowerButton(
              id='function-generator',
              on=cur_inputs[[cur_tab]][['function_generator']],
              label="Function Generator",
              labelPosition='bottom',
              color=theme[['primary']]),
          className='six columns',
          style=list('margin-bottom'='15px')),
        htmlDiv(
            daqPowerButton(
              id='oscilloscope',
              on=cur_inputs[[cur_tab]][['oscilloscope']],
              label="Oscilloscope",
              labelPosition='bottom',
              color=theme[['primary']]
            ),
          className='six columns',
          style=list('margin-bottom'='15px')),
        ),style=list(margin='15px 0'))
    )))
}


function_setting_div <- function(cur_input, cur_tab){
  if(is.na(cur_input)||rlang::is_empty(cur_input)){
    cur_inputs = init_input
  }
  return(htmlDiv(
    className='row power-settings-tab',
    children=list(
      htmlDiv(
        className='Title',
        style=list(color=theme[['primary']]),
        children=htmlH3("Function", id='function-title')),
      # Knobs
      knobs(cur_input, cur_tab),
      # LED Displays
      led_displays(cur_input, cur_tab),
      # # RadioItems
      radioitem(cur_input, cur_tab)
    )))
}

app$layout(htmlDiv(
  id='main-page',
  className='container',
  children=list(
    #toggle
    htmlDiv(
      id='toggleDiv',
    style=list(
      width='fit-content',
      margin='0 auto'
      ),
    children=list(
      daqToggleSwitch(
        id='toggleTheme',
        style=list(
          position='absolute',
          transform='translate(-50%, 20%)',
          'z-index'='9999'
        ),
        size=30,
        value=F
        )
    )),
    header()
)))

app$run_server(host = "0.0.0.0", port = Sys.getenv('PORT', 8050))