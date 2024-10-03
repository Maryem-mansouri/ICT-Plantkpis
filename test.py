import pandas as pd
from sqlalchemy import create_engine,text
import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import pandas as pd
# Database connection string

# Database connection string
conn_str = (
    'mssql+pyodbc://MAN61NBO1VZ06Y2\\SQLEXPRESS/Plantkpis_Sp_db?'
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Create SQL Alchemy engine
engine = create_engine(conn_str)

# Function to retrieve data from the Target_Table
def get_target_data():
    query = "SELECT Month, Target FROM Target_Table ORDER BY Month"
    df = pd.read_sql(query, engine)
    return df

# Function to update the Target value in the Target_Table
def update_target(month, new_target):
    query = text("UPDATE Target_Table SET Target = :new_target WHERE Month = :month")
    with engine.begin() as conn:  # Use transaction context
        conn.execute(query, {'new_target': new_target, 'month': month})

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H3("Manage Target Table"),
    
    dash_table.DataTable(
        id='target-table',
        columns=[
            {'name': 'Month', 'id': 'Month', 'editable': False},  # Month column uneditable
            {'name': 'Target', 'id': 'Target', 'editable': True}  # Target column editable
        ],
        data=get_target_data().to_dict('records'),  # Load data from the database
        editable=True,
        row_deletable=False,
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold'
        }
    ),
    
    html.Button('Save Changes', id='save-changes', n_clicks=0),
    html.Div(id='output-div')
])

# Callback to handle the update of target values in the database
@callback(
    Output('output-div', 'children'),
    Input('save-changes', 'n_clicks'),
    State('target-table', 'data')
)
def save_changes(n_clicks, rows):
    if n_clicks > 0:
        for row in rows:
            update_target(row['Month'], row['Target'])
        return "Changes saved successfully."
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)