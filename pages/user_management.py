from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div(
    id="main-container",
    children=[
        html.H1("user management  page", style={"text-align": "center", "margin-top": "40px"}),
    ],
    style={"padding": "0"}
)

if __name__ == "__main__":
    app.run_server(debug=True)
