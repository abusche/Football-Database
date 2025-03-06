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

def get_team(soup):
    code = soup.find("div", class_="scorebox").find_all("a")
    team = [c.text for c in code if "equipes" in c.get("href")]
    return team

def get_event_details(soup):

    code = soup.find_all("div", class_="scorebox_meta")[0]
    
    league = code.find_all("a")[1].text # league
    journey = re.search(r'Journée \d+', code.text).group(0) # Journée
    date = dateparser.parse(code.find("a").text, languages=['fr']).strftime("%d/%m/%Y")
    hours = re.sub(r'\s*\([^)]*\)', '', soup.find_all("span", class_="venuetime")[0].text)
    
    spectators = "NaN"
    for i in range(len(code.find_all("span"))):
        if "Arbitre" in code.find_all("span")[i].text:
            referee = code.find_all("span")[i].text.replace("\xa0", " ").replace(" (Arbitre)", "")
    for i in range(len(code.find_all("small"))):
        if "Tribune" in code.find_all("small")[i].text:
            stadium = code.find_all("small")[i+1].text.split(',')[0]
        if "Affluence" in code.find_all("small")[i].text:
            spectators = int(code.find_all("small")[i+1].text.replace(",", ""))
    
    date_obj = datetime.strptime(dateparser.parse(code.find("a").text, languages=['fr']).strftime("%d/%m/%Y"), "%d/%m/%Y")
    
    if date_obj.month >= 7:
        season = f"{date_obj.year}/{date_obj.year+1}"
    else:
        season = f"{date_obj.year-1}/{date_obj.year}"
        
    return [league, journey, season, date, hours, referee, spectators, stadium]

def get_score(soup):
    code = soup.find_all("div", class_="score")
    score = [int(c.text) for c in code]
    return score

def get_xg(soup):
    code = soup.find_all("div", class_="score_xg")
    xg = [float(c.text) for c in code]
    return xg

def get_possession(soup):
    code = soup.find_all('div', id='team_stats')[0].find_all("strong")
    possession = [float(code[0].text.strip('%'))/100, float(code[1].text.strip('%'))/100]
    return possession

def get_stats(soup):
    stats = []
    code = soup.find_all('div', id='team_stats')[0].find_all("div")
    for i in range(len(code)):
        c2 = code[i].text.replace("\n","").replace("\xa0—\xa0", " ")
        if i % 2 == 0:
            if "of" in c2:
                dom = int(re.findall(r'(\d+)\s+of\s+(\d+)', c2)[0][0])
                ext = int(re.findall(r'(\d+)\s+of\s+(\d+)', c2)[0][1])
                if ext != 0:
                    perc = round(dom/ext, 2)
                else:
                    perc = float(0)
                stats.append([dom, ext, perc])
    stats = [item for sublist in stats for item in sublist]
    return stats

