from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os
from assets.data_parts import number_to_month

file = ['C:\\', 'Users', 'Administrateur', 'Desktop', 'Enregistrement', 'Backup Data', 'Entree_Sortie_Inventaire_Magasin.xlsx']
#file = ['Y:\\', 'EAS QMS_Français', 'Enregistrements', 'Departement Logistique', 'Processus Gestion de l\'Inventaire et des Mouvements', 'Entree_Sortie_Inventaire_Magasin.xlsx']
file = os.path.join(*file)
edf = pd.read_excel(file, sheet_name='Enregistrements')
idf = pd.read_excel(file, sheet_name='Inventaire')

#Only take the material of priority "A"
idf = idf.loc[idf["PRIORITE"]=="A"]

edf['DATE'] = pd.to_datetime(edf['DATE'])
edf['JOUR'] = edf['DATE'].dt.day
edf['MOIS'] = edf['DATE'].dt.month
mois = edf['MOIS'].unique()


def mat(ident, what=''):
    x_type = idf.loc[idf["IDENTIFIANT"]==ident, "TYPE"].values
    if x_type.size > 0:
        x_type =  x_type[0]
    else:
        x_type = "Type Non Determiné"

    x_name = idf.loc[idf["IDENTIFIANT"]==ident, "NOM DE CATEGORIE"].values
    if x_name.size > 0:
        x_name = x_name[0]
    else:
        x_name = "Nom Non Reconnu"

    if what == "type_mat":
        return x_type
    else:
        return x_name

#Do not use apply here because it will return a data frame instead of a series
edf["TYPE"] = edf["IDENTIFIANT"].map(lambda xid : mat(xid, what='type_mat'))
edf["NOM DE CATEGORIE"] = edf["IDENTIFIANT"].map(lambda xid : mat(xid, what='name_mat'))

#Sort the list
idf.sort_values('NOM DE CATEGORIE', inplace=True)

#_______________________Consommable Tab____________________#
consomable_analysis = dbc.Row([
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Img(src='../assets/stock.png', height=50),
            html.Button("Stock Actuel: "),
            html.B(id="in_stock")]
            ),
        dbc.Col([
            html.Img(src='../assets/purchase.png', height=50),
            html.Button("Totale Achetée: "),
            html.B(id='total_purchased')]
            ),
        dbc.Col([
            html.Img(src='../assets/itemuse.png', height=50),
            html.Button("Totale Utilisée: "),
            html.B(id='total_used')]
            ),
        ],
        style={'display':'flex', 'align-items':'center', 'justify-content':'center'}),
    dcc.Graph(id='suivi_consommation'),
    ])

#_______________________Non Consommable Tab________________#
non_consomable_analysis = dbc.Row([
    html.Hr(),
    dbc.Row([
        "Comming Soon..."],
        style={'display':'flex', 'align-items':'center', 'justify-content':'center'})
    ])

#________________________________________Layout______________________________#
layout = dbc.Container([
    html.H1(
        "Gestion du Materiel",
        style={'color':'#29465B', 'fontSize':30, 'textAlign':'center'}
        ),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Selection de Categorie"),
            dbc.Tabs([
                dbc.Tab(label='Consommable', tab_id='consommable'),
                dbc.Tab(label='Non Consommable', tab_id='non_consommable'),
                ],
                id='category_tabs',
                active_tab = 'consommable',
                )
            ]),
        dbc.Col([
            html.Label("Selection de Materiel"),
            dcc.Dropdown(id='selection_materiel')
            ]),
        dbc.Col([
            html.Label("Selection des Equipes"),
            dcc.Dropdown(
                id='selection_equipes',
                searchable=True)
            ]),
        ]),

    dbc.Row(id='selected_tab_content'),

    dcc.RangeSlider(mois.min(), mois.max(), step=None,
                    marks= number_to_month,
                    value= [mois.min(), mois.max()],
                    id = 'months_slider',
                    allowCross=False
               ),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_chart_sorties'),
            ]),
        ])
    #Uncomment below if you want the container to fill horizontal space
    #fluid=True
    ])

@callback(
    Output('selected_tab_content', 'children'),
    Input('category_tabs', 'active_tab'))
def choose_tab(activated):
    choice = {'consommable':consomable_analysis, 'non_consommable':non_consomable_analysis}
    return choice[activated]

@callback(
    Output('selection_materiel', 'options'),
    Output('selection_materiel', 'value'),
    Input('category_tabs', 'active_tab')
    )
