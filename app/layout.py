# layout.py
import dash_html_components as html
import dash_core_components as dcc
from components import navbar, sidebar
from pages import STR_Summary, Inventory, STR, Overall_dashboard, targets_config,Mapping_files_config
from components.ManageUsers.manage_users_layout import manage_users_layout
from components.ManageUsers.currentUser import get_logged_in_user_info

def create_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(
            id='navbar-container',
            children=navbar.create_navbar()
        ),
        html.Div(
            id='page-content',
            style={
                "margin-left": "0",  # No margin left to avoid pushing the content
                "position": "relative",
                "z-index": 1,  # Ensure content appears below the sidebar
            },
        ),
        sidebar.sidebar,
    ])

def display_page(pathname):
    user_id, email, department, role = get_logged_in_user_info()
    if pathname == '/Inventory':
        return Inventory.layout()
    elif pathname == '/STR_Summary':
        return STR_Summary.layout()
    elif pathname == '/STR':
        return STR.layout()
    elif pathname == '/Overall_dashboard':
        return Overall_dashboard.layout()
    elif pathname == '/targets_config':
        return targets_config.layout()
    elif pathname == '/Mapping_files_config':
        return Mapping_files_config.layout()

    elif pathname == '/ManageUsers':
        if role == 'Admin':  # Only allow access if the user is an Admin
            return manage_users_layout()
        else:
            return html.Div([
                html.H1("Access Denied"),
                html.P("You do not have permission to access this page.")
            ])
    else:
        # Ensure that the default case correctly renders the correct page
        return Overall_dashboard.layout()
