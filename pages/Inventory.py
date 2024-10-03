import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, MATCH, State, ALL
import pandas as pd
import time
from datetime import datetime
from sqlalchemy import create_engine,text
from components import card 
from components.filter import create_filter_dropdown
from components.card import create_card
from dataprocessing.Inventory import ( engine ,filter_data,filtered_inventory_melted, filter_week, filter_plant, filter_year, create_summary_dataframe, create_pivot_table, create_pivot_table_with_columns)
from config.config import (create_config, format_value)
import logging
import plotly.graph_objs as go

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the function to get the current year
def get_current_year():
    return datetime.now().year
def create_evolution_chart():
    # Query the target values from the Target_Table
    target_query = "SELECT Month, Target FROM Target_Table ORDER BY Month"
    target_data = pd.read_sql(target_query, engine)
    
    # Query the inventory values from the two_plants_inventory_ICT table for the last week of each month
    inventory_query = """
        SELECT
            t.Month,
            t.Inventory_Value
        FROM
        (
            SELECT
                Month,
                Inventory_Value,
                ROW_NUMBER() OVER (PARTITION BY Month ORDER BY Weeks DESC) AS rn
            FROM
                two_plants_inventory_ICT
        ) AS t
        WHERE t.rn = 1
        ORDER BY t.Month
    """
    inventory_data = pd.read_sql(inventory_query, engine)
    
    month_order = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    # Convert the 'Month' column to a categorical type with the specified order
    target_data['Month'] = pd.Categorical(target_data['Month'], categories=month_order, ordered=True)
    inventory_data['Month'] = pd.Categorical(inventory_data['Month'], categories=month_order, ordered=True)
    
    # Merge the two DataFrames on the 'Month' column to align the data
    merged_data = pd.merge(target_data, inventory_data, on='Month', how='outer')
    
    # Sort the merged data based on the custom month order
    merged_data = merged_data.sort_values('Month')
    
    # Print merged data for debugging
    print("Merged Data:")
    print(merged_data)

    # Create a line chart with Plotly
    fig = go.Figure()

    # Add the target evolution line
    fig.add_trace(go.Scatter(
        x=merged_data['Month'],
        y=merged_data['Target'],
        mode='lines+markers',
        name='Target Evolution',
        line=dict(color='#2FA9A1', width=2),
        marker=dict(size=6)  # Reduce marker size
    ))

    # Add the inventory evolution line
    fig.add_trace(go.Scatter(
        x=merged_data['Month'],
        y=merged_data['Inventory_Value'],
        mode='lines+markers',
        name='Inventory Value Evolution',
        line=dict(color='#FB8500', width=2),
        marker=dict(size=6)  # Reduce marker size
    ))

    # Adjust layout to fit the card size
    fig.update_layout(
        
        legend=dict(
            orientation='h',
            y=1,
            xanchor='left',
            x=0,
            bgcolor='rgba(255, 255, 255, 0.25)',
            font=dict(size=8)
        ), # Adjust legend position and size
        margin=dict(l=20, r=20, t=30, b=20),  # Adjust margins to fit content better
        plot_bgcolor='#f2f7fc',  # Background color of the plotting area
        paper_bgcolor='#FFFFFF',
        height=150,  # Set graph height to fit the card
    )
    
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6("Target Evolution vs Inventory Value Evolution", className="card-title"),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ]
        ),
        style={"height": "14em", "borderRadius": "10px"},  # Adjust card height to fit the graph
        className="shadow-sm"
    )
def create_gauge_chart(value, target):
    if target is None:
        target = 5000000  # default target value
    else:
        target = float(target)

    value = float(value)
    color = "orange" if value < target else "#6cb284"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "$", 'font': {'size': 30, 'color': 'orange'}},
        gauge={
            'axis': {'range': [0, 12000000], 'tickwidth': 1, 'tickcolor': "gray"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, target], 'color': "lightgray"},
                {'range': [target, 12000000], 'color': "lightgray"},
                {'range': [0, value], 'color': color}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=100,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig

