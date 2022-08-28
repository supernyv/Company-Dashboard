from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

file = ['C:\\', 'Users', 'Administrateur', 'Desktop', 'Enregistrement', 'Backup Data', 'Registre des Achats.xlsx']
#file = ['Y:\\', 'EAS SMQ_Français', 'Enregistrements', 'Departement Logistique', 'Processus Achat', 'Registre des Achats.xlsx']
file = os.path.join(*file)

df = pd.read_excel(file, sheet_name='Registres_des_Achats')
df["DATE"] = pd.to_datetime(df["DATE"])
mois = df["DATE"].dt.month.unique()

achat_produits = dbc.Row([
    dbc.Row([
        html.Label("Achat de Produit par Mois, Quantité et Montant"),
        dcc.Graph(id='bubble_quantite_prix_mois')]),
    dbc.Row([
        dbc.Col([
            html.Label("Fournisseurs par Quantité"),
            dcc.Graph(id='bars_fournisseurs_quantite')
            ]),
        dbc.Col([
            html.Label("Fournisseurs par Prix"),
            dcc.Graph(id='bars_fournisseurs_prix')
            ])
        ]),
    ])

achat_services = dbc.Row(["Empty for now"])

#________________________________Layout_______________________________________________#
layout = dbc.Container([
    html.H1(
        "Gestion des Achats",
        style={'color':'#29465B', 'fontSize':30, 'textAlign':'center'}),
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label='Produits', tab_id='tab-produits'),
                dbc.Tab(label='Services', tab_id='tab-services'),
                ],
            id='tabs',
            active_tab='tab-produits')
            ]),
        dbc.Col([
            html.Label('Options'),
            dcc.Dropdown(id='produit_ou_service')
            ]),
        dbc.Col([
            html.Label('Selection des Fournisseurs'),
            dcc.Dropdown(id='choix_fournisseurs')
            ])
        ]),

    dbc.Row(id='tab_content')
    ])

#_______________________________________Callbacks___________________________________#
@callback(
    Output('tab_content', 'children'),
    Input('tabs', 'active_tab'))
def switch_tabs(selected_tab):
    if selected_tab == 'tab-produits':
        return achat_produits
    elif selected_tab == 'tab-services':
        return achat_services

@callback(
    Output('produit_ou_service', 'options'),
    Output('produit_ou_service', 'value'),
    Input('tabs', 'active_tab')
    )
def nom_produit_service(selected_tab):
    if selected_tab == 'tab-produits':
        dfs = df.loc[df['TYPE']=='Produit']
    else:
        dfs = df.loc[df['TYPE']=='Service']
    designation = sorted(dfs['DESIGNATION'].unique())
    content = [{'label':'Tout', 'value':'TOUT'}]+[{'label':i, 'value':i} for i in designation]
    return content, content[0]['value']

@callback(
    Output('choix_fournisseurs', 'options'),
    Output('choix_fournisseurs', 'value'),
    Input('produit_ou_service', 'value')
    )
def choix_fournisseur(selected_designation):
    dfcurrent = df.loc[df['DESIGNATION']==selected_designation]
    fournisseurs = sorted(dfcurrent['FOURNISSEUR'].unique())
    options_fournisseurs = [{'label':'Tout', 'value':'TOUT'}]+[{'label':i, 'value':i} for i in fournisseurs]
    if len(options_fournisseurs)>2:
        return options_fournisseurs, options_fournisseurs[0]['value']
    else:
        return options_fournisseurs, options_fournisseurs[-1]['value']

#_________Pour les produits_____________#
@callback(
    Output('bubble_quantite_prix_mois', 'figure'),
    Input('produit_ou_service', 'value'),
    Input('choix_fournisseurs', 'value')
    )
def graph_bubble(selected_designation, selected_fournisseur):
    dfb = df.loc[:]
    if selected_designation != 'TOUT':
        dfb = dfb.loc[dfb['DESIGNATION']==selected_designation]
    if selected_fournisseur != 'TOUT':
        dfb = dfb.loc[dfb['FOURNISSEUR']==selected_fournisseur]

    dfb = dfb.groupby(dfb['DATE'].dt.month).agg({'QUANTITE': 'sum', 'PRIX TTC':'sum'}).reset_index()
    dfb.rename(columns={'DATE':'Mois', 'QUANTITE':'Quantité', 'PRIX TTC':'Montant'}, inplace=True)

    fig = px.scatter(dfb, x=dfb['Mois'], y=dfb['Quantité'], size = dfb['Montant'], log_x=True)
    highest = dfb['Quantité'].max()
    step = 1
    if highest > 10:
        step = int(highest/10)+1
    fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
    fig.update_xaxes(dtick=1, showline=True, linecolor='black')
    fig.update_yaxes(dtick=1, ticklabelstep=step, showline=True, linecolor='black')
    return fig