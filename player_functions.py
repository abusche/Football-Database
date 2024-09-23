from datetime import datetime, timedelta
import random
import re
import functools
import time
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import dateparser
import locale

from base_functions import get_link_matchs, page

from match_functions import get_team, get_event_details

# Résumé

def get_summary(soup):
    
    index = get_team(soup)[0] + "_" + get_team(soup)[1] + "_" + get_event_details(soup)[0] + "_" + get_event_details(soup)[1] + "_" + get_event_details(soup)[2]
    
    var = ["Match_Index", "Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "Buts", "PD", "PénM", "PénT", "Tirs", "TC", "CJ", "CR", "Touches", "Tcl", "Int", "BallContr", "xG", "npxG", "xAG", "AMT", "AMB", "PassR", "PassT", 
           "%PassR", "PrgP", "BallPied", "PrgC", "DriT", "DriR"]
    
    data = []

    code = soup.find_all("div", class_="table_container tabbed current")[0].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [index, name]
        code2 = soup.find_all("div", class_="table_container tabbed current")[0].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed current")[1].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [index, name]
        code2 = soup.find_all("div", class_="table_container tabbed current")[1].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data, columns=var)
    
    return data


# Passes

def get_passes(soup):

    var = ["Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "PassR", "PassT", "%PassR", "PassTotDist", "PassDistBut", "PassCR", "PassCT", "%PassCR", "PassMR", "PassMT", "%PassMR", "PassLR", "PassLT", 
           "%PassLR", "PD", "xAG", "xA", "PC", "Pass1/3", "PPA", "CntSR", "PrgP"]
    
    data = []

    code = soup.find_all("div", class_="table_container tabbed")[0].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[0].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed")[5].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[5].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data, columns=var)
    
    return data


# Type de passe
def get_passes_type(soup):
    
    var = ["Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "PassT", "ActJeu", "CdPA", "CF", "PassProf", "Tr", "Ctr", "PCF", "Co", "CoRentrant", "CoSortant", "CoDroit", "PassR", "PassHJ", 
           "PassBlqAdv"]

    data = []

    code = soup.find_all("div", class_="table_container tabbed")[1].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[1].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed")[6].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[6].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data, columns=var)
    return data


# Action défensive
def get_defensive_action(soup):
    
    var = ["Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "Tcl", "TclR", "TclZDéf", "TclMilTer", "TclZOff", "TclDribT", "TclDribR", "%TclDrib", "TclDribM", "BallContr", "TirBlq", "PassBlq", "Int",
          "Tcl+Int", "Dég", "Err"]
    
    data = []

    code = soup.find_all("div", class_="table_container tabbed")[2].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[2].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed")[7].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[7].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data,columns=var)
    return data


# Possession
def get_Possession(soup):
    
    var = ["Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "Touches", "TouchesSurfRépDéf", "TouchesZDéf", "TouchesMilTer", "TouchesZOff", "TouchesSurfRépAdv", "Touches2", "DriT", "DriR", "%DriR", 
           "Tkld", "%Tkld", "BallPied", "TotDist", "DistBut", "PrgC", "Chev1/3", "CSR", "CtrM", "PerteBall", "PassRecu", "PrgPR"]
    
    data = []

    code = soup.find_all("div", class_="table_container tabbed")[3].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[3].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed")[8].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[8].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data, columns=var)
    data = data.drop("Touches2", axis=1)
    return data


