import plotly.express as px
 
def create_config(data, data_table, x_col, y_cols, y1_cols=None, line_col=None, color_col=None):
    config = {'data': data, 'dataTable': data_table, 'columns': {'x': x_col, 'y': y_cols}}
    if line_col:
        config['columns']['line'] = line_col
    if y1_cols:
        config['columns']['y1'] = y1_cols
    if color_col:
        config['columns']['color'] = color_col
    return config
 

def format_value(value):
    if isinstance(value, (int, float)):
        if value >= 1e6:
            return f'{value/1e6:.2f}M$'
        elif value >= 1e3:
            return f'{value/1e3:.2f}K$'
        else:
            return f'{value:.2f}$'
    return value  # Return the value as is if it's already a string

def format_value_STR(value):
    if isinstance(value, (int, float)):
       return f'{value:.2f}%'
    return value 
