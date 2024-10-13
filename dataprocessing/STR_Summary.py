import pandas as pd
from datetime import datetime
import logging

# Read the Excel files into pandas DataFrames
STR_file_path = r'..\data\DSCD - STR Standard report FY24 - 2.0.xlsx'
STR = pd.read_excel(STR_file_path, sheet_name='Delivery Scorecard-STR')
STR_GPL = pd.read_excel(STR_file_path, sheet_name='Data')

# Merge the STR DataFrame with the fiscal mapping DataFrame
STR = STR.merge(STR_GPL, left_on='Material Number', right_on='Material', how='left')
STR['Technology'] = STR['Non-Tyco Ctrld Dlvry Block On']

# Convert 'Shipment Date' to datetime
STR['Shipment Date'] = pd.to_datetime(STR['Shipment Date'], errors='coerce')

# Convert to categorical as needed
for col in ['MRP Contr.', 'Sold To Customer', 'GPL', 'Material Number', 'STR Status', 'Technology', 'Shipment Fiscal Week', 'Shipment Fiscal Month','Shipment Fiscal Quarter', 'Shipment Fiscal Year']:
    STR[col] = STR[col].astype('category')

# Function to format 'Shipment Date'
def format_shipment_date(row):
    fiscal_week = row['Shipment Fiscal Week'].split('-')[1]
    day_name = row['Shipment Date'].strftime('%A')
    return f"{fiscal_week}-{day_name}"

# Apply the formatting function
STR['Formatted Shipment Date'] = STR.apply(format_shipment_date, axis=1)


# Custom sort order for days of the week
day_order = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
day_order_dict = {day: i for i, day in enumerate(day_order)}

def custom_sort_key(date_str):
    parts = date_str.split('-')
    if len(parts) == 2:
        fiscal_week, day_name = parts
        return (day_order_dict.get(day_name, len(day_order)), date_str)
    return (len(day_order), date_str)

# Sort the DataFrame by the custom day order
STR = STR.sort_values(by='Formatted Shipment Date', key=lambda x: x.map(custom_sort_key))

# Update filter options
filter_day = STR['Formatted Shipment Date'].unique().tolist()
filter_year = STR['Shipment Fiscal Year'].unique().tolist()
filter_week = STR['Shipment Fiscal Week'].unique().tolist()
filter_month = STR['Shipment Fiscal Month'].unique().tolist()
filter_quarter = STR['Shipment Fiscal Quarter'].unique().tolist()

def filter_daily_data(day, year, week):
    logging.debug(f"Filtering daily data with day: {day}, year: {year}, week: {week}")
    if isinstance(day, str):
        day = [day]
    if isinstance(year, str):
        year = [year]
    if isinstance(week, str):
        week = [week]
    
    filtered_data = STR[
        (STR['Formatted Shipment Date'].isin(day)) &
        (STR['Shipment Fiscal Year'].isin(year)) &
        (STR['Shipment Fiscal Week'].isin(week))
    ]
    
    logging.debug(f"Filtered daily data: {filtered_data.shape[0]} rows")
    return filtered_data

def filter_weekly_data(year, month=None, week_for_weekly=None):
    logging.debug(f"Filtering weekly data with year: {year}, month: {month}, week_for_weekly: {week_for_weekly}")
    if isinstance(year, str):
        year = [year]
    if month and isinstance(month, str):
        month = [month]
    if week_for_weekly and isinstance(week_for_weekly, str):
        week_for_weekly = [week_for_weekly]

    condition = STR['Shipment Fiscal Year'].isin(year)
    if month:
        condition &= STR['Shipment Fiscal Month'].isin(month)
    if week_for_weekly:
        condition &= STR['Shipment Fiscal Week'].isin(week_for_weekly)

    filtered_data = STR[condition]
    logging.debug(f"Filtered weekly data: {filtered_data.shape[0]} rows")
    return filtered_data

