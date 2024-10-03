import pandas as pd
from sqlalchemy import create_engine, text
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, dash_table
from dataprocessing.Mapping_files_config import delete_material_type, available_material_types, insert_new_material,update_material_type, get_calendar_data ,update_calendar,get_material_type_data
from dash.exceptions import PreventUpdate

def layout():
    calendar_data = get_calendar_data()
    return dbc.Container([
        dbc.Card(
            [
                dbc.CardHeader(
                    dbc.Row(
                        [
                            dbc.Col(html.H3("Calendar Table", className="card-title text-white my-auto"), width=9),
                            dbc.Col(html.Button('Save Changes', id='save-calendar-changes', n_clicks=0,
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
                    dash_table.DataTable(
                        id='calendar-table',
                        columns=[{'name': i, 'id': i, 'editable': True} for i in calendar_data.columns],
                        data=calendar_data.to_dict('records'),  # Load data from the database
                        editable=True,
                        row_deletable=False,
                        style_cell={
                            'textAlign': 'center',
                            'padding': '5px',  # Smaller padding for smaller cell height
                            'font-size': '12px',  # Smaller font size for smaller text
                            'border': '1px solid #e0e0e0',
                            'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',  # Smaller width
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': '#F1F4F9',
                            'fontWeight': 'bold',
                            'font-size': '12px',  # Smaller header font size
                            'border': 'none'
                        },
                        style_table={'width': '100%', 'margin': '0 auto'},  # Full width for table
                    ),
                    style={'padding': '10px'}
                ),
                dbc.Alert(
                    id='calendar-alert',
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
            style={'margin': '20px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}  # Adjust the card width and center it
        ),
 dbc.Card(
    [
        dbc.CardHeader(
            dbc.Row(
                [
                    dbc.Col(html.H3("Material Type Table", className="card-title text-white my-auto"), width=9),
                    dbc.Col(html.Button('Save Changes', id='save-material-changes', n_clicks=0,
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
                dbc.Row(
                    [
                        dbc.Col(dcc.Input(id='new-material-number', type='text',
                                          placeholder='Enter Material Number',
                                          style={
                                              'height': '35px',
                                              'padding': '0 10px',
                                              'border-radius': '5px 0 0 5px',
                                              'border': '1px solid #ced4da',
                                              'box-shadow': 'none',
                                              'outline': 'none',
                                              'width': '100%'
                                          }), width=5),
                        dbc.Col(dcc.Dropdown(id='new-material-type', options=[
                            {'label': i, 'value': i} for i in available_material_types],
                            placeholder='Select Material Type',
                            style={
                                'height': '35px',
                                'padding': '0 10px',
                                'border-radius': '0 5px 5px 0',
                                'border': '1px solid #ced4da',
                                'border-left': 'none',
                                'box-shadow': 'none',
                                'outline': 'none',
                                'width': '100%',
                                'background-color': '#fff',
                                'color': '#6c757d',
                                'font-size': '16px'
                            }), width=5),
                        dbc.Col(html.Button('Add', id='add-material-btn', n_clicks=0,
                                            style={
                                                'backgroundColor': '#FF8200',
                                                'color': 'white',
                                                'height': '35px',
                                                'border-radius': '20px',
                                                'width': '100%',
                                                'border': '2px solid #FF8200',
                                                'box-shadow': 'none',
                                                'outline': 'none',
                                            }), width=2)
                    ],
                    style={'margin-bottom': '20px'}
                ),
                dash_table.DataTable(
                    id='material-type-table',
                    columns=[
                        {'name': 'Material Number', 'id': 'Material Number', 'editable': False},
                        {'name': 'Material Type', 'id': 'Material Type', 'editable': True}
                    ],
                    data=get_material_type_data().to_dict('records'),
                    editable=True,
                    row_deletable=True,
                    style_cell={
                        'textAlign': 'left',
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
                    filter_action="native",
                    sort_action="native",
                    sort_mode='multi',
                    page_action='native',
                    page_current=0,
                    page_size=10,
                ),
                dbc.Alert(
                    id='material-alert',
                    is_open=False,
                    duration=5000,
                    style={
                        'backgroundColor': 'rgb(173,216,228,0.88)',
                        'color': 'white',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'border': '0',
                        'fontWeight': 'bold',
                        'width': 'fit-content',
                        'position': 'fixed',
                        'top': '20px',
                        'right': '20px',
                        'zIndex': 9999,
                    },
                    dismissable=True,
                    className="custom-alert",
                    children="Changes saved successfully!"
                ),
                dcc.ConfirmDialog(
                    id='confirm-delete-dialog',
                    message='Are you sure you want to delete this row?',
                )
            ],
            style={'padding': '10px'}
        )
    ],
    style={'margin': '20px', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
)

    ],
    fluid=True)

def register_callbacks(app):
    @app.callback(
        Output('calendar-alert', 'is_open'),
        Input('save-calendar-changes', 'n_clicks'),
        State('calendar-table', 'data')
    )
    def save_calendar_changes(n_clicks, rows):
        if n_clicks > 0:
            df = pd.DataFrame(rows)
            original_data = get_calendar_data()  # Get the original data from the database

            # Compare the new data with the original data to find the changes
            for month in df.columns:
                for i in range(len(df)):
                    new_fiscal_week = df.loc[i, month]
                    old_fiscal_week = original_data.loc[i, month]

                    if new_fiscal_week != old_fiscal_week:
                        update_calendar(month, new_fiscal_week, old_fiscal_week)

            return True
        return False
    

    @app.callback(
        [Output('material-type-table', 'data'),
         Output('material-alert', 'is_open'),
         Output('confirm-delete-dialog', 'displayed')],
        [Input('add-material-btn', 'n_clicks'),
         Input('save-material-changes', 'n_clicks'),
         Input('material-type-table', 'data_previous')],
        [State('material-type-table', 'data'),
         State('new-material-number', 'value'),
         State('new-material-type', 'value')]
    )
    def handle_table_actions(add_n_clicks, save_n_clicks, previous_data, current_data, new_material_number, new_material_type):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle adding a new material
        if triggered_id == 'add-material-btn' and add_n_clicks:
            if new_material_number and new_material_type:
                existing_material_numbers = [row['Material Number'] for row in current_data]

                if new_material_number not in existing_material_numbers:
                    new_row = {'Material Number': new_material_number, 'Material Type': new_material_type}
                    current_data.append(new_row)
                    insert_new_material(new_material_number, new_material_type)
                return current_data, False, False

        # Handle saving changes to the material type
        elif triggered_id == 'save-material-changes' and save_n_clicks:
            original_df = get_material_type_data()
            current_df = pd.DataFrame(current_data)
            merged_df = current_df.merge(original_df, on='Material Number', how='left', suffixes=('_new', '_orig'))

            updates = merged_df[merged_df['Material Type_new'] != merged_df['Material Type_orig']]
            for _, row in updates.iterrows():
                update_material_type(row['Material Number'], row['Material Type_new'])

            return current_data, True, False  # Show success alert

        # Handle row deletion (Trigger confirmation dialog)
        elif previous_data is not None and len(current_data) < len(previous_data):
            return current_data, False, True  # Display confirmation dialog

        return current_data, False, False

    @app.callback(
        Output('confirm-delete-dialog', 'submit_n_clicks'),
        [Input('confirm-delete-dialog', 'submit_n_clicks')],
        [State('material-type-table', 'data_previous'),
         State('material-type-table', 'data')]
    )
    def confirm_delete(confirm_delete_clicks, previous_data, current_data):
        if confirm_delete_clicks:
            deleted_rows = list(set(tuple(row.items()) for row in previous_data) - set(tuple(row.items()) for row in current_data))
            if deleted_rows:
                deleted_row = dict(deleted_rows[0])
                material_number = deleted_row['Material Number']

                # Perform the deletion in the database
                delete_material_type(material_number)

        return confirm_delete_clicks