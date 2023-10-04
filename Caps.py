import pandas as pd
import dash
from dash import Dash, html, dcc, callback, Output, Input
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt
import requests
import io

app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
resp = requests.get(URL)
text = io.StringIO(resp.text)
spacex_df = pd.read_csv(text)
# spacex_df.to_csv("10. CAPSTONE/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app.layout = html.Div(children=[                
                html.H1('SpaceX Launch Records Dashboard',style={'textAlign': 'center', 'color': '#503D36',
                                                                 'font-size': 40}),                                                     
                dcc.Dropdown(id='site-dropdown',
                             options=[{'label': 'All Sites', 'value': 'ALL'}]+[
                                 {'label': category, 'value': category} for category in spacex_df['Launch Site'].unique()],
                                 value='ALL',
                                 searchable=True
                                 ),
                html.Br(),
                html.Div(children=[ ],id='output-container'),
                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0',100: '100'},
                                value=[min_payload, max_payload]),
                html.Div(children=[ ],id='output_scatter_cont')

                ])

@app.callback(
    Output(component_id='output-container', component_property='children'),
    Input(component_id='site-dropdown',component_property='value')
)
def buildpie(category):
    if category == 'ALL' :
        filtdf = spacex_df[spacex_df['class']==1]
        piedf = filtdf.groupby(["Launch Site"]).count().reset_index()
        pietitl = 'Total Succes Launches By ' + str(category)
        piefig = px.pie(piedf,values='Flight Number',names='Launch Site', title=pietitl)
    else:
        filtdf = spacex_df[spacex_df['Launch Site']==category]
        piedf = filtdf.groupby(["Launch Site","class"]).count().reset_index()
        pietitl = 'Total Succes Launches By ' + str(category)
        piefig = px.pie(piedf,values='Flight Number',names='class', title=pietitl)
    return [dcc.Graph(figure=piefig)]

@app.callback(
    Output(component_id='output_scatter_cont', component_property='children'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def succ_plot(site_cat, payl):
    if site_cat == 'ALL':
        scat_fig = px.scatter(spacex_df, x='Payload Mass (kg)', y='class',color="Booster Version Category",
                              title="Correlation between Payload and Success for all sites")        
    else:
        scat_filtdf = spacex_df[spacex_df['Launch Site']==site_cat]
        scat_fig = px.scatter(scat_filtdf, x='Payload Mass (kg)', y='class',color="Booster Version Category",
                              title="Correlation between Payload and Success for "+ str(site_cat))
    return [dcc.Graph(figure=scat_fig)]

if __name__ == '__main__':
    app.run_server(debug=True)