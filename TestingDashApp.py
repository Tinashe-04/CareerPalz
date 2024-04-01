import dash
from dash import dcc, html
import plotly.graph_objs as go

# Create Dash app
app = dash.Dash(__name__)

# Define data for the scatter plot
x_data = [1, 2, 3, 4, 5]
y_data = [2, 3, 5, 7, 11]

# Define layout of the Dash app
app.layout = html.Div([
    dcc.Graph(
        id='scatter-plot',
        figure={
            'data': [
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    marker=dict(color='blue', size=10),
                    name='Scatter Plot'
                )
            ],
            'layout': go.Layout(
                title='Simple Scatter Plot',
                xaxis={'title': 'X-axis'},
                yaxis={'title': 'Y-axis'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                hovermode='closest'
            )
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
