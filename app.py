from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pages import accueil, formation, cnd, inspection_levage, analyses_environnement, gestion_materiel, satisfaction_formation, achats
from components import navigation_bar
import os

sheet = os.path.join("assets", "bootstrap.min_litera.css")

app = Dash(__name__,
    title = "Dash EAS",
           external_stylesheets = [sheet],
           meta_tags = [{"name":"viewport", "content":"width=device-width"}],
           suppress_callback_exceptions = True)

navbar = navigation_bar.Navbar()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
    ])

pages = {
                '/':accueil.layout,
                '/pages/formation':formation.layout,
                '/pages/cnd':cnd.layout,
                '/pages/inspection_levage':inspection_levage.layout,
                '/pages/analyses_environnement':analyses_environnement.layout,
                '/pages/achats':achats.layout,
                '/pages/gestion_materiel':gestion_materiel.layout,
                '/pages/satisfaction_formation':satisfaction_formation.layout}

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
    )
def display_page(pathname):
    if pathname in pages:
        return pages[pathname]
    else:
        return "404 Page Error ..."

if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(host="192.168.88.150", port=8081, debug=True)