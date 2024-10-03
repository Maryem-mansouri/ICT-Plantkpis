from dash import Dash, html, dcc
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def create_navbar(style=None):
    return dbc.Navbar(
        children=[
            dbc.Container(fluid=True, children=[
                dcc.Location(id='url', refresh=False),  # Add this line to capture the URL path
                dbc.Row(
                    [
                        dbc.Col(html.A(dbc.NavbarBrand(html.Img(src="/assets/image-removebg-preview 1.png", height="30px")), href="/"), width="auto"),
                    ],
                    align="center",
                    className="my-navbar"
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink([html.Img(src="/assets/mage_dashboard-3.png", height="15px", className="m-1"), "Inventory"], href="/Inventory", id="navitem-Inventory")),
                            dbc.NavItem(dbc.NavLink([html.Img(src="/assets/mage_dashboard-3.png", height="15px", className="m-1"), "STR_Summary"], href="/STR_Summary", id="navitem-STR_Summary")),
                            dbc.NavItem(dbc.NavLink([html.Img(src="/assets/mage_dashboard-3.png", height="15px", className="m-1"), "STR"], href="/STR", id="navitem-STR")),





                        ],
                        className="ml-auto", navbar=True, id="navbar"
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    dbc.Input(placeholder="Search...", className="ps-3 input border-0"),
                                    dbc.Button(
                                        html.Img(src="/assets/Vector-1.png", height="20px"),
                                        color="light",
                                        className="border-0",
                                        id="search-button"
                                    )
                                ],
                            ),
                            width="auto",
                        ),
                        dbc.Col(html.Img(src="/assets/Vector.png", height="20px"), width="auto"),
                         dbc.Col(dbc.DropdownMenu(
    children=[
       
        dbc.DropdownMenuItem("Log Out", href="http://localhost:8000/logout"),
 
    ],
    toggle_class_name="p-0 border-0",  # Remove padding and border from the toggle button
    toggle_style={"backgroundColor": "transparent"},  # Make the background transparent
    label=html.Img(src="/assets/Ellipse 2.png", height="30px"),  # Set the image as the trigger
    nav=False,  # Ensure it works correctly inside a non-nav element
    in_navbar=False,  # Make sure it's not in a navbar context
    align_end=True,  # Align the dropdown to the end of the column
), width="auto"),
                    ],
                    align="center",
                    className="ml-auto flex-nowrap mt-3 mt-md-0"
                ),
            ])
        ],
        color="white",
        dark=False,
        className="rounded-pill m-3",
        style=style
    )

