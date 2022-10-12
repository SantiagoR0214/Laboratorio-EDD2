import dash
from dash import html
from dash.dependencies import Input, Output
from dash import dcc
import folium
import model

vertices = model.get_vertices()     # Creates vertices (names and coordinates)
model.get_destinations(vertices)    # Gets destinations for each vertex


app = dash.Dash()

options_origin = [{'label':i.name, 'value':vertices.index(i)} for i in vertices]
options_destinations = []
for d in options_origin:
    options_destinations.append(d.copy())
options_destinations.append({'label':'Todos', 'value':33})

app.layout = html.Div([
    html.H1 ('Vuelos Nacionales'), 
    html.Iframe (id ='map', srcDoc = None, width ='100%', height='600'),
    html.Div([

        html.Br(),
        html.Div(id='output_data'),
        #html.Br(),

        html.Label(['Escoja un origen:'],style={'font-weight': 'bold', "text-align": "center"}),

        dcc.Dropdown(id='origin_dropdown',
            options=options_origin,
            optionHeight=35,                    #height/space between dropdown options
            value=0,                    #dropdown value selected automatically when page loads
            disabled=False,                     #disable dropdown value selection
            multi=False,                        #allow multiple dropdown values to be selected
            searchable=True,                    #allow user-searching of dropdown values
            search_value='',                    #remembers the value searched in dropdown
            placeholder='...',     #gray, default text shown when no option is selected
            clearable=True,                     #allow user to removes the selected value
            style={'width':"100%"},             #use dictionary to define CSS styles of your dropdown
            ),                                  #'memory': browser tab is refreshed
                                                #'session': browser tab is closed
                                                #'local': browser cookies are deleted
        
        html.Label(['Escoja un destino:'],style={'font-weight': 'bold', "text-align": "center"}),
        
        dcc.Dropdown(id='destination_dropdown',
            options=options_destinations,
            optionHeight=35,                    #height/space between dropdown options
            value=33,                    #dropdown value selected automatically when page loads
            disabled=False,                     #disable dropdown value selection
            multi=False,                        #allow multiple dropdown values to be selected
            searchable=True,                    #allow user-searching of dropdown values
            search_value='',                    #remembers the value searched in dropdown
            placeholder='...',     #gray, default text shown when no option is selected
            clearable=True,                     #allow user to removes the selected value
            style={'width':"100%"},             #use dictionary to define CSS styles of your dropdown
            ),                                  #'memory': browser tab is refreshed
                                                #'session': browser tab is closed
                                                #'local': browser cookies are deleted

    ],className='three columns'),

])

#---------------------------------------------------------------
# Connecting the Dropdown values to the graph
@app.callback(
    Output('map', 'srcDoc'),
    [Input('origin_dropdown', 'value'),
    Input('destination_dropdown', 'value')],
)
def get_map(origin_id, destination_id):
    """
    Returns map with markers and shortest path drawn.
    
    Parameters
    ----------
    origin_id: int
        Index of origin of shortest path in vertices list.
    destination_id: int
        Index of destination of shortest path in vertices list.
    """
    
    # Creates map
    m = folium.Map(
        location=[3.7527349321953283, -73.09200342884061],
        zoom_start=6,
    )

    # Places Circlemarkers for each vertex
    for v in vertices:
        v.marker = folium.CircleMarker([v.coords[0], v.coords[1]],
                                    radius=10,
                                    fill_color="#3db7e4",
                                    popup=v.name.upper(),
                                    ).add_to(m)
    
    if destination_id == 33:
        model.draw_shortest_path(m, vertices, vertices[origin_id])
    else:        
        model.draw_shortest_path(m, vertices, vertices[origin_id], [vertices[destination_id]])
    
    m.save('map.html')
    return open(file='map.html', mode='r', encoding='utf8').read()
#---------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