def createtarget_card(title, value, target):
    difference = value - target
    if difference < 0:
        status = f"Below target by {format_value(abs(difference))}"
    else:
        status = f"Above target by {format_value(difference)}"

    fig = create_gauge_chart(value, target)

    card = dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.H6(title, className="card-title", style={'display': 'inline-block'}),
                        html.Span(f"Target: {format_value(target)}", className="card-target", style={'float': 'right', 'color': '#000000','fontSize': '12px'}),
                    ],
                    style={'width': '100%'}
                ),
                html.P(status, className="card-text", style={'color': 'grey'}),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ],
            style={"background": "linear-gradient(135deg, #ffffff 0%, #FFE7CC 100%)", "borderRadius": "10px"}
        ),
        style={"height": "14em", "borderRadius": "20px"}, className="border-0"
    )

    return card


# Define the layout function
def layout():
    current_year = get_current_year()
    return dbc.Container(
        fluid=True,
        children=[
            dcc.Store(id='available-year'),
            dcc.Store(id='available-weeks'),
            dcc.Store(id='dashboard1-filters'),
            dcc.Store(id='stored-target', data=5000000),  # Initialize with default target value

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            children=[
                                "Generate a report",
                                html.Img(src="assets/solar_export-outline.png", className='ms-2', height="20px")
                            ],
                            className="me-2",
                            id="dashboard4-generate-report-btn",
                            style={'fontWeight': 'bold', 'backgroundColor': '#FB8500', 'borderColor': '#FB8500', 'borderRadius': '10px'}
                        ),
                        width="auto",
                        className="d-flex align-items-center"
                    ),
                    dbc.Col(
                        html.Div(id="target-output", style={'fontWeight': 'bold', 'color': '#668586'}),
                        width="auto",
                        className="d-flex align-items-center"
                    ),
                    dbc.Col(
                        [
                            create_filter_dropdown("Plant", 'filter-location', filter_plant, ['TE Connectivity Morocco ICT', 'TE Connectivity Morocco']),
                            create_filter_dropdown("Year", 'filter-year', filter_year),
                            create_filter_dropdown("Week", 'filter-week', filter_week),
                        ],
                        className="d-flex justify-content-end align-items-center"
                    )
                ],
                className="m-3"
            ),
            dbc.Row(
                [
                    dbc.Col(create_evolution_chart(), width=8, className="p-1"),
                    dbc.Col(id='card-TE-Inventory-ICT', width=4, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Inventory Value in Moroccan Plants", 1, 'dashboard1', True, 'Bar', barmode_group=True), width=8, className="p-1"),
                    dbc.Col(create_card("Weekly Inventory Trend", 2, 'dashboard1', True, 'Line', barmode_group=False), width=4, className="p-1"),
                ],
                className="m-1"
            ),
             dbc.Row(
                [
                    dbc.Col(create_card("Inventory Value By Material Type", 3, 'dashboard1', True, 'Bar', barmode_group=False), width=6, className="p-1"),
                    dbc.Col(create_card("Inventory Value By MRP Controller", 4, 'dashboard1', False, 'Bar', barmode_group=True), width=6, className="p-1"),
                ],
                className="m-1"
            ),
        ]
    )

