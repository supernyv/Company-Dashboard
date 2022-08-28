number_to_month = {1:"Janvier", 2:"Fevrier", 3:"Mars", 4:"Avril", 5:"Mai", 6:"Juin", 7:"Juillet", 8:"Aout", 9:"Septembre", 10:"Octobre", 11:"Novembre", 12:"Decembre"}
month_to_number = {"Janvier" : 1, "Fevrier" : 2, "Mars" : 3, "Avril" : 4, "Mai" : 5, "Juin" : 6, "Juillet" : 7, "Aout" : 8, "Septembre" : 9, "Octobre" : 10, "Novembre" : 11, "Decembre" : 12}

#Satisfaction de la formation
def etalons_satisfaction(date):
    """Hard coded dates posed problems when filtering data by date 
    because etalons were given one month and callbacks filtered them out"""
    x = "ETALON MIN"
    y = "ETALON MAX"
    etalons = [
    {"NOM" : x, "PRENOM":x, "SOCIETE":x, "POSTE":x, "FORMATION":x, "FORMATEUR":x, "SESSION DU":date, "LIEU":x,
     "Q1A":0, "Q1B":0, "Q1C":0, "Q1D":0, "Q1E":0, "Q1F":0, "Q2A":0, "Q2B":0, "Q2C":0, "Q3A":0, "Q3B":0, "Q3C":0, "Q3D":0,
     "POINT FORT":x, "POINT FAIBLE":x},
    {"NOM" : y, "PRENOM":y, "SOCIETE":y, "POSTE":y, "FORMATION":y, "FORMATEUR":y, "SESSION DU":date, "LIEU":y,
     "Q1A":10, "Q1B":10, "Q1C":10, "Q1D":10, "Q1E":10, "Q1F":10, "Q2A":10, "Q2B":10, "Q2C":10, "Q3A":10, "Q3B":10, "Q3C":10, "Q3D":10,
     "POINT FORT":y, "POINT FAIBLE":y}
    ]
    return etalons