# Statistiques diverses
def get_divers_stats(soup):
    
    var = ["Nom", "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "CJ", "CR", "2CrtJ", "FtC", "FtP", "HJ", "Ctr", "Int", "TclR", "PénM", "PCon", "CSC", "Récup", "DAG", "DAP", "%DAG"]
    
    data = []

    code = soup.find_all("div", class_="table_container tabbed")[4].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[4].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    code = soup.find_all("div", class_="table_container tabbed")[9].find_all('th', class_="left")
    for i in range(len(code)-2):
        name = code[i+1].text
        stat = [name]
        code2 = soup.find_all("div", class_="table_container tabbed")[9].find_all('tr')[i+2].find_all("td")
        for i in range(len(code2)):
            stat.append(code2[i].text)
        data.append(stat)

    data = pd.DataFrame(data, columns=var)
    return data


def keep_uppercase(input_string):
    return ''.join([char for char in input_string if char.isupper()])


def get_stat_goal(soup):
    GK1 = []
    GK2 = []
    var = ["Nom", "Nationalité", "Âge", "Minutes", "TCC", "BE", "Arrêts", "%Arrêts", "PSxG", "DégR", "DégT", "%DégR", "PassTent", "LancT", "%PassLanc", "LongPassMoy", "DégSixMetres", "%DégSixMetres", 
               "LongMoySixMetres", "CtrConc", "CtrStop", "%CtrStop", "ActDéfSurfRép", "DistMoyActDéf"]
    code = soup.find_all("div", class_="table_container")[6].find_all("th", class_="left")
    code2 = soup.find_all("div", class_="table_container")[6].find_all("td")
    for i in range(len(code)):
        GK11 = [soup.find_all("div", class_="table_container")[6].find_all("th", class_="left")[i].text]
        if i == 1:
            for j in range(len(code2)):
                if j > 22:
                    k=22
                    next
                else:
                    GK11.append(code2[j].text)
            GK1.append(GK11)
        if i == 2:
            for j in range(len(code2)):
                if j < 23:
                    next
                else:
                    GK11.append(code2[j].text)
            GK1.append(GK11)

    code = soup.find_all("div", class_="table_container")[13].find_all("th", class_="left")
    code2 = soup.find_all("div", class_="table_container")[13].find_all("td")
    for i in range(len(code)):
        GK22 = [soup.find_all("div", class_="table_container")[13].find_all("th", class_="left")[i].text]
        if i == 1:
            for j in range(len(code2)):
                if j > 22:
                    k=22
                    next
                else:
                    GK22.append(code2[j].text)
            GK2.append(GK22)
        if i == 2:
            for j in range(len(code2)):
                if j < 23:
                    next
                else:
                    GK22.append(code2[j].text)
            GK2.append(GK22)

    GK = []
    for i in range(len(GK1)):
        GK.append(GK1[i])
    for i in range(len(GK2)):
        GK.append(GK2[i])
    GK = pd.DataFrame(GK, columns=var)

    return GK


def get_stats_player(soup):
    
    df = get_summary(soup).merge(get_passes(soup), on=['Nom', "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "PassR", "PassT", "%PassR", "PD", "xAG", "PrgP"], how='left')
    df2 = df.merge(get_passes_type(soup), on=['Nom', "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "PassT", "PassR"], how='left')
    df3 = df2.merge(get_defensive_action(soup), on=['Nom', "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "Tcl", "BallContr", "Int"], how='left')
    df4 = df3.merge(get_Possession(soup), on=['Nom', "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "Touches", "DriT", "DriR", "BallPied", "PrgC"], how='left')
    df5 = df4.merge(get_divers_stats(soup), on=['Nom', "Numéro", "Nationalité", "Poste", "Âge", "Minutes", "CJ", "CR", "Ctr", "Int", "TclR", "PénM"], how='left')
    df6 = df5.merge(get_stat_goal(soup), on=['Nom', "Nationalité", "Âge", "Minutes"], how='left')
    df6["Nationalité"] = df6["Nationalité"].apply(keep_uppercase)
    return df6


def get_player_database(date_start, date_end, leagues, save, add):
    t = time.time()
    links = get_link_matchs(date_start, date_end, leagues, save, add)
    data = pd.DataFrame()
    z=0 # Initialisation d'un compteur
    print("Chargement de la base de données...")
    print(" ")
    for link in links:
        z+=1
        soup = page(link)
        print("Chargement : ", round((z/len(links))*100), "%", end="\r") # Affichage du compteur pour indiquer l'évolution du chargement des données
        info = get_stats_player(soup) # On récupère le vecteur des caractéristiques d'un logement à partir des liens que nous avons récupérés
        data = pd.concat([data, info]) # On ajoute notre observation au vecteur data qui regroupe toutes les observations
    
    print("Extraction terminée en ", round((time.time() - t)/60, 2), "minutes")
    return data