def filter_monthly_data(year, month=None, quarter=None):
    logging.debug(f"Filtering monthly data with year: {year}, month: {month}, quarter: {quarter}")
    if isinstance(year, str):
        year = [year]
    if month and isinstance(month, str):
        month = [month]
    if quarter and isinstance(quarter, str):
        quarter = [quarter]

    condition = STR['Shipment Fiscal Year'].isin(year)
    if month:
        condition &= STR['Shipment Fiscal Month'].isin(month)
    if quarter:
        condition &= STR['Shipment Fiscal Quarter'].isin(quarter)

    filtered_data = STR[condition]
    logging.debug(f"Filtered monthly data: {filtered_data.shape[0]} rows")
    return filtered_data





# Define the create_conformance_dataframe function
def create_conformance_dataframe(df, group_by_columns):
    if isinstance(group_by_columns, str):
        group_by_columns = [group_by_columns]

    aggregation = {
        'Conforming': pd.NamedAgg(column='STR Status', aggfunc=lambda x: (x == 'Conforming').sum()),
        'Non_Conforming': pd.NamedAgg(column='STR Status', aggfunc=lambda x: (x == 'Non-Conforming').sum())
    }

    grouped = df.groupby(group_by_columns).agg(**aggregation).reset_index()

    grouped['Total'] = grouped['Conforming'] + grouped['Non_Conforming']
    grouped['Conforming%'] = (grouped['Conforming'] / grouped['Total']) * 100
    grouped['Non_Conforming%'] = (grouped['Non_Conforming'] / grouped['Total']) * 100

    melted = grouped.melt(id_vars=group_by_columns, 
                          value_vars=['Conforming%', 'Non_Conforming%'], 
                          var_name='Status', 
                          value_name='Percentage')

    return melted



def create_pivot_table(dataframe, index_col, value_col, column_cols):
    """
    Create a pivot table to calculate the percentage of 'Conforming' values,
    append a row with the count of 'Conforming' rows, and add a WTD column.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame.
    index_col (str): The column name to be used as the index for the pivot table.
    value_col (str): The column name where the 'Conforming' status is checked.
    column_cols (list): List of column names to be used as columns in the pivot table.

    Returns:
    pd.DataFrame: A pivot table with the percentage of 'Conforming' values, an additional row for the count of 'Conforming' rows, and a WTD column.
    """
    # Set the order of the technologies
    technology_order = ['MOL', 'ConA', 'CAS', 'Plant']
    dataframe[index_col] = pd.Categorical(dataframe[index_col], categories=technology_order, ordered=True)

    # Create a pivot table for percentage of 'Conforming' values
    pivot_table = pd.pivot_table(
        dataframe,
        values=value_col,
        index=index_col,
        columns=column_cols,
        aggfunc=lambda x: (x == 'Conforming').sum() / len(x) * 100,
        fill_value=0  # Fill missing values with 0
    )
    
    # Calculate the count of 'Conforming' rows for each column
    conforming_counts = pd.pivot_table(
        dataframe,
        values=value_col,
        columns=column_cols,
        aggfunc=lambda x: (x == 'Conforming').sum(),
        fill_value=0  # Fill missing values with 0
    )
    
    # Reset index to have a DataFrame with columns
    pivot_table = pivot_table.reset_index()
    conforming_counts = conforming_counts.reset_index(drop=True)
    conforming_counts[index_col] = 'Total Shipment'
    
    # Format the values to include percentage sign and two decimal places, replace 0% with '-'
    pivot_table = pivot_table.map(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) and x != 0 else ("-" if x == 0 else x))
    
    # Calculate the overall percentage and count for 'Plant'
    overall_percentage = dataframe.groupby(column_cols)[value_col].apply(lambda x: (x == 'Conforming').sum() / len(x) * 100).reset_index()
    overall_percentage[index_col] = 'Plant'
    
    # Pivot the overall_percentage to match the format of pivot_table
    overall_percentage_pivot = overall_percentage.pivot(index=index_col, columns=column_cols, values=value_col).reset_index()
    
    # Format the values to include percentage sign and two decimal places, replace 0% with '-'
    overall_percentage_pivot = overall_percentage_pivot.map(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) and x != 0 else ("-" if x == 0 else x))
    
    # Concatenate the results
    result_table = pd.concat([pivot_table, overall_percentage_pivot, conforming_counts], ignore_index=True)
    return result_table