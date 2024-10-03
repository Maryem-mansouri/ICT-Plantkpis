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
from dataprocessing.STR_Summary import (
     custom_sort_key, filter_month,filter_quarter,filter_monthly_data, create_pivot_table,filter_weekly_data, filter_daily_data,STR, filter_week, filter_day, filter_year, create_conformance_dataframe
)
from config.config import (
    create_config, format_value, format_value_STR
)
import logging
import plotly.graph_objs as go

logging.basicConfig(level=logging.INFO)

def get_current_year():
    return datetime.now().year

def get_last_month(months):
    if not months:
        return None
    sorted_months = sorted(months)
    return sorted_months[-1]

def get_last_quarter(quarter):
    if not quarter:
        return None
    sorted_quarter = sorted(quarter)
    return sorted_quarter[-1]


def create_gauge_chart(value, target):
    if target is None:
        target = 95
    else:
        target = float(target)

    value = float(value)
    color = "orange" if value < target else "#6cb284"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'size': 30, 'color': 'orange'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "gray"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, target], 'color': "lightgray"},
                {'range': [target, 100], 'color': "lightgray"},
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
        status = f"Below target by {format_value_STR(abs(difference))}"
    else:
        status = f"Above target by {format_value_STR(difference)}"

    fig = create_gauge_chart(value, target)

    card = dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.H6(title, className="card-title", style={'display': 'inline-block'}),
                        html.Span(f"Target: {format_value_STR(target)}", className="card-target", style={'float': 'right', 'color': '#000000', 'fontSize': '12px'}),
                    ],
                    style={'width': '100%', 'margin-bottom': '10px'}
                ),
                html.P(status, className="card-text", style={'color': 'grey', 'text-align': 'center', 'margin-bottom': '10px'}),
                html.Div(
                    dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '200px', 'width': '100%'}),
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': 'calc(100% - 60px)'}
                )
            ],
            style={"background": "linear-gradient(135deg, #ffffff 0%, #FFE7CC 100%)", "borderRadius": "10px", "padding": "20px"}
        ),
        style={"height": "25em", "borderRadius": "20px"}, className="border-0"
    )

    return card

