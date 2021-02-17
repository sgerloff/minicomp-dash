import joblib
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go


def get_options(dataframe):
    options = []
    for s in dataframe.drop(["Store", "Date"], axis=1).columns:
        options.append({"label": s, "value": s})
    return options


# Load Data
df = joblib.load("data/predictions.jbl")
df["Date"] = df.index

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Generate Plot from Slider and Dropdown input:
@app.callback(Output('timeseries', 'figure'),
              [Input('store_id', 'value'), Input("prediction_selector", "value")])
def update_timeseries(index, cols):
    trace = []
    store_id = sorted(df["Store"].unique())[index]
    store_df = df[df["Store"] == store_id]

    for col in cols:
        trace.append(go.Scatter(x=store_df.index,
                                y=store_df[col],
                                mode='lines',
                                opacity=1.,
                                name=col,
                                textposition='bottom center'))

    figure = {'data': trace,
              'layout': go.Layout(
                  colorway=["#000000", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  plot_bgcolor='#FAFAFA',
                  margin={'b': 50, "t": 50, "l": 100, "r": 50},
                  hovermode='x',
                  autosize=True,
                  title={'text': f'Store ID: {store_id}', 'font': {'color': 'black'}, 'x': 0.5},
                  xaxis={'range': [df.index.min(), df.index.max()],
                         "title": "Date"},
                  yaxis={"title": "Sales",
                         "range": [store_df["Sales"].min() - 1000,
                                   store_df["Sales"].max() + 1000]}
              )
              }
    return figure


slider = dcc.Slider(id='store_id',
                    min=0,
                    max=df["Store"].nunique() - 1,
                    step=1,
                    value=0,
                    tooltip={"always_visible": False, "placement": "bottom"},
                    className='store_id')

dropdown = dcc.Dropdown(id='prediction_selector',
                        options=get_options(df),
                        multi=True,
                        value=["Sales"],
                        style={'backgroundColor': '#ffffff'},
                        className='prediction_selector')

description = html.Div(className='description',
                       children=[
                           html.P(children=[
                               '''Predictions of sales from rossman stores, using various models (''',
                               html.A('''github''', href='https://github.com/jdw/minicomp-rossman'),
                               '''). The models were trained on two years prior to the displayed time period.'''])
                       ])

plot = html.Div(className='plot',
                children=[
                    dcc.Graph(id='timeseries',
                              config={'displayModeBar': False}
                              )
                ])

slider_block = html.Div(
    className="div-for-options",
    children=[
        html.P('''Store ID:''', className="menu-description"),
        slider
    ]
)

dropdown_block = html.Div(
    className="data-selection",
    children=[
        html.P('''Graphs:''', className="menu-description"),
        dropdown
    ],
)

app.layout = html.Div(
    className="container",
    children=[
        html.Div(className="menu-container",
                 children=[
                     html.Div(style={"height": "2cm"}),
                     description,
                     slider_block,
                     dropdown_block]),
        html.Div(className="plot-container",
                 children=[
                     html.Center(html.H2('''ROSSMAN SALES - Predictions''')),
                     plot
                 ])
    ]
)

if __name__ == "__main__":
    app.run_server(debug=False)
