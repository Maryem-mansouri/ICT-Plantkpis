import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, MATCH, State, ALL
import pandas as pd
import time
from datetime import datetime
from components import card 
from components.filter import create_filter_dropdown
from components.card import create_card
from dataprocessing.STR import (filter_data, create_pivot_table, filter_mrp, STR, filter_week, filter_year, create_conformance_dataframe)
from config.config import (create_config, format_value_STR)
import logging
import plotly.graph_objs as go

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the function to get the current year
def get_current_year():
    return datetime.now().year

def get_last_week(weeks):
    if not weeks:
        return None
    sorted_weeks = sorted(weeks)
    return sorted_weeks[-1]

def layout():
    current_year = get_current_year()
    return dbc.Container(
        fluid=True,
        children=[
            dcc.Store(id='available-year'),
            dcc.Store(id='available-weeks'),
            dcc.Store(id='dashboard3-filters'),
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
                        [
                            create_filter_dropdown("MRP Cont", 'filter-mrp', filter_mrp),
                            create_filter_dropdown("Year", 'filter-year', filter_year),
                            create_filter_dropdown("Week", 'filter-week-STRD', filter_week),
                        ],
                        className="d-flex justify-content-end align-items-center"
                    )
                ],
                className="m-3"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Customer STR", 1, 'dashboard3', False, 'Bar', barmode_group=True), width=8, className="p-1"),
                    dbc.Col(create_card("GPL STR", 2, 'dashboard3', True, 'Bar', barmode_group=False), width=4, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Top 10 Shipped PNs", 3, 'dashboard3', True, 'Bar', barmode_group=False), width=4, className="p-1"),
                    dbc.Col(create_card("DDPs shipments & STR (TOP 10)", 4, 'dashboard3', False, 'Bar', barmode_group=False), width=8, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("DDP STR Evolution % & shipments(1230 - ICT NA Virtual Plant)", 5, 'dashboard3', True, 'Line', barmode_group=False), width=12, className="p-1"),
                ],
                className="m-1"
            ),
        ]
    )

# Register callbacks
def register_callbacks(app):
    @app.callback(
        Output('available-weeks-STRD', 'data'),
        [Input('filter-year', 'value')]
    )
    def update_week_based_on_year(selected_years):
        if not selected_years:
            selected_years = [get_current_year()]
        filtered_df_STR = STR[STR['Shipment Fiscal Year'].isin(selected_years)]
        weeks_STR = filtered_df_STR['Shipment Fiscal Week'].unique().tolist()
        weeks_combined = list(set(weeks_STR))
        weeks_combined.sort()
        return weeks_combined

    @app.callback(
        Output('filter-week-STRD', 'options'),
        [Input('available-weeks-STRD', 'data')]
    )
    def update_week_dropdown(available_weeks):
        if available_weeks is None:
            return []
        sorted_weeks = sorted(available_weeks, key=lambda x: int(x.split('-')[1][2:]))
        return [{'label': week, 'value': week} for week in sorted_weeks]

    @app.callback(
        Output('dashboard3-filters', 'data'),
        [
            Input('filter-mrp', 'value'),
            Input('filter-year', 'value'),
            Input('filter-week-STRD', 'value'),
        ]
    )
    def update_filters(mrp, year, week):
        start_time = time.time()
        if not year:
            year = [get_current_year()]
        if not mrp:
            mrp = filter_mrp
        if not week:
            week = filter_week
        
        filtered_data = filter_data(year, week, mrp)
        end_time = time.time()
        logging.info(f"Filter update took {end_time - start_time:.2f} seconds")
        logging.info(f"Filtered Data: {filtered_data.head()}")
        
        return filtered_data.to_dict('records')
        
    @app.callback(
        [
            Output({'type': 'dashboard3-dynamic-content', 'index': MATCH}, 'children'),
            Output({'type': 'dashboard3-dynamic-content-modal', 'index': MATCH}, 'children'),
        ],
        [
            Input({'type': 'dashboard3-Graph-switch', 'index': MATCH}, 'value'),
            Input({'type': 'dashboard3-chart-type', 'index': MATCH}, 'value'),
            Input('dashboard3-filters', 'data'),
            Input('filter-week-STRD', 'value'),
        ],
        [State({'type': 'dashboard3-dynamic-content', 'index': MATCH}, 'id')]
    )
    def update_charts(switch_value, chart_type, filters, selected_weeks, component_id):
        start_time = time.time()
        if not filters:
            return dash.no_update, dash.no_update

        filtered_df_STR = pd.DataFrame(filters)
        logging.info(f"Filtered DataFrame: {filtered_df_STR.head()}")  # Log the filtered DataFrame
        index = component_id['index']

        if index == 1:
            group_by_cols = ['Sold To Customer']
        elif index == 2:
            group_by_cols = ['GPL']
        elif index == 3:
            group_by_cols = ['Material Number']
        elif index == 4:
            group_by_cols = ['ship from Site']
        elif index == 5:
            group_by_cols = ['Shipment Fiscal Week']
            filtered_df_STR = filtered_df_STR[filtered_df_STR['ship from Site'] == '1230 - ICT NA Virtual Plant']
        else:
            return dash.no_update, dash.no_update

        # Create conformance dataframe for table
        config_data_table = create_pivot_table(filtered_df_STR, group_by_cols)

        if index == 5:
            config_data_graph = create_conformance_dataframe(filtered_df_STR, group_by_cols)
            config_data_graph = config_data_graph[config_data_graph['Status'] == 'Conforming%']
        else:
            # Create conformance dataframe for graph and get top 10 entries
            top10_df = (filtered_df_STR
                        .groupby(group_by_cols)
                        .size()
                        .reset_index(name='Total Lines')
                        .sort_values(by='Total Lines', ascending=False)
                        .head(10))
            
            top10_filtered_df_STR = filtered_df_STR[filtered_df_STR[group_by_cols[0]].isin(top10_df[group_by_cols[0]])]
            config_data_graph = create_conformance_dataframe(top10_filtered_df_STR, group_by_cols)

        config = create_config(config_data_graph, config_data_table, group_by_cols[0], 'Percentage', None, None, 'Status')

        logging.info(f"Config Data: {config_data_graph.head()}")  # Log the config data for graph
        logging.info(f"Config Data Table: {config_data_table.head()}")  # Log the pivot table data

        if switch_value:
            fig = card.get_figure(chart_type, config, "/STR")
            end_time = time.time()
            logging.info(f"Chart update took {end_time - start_time:.2f} seconds")
            return (
                dcc.Graph(figure=fig),
                dcc.Graph(figure=fig)
            )
        else:
            data = config['dataTable']
            
            # Apply formatting to the entire DataFrame except for non-numeric columns
            formatted_data = data.copy()
            for col in formatted_data.columns:
                if 'STR%' in col:
                    formatted_data[col] = formatted_data[col].apply(format_value_STR)

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
                        {
                            'if': {'column_id': 'Conforming STR%'},
                            'color': '#3B8AD9',
                            'backgroundColor': '#daf7fb',
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'column_id': 'Non-Conforming STR%'},
                            'color': '#F18226',
                            'backgroundColor': '#fce6d3',
                            'fontWeight': 'bold'
                        },
                        {
                             'if': {'column_id': 'Total n° of lines'},
                             'backgroundColor': '#feffba',
                             'fontWeight': 'bold'
                        }
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

