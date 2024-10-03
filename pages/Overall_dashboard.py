# Overall_dashboard.py
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dash import dcc, html
import dash_bootstrap_components as dbc
from components.sidebar import sidebar
import datetime  # Import datetime module
from components.overall_card import create_overall_card, create_sub_card, create_notification_card,create_graph_card

# Your data for the graph
data = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
    "Value": [7.8, 8.2, 7.5, 8.0, 7.9],
    "Color": ["orange"] * 5  # Use color if necessary
})
graph_title = "CAS Monthly Values"
# Function to get the current date with the correct ordinal suffix
def get_current_date_with_suffix():
    today = datetime.datetime.now()
    day = today.day

    # Determine the suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    formatted_date = today.strftime(f"%b, {day}{suffix}, %Y")
    return formatted_date

# Get the formatted date
current_date = get_current_date_with_suffix()

def layout():
    return html.Div(
        className="overall-dashboard",
        id="main-container",
        children=[
            html.Div(
                className="header-background",
                children=[
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/image-removebg-preview 1.png", style={"height": "60px", "display": "block", "margin-left": "auto", "margin-right": "auto"}), width=2),
                        dbc.Col(html.H3(current_date, style={"text-align": "center", "font-size": "1.5em", "color": "#023047"}), width=8, className="d-flex align-items-center justify-content-center"),
                        dbc.Col(
                            html.Div(
                                className="user-info d-flex justify-content-end align-items-center",
                                children=[
                                    html.Div(
                                        [
                                            html.P("Maryem ELMANSOURI", className="user-name", style={"margin-bottom": "0", "font-weight": "bold", "font-size": "0.8em"}),
                                            html.P("Data Analyst", className="user-role", style={"margin-bottom": "0", "font-size": "0.7em"}),
                                            html.P("IT Department", className="user-department", style={"margin-top": "0", "font-size": "0.7em"})
                                        ],
                                        style={"padding-right": "5px","padding-top": "10px"}
                                    ),
                                    html.Img(
                                        src="/assets/user_image.png",
                                        className="user-image",
                                        style={
                                            "height": "50px",
                                            "border-radius": "50%",
                                            "vertical-align": "middle",
                                            "margin-right": "10px"
                                
                                        }
                                    ),
                                ]
                            ), width=2),
                    ], align="center", style={"margin-bottom": "40px"})
                ],
            ),
            html.Div(
                className="content-background",
                children=[
                    dbc.Row([
                        dbc.Col(create_overall_card("Overall Dashboard",
                            dbc.Container([
                                dbc.Row([
                                    create_sub_card("Today's TOP Team", "12,345.056", None),
                                    create_sub_card("Today's Inv Value", "12,345.056", 15),
                                    create_sub_card("Value for 1249", "12,345.056", -15),
                                    create_sub_card("Value for 1249", "12,345.056", -15)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row([
                                             create_graph_card(data, x="Month", y="Value", color="Color", title=graph_title, height='230px')
                                        ])
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Row([
                                            create_sub_card("Stamping", "2,45 M$", -5, width=12, height='110px'),
                                            create_sub_card("Today's TOP Project", "12,345.056", width=12, height='110px')
                                        ])
                                    ], width=6)
                                ])
                            ])
                        ), width=9),
                        dbc.Col(create_notification_card(), width=3),
                    ])
                ],
                style={"padding": "10px"}
            )
        ],
        style={
            "height": "50vh",
            "padding": "0",
            "background": "linear-gradient(135deg, rgba(255, 165, 0, 0.5), rgba(255, 165, 0, 0) 40%), "
                         "linear-gradient(225deg, rgba(47, 169, 161, 0.5), rgba(0, 255, 255, 0) 40%)",
        }
    )



def register_callbacks(app):
    pass  