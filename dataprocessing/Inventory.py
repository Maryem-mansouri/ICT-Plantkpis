import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

conn_str = (
    'mssql+pyodbc://MAN61NBO1VZ06Y2\SQLEXPRESS/Plantkpis_Sp_db?'
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Create SQL Alchemy engine
engine = create_engine(conn_str)

# Load the data from the SQL database
query = "SELECT * FROM Inventory_ICT"
filtered_inventory_melted = pd.read_sql(query, engine)

## Paths to your Excel files
#ICT_inventory_path = r'.\data\Inventory data.xlsx'
#Material_Type_path = r'.\data\Inventory Repartition.xlsx'
#
## Load the Excel files
#ICT_inventory = pd.read_excel(ICT_inventory_path)
#Material_Type = pd.read_excel(Material_Type_path)
#
## Merge the dataframes on 'Material Number'
#ICT_inventory = pd.merge(ICT_inventory, Material_Type, on='Material Number', how='left')
#
## Verify the loaded data
#print("Loaded ICT Inventory Data:")
#print(ICT_inventory.head())
#
## Filter the DataFrame for the specified plant names
#
#
#print("Filtered Inventory Data for Specified Plants:")
#print(ICT_inventory.head())
#
#def get_latest_weeks_columns(df, weeks_count=6):
#    # Find all column headers that match the "WK" pattern
#    week_columns = [col for col in df.columns if "WK" in col]
#    # Sort them to make sure they are in the correct order (newest last)
#    week_columns.sort(key=lambda date: datetime.strptime(date, "2024-WK%U"), reverse=True)
#    # Return the latest 'weeks_count' weeks
#    return week_columns[:weeks_count]
#
#latest_weeks = get_latest_weeks_columns(ICT_inventory)
#
#print("Latest Weeks Columns:")
#print(latest_weeks)
#
## Melt the dataframe to reshape it and include all other columns
#filtered_inventory_melted = ICT_inventory.melt(
#    id_vars=['Material Number', 'GPL', 'BU', 'Plant Name', 'Storage Location', 'Region', 
#             'MRP Controller', 'Special Stock Name', 'Stock Category Name', 'Material Type Description', 
#             'Procurement Type', 'Procurement Type Name', 'Material Type'],
#    value_vars=latest_weeks,
#    var_name='Weeks',
#    value_name='Inventory_Value'
#)
#
## Extract the year and week number from the Weeks column
#filtered_inventory_melted['Year'] = filtered_inventory_melted['Weeks'].apply(lambda x: x.split('-')[0])
#filtered_inventory_melted['Week Number'] = filtered_inventory_melted['Weeks'].apply(lambda x: int(x.split('-WK')[1]))
#
## Verify the melted dataframe
#print("Melted DataFrame:")
#print(filtered_inventory_melted.head())

# Create filters
filter_plant = filtered_inventory_melted['Plant Name'].unique().tolist()
filter_year = filtered_inventory_melted['Year'].unique().tolist()
filter_week = filtered_inventory_melted['Week Number'].unique().tolist()

print("Filter Plant:", filter_plant)
print("Filter Year:", filter_year)
print("Filter Week:", filter_week)

# Functions for filtering and summary
def filter_data(plant, year, week):
    mask = (
        filtered_inventory_melted['Week Number'].isin(week) &
        filtered_inventory_melted['Year'].isin(year) &
        filtered_inventory_melted['Plant Name'].isin(plant)
    )
    filtered_data = filtered_inventory_melted[mask]
    print("Filtered Data inside filter_data function:")
    print(filtered_data.head())
    return filtered_data

def create_summary_dataframe(df, group_by_cols, agg_cols):
    if isinstance(agg_cols, str):
        agg_cols = {agg_cols: 'sum'}
    elif not isinstance(agg_cols, dict):
        raise ValueError("agg_cols should be a dictionary with columns and their respective aggregation functions.")
    df = df.sort_values(by=group_by_cols)
    summary_df = df.groupby(group_by_cols).agg(agg_cols).reset_index()
    return summary_df

def create_pivot_table(df, index_col, columns_col, values_col):
    df[columns_col] = df[columns_col].astype(int)
    df = df.sort_values(by=columns_col)

    pivot_table = df.pivot_table(
        values=values_col,
        index=index_col,
        columns=columns_col,
        aggfunc='sum',
        fill_value=0
    )
    
    totals = pivot_table.sum(axis=0).to_frame().T
    totals[index_col] = 'Total'
    totals = totals.set_index(index_col)
    
    pivot_table = pd.concat([pivot_table, totals])
    
    weeks = sorted(df[columns_col].unique())
    if len(weeks) > 1:
        last_week = weeks[-1]
        previous_week = weeks[-2]
        pivot_table['Gap'] = pivot_table[last_week] - pivot_table[previous_week]
        pivot_table['Gap %'] = ((pivot_table['Gap'] / pivot_table[previous_week]) * 100).fillna(0).round(1).astype(str) + '%'
    else:
        pivot_table['Gap'] = 0
        pivot_table['Gap %'] = 0
    
    pivot_table = pivot_table.reset_index()
    return pivot_table

def create_pivot_table_with_columns(df, columns, values):
    # Ensure the values are numerical
    df[values] = pd.to_numeric(df[values], errors='coerce')
    
    pivot_table = df.pivot_table(
        values=values,
        columns=columns,
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    weeks = [col for col in pivot_table.columns if col != 'index']
    if len(weeks) > 1:
        last_week = weeks[-1]
        previous_week = weeks[-2]
        pivot_table['Gap'] = pivot_table[last_week] - pivot_table[previous_week]
        pivot_table['Gap %'] = ((pivot_table['Gap'] / previous_week) * 100).fillna(0).round(1).astype(str) + '%'
    else:
        pivot_table['Gap'] = 0
        pivot_table['Gap %'] = 0

    return pivot_table


#filtered_data = filter_data(['TE Connectivity Morocco'], ['2024'], [18, 19,20,21,22,23])
#
## Create a summary dataframe
#summary_df = create_summary_dataframe(filtered_data, group_by_cols=['Plant Name', 'Week Number'], agg_cols='Inventory_Value')
#
## Create a pivot table
#pivot_table = create_pivot_table(filtered_data, index_col='Plant Name', columns_col='Week Number', values_col='Inventory_Value')
#
#print("Summary DataFrame:")
#print(summary_df)
#
#print("Pivot Table:")
#print(pivot_table)