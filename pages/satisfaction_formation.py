from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os
from assets.data_parts import number_to_month, etalons_satisfaction

file = ['C:\\', 'Users', 'Administrateur', 'Desktop', 'Enregistrement', 'Backup Data', 'Satisfaction_formation.xlsx']
#file = ['Y:\\', 'EAS SMQ_Français', 'Enregistrements', 'Departement Qualité', 'Processus Control de la Formation', 'Satisfaction_formation.xlsx']
file = os.path.join(*file)

def normalize_data(raw_column):
    normalized_column = (raw_column - raw_column.min())/( raw_column.max()-  raw_column.min())
    return normalized_column.map(lambda d : round(d*100, 2))

def set_class(value):
    if value == 100:
        return "Trés Elevé"
    elif value > 95:
        return 'Elevé'
    elif value > 80:
        return 'Moyen'
    elif value > 75:
        return 'Bas'
    else:
        return 'Très Bas'

df = pd.read_excel(file, sheet_name="Sondage" )
df.replace({"CONDUITE PREVENTIVE (Véhicule Leger)":"V. Leger"}, inplace=True)

#Changer le type pour la date
df['SESSION DU'] = pd.to_datetime(df['SESSION DU'])

#Pour les etalons
start_date = df['SESSION DU'].min()
end_date = df['SESSION DU'].max()
dates_range = pd.date_range(start = start_date, end=end_date, inclusive='both', freq='30D')
etalons_min_df = [etalons_satisfaction(date_x)[0] for date_x in dates_range]
etalons_max_df = [etalons_satisfaction(date_x)[1] for date_x in dates_range]
df = pd.concat([df, pd.DataFrame(etalons_max_df)])
df = pd.concat([df, pd.DataFrame(etalons_min_df)])

#Les questions du sondage
Q = [attr for attr in df.columns if attr.startswith("Q")]
df["SCORE BRUT"] = df[Q].sum(axis=1)
df["SCORE NORMAL"] = normalize_data(df["SCORE BRUT"])

mois = df['SESSION DU'].dt.month.unique()

layout = dbc.Container([
    html.H1(
        "Resultat des Enquetes Satisfaction de la Formation",
        style={'color':'#29465B', 'fontSize':30, 'textAlign':'center'}),
    html.Hr(),
    dbc.Row([
        #In a row there are 12 columns, so width parameters in columns will decide how many should each take
        dbc.Col([
            html.Label("Choix de Cible"),
            dcc.Dropdown(
                [{'label':'Formateur', 'value':'FORMATEUR'},
                 {'label':'Société', 'value':'SOCIETE'},
                 {'label':'Formation', 'value':'FORMATION'},
                 {'label':'Qualification', 'value':'POSTE'}],
                'FORMATEUR',
                id='choix_cible')
            ], width = 7),
        dbc.Col([
            html.Label("Satisfaction Par Question"),
            dcc.Dropdown(id='options_cible')
            ])
        ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="performance_pour_cible")
            ], width = 7),
        dbc.Col([
            dcc.Graph(id="performance_pour_option")
            ])
        ]),
    dcc.RangeSlider(mois.min(), mois.max(), step=None,
                marks= number_to_month,
                value= [mois.min(), mois.max()],
                id = 'months_slider',
                allowCross=False
           ),
    html.Div([
        dcc.Graph(id="heatmap_comparaison")
        ])
    ])

@callback(
    Output('performance_pour_cible', 'figure'),
    [Input('choix_cible', 'value'),
    Input('months_slider', 'value')]
    )
def scores_graph(cible, mois):
    performance = "SCORE NORMAL"
    moyenne = "MOYENNE NORMALE"
    dfs = df[df["SESSION DU"].dt.month.isin(range(mois[0], mois[-1]+1))]
    dfsample = dfs[[cible, performance]]
    dfcible  = dfsample.groupby(cible)[performance].agg(['mean']).reset_index()
    dfcible[moyenne] = normalize_data(dfcible["mean"])
    dfcible.sort_values(moyenne, inplace=True)
    dfcible["Note"] = dfcible[moyenne].map(set_class)

    #Abandonner les etalons
    dfcible = dfcible[(dfcible[cible]!="ETALON MIN")&(dfcible[cible]!="ETALON MAX")]
    
    x_title = 'Satisfaction Normalisée'
    fig_title = "Mésure de Satisfaction"
    
    if cible == 'FORMATEUR':
        x_title = 'Performance Normalisée'
        fig_title = "Mésure de Performance des Formateurs"
        
    fig = px.bar(dfcible, x=moyenne, y=cible, color = "Note",
        labels={moyenne:x_title, cible:cible.title()},
        title = fig_title)
    fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
    #fig.update_xaxes(showline=True, linecolor='black', showgrid=True, gridwidth=1, gridcolor='black', mirror=True)
    #fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    return fig

@callback(
    Output('options_cible', 'options'),
    Output('options_cible', 'value'),
    Input('choix_cible', 'value'),
    )
def options_pour_cibles(cible):
    options = [c for c in df[cible].unique() if c[:6]!= "ETALON"]
    toutes_options = [{'label':'Tout', 'value':'TOUT'}]+[{'label':i, 'value':i} for i in sorted(options)]
    return toutes_options, toutes_options[0]['value']
    
@callback(
    Output('performance_pour_option', 'figure'),
    Input('choix_cible', 'value'),
    Input('options_cible', 'value'),
    Input('months_slider', 'value')
    )
def questions_graph(cible, valeur, mois):
    dfs = df[df["SESSION DU"].dt.month.isin(range(mois[0], mois[-1]+1))]
    dfcut = dfs[[cible] + Q]
    if valeur != 'TOUT':
        #Par exemple cible=SOCIETE et valeur = RENCO
        dfcut = dfcut.loc[dfcut[cible]==valeur, Q]
        dfcut = dfcut[Q].mean()
        #Transposer
        dfcut = dfcut.T.reset_index()
    else:
        dfcut = dfcut[Q].mean().reset_index()
    dfcut.rename(columns={dfcut.columns[0]:'QUESTION', dfcut.columns[1]:'SCORE'}, inplace=True)
    
    fig = px.bar(dfcut, x='QUESTION', y='SCORE',
        labels={'QUESTION':"Questions du Sondage", 'SCORE':"Score moyen pour la selection"},
        title = "Score pour chaque question")
    fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
    #fig.update_xaxes(showline=True, linecolor='black', showgrid=True, gridwidth=1, gridcolor='black', mirror=True)
    #fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    return fig

@callback(
    Output('heatmap_comparaison', 'figure'),
    Input('choix_cible', 'value'),
    Input('months_slider', 'value')
    )
def heat_map(cible, mois):
    dfs = df[df["SESSION DU"].dt.month.isin(range(mois[0], mois[-1]+1))]
    dfselect = dfs[[cible]+Q]
    dfselect = dfselect.groupby(cible)[Q].mean()
    #Standardiser pour permettre une comparaison
    dfselect[Q] = dfselect[Q].apply(lambda col:normalize_data(col))

    #Drop the name of index column
    dfselect.rename_axis(index=None, inplace=True)

    #Abandonner les etalons. Ici ils sont des index puisque les groupes sont par
    dfselect.drop(labels = ["ETALON MIN", "ETALON MAX"], axis=0, inplace=True)
    
    fig = px.imshow(dfselect, text_auto=True,
                    title = "Heatmap des Scores Comparés")
    return fig