from dash import html
import dash_bootstrap_components as dbc

sidebar = html.Div(
    [
        html.Img(
            src="/assets/image-removebg-preview 1.png",
            style={"height": "60px", "width": "auto", "padding": "10px"}
        ),
        
        html.Div(
            [
                dbc.NavLink("Overall dahboard", href="/Overall_dashboard", id="navitem-Overall_dashboard", className="nav-link"),
                dbc.NavLink("Targets Config", href="/targets_config", id="navitem-targets_config", className="nav-link"),
                dbc.NavLink("Mapping Files", href="/Mapping_files_config", id="navitem-Mapping_files_config", className="nav-link"),
                dbc.NavLink("User Management", href="/user-management", id="navitem-user-management", className="nav-link"),
                html.Div(
                    
                    [   
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem("Inventory", href="/Inventory", id="navitem-Inventory"),
                                dbc.DropdownMenuItem("STR Summary", href="/STR_Summary", id="navitem-STR_Summary"),
                                dbc.DropdownMenuItem("STR", href="/STR", id="navitem-STR"),
                            ],
                            label="All Dashboards",
                            nav=True,
                            in_navbar=False,
                            className="w-100",
                        ),
                    ],
                    id="dropdown-container",
                    style={"width": "100%"}
                ),
            ],
            id="sidebar-content",
            style={"display": "block"},
        ),
        html.Div(
            "Sidebar", id="sidebar-handle", className="sidebar-handle"
        ),
    ],
    id="sidebar",
    className="sidebar"
)
