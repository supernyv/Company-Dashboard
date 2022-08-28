import pandas as pd
import numpy as np
import os

def get_data():
    file = ['C:\\', 'Users', 'Administrateur', 'Desktop', 'Enregistrement', 'Backup Data', 'Presence_et_Certificats.xlsx']
    #file = ['Y:\\', 'EAS SMQ_Français', 'Enregistrements', 'Departement Technique', 'Division Formation', 'Processus Formation', 'Presence_et_Certificats.xlsx']
    file = os.path.join(*file)
    df = pd.read_excel(file, sheet_name='Liste_Presence')

    #Change phone column to str, then add 0 back to the front
    df['TELEPHONE'].replace(np.nan, 'None', inplace=True)
    df['TELEPHONE'] = df['TELEPHONE'].apply(lambda data: '0'+str(data).split('.')[0] if data else '')

    #Replace empty Birth Dates with 01-01-1900 but drop those cells during analysis
    epoque = pd.Timestamp('01/01/1900').date()

    df['DATE DE NAISSANCE'].replace(np.nan, epoque, inplace=True)
    #Change format of the dates
    df['DATE DE NAISSANCE'] = pd.to_datetime(df['DATE DE NAISSANCE'], infer_datetime_format=True)
    df['SESSION DU'] = pd.to_datetime(df['SESSION DU'], infer_datetime_format=True)

    df['JOUR'] = df['SESSION DU'].dt.weekday
    dt_to_day = {0:"Lundi", 1:"Mardi", 2:"Mercredi", 3:"Jeudi", 4:"Vendredi", 5:"Samedi", 6:"Dimanche"}
    df['JOUR'] = df['JOUR'].map(lambda day: dt_to_day[day])

    df['MOIS'] = df['SESSION DU'].dt.month
    dt_to_month = {1:'Janvier', 2:'Fevrier', 3:'Mars', 4:'Avril', 5:'Mai', 6:'Juin', 7:'Juillet',
                       8:'Aout', 9:'Septembre', 10:'Octobre', 11:'Novembre', 12:'Decembre'}
    df['MOIS'] = df['MOIS'].map(lambda month: dt_to_month[month])

    df['ANNEE'] = df['SESSION DU'].dt.year

    df['SESSION DU'] = df['SESSION DU'].dt.date
    df['DATE DE NAISSANCE'] = df['DATE DE NAISSANCE'].dt.date

    #Sort the list
    df.sort_values('SESSION DU', inplace=True)

    return df

df = get_data()