# Register callbacks
def register_callbacks(app):
    @app.callback(
        Output('available-weeks', 'data'),
        [Input('filter-year', 'value')]
    )
    def update_week_based_on_year(selected_years):
        if not selected_years:
            selected_years = [get_current_year()]
        
        # Query data from the database based on selected year(s)
        query = f"SELECT * FROM Inventory_ICT WHERE Year IN ({', '.join([str(year) for year in selected_years])})"
        filtered_df_EDI = pd.read_sql(query, engine)
        weeks_EDI = filtered_df_EDI['Week Number'].unique().tolist()        
        weeks_combined = list(set(weeks_EDI))
        weeks_combined.sort()
        
        return weeks_combined

    @app.callback(
        Output('filter-week', 'options'),
        [Input('available-weeks', 'data')]
    )
    def update_week_dropdown(available_weeks):
        if available_weeks is None:
            return []
        sorted_weeks = sorted(available_weeks, key=lambda x: int(x))
        return [{'label': week, 'value': week} for week in sorted_weeks]

    @app.callback(
        Output('dashboard1-filters', 'data'),
        [
            Input('filter-location', 'value'),
            Input('filter-year', 'value'),
            Input('filter-week', 'value'),
        ]
    )
    def update_filters(loc, year, week):
        start_time = time.time()
        if not year:
            year = [get_current_year()]
        if not loc:
            loc = filter_plant
        if not week:
            week = filter_week
        
        # Query data from the database based on filters
        query = f"""
        SELECT * FROM Inventory_ICT
        WHERE [Plant Name] IN ({', '.join([f"'{plant}'" for plant in loc])})
        AND Year IN ({', '.join([str(y) for y in year])})
        AND [Week Number] IN ({', '.join([str(w) for w in week])})
        """
        filtered_data = pd.read_sql(query, engine)
        end_time = time.time()
        logging.info(f"Filter update took {end_time - start_time:.2f} seconds")
        logging.info(f"Filtered Data: {filtered_data.head()}")
        return filtered_data.to_dict('records')
    
    @app.callback(
        [
            Output({'type': 'dashboard1-dynamic-content', 'index': MATCH}, 'children'),
            Output({'type': 'dashboard1-dynamic-content-modal', 'index': MATCH}, 'children'),
        ],
        [
            Input({'type': 'dashboard1-Graph-switch', 'index': MATCH}, 'value'),
            Input({'type': 'dashboard1-chart-type', 'index': MATCH}, 'value'),
            Input('dashboard1-filters', 'data'),
            Input('filter-week', 'value'),
        ],
        [State({'type': 'dashboard1-dynamic-content', 'index': MATCH}, 'id')]
    )
    def update_charts(switch_value, chart_type, filters, selected_weeks, component_id):
        start_time = time.time()
        if not filters:
            return dash.no_update, dash.no_update

        filtered_df_EDI = pd.DataFrame(filters)
        logging.info(f"Filtered DataFrame: {filtered_df_EDI.head()}")  # Log the filtered DataFrame
        index = component_id['index']

        if index == 1:
            group_by_cols = ['Week Number', 'Plant Name']
            agg_col = 'Inventory_Value'
            config_data = create_summary_dataframe(filtered_df_EDI, group_by_cols, agg_col)
            config_data_table = create_pivot_table(filtered_df_EDI,'Plant Name','Week Number', 'Inventory_Value')
        elif index == 2:
            group_by_cols = ['Week Number']
            agg_col = 'Inventory_Value'
            config_data = create_summary_dataframe(filtered_df_EDI, group_by_cols, agg_col)
            config_data_table = create_pivot_table_with_columns(filtered_df_EDI,'Week Number', 'Inventory_Value')
        elif index == 3:
            group_by_cols = ['Week Number', 'Material Type']
            agg_col = 'Inventory_Value'
            config_data = create_summary_dataframe(filtered_df_EDI, group_by_cols, agg_col)
            config_data_table = create_pivot_table(filtered_df_EDI, 'Material Type', 'Week Number', 'Inventory_Value')
        elif index == 4:
            group_by_cols = ['Week Number', 'MRP Controller']
            agg_col = 'Inventory_Value'
            config_data = create_summary_dataframe(filtered_df_EDI, group_by_cols, agg_col)
            top_10_mrp_controllers = (config_data.groupby('MRP Controller')['Inventory_Value']
                                      .sum()
                                      .nlargest(10)
                                      .index)
            config_data = config_data[config_data['MRP Controller'].isin(top_10_mrp_controllers)]
            config_data_table = create_pivot_table(filtered_df_EDI, 'MRP Controller', 'Week Number', 'Inventory_Value')
        else:
            return dash.no_update, dash.no_update

        config = create_config(
            config_data,
            config_data_table,
            'Week Number' if index in [1, 2, 3, 4] else None,
            'Inventory_Value',
            None,
            None,
            'Plant Name' if index == 1 else 'Material Type' if index == 3 else 'MRP Controller' if index == 4 else None
        )

        logging.info(f"Config Data: {config_data.head()}")  # Log the config data
        logging.info(f"Config Data Table: {config_data_table.head()}")  # Log the pivot table data

        if switch_value:
            fig = card.get_figure(chart_type, config, "/Inventory")
            end_time = time.time()
            logging.info(f"Chart update took {end_time - start_time:.2f} seconds")
            return (
                dcc.Graph(figure=fig),
                dcc.Graph(figure=fig)
            )
        else:
            data = config['dataTable']
            
            formatted_data = data.copy()
            for col in formatted_data.columns:
                if formatted_data[col].dtype in ['int64', 'float64']:
                    formatted_data[col] = formatted_data[col].apply(format_value)

            table = dcc.Loading(
                children=[dash_table.DataTable(
                    data=formatted_data.to_dict('records'),
                    columns=[{'name': str(i), 'id': str(i)} for i in formatted_data.columns],
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'font-size': '14px',
                        'border': '1px solid #e0e0e0'
                    },
                    style_header={
                        'backgroundColor': '#F1F4F9',
                        'fontWeight': 'bold',
                        'font-size': '14px',
                        'border': 'none'
                    },
                    style_data={
                        'border': 'none',
                        'font-size': '14px',
                        'color': 'black',
                        'borderBottom': '1px solid #F6F6F6'
                    },
                    style_filter={
                        'border': 'none',
                        'font-size': '14px',
                        'color': 'black',
                        'borderBottom': '1px solid #e0e0e0'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        },
                        {
                            'if': {'row_index': 'even'},
                            'backgroundColor': 'white'
                        },
                    ],
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode='multi',
                    page_action='native',
                    page_current=0,
                    page_size=10,
                )], type="default"
            )
            end_time = time.time()
            logging.info(f"Table update took {end_time - start_time:.2f} seconds")
            return table, table


    
    
    @app.callback(
    Output('card-TE-Inventory-ICT', 'children'),
    [Input('dashboard1-filters', 'data')]
)
    
        
    def update_combined_card(filters):
        if not filters:
            return dash.no_update
    
        # Convert the filters to a DataFrame
        filtered_df_EDI = pd.DataFrame(filters)
        logging.info(f"Filtered DataFrame for Combined Card: {filtered_df_EDI.head()}")
    
        # Get the last week inventory value for both plants combined
        last_week = filtered_df_EDI['Week Number'].max()
        last_week_data = filtered_df_EDI[filtered_df_EDI['Week Number'] == last_week]
    
        combined_value = last_week_data['Inventory_Value'].sum()
    
        # Get the current month associated with the last week
        current_month_query = f"""
        SELECT DISTINCT Month FROM two_plants_inventory_ICT
        WHERE Weeks = (SELECT MAX(Weeks) FROM two_plants_inventory_ICT)
        """
        
        with engine.connect() as connection:
            current_month_result = connection.execute(text(current_month_query)).fetchone()
            if current_month_result:
                current_month = current_month_result[0]
            else:
                current_month = None
        
        # Fetch the target from the Target_Table for the current month
        if current_month:
            target_query = f"SELECT Target FROM Target_Table WHERE Month = '{current_month}'"
            with engine.connect() as connection:
                target_result = connection.execute(text(target_query)).fetchone()
                if target_result:
                    target_value = target_result[0]
                else:
                    target_value = 12000000  # fallback target value
        else:
            target_value = 12000000  # fallback target value if month is not found
    
        # Create the card with the fetched target value
        combined_card = createtarget_card(f"Inventory Value vs Target ({current_month})", combined_value, target_value)
    
        return combined_card