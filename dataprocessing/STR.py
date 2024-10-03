import pandas as pd
from datetime import datetime
import logging
from dataprocessing.STR_Summary import STR , create_conformance_dataframe




# Update filter options

filter_year = STR['Shipment Fiscal Year'].unique().tolist()
filter_week = STR['Shipment Fiscal Week'].unique().tolist()
filter_mrp = STR['MRP Contr.'].unique().tolist()


def filter_data(year, week, mrp):
    logging.debug(f"Filtering data with year: {year}, week: {week}, mrp: {mrp}")

    # Convert inputs to lists if they are not already
    if isinstance(year, str):
        year = [year]
    if isinstance(week, str):
        week = [week]
    if isinstance(mrp, str):
        mrp = [mrp]

    # Print unique values in the DataFrame columns
    logging.debug(f"Unique years in data: {STR['Shipment Fiscal Year'].unique()}")
    logging.debug(f"Unique weeks in data: {STR['Shipment Fiscal Week'].unique()}")
    logging.debug(f"Unique mrp in data: {STR['MRP Contr.'].unique()}")

    # Print the first few rows of the DataFrame
    logging.debug(f"First few rows of STR:\n{STR.head()}")

    # Apply the filter step by step
    year_filtered = STR[STR['Shipment Fiscal Year'].isin(year)]
    logging.debug(f"Data after year filter: {year_filtered.shape[0]} rows")
    logging.debug(f"First few rows after year filter:\n{year_filtered.head()}")

    week_filtered = year_filtered[year_filtered['Shipment Fiscal Week'].isin(week)]
    logging.debug(f"Data after week filter: {week_filtered.shape[0]} rows")
    logging.debug(f"First few rows after week filter:\n{week_filtered.head()}")

    mrp_filtered = week_filtered[week_filtered['MRP Contr.'].isin(mrp)]
    logging.debug(f"Data after mrp filter: {mrp_filtered.shape[0]} rows")
    logging.debug(f"First few rows after mrp filter:\n{mrp_filtered.head()}")

    return mrp_filtered



def create_pivot_table(df, group_by_cols):
    # Ensure group_by_cols is a list
    if isinstance(group_by_cols, str):
        group_by_cols = [group_by_cols]

    # Filter conforming and non-conforming rows
    conforming = df[df['STR Status'] == 'Conforming']
    non_conforming = df[df['STR Status'] == 'Non-Conforming']

    # Group by the specified column(s) and calculate metrics
    pivot_table = df.groupby(group_by_cols).size().reset_index(name='Total n° of lines')
    
    conforming_grouped = conforming.groupby(group_by_cols).size().reset_index(name='Conforming n° of lines')
    non_conforming_grouped = non_conforming.groupby(group_by_cols).size().reset_index(name='Non-Conforming n° of lines')
    
    # Merge the grouped data back to the pivot table
    pivot_table = pivot_table.merge(conforming_grouped, on=group_by_cols, how='left')
    pivot_table = pivot_table.merge(non_conforming_grouped, on=group_by_cols, how='left')
    
    # Calculate STR percentages
    pivot_table['Conforming STR%'] = (pivot_table['Conforming n° of lines'] / pivot_table['Total n° of lines']) * 100
    pivot_table['Non-Conforming STR%'] = (pivot_table['Non-Conforming n° of lines'] / pivot_table['Total n° of lines']) * 100
    pivot_table['Total STR%'] = 100

    # Fill NaN values with 0
    pivot_table = pivot_table.fillna(0)

    # Reorder columns to match the desired order
    column_order = ['Conforming STR%', 'Conforming n° of lines', 'Non-Conforming STR%', 'Non-Conforming n° of lines', 'Total STR%', 'Total n° of lines']
    pivot_table = pivot_table[group_by_cols + column_order]

    # Add a grand total row
    grand_total = pd.DataFrame({
        group_by_cols[0]: ['Grand Total'],
        'Total n° of lines': [pivot_table['Total n° of lines'].sum()],
        'Conforming n° of lines': [pivot_table['Conforming n° of lines'].sum()],
        'Non-Conforming n° of lines': [pivot_table['Non-Conforming n° of lines'].sum()],
        'Conforming STR%': [pivot_table['Conforming n° of lines'].sum() / pivot_table['Total n° of lines'].sum() * 100],
        'Non-Conforming STR%': [pivot_table['Non-Conforming n° of lines'].sum() / pivot_table['Total n° of lines'].sum() * 100],
        'Total STR%': [100]
    })
    pivot_table = pd.concat([pivot_table, grand_total], ignore_index=True)

    return pivot_table