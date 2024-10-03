import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
 
def create_gauge_chart(value):
    # Create a gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "k", 'font': {'size': 48, 'color': 'orange'}},
        gauge={
            'axis': {'range': [-2000, 2000], 'tickwidth': 1, 'tickcolor': "gray"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [-2000, 0], 'color': "lightgray"},
                {'range': [0, 2000], 'color': "lightgray"},
                {'range': [-2000, value], 'color': "orange"} if value < 0 else {'range': [0, value], 'color': "orange"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
 
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # transparent background
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(l=0, r=0, t=0, b=0)
    )
 
    return fig
 
def createppv_card(title, subtitle, value):
    fig = create_gauge_chart(value)
   
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-title"),
                html.P(subtitle, className="card-text", style={'color': 'grey'}),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ],
            style={"background": "linear-gradient(135deg, #ffffff 0%, #FFE7CC 100%)", "borderRadius": "10px"}
        ),
       style={"height": "20em", "borderRadius": "20px"}, className="border-0"
    )
   
    return card
 