from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from assets import donnees_formation
from assets.data_parts import month_to_number

df = donnees_formation.get_data()
#We're using 2022 alone for now
df = df[df['ANNEE']==2022]
mois = df['MOIS'].unique()

layout = dbc.Container([
        html.H1(
                "Formations Professionnelles",
                style={'color':'#29465B', 'fontSize':30, 'textAlign':'center'}),
        html.Hr(),
        dbc.Row([
                dbc.Col([
                        html.Label('Selection de Catégorie'),
                        dcc.Dropdown(
                                [
                                        {'label':'Société', 'value':'SOCIETE'},
                                        {'label':'Formateur', 'value':'FORMATEUR'},
                                        {'label':'Formation', 'value':'FORMATION'},
                                ],
                                "SOCIETE", id='attributes_dropdown', searchable=False,  clearable=False),
                        ]),
                dbc.Col([
                        html.Label('Options pour la Categorie Selectionnées'),
                        dcc.Dropdown(id='selected_attribute_options')
                        ])
                ]),
        dbc.Row([
                dbc.Col([
                        dcc.Graph(id='top_left_graph')
                        ]),
                dbc.Col([
                        dcc.Graph(id='top_right_graph')])
        ]),
        dbc.Row([
                dbc.Col([
                                html.Label("Coche des Mois"),
                                dcc.Checklist(mois, mois, id='months_checklist'),
                        ]),
                ]),
        dbc.Row([
                dbc.Col([
                        dcc.Graph(id='bottom_left_graph')
                        ]),
                dbc.Col([
                        dcc.Graph(id='bottom_middle_graph')
                        ]),
                dbc.Col([
                        dcc.Graph(id='bottom_right_graph')
                        ])
                ]),
        ],
                  style={'textAlign':'center'}
                  )

@callback(
        Output(component_id='top_left_graph', component_property='figure'),
        Input(component_id='months_checklist', component_property='value'),
        Input(component_id='attributes_dropdown', component_property='value'))
def Top_left_graph(selected_month, attribute):
        others_df = df[df.MOIS.isin(selected_month)]
        others_df = others_df[[attribute]].value_counts().to_frame().reset_index().rename(columns={0:'NOMBRE'})
        titre = f"Nombre d'apprenant pour les mois selectionnés"
        attr = attribute.title()
        #If there are more than 20 Items, we only take the first 20 so we don't have too many bars
        if others_df.shape[0] > 20:
                others_df = others_df.iloc[:19]
                titre = f"Top 19 {attr} pour les mois selectionnés"

        fig = px.bar(others_df, x='NOMBRE', y=attribute,
                     labels={'NOMBRE':'Nombre d\'Apprenants', attribute:attr},
                     title = titre)
        fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
        return fig

@callback(
        Output('selected_attribute_options', 'options'),
        Output('selected_attribute_options', 'value'),
        Input('attributes_dropdown', 'value')
        )
def choose_options(chosen_attribute):
        #Update the dropdown for the chosen attribute
        selected_attribute = sorted(df[chosen_attribute].unique())
        attribute_dropdown = [{'label':'Tout', 'value':'TOUT'}] + [{'label':i, 'value':i} for i in selected_attribute]
        #If no month is selected there will be not attribute_dropdown, to prevent the error this will produce:
        if not attribute_dropdown:
                attribute_dorpdown = [{'label':"Tout", 'value':'TOUT'}]
        return attribute_dropdown, attribute_dropdown[0]['value']

@callback(
        Output('top_right_graph', 'figure'),
        Input('months_checklist', 'value'),
        Input('attributes_dropdown', 'value'),
        Input('selected_attribute_options', 'value')
        )
def per_month(selected_month, attr, option):
        if option != 'TOUT':
                selected_df = df[df[attr]==option]
        else:
                selected_df = df
        selected_df = selected_df[selected_df.MOIS.isin(selected_month)]
        selected_df = selected_df.groupby('MOIS').size().reset_index(name='NOMBRE')
        selected_df["MOIS_N"] = selected_df['MOIS'].map(lambda m : month_to_number[m])
        selected_df.sort_values("MOIS_N", inplace=True)
        fig = px.line(selected_df, x='MOIS', y='NOMBRE', text = 'NOMBRE',
                      title=f"Nombre d'apprenants par mois")
        fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)',
                       'paper_bgcolor':'rgba(0,0,0,0)'})
        fig.update_xaxes(showline=True, linecolor='black')
        fig.update_yaxes(showline=True, linecolor='black')
        fig.update_traces(textposition='top center')
        return fig
        #fig.update_traces(marker_color='#508090')