def info_match(soup):
    
    info_match = []
    code = soup.find_all('div', id='team_stats_extra')[0].find_all("div")
    
    for i in range(len(code)):
        if "Fautes" in code[i].text and "Corners" in code[i].text and "Centres" in code[i].text and "Touches" in code[i].text:
            for k in list(re.findall(r'(\d+)\s*Fautes\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Corners\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Centres\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Touches\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
                
        if "Tacles" in code[i].text and "Interceptions" in code[i].text and "Duels aériens gagnés" in code[i].text and "Dégagements" in code[i].text:
            for k in list(re.findall(r'(\d+)\s*Tacles\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Interceptions\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Duels aériens gagnés\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Dégagements\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
                
        if "Hors-jeux" in code[i].text and "Dégagements au six mètres" in code[i].text and "Rentrée de touche" in code[i].text and "Longs ballons" in code[i].text:
            for k in list(re.findall(r'(\d+)\s*Hors-jeux\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Dégagements au six mètres\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Rentrée de touche\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Longs ballons\s*(\d+)', code[i].text)[0]):
                info_match.append(int(k))
                
    return info_match

def get_coach(soup):
    code = soup.find_all("div", class_="datapoint")
    coach = [
        c.text.replace("\xa0", " ").split(": ")[1]
        for c in code
        if "Entraineur" in c.text.replace("\xa0", " ").split(": ")[0]
    ]
    return coach

def get_compo(soup):
    code = soup.find_all("div", class_="lineup")
    compo = [
        c.find('tr').text.split(" (")[1].replace(")", "")
        for c in code
    ]
    return compo

def get_effectif(soup):
    equipe1 = []
    equipe2 = []
    code = soup.find_all("div", class_="lineup")
    for i in range(len(code[0].find_all("a"))):
        equipe1.append(code[0].find_all("a")[i].text)

    for i in range(len(code[1].find_all("a"))):
        equipe2.append(code[1].find_all("a")[i].text) 
            
    return [equipe1,equipe2]

def get_cards(soup):
    code = soup.find_all("div", class_="cards")

    dom = code[0].find_all("span")
    yellow_card_dom = 0
    red_card_dom = 0
    for d in dom:
        if "yellow" in re.findall(r'["\'](.*?)["\']', str(d))[0]:
            yellow_card_dom += 1
        if "red" in re.findall(r'["\'](.*?)["\']', str(d))[0]:
            red_card_dom += 1

    ext = code[1].find_all("span")
    yellow_card_ext = 0
    red_card_ext = 0
    for e in ext:
        if "yellow" in re.findall(r'["\'](.*?)["\']', str(e))[0]:
            yellow_card_ext += 1
        if "red" in re.findall(r'["\'](.*?)["\']', str(e))[0]:
            red_card_ext += 1
        
    cards = [yellow_card_dom, yellow_card_ext, red_card_dom, red_card_ext]
    return cards

def get_match(soup):
    match = get_event_details(soup)[0:3] + get_team(soup) + get_score(soup) + get_xg(soup) + get_possession(soup) + get_stats(soup)
    match = match + info_match(soup)+ get_cards(soup) + get_event_details(soup)[3:8] + get_coach(soup) + get_compo(soup) + get_effectif(soup)
    return match

def get_match_database(date_start, date_end, leagues, save, add):
    t = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    var = ["Championnat", "Journée", "Saison", "Equipe1", "Equipe2", "Score1", "Score2", "xG1", "xG2", "Possession1", "Possession2", "Passes1", "Passes réussies1", "% Passes réussies1", "Passes2", "Passes réussies2", "% Passes réussies2", "Tirs1", "Tirs cadrés1", "% Tirs cadrés1", "Tirs2", "Tirs cadrés2", "% Tirs cadrés2", "Arrêts possibles1", "Arrêts1", "% Arrêts1", "Arrêts possibles2", "Arrêts2", "% Arrêts2", "Fautes1" , "Fautes2", "Corners1", "Corners2", "Centres1", "Centres2", "Touches1", "Touches2", "Tacles1", "Tacles2", "Interceptions1", "Interceptions2", "Duels aériens gagnés1", "Duels aériens gagnés2", "Dégagements1", "Dégagements2", "Hors-jeux1","Hors-jeux2", "Dégagements au six mètres1", "Dégagements au six mètres2", "Rentrée de touche1", "Rentrée de touche2", "Longs ballons1", "Longs ballons2", "Cartons jaunes1", "Cartons jaunes2", "Cartons rouges1", "Cartons rouges2", "Date", "Heure", "Arbitre", "Affluence", "Stade", "Entraineur1", "Entraineur2", "Dispositif1", "Dispositif2", "Composition1", "Composition2"]
    data = []
    z=0 # Initialisation d'un compteur
    print("Chargement de la base de données...")
    print(" ")
    for link in links:
        z+=1
        soup = page(link)
        print("Chargement : ", round((z/len(links))*100), "%", end="\r") # Affichage du compteur pour indiquer l'évolution du chargement des données
        info = get_match(soup) # On récupère le vecteur des caractéristiques d'un logement à partir des liens que nous avons récupérés
        data.append(info) # On ajoute notre observation au vecteur data qui regroupe toutes les observations
    data = pd.DataFrame(data, columns=var)
    print("Extraction terminée en ", round((time.time() - t)/60, 2), "minutes")
    return data