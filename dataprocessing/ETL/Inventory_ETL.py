import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# Connection string for SQL Server
conn_str = (
    'mssql+pyodbc://MAN61NBO1VZ06Y2\SQLEXPRESS/Plantkpis_Sp_db?'
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Create SQL Alchemy engine with fast execution parameters
engine = create_engine(conn_str, fast_executemany=True)

def get_latest_weeks_columns(df, weeks_count=6):
    # Find all column headers that match the "WK" pattern
    week_columns = [col for col in df.columns if "WK" in col]
    # Sort them to make sure they are in the correct order (newest last)
    week_columns.sort(key=lambda date: datetime.strptime(date, "2024-WK%U"), reverse=True)
    # Return the latest 'weeks_count' weeks
    return week_columns[:weeks_count]

def processing(file_path, chunk_size=1000):
    # Load the ICT inventory data from Excel
    ICT_inventory = pd.read_excel(file_path)

    # Load Material_Type from the SQL database
    material_type_query = "SELECT * FROM Material_Type"  # Adjust the table name if needed
    Material_Type = pd.read_sql(material_type_query, engine)

    # Merge the dataframes on 'Material Number'
    ICT_inventory = pd.merge(ICT_inventory, Material_Type, on='Material Number', how='left')

    # Get the latest 6 weeks
    latest_weeks = get_latest_weeks_columns(ICT_inventory)

    # Melt the dataframe to reshape it and include all other columns
    filtered_inventory_melted = ICT_inventory.melt(
        id_vars=['Material Number', 'GPL', 'BU', 'Plant Name', 'Storage Location', 'Region', 
                 'MRP Controller', 'Special Stock Name', 'Stock Category Name', 'Material Type Description', 
                 'Procurement Type', 'Procurement Type Name', 'Material Type'],
        value_vars=latest_weeks,
        var_name='Weeks',
        value_name='Inventory_Value'
    )

    # Extract the year and week number from the Weeks column
    filtered_inventory_melted['Year'] = filtered_inventory_melted['Weeks'].apply(lambda x: x.split('-')[0])
    filtered_inventory_melted['Week Number'] = filtered_inventory_melted['Weeks'].apply(lambda x: int(x.split('-WK')[1]))

    # Keep only the specified columns
    filtered_inventory_melted = filtered_inventory_melted[['Material Number', 'GPL', 'BU', 'Plant Name', 'Region', 
                                                          'MRP Controller', 'Material Type Description', 
                                                          'Material Type', 'Weeks', 'Week Number', 'Inventory_Value', 'Year']]

    # SQL statement to create the Inventory_ICT table if it doesn't exist
    create_inventory_table_query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Inventory_ICT' AND xtype='U')
    BEGIN
        CREATE TABLE dbo.Inventory_ICT (
            [Material Number] VARCHAR(255),
            GPL VARCHAR(255),
            BU VARCHAR(255),
            [Plant Name] VARCHAR(255),
            Region VARCHAR(255),
            [MRP Controller] VARCHAR(255),
            [Material Type Description] VARCHAR(255),
            [Material Type] VARCHAR(255),
            Weeks VARCHAR(255),
            [Week Number] INT,
            Inventory_Value FLOAT,
            Year VARCHAR(255)
        );
    END
    """

    # Execute the create table query
    with engine.connect() as connection:
        connection.execute(text(create_inventory_table_query))

    # Insert data into SQL table using chunks
    table_name = 'Inventory_ICT'
    
    for i, chunk in enumerate(range(0, len(filtered_inventory_melted), chunk_size)):
        data_chunk = filtered_inventory_melted.iloc[chunk:chunk + chunk_size]
        data_chunk.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Inserted chunk {i + 1}/{(len(filtered_inventory_melted) // chunk_size) + 1}")

    print(f"Data has been successfully inserted into the {table_name} table.")
    
    # Debugging: Check if any rows match the plants of interest
    plant_check_query = """
    SELECT COUNT(*) FROM dbo.Inventory_ICT
    WHERE [Plant Name] IN ('TE Connectivity Morocco', 'TE Connectivity Morocco ICT');
    """
    with engine.connect() as connection:
        result = connection.execute(text(plant_check_query)).fetchone()
        print(f"Number of rows matching the plants: {result[0]}")
    
    # Check the data to be inserted into two_plants_inventory_ICT
    debug_query = """
    SELECT 
        ICT.Weeks,
        Cal.Month,
        SUM(ICT.Inventory_Value) AS Inventory_Value
    FROM 
        dbo.Inventory_ICT ICT
    JOIN 
        dbo.Calendar Cal 
    ON 
        ICT.Weeks = Cal.[Fiscal Week]
    WHERE 
        ICT.[Plant Name] IN ('TE Connectivity Morocco', 'TE Connectivity Morocco ICT')
    GROUP BY 
        ICT.Weeks, 
        Cal.Month;
    """
    
    with engine.connect() as connection:
        debug_result = connection.execute(text(debug_query)).fetchall()
        print("Data to be inserted into two_plants_inventory_ICT:")
        for row in debug_result:
            print(row)
    
    # Populate the two_plants_inventory_ICT table
    insert_two_plants_query = """
    INSERT INTO dbo.two_plants_inventory_ICT (Weeks, Month, Inventory_Value)
    SELECT 
        ICT.Weeks,
        Cal.Month,
        SUM(ICT.Inventory_Value) AS Inventory_Value
    FROM 
        dbo.Inventory_ICT ICT
    JOIN 
        dbo.Calendar Cal 
    ON 
        ICT.Weeks = Cal.[Fiscal Week]
    WHERE 
        ICT.[Plant Name] IN ('TE Connectivity Morocco', 'TE Connectivity Morocco ICT')
    GROUP BY 
        ICT.Weeks, 
        Cal.Month;
    """
    
    with engine.begin() as connection:  # using begin() to ensure commit
        result = connection.execute(text(insert_two_plants_query))
        print(f"Inserted rows into two_plants_inventory_ICT: {result.rowcount}")

    print("Data has been successfully inserted into the two_plants_inventory_ICT table.")

# Example usage of the processing function
file_path = r'C:\Users\TE582412\Desktop\Plant KPIS\ICT\Data before ETL\Inventory data.xlsx'
processing(file_path)
