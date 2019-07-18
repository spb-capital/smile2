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
library(purrr)
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
      className='four columns')
    ), style=list(marginLeft = '20%', textAlign = 'center')))
}

radioitem <- function(cur_input, cur_tab){
  return(dccRadioItems(
    id='function-type',
    options=list(
      list(label= 'Sine', value= 'SIN'),
      list(label= 'Square', value= 'SQUARE'),
      list(label= 'Ramp', value= 'RAMP')
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
          style=list('margin-bottom'='15px'))
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
          'z-index'='9999',
          float = 'center'
        ),
        size=30,
        value=F
        )
    )),
    header(),
    htmlDiv(
      children=htmlDiv(
        children=list(
          htmlDiv(
            className='five columns left-panel',
            children=list(
              htmlDiv(
                id='dark-theme-components',
                children=daqDarkThemeProvider(
                  theme=theme,
                  children=list(
                    power_setting_div(NULL, 1),
                    function_setting_div(NULL, 1)
                  )
                )
              ),
              daqColorPicker(
                id='color-picker',
                label='Color Picker',
                value=list(hex='#6682C0'),
                size=164,
                style=list(marginTop = '20px', backgroundColor = 'inherit')
              )
            )
          ),
          #Oscillator Panel - Right
          htmlDiv(
            className='seven columns right-panel',
            children=list(
              htmlDiv(htmlH3("Graph", id='graph-title'),
                      style=list(color=theme[['primary']]),
                      className='Title'),
              dccTabs(
                id='tabs',
                children=dccTab(
                  label='Run #1',
                  value='1'),
                value='1',
                className='oscillator-tabs',
                colors=list(
                  border='#d6d6d6',
                  primary='#6682C0',
                  background='#f2f2f2'
                )
              ),
              
              htmlDiv(
                className='row oscope-info',
                children=list(
                  htmlDiv(),
                  htmlButton(
                    '+',
                    id='new-tab',
                    n_clicks=0,
                    type='submit',
                    style=list(
                      height='20px',
                      width='20px',
                      padding='2px',
                      lineHeight='10px',
                      float='right',
                      color='inherit'
                    ))
                  )
              ),
              htmlHr(),
              dccGraph(id='oscope-graph', figure=list())
            )
          )
        )
      )
    ),
    dccStore(id='control-inputs', data=list())
    # {tabs_number: {value1=x, value2=x}}
)))

#Does not support multiple outputs - need to be updated
app$callback(
  output=list(id='oscilloscope', property='on'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return(osci_on)
    }
    td <- cur_inputs[[tab_index]]
    return(td[['oscilloscope']])
  }
)

app$callback(
  output=list(id='function-generator', property='on'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return(func_gen)
    }
    td <- cur_inputs[[tab_index]]
    return(td[['function_generator']])
  }
)


app$callback(
  output=list(id='frequency-input', property='value'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return(1000000)
    }
    td <- cur_inputs[[tab_index]]
    return(td[['frequency_input']])
  }
)

app$callback(
  output=list(id='amplitude-input', property='value'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return(1)
    }
    td <- cur_inputs[[tab_index]]
    return(td[['amplitude_input']])
  }
)

app$callback(
  output=list(id='offset-input', property='value'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return(0)
    }
    td <- cur_inputs[[tab_index]]
    return(td[['offset_input']])
  }
)

app$callback(
  output=list(id='function-type', property='value'),
  params=list(input(id='tabs', property='value'), 
              state(id='control-inputs', property='value'),
              state(id='oscilloscope', property='on'),
              state(id='function-generator', property='on')),
  function(tab_index, cur_inputs, osci_on, func_gen){
    if(!tab_index %in% cur_inputs){
      return('SIN')
    }
    td <- cur_inputs[[tab_index]]
    return(td[['function_type']])
  }
)

app$callback(
  output=list(id='control-inputs', property='data'),
  params=list(
    input(id='oscilloscope',property='on'),
    input(id='function-generator',property='on'),
    input(id='frequency-input',property='value'),
    input(id='amplitude-input',property='value'),
    input(id='offset-input',property='value'),
    input(id='function-type',property='value'),
    state(id='tabs', property='value'),
    state(id='control-inputs', property='data')),
  function(osc_on, fnct_on, freq, amp, offset, wave, sel_tab, cur_inputs){
    cur_inputs[[sel_tab]] = list(oscilloscope=osc_on, 
                                 function_generator=fnct_on, 
                                 frequency_input=freq,
                                 amplitude_input=amp,
                                 offset_input=offset,
                                 function_type=wave
                                 )
    return(cur_inputs)
  }
)

# new tab created, not saved to store unless control inputs changes 

app$callback(
  output=list(id='oscope-graph', property='figure'),
  params=list(input(id='control-inputs', property='data'),
              input(id='toggleTheme', property='value'),
              state(id='tabs', property='value')),
  function(cur_inputs, theme_value, tab_index){
    theme_select <- ifelse(theme_value, 'dark', 'light')
    axis <- axis_color[[theme_select]]
    marker <- marker_color[[theme_select]]
    time <- seq(-0.00045, 0.000045, length.out = 1000)
    base_figure <- list(
      data=list(type='scatter',
                x=time, 
                y=numeric(length(time)),
                marker=list(color=marker),
                mode='lines'),
      layout= list(xaxis=list(title='s',
                             color=axis,
                             titlefont=list(family='Dosis'), 
                             size=13),
                  yaxis=list(title='Voltage (mV)',
                             color=axis,
                             range=c(-10, 10),
                             titlefont=list(family='Dosis'), 
                             size=13),
                  margin=list(l=40, b=40, t=20, r=50),
                  plot_bgcolor='rgba(0,0,0,0)',
                  paper_bgcolor='rgba(0,0,0,0)'
                  )
    )
    if(!tab_index %in% cur_inputs){
      return(base_figure)
    }
    tab_data <- cur_inputs[[tab_index]]
    
    if(rlang::is_empty(tab_data[['oscilloscope']])||is.na(tab_data[['oscilloscope']])){
      base_figure[[data]] = list()
      base_figure[['layout']][['xaxis']][['showticklabels']] <- F
      base_figure[['layout']][['xaxis']][['showline']] <- F
      base_figure[['layout']][['xaxis']][['zeroline']] <- F
      return(base_figure)
    }
    
    if(rlang::is_empty(tab_data[['function_generator']])||is.na(tab_data[['function_generator']])){
      return(base_figure)
    }
    
    if(tab_data[['function_type']]=='SIN'){
      y <- unlist(lapply(time, function(n){
          return(tab_data[['offset_input']]+tab_data[['amplitude_input']]*sinpi(2*tab_data[['frequency_input']]*n))
          }))
    } else if(tab_data[['function_type']]=='SQUARE'){
      
    } else if(tab_data[['function_type']]=='RAMP'){
      
    } else {
      
    }
    
  }
  
  
)

####### LAUNCH THE APP
app$run_server(host = "0.0.0.0", port = Sys.getenv('PORT', 8050))