# callbacks.py
from dash import Input, Output
import dash
from app import app, layout
from pages import  STR_Summary, Inventory , STR,Overall_dashboard,targets_config,Mapping_files_config
from dash.dependencies import Input, Output, MATCH, State, ALL
from dash.exceptions import PreventUpdate

from components.ManageUsers import manage_users_layout
# Liste des dashboards
dashboards = [ 'Inventory','STR_Summary','STR','Overall_dashboard','targets_config','Mapping_files_config']

@app.callback(
    [Output('page-content', 'children'),
     Output('navbar-container', 'className')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    # Handle the case where the URL is not recognized or is the root
    if pathname is None or pathname == '/':
        pathname = '/Overall_dashboard'  # Default to Overall_dashboard

    # Determine if the navbar should be hidden
    if pathname == '/Overall_dashboard' :
        navbar_class = 'hidden-navbar'
    else:
        navbar_class = ''  # Show the navbar for other pages

    # Display the corresponding page layout
    page_content = layout.display_page(pathname)
    return page_content, navbar_class


@app.callback(
    Output({'type': 'modal', 'index': MATCH}, 'is_open'),
    Input({'type': 'open-modal', 'index': MATCH}, 'n_clicks'),
    State({'type': 'modal', 'index': MATCH}, 'is_open')
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    [
        Output(f'navitem-{dashboard}', 'className') for dashboard in dashboards
    ],
    [Input('url', 'pathname')]
)
def update_active_nav_item(pathname):
    # Définir la classe de base pour les liens non actifs et une classe pour les liens actifs
    base_class = 'nav-link'
    active_class = 'nav-link active'
    
    # Traiter le cas où pathname est '/'
    if pathname == '/':
        return [active_class if dashboard == 'Overall_dashboard' else base_class for dashboard in dashboards]
    
    # Mettre à jour la classe en fonction du pathname actuel
    return [
        active_class if pathname == f'/{dashboard}' else base_class for dashboard in dashboards
    ]


@app.callback(
    Output("sidebar", "style"),
    [Input("sidebar-handle", "n_clicks")],
    [State("sidebar", "style")],
)
def toggle_sidebar(n_clicks_handle, sidebar_style):
    print(f"n_clicks_handle: {n_clicks_handle}, sidebar_style: {sidebar_style}")  # Debug output
    
    if n_clicks_handle is None:
        raise PreventUpdate

    if sidebar_style is None:
        sidebar_style = {"transform": "translateX(0)"}

    if sidebar_style.get("transform") == "translateX(0)":
        sidebar_style["transform"] = "translateX(-210px)"  # Move sidebar out of view
    else:
        sidebar_style["transform"] = "translateX(0)"  # Move sidebar into view

    print(f"Updated sidebar_style: {sidebar_style}")  # Debug output
    return sidebar_style


# Register callbacks for each dashboard
for dashboard in [STR_Summary, Inventory, STR, Overall_dashboard,manage_users_layout,targets_config,Mapping_files_config]:
    dashboard.register_callbacks(app)