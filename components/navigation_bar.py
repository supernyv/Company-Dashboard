from dash import html
import dash_bootstrap_components as dbc

def Navbar():

    dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem("Accueill", href='/'),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem("Formations Professionnelles", href='/pages/formation'),
            dbc.DropdownMenuItem("Controls Non Destructifs", href='/pages/cnd'),
            dbc.DropdownMenuItem("Inspection Equipements de Levage", href='/pages/inspection_levage'),
            dbc.DropdownMenuItem("Analyses Environnementales", href='/pages/analyses_environnement'),
            dbc.DropdownMenuItem("Gestion des Achats", href='/pages/achats'),
            dbc.DropdownMenuItem('Gestion du Materiel', href='/pages/gestion_materiel'),
            dbc.DropdownMenuItem('Mesure Satisfaction Formation', href='/pages/satisfaction_formation')
            ],
            color ='secondary',
            nav = False,
            in_navbar = True,
            label = 'Choisir le Processus',
            align_end = True,
        )

    logo = html.Img(src="../assets/Logo ECOGLOBAL.png", height="50px")
    brand = dbc.NavbarBrand (
        "Tableau de Bord",
        href = '/')
    
    bar = dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col(logo),
                dbc.Col(brand),
                ],
                    align = "center"
                    ),
            dropdown
            ],
                      )
        ],
                     color = "dark",
                     dark = True,
                     sticky = "top"
                     )
    return bar
