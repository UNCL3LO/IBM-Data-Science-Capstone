# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Extract unique launch sites dynamically for dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
    site_options.append({'label': site, 'value': site})

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show successful launches count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Callback function for `site-dropdown` -> `success-pie-chart`
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count outcomes (0 = Failure, 1 = Success)
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['outcome'] = site_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            site_counts,
            values='count',
            names='outcome',
            title=f'Total Success vs Failure Launches for Site {entered_site}'
        )
    return fig


# TASK 4: Callback function for `site-dropdown` & `payload-slider` -> `success-payload-scatter-chart`
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter dataframe by selected payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for Site {entered_site}'
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
