import pandas as pd
from sqlalchemy import create_engine, text
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, dash_table

# Database connection string
conn_str = (
    'mssql+pyodbc://MAN61NBO1VZ06Y2\\SQLEXPRESS/Plantkpis_Sp_db?'
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Create SQL Alchemy engine
engine = create_engine(conn_str)

# Function to retrieve data from the Target_Table
def get_target_data():
    query = """
    SELECT Month, Target 
    FROM Target_Table 
    ORDER BY 
        CASE 
            WHEN Month = 'Oct' THEN 1
            WHEN Month = 'Nov' THEN 2
            WHEN Month = 'Dec' THEN 3
            WHEN Month = 'Jan' THEN 4
            WHEN Month = 'Feb' THEN 5
            WHEN Month = 'Mar' THEN 6
            WHEN Month = 'Apr' THEN 7
            WHEN Month = 'May' THEN 8
            WHEN Month = 'Jun' THEN 9
            WHEN Month = 'Jul' THEN 10
            WHEN Month = 'Aug' THEN 11
            WHEN Month = 'Sep' THEN 12
        END
    """
    df = pd.read_sql(query, engine)

    # Transpose the DataFrame to get the desired grid format
    df_transposed = df.set_index('Month').T.reset_index(drop=True)

    return df_transposed


# Function to update the Target value in the Target_Table
def update_target(month, new_target):
    query = text("UPDATE Target_Table SET Target = :new_target WHERE Month = :month")
    with engine.begin() as conn:  # Use transaction context
        conn.execute(query, {'new_target': new_target, 'month': month})
