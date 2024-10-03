import pandas as pd
from sqlalchemy import create_engine, text
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, dash_table
from dataprocessing.targets_config import get_target_data, update_target
# Define the static STR target data
def get_static_str_target_data():
    # Static data for STR Target Table with values between 90% and 95%
    data = {
        'Months' : ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
        'Target': ['90.1%', '91%', '92.5%', '93%', '94.3%', '95%', '90%', '91.8%', '92%', '93.6%', '94%', '95%']
    
    }
    return pd.DataFrame(data)

# Layout of the app
# Layout of the app
def layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(html.H3("Inventory Targets Table", className="card-title text-white my-auto"), width=9),
                        dbc.Col(html.Button('Save Changes', id='save-changes', n_clicks=0, 
                                            style={
                                                'backgroundColor': 'white',
                                                'color': 'green',
                                                'border': '2px solid green',
                                                'borderRadius': '20px',
                                                'fontWeight': 'bold',
                                                'fontSize': '14px',
                                                'padding': '5px 15px',
                                                'boxShadow': '0px 0px 5px rgba(0,0,0,0.1)'
                                            }), width=3, 
                                style={'textAlign': 'right'})
                    ]
                ),
                style={"backgroundColor": "#fb8500"},
            ),
            dbc.CardBody(
                [
                    # Inventory Targets Table
                    dash_table.DataTable(
                        id='target-table',
                        columns=[{'name': i, 'id': i, 'editable': True} for i in get_target_data().columns],
                        data=get_target_data().to_dict('records'),
                        editable=True,
                        row_deletable=False,
                        style_cell={
                            'textAlign': 'center',
                            'padding': '5px',
                            'font-size': '12px',
                            'border': '1px solid #e0e0e0',
                            'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': '#F1F4F9',
                            'fontWeight': 'bold',
                            'font-size': '12px',
                            'border': 'none'
                        },
                        style_table={'width': '100%', 'margin': '0 auto'},
                    ),
                    html.Br(),  # Add some space between the tables
                    
                    # STR Targets Table (Static)
                    dbc.CardHeader(html.H3("STR Targets Table", className="card-title text-white my-auto"), style={"backgroundColor": "#219ebc"}),
                    dash_table.DataTable(
                        id='str-target-table',
                        columns=[{'name': i, 'id': i, 'editable': True} for i in get_static_str_target_data().columns],
                        data=get_static_str_target_data().to_dict('records'),
                        editable=True,
                        row_deletable=False,
                        style_cell={
                            'textAlign': 'center',
                            'padding': '5px',
                            'font-size': '12px',
                            'border': '1px solid #e0e0e0',
                            'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': '#F1F4F9',
                            'fontWeight': 'bold',
                            'font-size': '12px',
                            'border': 'none'
                        },
                        style_table={'width': '100%', 'margin': '0 auto'},
                    ),
                ],
                style={'padding': '10px'}
            ),
            dbc.Alert(
                id='saveto-alert',
                is_open=False,
                duration=5000,
                style={
                    'backgroundColor': 'rgb(173,216,228,0.88)',  # Light blue background
                    'color': 'white',  # White text
                    'borderRadius': '10px',  # Rounded corners
                    'textAlign': 'center',  # Centered text
                    'border': '0',
                    'fontWeight': 'bold',
                    'width': 'fit-content',  # Fit content width
                    'position': 'fixed',  # Fixed position
                    'top': '20px',  # Position at the top of the page
                    'right': '20px',  # Position on the right side of the page
                    'zIndex': 9999,  # High z-index to appear in front of other elements
                },
                dismissable=True,
                className="custom-alert",
                children="Changes saved successfully!"  # Message in the alert
            )
        ],
        style={'margin': '20px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
    )


def register_callbacks(app):
    # Callback to handle the update of target values in the database
    @app.callback(
        Output('saveto-alert', 'is_open'),
        Input('save-changes', 'n_clicks'),
        State('target-table', 'data')
    )
    def save_changes(n_clicks, rows):
        if n_clicks > 0:
            df = pd.DataFrame(rows)
            # Transpose back to the original format for updating the database
            df_original = df.T.reset_index()
            df_original.columns = ['Month', 'Target']  # Reset column names

            for index, row in df_original.iterrows():
                update_target(row['Month'], row['Target'])

            # Only return True to open the alert
            return True
        return False