def layout():
    current_year = get_current_year()
    return dbc.Container(
        fluid=True,
        children=[
            dcc.Store(id='available-year'),
            dcc.Store(id='available-weeks-STR'),
            dcc.Store(id='available-days-STR'),
            dcc.Store(id='available-months'),
            dcc.Store(id='available-weeks-for-weekly'),
            dcc.Store(id='available-months-for-monthly'),
            dcc.Store(id='dashboard2-filters'),
            dcc.Store(id='available-quarters'),
            dcc.Store(id='stored-target-STR', data=95),

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
                        dbc.Input(
                            id="target-input-STR",
                            type="number",
                            placeholder="  Set Target in %",
                            className="me-2",
                            style={'width': '200px', 'borderRadius': '10px'}
                        ),
                        width="auto",
                        className="d-flex align-items-center"
                    ),
                    dbc.Col(
                        dbc.Button(
                            children=[
                                "Set Target",
                                html.Img(src="assets/goals.png", className='ms-2', height="20px")
                            ],
                            id="set-target-btn-STR",
                            className="me-2",
                            style={
                                'fontWeight': 'bold',
                                'borderRadius': '10px',
                                'backgroundColor': '#FFFFFF',
                                'color': '#FB8500',
                                'borderColor': '#FB8500'
                            }
                        ),
                        width="auto",
                        className="d-flex align-items-center"
                    ),
                    dbc.Col(
                        html.Div(id="target-output-STR", style={'fontWeight': 'bold', 'color': '#668586'}),
                        width="auto",
                        className="d-flex align-items-center"
                    ),
                    
                    dbc.Col(
                        [
                            create_filter_dropdown("Year", 'filter-year', filter_year, [current_year]),
                           
                            create_filter_dropdown("Week for Daily", 'filter-week-STR', filter_week, ['2024-WK23']),
                            create_filter_dropdown("Day", 'filter-day', filter_day),
                             
                        ],
                        className="d-flex justify-content-end align-items-center"
                    )
                ],
                className="m-3"
            ),
            dbc.Row(
                [
                    dbc.Col(id='daily-target-card', width=2, className="p-1"),
                    dbc.Col(create_card("Daily STR", 4, 'dashboard2', False, 'Bar', barmode_group=True, show_switch=False), width=10, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Daily STR CAS", 1, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Daily STR MOL", 2, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Daily STR ConA", 3, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Col(
                [
                    create_filter_dropdown("Year", 'filter-year', filter_year, [current_year]),
                    create_filter_dropdown("Month", 'filter-month', filter_month,get_last_month(filter_month)),  # Month filter without default value
                    create_filter_dropdown("Week for Weekly", 'filter-week-for-weekly', filter_week)  # Week filter for weekly STR
                ],
                className="d-flex justify-content-end align-items-center"
            ),
            dbc.Row(
                [
                    dbc.Col(id='weekly-target-card', width=2, className="p-1"),
                    dbc.Col(create_card("Weekly STR", 5, 'dashboard2', False, 'Bar', barmode_group=True, show_switch=False), width=10, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Weekly STR CAS", 6, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Weekly STR MOL", 7, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Weekly STR ConA", 8, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Col(
                [
                    create_filter_dropdown("Year", 'filter-year', filter_year, [current_year]),
                    create_filter_dropdown("Quarter", 'filter-Quarter', filter_quarter,get_last_quarter(filter_quarter)),  # Month filter without default value
                    create_filter_dropdown("Month", 'filter-month-monthly', filter_month),
                    # Month filter without default value
                ],
                className="d-flex justify-content-end align-items-center"
            ),
             dbc.Row(
                [
                    dbc.Col(id='Monthly-target-card', width=2, className="p-1"),
                    dbc.Col(create_card("Monthly STR", 9, 'dashboard2', False, 'Bar', barmode_group=True, show_switch=False), width=10, className="p-1"),
                ],
                className="m-1"
            ),
            dbc.Row(
                [
                    dbc.Col(create_card("Monthly STR CAS", 10, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Monthly STR MOL", 11, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                    dbc.Col(create_card("Monthly STR ConA", 12, 'dashboard2', True, 'Bar', barmode_group=True), width=4, className="p-1"),
                ],
                className="m-1"
            ),
        ]
    )

def register_callbacks(app):
    # Callbacks for daily tracking filters
    @app.callback(
        Output('available-weeks-STR', 'data'),
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
        Output('filter-week-STR', 'options'),
        [Input('available-weeks-STR', 'data')]
    )
    def update_week_dropdown(available_weeks):
        if available_weeks is None:
            return []
        sorted_weeks = sorted(available_weeks, key=lambda x: int(x.split('-')[1][2:]))
        return [{'label': week, 'value': week} for week in sorted_weeks]

    @app.callback(
        Output('available-days-STR', 'data'),
        [Input('filter-week-STR', 'value')]
    )
    def update_day_based_on_week(selected_weeks):
        if not selected_weeks:
            return []
        if isinstance(selected_weeks, str):
            selected_weeks = [selected_weeks]
        filtered_df_STR = STR[STR['Shipment Fiscal Week'].isin(selected_weeks)]
        days_STR = filtered_df_STR['Formatted Shipment Date'].unique().tolist()
        days_combined = list(set(days_STR))
        days_combined.sort()
        return days_combined

    @app.callback(
        Output('filter-day', 'options'),
        [Input('available-days-STR', 'data')]
    )
    def update_day_dropdown(available_days):
        if available_days is None:
            return []
        day_order = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_order_dict = {day: i for i, day in enumerate(day_order)}
        sorted_days = sorted(available_days, key=lambda x: (day_order_dict.get(x.split('-')[1], len(day_order)), x))
        return [{'label': day, 'value': day} for day in sorted_days]

    # Callbacks for weekly tracking filters
    @app.callback(
        Output('available-months', 'data'),
        [Input('filter-year', 'value')]
    )
    def update_month_based_on_year(selected_years):
        if not selected_years:
            selected_years = [get_current_year()]
        filtered_df_STR = STR[STR['Shipment Fiscal Year'].isin(selected_years)]
        months = filtered_df_STR['Shipment Fiscal Month'].unique().tolist()
        months_combined = list(set(months))
        months_combined.sort()
        return months_combined

    @app.callback(
        Output('filter-month', 'options'),
        [Input('available-months', 'data')]
    )
    def update_month_dropdown(available_months):
        if available_months is None:
            return []
        options = [{'label': month, 'value': month} for month in available_months]
        return options

    @app.callback(
        Output('available-weeks-for-weekly', 'data'),
        [Input('filter-month', 'value')]
    )
    def update_weeks_based_on_month(selected_months):
        if not selected_months:
            return []
        if isinstance(selected_months, str):
            selected_months = [selected_months]
        filtered_df_STR = STR[STR['Shipment Fiscal Month'].isin(selected_months)]
        weeks = filtered_df_STR['Shipment Fiscal Week'].unique().tolist()
        weeks_combined = list(set(weeks))
        weeks_combined.sort()
        return weeks_combined

    @app.callback(
        Output('filter-week-for-weekly', 'options'),
        [Input('available-weeks-for-weekly', 'data')]
    )
    def update_week_for_weekly_dropdown(available_weeks):
        if available_weeks is None:
            return []
        return [{'label': week, 'value': week} for week in available_weeks]

    
    @app.callback(
        Output('available-quarters', 'data'),
        [Input('filter-year', 'value')]
    )
    def update_quarter_based_on_year(selected_years):
        if not selected_years:
            selected_years = [get_current_year()]
        filtered_df_STR = STR[STR['Shipment Fiscal Year'].isin(selected_years)]
        quarters = filtered_df_STR['Shipment Fiscal Quarter'].unique().tolist()
        quarters_combined = list(set(quarters))
        quarters_combined.sort()
        return quarters_combined

    @app.callback(
        Output('filter-Quarter', 'options'),
        [Input('available-quarters', 'data')]
    )
    def update_quarter_dropdown(available_quarters):
        if available_quarters is None:
            return []
        options = [{'label': quarter, 'value': quarter} for quarter in available_quarters]
        return options

    @app.callback(
        Output('available-months-for-monthly', 'data'),
        [Input('filter-Quarter', 'value')]
    )
    def update_months_based_on_quarter(selected_quarter):
        if not selected_quarter:
            return []
        if isinstance(selected_quarter, str):
            selected_quarter = [selected_quarter]
        filtered_df_STR = STR[STR['Shipment Fiscal Quarter'].isin(selected_quarter)]
        months = filtered_df_STR['Shipment Fiscal Month'].unique().tolist()
        months_combined = list(set(months))
        months_combined.sort()
        return months_combined

    @app.callback(
        Output('filter-month-monthly', 'options'),
        [Input('available-months-for-monthly', 'data')]
    )
    def update_month_for_monthly_dropdown(available_months):
        if available_months is None:
            return []
        return [{'label': month, 'value': month} for month in available_months]

    
    @app.callback(
    Output('dashboard2-filters', 'data'),
    [
        Input('filter-day', 'value'),
        Input('filter-year', 'value'),
        Input('filter-week-STR', 'value'),
        Input('filter-month', 'value'),
        Input('filter-week-for-weekly', 'value'),
        Input('filter-month-monthly', 'value'),
        Input('filter-Quarter', 'value')
    ]
)
    def update_filters(day, year, week, month, week_for_weekly, month_for_monthly, quarter):
        logging.debug(f"Updating filters with day: {day}, year: {year}, week: {week}, month: {month}, quarter: {quarter}, week_for_weekly: {week_for_weekly}, month_for_monthly: {month_for_monthly}")
        
        if not year:
            year = [get_current_year()]
        daily_filtered_data = pd.DataFrame()
        weekly_filtered_data = pd.DataFrame()
        monthly_filtered_data = pd.DataFrame()
    
        if isinstance(month_for_monthly, str):
            month_for_monthly = [month_for_monthly]
        if isinstance(quarter, str):
            quarter = [quarter]
        
        if day and week:
            daily_filtered_data = filter_daily_data(day, year, week)
            
        if month or week_for_weekly:
            weekly_filtered_data = filter_weekly_data(year, month, week_for_weekly)
            
        if quarter or month_for_monthly:
            monthly_filtered_data = filter_monthly_data(year, month_for_monthly, quarter)
            
        logging.debug(f"Daily filtered data: {daily_filtered_data.shape[0]} rows")
        logging.debug(f"Weekly filtered data: {weekly_filtered_data.shape[0]} rows")
        logging.debug(f"Monthly filtered data: {monthly_filtered_data.shape[0]} rows")
        
        return {
            "daily": daily_filtered_data.to_dict('records'),
            "weekly": weekly_filtered_data.to_dict('records'),
            "monthly": monthly_filtered_data.to_dict('records')
        }


    @app.callback(
        Output('stored-target-STR', 'data'),
        Output('target-output-STR', 'children'),
        [Input('set-target-btn-STR', 'n_clicks')],
        [State('target-input-STR', 'value')]
    )
    def set_target(n_clicks, target_value):
        if n_clicks and target_value is not None:
            set_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_message = f"Target set at {target_value}% on {set_date}"
            return target_value, target_message
        return 95, "Using default target value of 95%"

    @app.callback(
        Output('daily-target-card', 'children'),
        [
            Input('dashboard2-filters', 'data'),
            Input('stored-target-STR', 'data')
        ]
    )
    def update_daily_target_card(filters, target_value):
        if not filters or 'daily' not in filters:
            return dash.no_update
        df = pd.DataFrame(filters['daily'])
        total_lines = len(df)
        conforming_lines = len(df[df['STR Status'] == 'Conforming'])
        plant_value = (conforming_lines / total_lines) * 100 if total_lines else 0
        target_card = createtarget_card("Daily STR", plant_value, target_value)
        return target_card

    @app.callback(
        Output('weekly-target-card', 'children'),
        [
            Input('dashboard2-filters', 'data'),
            Input('stored-target-STR', 'data')
        ]
    )
    def update_weekly_target_card(filters, target_value):
        if not filters or 'weekly' not in filters:
            return dash.no_update
        df = pd.DataFrame(filters['weekly'])
        total_lines = len(df)
        conforming_lines = len(df[df['STR Status'] == 'Conforming'])
        plant_value = (conforming_lines / total_lines) * 100 if total_lines else 0
        target_card = createtarget_card("WTD", plant_value, target_value)
        return target_card
    
    @app.callback(
    Output('Monthly-target-card', 'children'),
    [
        Input('dashboard2-filters', 'data'),
        Input('stored-target-STR', 'data'),
        Input('filter-Quarter', 'value'),
        Input('available-quarters', 'data')
    ]
)
    def update_monthly_target_card(filters, target_value, selected_quarters, available_quarters):
        if not filters or 'monthly' not in filters:
            return dash.no_update
        
        df = pd.DataFrame(filters['monthly'])
        total_lines = len(df)
        conforming_lines = len(df[df['STR Status'] == 'Conforming'])
        plant_value = (conforming_lines / total_lines) * 100 if total_lines else 0
        
        title = "MTD"
        if selected_quarters and available_quarters:
            if set(selected_quarters) == set(available_quarters):
                title = "YTD"
        
        target_card = createtarget_card(title, plant_value, target_value)
        return target_card

    @app.callback(
    [
        Output({'type': 'dashboard2-dynamic-content', 'index': MATCH}, 'children'),
        Output({'type': 'dashboard2-dynamic-content-modal', 'index': MATCH}, 'children'),
    ],
    [
        Input({'type': 'dashboard2-Graph-switch', 'index': MATCH}, 'value'),
        Input({'type': 'dashboard2-chart-type', 'index': MATCH}, 'value'),
        Input('dashboard2-filters', 'data'),
        Input('filter-month', 'value'),
        Input('filter-week-for-weekly', 'value'),
        Input('filter-month-monthly', 'value'),
        Input('filter-Quarter', 'value')
    ],
    [State({'type': 'dashboard2-dynamic-content', 'index': MATCH}, 'id')]
)
        
    def update_charts(switch_value, chart_type, filters, selected_month, selected_week_for_weekly,selected_month_for_monthly,Quarter, component_id):
        start_time = time.time()
        if not filters:
            logging.debug("No filters provided")
            return dash.no_update, dash.no_update

        filtered_df_STR = pd.DataFrame()
        index = component_id['index']

        if index in [1, 2, 3, 4]:
            if 'daily' in filters:
                filtered_df_STR = pd.DataFrame(filters['daily'])
            group_by_cols = ['Formatted Shipment Date', 'Technology']
            if index == 1:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'CAS']
            elif index == 2:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'MOL']
            elif index == 3:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'ConA']
            config_data = create_conformance_dataframe(filtered_df_STR, group_by_cols)
            config_data_table = create_pivot_table(filtered_df_STR, 'Technology', 'STR Status', 'Formatted Shipment Date')

            config_data_table = config_data_table.reindex(sorted(config_data_table.columns, key=custom_sort_key), axis=1)
            config_data_table = config_data_table[['Technology'] + [col for col in config_data_table.columns if col != 'Technology']]
            config_data = config_data.sort_values(by='Formatted Shipment Date', key=lambda x: x.map(custom_sort_key))

            config = create_config(config_data, config_data_table, 'Formatted Shipment Date', 'Percentage', None, None, 'Status')

        elif index in [5,6,7,8] :
            if 'weekly' in filters:
                filtered_df_STR = pd.DataFrame(filters['weekly'])
            group_by_cols = ['Shipment Fiscal Week', 'Technology']
            if index == 6:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'CAS']
            elif index == 7:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'MOL']
            elif index == 8:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'ConA']
                
            config_data = create_conformance_dataframe(filtered_df_STR, group_by_cols)
            config_data_table = create_pivot_table(filtered_df_STR, 'Technology', 'STR Status', 'Shipment Fiscal Week')
            config = create_config(config_data, config_data_table, 'Shipment Fiscal Week', 'Percentage', None, None, 'Status')
        
        elif index in [9,10,11,12]:
            if 'monthly' in filters:
                filtered_df_STR = pd.DataFrame(filters['monthly'])
            group_by_cols = ['Shipment Fiscal Month', 'Technology']
            if index == 10:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'CAS']
            elif index == 11:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'MOL']
            elif index == 12:
                filtered_df_STR = filtered_df_STR[filtered_df_STR['Technology'] == 'ConA']
                
            config_data = create_conformance_dataframe(filtered_df_STR, group_by_cols)
            config_data_table = create_pivot_table(filtered_df_STR, 'Technology', 'STR Status', 'Shipment Fiscal Month')
            config = create_config(config_data, config_data_table, 'Shipment Fiscal Month', 'Percentage', None, None, 'Status')
    

        else:
            return dash.no_update, dash.no_update
        
        

        if switch_value:
            fig = card.get_figure_STR(chart_type, config, "/STR_Summary")
            end_time = time.time()
            logging.info(f"Chart update took {end_time - start_time:.2f} seconds")
            return dcc.Graph(figure=fig), dcc.Graph(figure=fig)
        else:
            data = config['dataTable']
            table = dcc.Loading(
                children=[dash_table.DataTable(
                    data=data.to_dict('records'),
                    columns=[{'name': str(i), 'id': str(i)} for i in data.columns],
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '11px',
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
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                        {'if': {'row_index': 'even'}, 'backgroundColor': 'white'},
                        {'if': {'filter_query': '{Technology} = "Plant"'}, 'backgroundColor': '#d4edda', 'color': 'black'},
                        {'if': {'filter_query': '{Technology} = "Total Shipment"'}, 'backgroundColor': '#daf7fb', 'color': 'black'}
                    ],
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode='multi',
                    page_action='native',
                    page_current=0,
                    page_size=10,
                )],
                type="default"
            )
            end_time = time.time()
            logging.info(f"Table update took {end_time - start_time:.2f} seconds")
            return table, table