def options_par_categorie(selected_tab):
    cons = {'consommable':'OUI', 'non_consommable':'NON'}
    selection = cons[selected_tab]

    cat_df = idf[idf['CONSOMMABLE']==selection]
    materiel = cat_df['NOM DE CATEGORIE'].unique()
    menu_materiel = [{'label':i, 'value':i} for i in materiel]
    return menu_materiel, menu_materiel[0] ['value']

@callback(
    Output('selection_equipes', 'options'),
    Output('selection_equipes', 'value'),
    Input('selection_materiel', 'value'),
    Input('months_slider', 'value'))
def equipes_drop(nom_materiel, mois):
    #Available Ids for the kind of material selected
    selected_ids = idf[idf["NOM DE CATEGORIE"]==nom_materiel]["IDENTIFIANT"].unique()
    #Find teams for all incoming and outgoing materials whose ids are in selected_ids
    equipes_df = edf[edf["IDENTIFIANT"].isin(selected_ids)]
    equipes_list = sorted(equipes_df["EQUIPE"].dropna().unique())

    tout = [{'label':'Toutes les Equipes', 'value':'TOUT'}]
    selection = [{'label':i, 'value':i} for i in equipes_list]
    equipes = tout+selection
    return equipes, equipes[0]['value']

@callback(
    Output('suivi_consommation', 'figure'),
    Input('selection_materiel', 'value'),
    Input('months_slider', 'value'),
    Input('selection_equipes', 'value')
    )
def graphe_consommation(materiel, mois, selected_equipe):
    cat_df = edf[(edf['NOM DE CATEGORIE']==materiel) & (edf['ACTION']=='SORTIE')]
    if selected_equipe !='TOUT':
        cat_df = cat_df[cat_df['EQUIPE']==selected_equipe]
    cat_df = cat_df.groupby(["TYPE", "DATE"])["QUANTITE"].sum().reset_index(name="QUANTITE")
    cat_df = cat_df[cat_df['DATE'].dt.month.isin(range(mois[0], mois[-1]+1))]

    fig = px.line(cat_df, x='DATE', y='QUANTITE', color='TYPE', markers=True, 
        title=f'Graphe de consommation pour {materiel} par les Equipes selectionnées')
    #Adjust tick marks to display nicely depending on the maximum quantity
    highest = cat_df['QUANTITE'].max()
    step = 1
    if highest > 10:
        step = int(highest/10)+1
    fig.update_yaxes(dtick=1, ticklabelstep=step)
    fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
    return fig

@callback(
    Output('in_stock', 'children'),
    Output('total_purchased', 'children'),
    Output('total_used', 'children'),
    Input('selection_materiel', 'value'))
def kpi_stock(materiel):
    #Available Ids for the kind of material selected
    ids = idf[idf["NOM DE CATEGORIE"]==materiel]["IDENTIFIANT"]
    #Find teams for all incoming and outgoing materials whose ids are in selected_ids
    in_out_df = edf[edf["IDENTIFIANT"].isin(ids)]

    total_in = in_out_df[in_out_df['ACTION']=='ENTREE']['QUANTITE'].sum()
    total_out = in_out_df[in_out_df['ACTION']=='SORTIE']['QUANTITE'].sum()
    total_returned = in_out_df[in_out_df['ACTION']=='RETOUR']['QUANTITE'].sum()
    used = total_out - total_returned

    current = idf[idf["NOM DE CATEGORIE"]==materiel]["QUANTITE"].sum()
    return current, total_in, used

@callback(
    Output('bar_chart_sorties', 'figure'),
    Input('selection_materiel', 'value'),
    Input('months_slider', 'value'))
def bar_utilisateurs(materiel, mois):
    #Available Ids for the kind of material selected
    ids = idf.loc[idf["NOM DE CATEGORIE"]==materiel, "IDENTIFIANT"]
    selected_df = edf[edf['MOIS'].isin(range(mois[0], mois[-1]+1))]

    #Find teams for all incoming and outgoing materials whose ids are in selected_ids
    selected_df = selected_df[selected_df["IDENTIFIANT"].isin(ids)]

    selected_df = selected_df.groupby(["TYPE", "EQUIPE", "MOIS", "ACTION"])["QUANTITE"].sum().reset_index(name="QUANTITE")

    out_df = selected_df[selected_df['ACTION']=='SORTIE']

    fig_out = px.bar(out_df, x='QUANTITE', y='EQUIPE', color = 'TYPE',
                     title = f'Sortie de {materiel} par Equipe, divisée en mois.')
    fig_out.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
    return fig_out