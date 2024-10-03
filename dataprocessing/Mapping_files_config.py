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
def get_calendar_data():
    query = """
    SELECT [Fiscal Week], Month 
    FROM Calendar 
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
        END, [Fiscal Week]
    """
    df = pd.read_sql(query, engine)

    # Create an empty dataframe to hold the pivoted data with a fixed number of rows (e.g., 5)
    max_weeks = 5  # Set to maximum possible weeks in a month
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    pivot_data = pd.DataFrame(index=range(max_weeks), columns=months)

    # Fill in the pivot table
    for month in months:
        weeks = df[df['Month'] == month]['Fiscal Week'].values
        pivot_data[month].iloc[:len(weeks)] = weeks

    return pivot_data.fillna('')

def update_calendar(month, new_fiscal_week, old_fiscal_week):
    query = text("""
    UPDATE Calendar 
    SET [Fiscal Week] = :new_fiscal_week 
    WHERE Month = :month AND [Fiscal Week] = :old_fiscal_week
    """)
    with engine.begin() as conn:  # Use transaction context
        conn.execute(query, {'new_fiscal_week': new_fiscal_week, 'month': month, 'old_fiscal_week': old_fiscal_week})


def get_material_type_data():
    query = """
    SELECT [Material Number], [Material Type]
    FROM [dbo].[Material_Type]
    ORDER BY [Material Number]
    """
    df = pd.read_sql(query, engine)
    return df


def update_material_type(material_number, new_material_type):
    print(f"Updating Material Number: {material_number}, New Material Type: {new_material_type}")  # Debug info
    query = text("UPDATE [Material_Type] SET [Material Type] = :new_material_type WHERE [Material Number] = :material_number")
    with engine.begin() as conn:
        conn.execute(query, {'new_material_type': new_material_type, 'material_number': material_number})
    print("Update executed successfully")  # Confirmation message


def insert_new_material(material_number, material_type):
    query = text("INSERT INTO [Material_Type] ([Material Number], [Material Type]) VALUES (:material_number, :material_type)")
    with engine.begin() as conn:
        conn.execute(query, {'material_number': material_number, 'material_type': material_type})

# Define available material types
available_material_types = ['RM', 'Spare Parts', 'Finished Goods', 'Semi-Finished Goods']

def delete_material_type(material_number):
    print(f"Attempting to delete Material Number: {material_number}")  # Debugging statement
    query = text("DELETE FROM [Material_Type] WHERE [Material Number] = :material_number")
    try:
        with engine.begin() as conn:
            result = conn.execute(query, {'material_number': material_number})
            print(f"Rows affected: {result.rowcount}")  # Check if rows are actually being deleted
    except Exception as e:
        print(f"Error deleting Material Number: {material_number}. Exception: {str(e)}")
