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

@functools.cache
def page(urlpage): 
    """
    Récupération du HTML d'un site internet via Beautifulsoup
    """
    user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'}
    time.sleep(3) # Retarder le téléchargement pour pas se faire ban
    res = requests.get(urlpage, headers = user_agent)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

def get_link_matchs(date_start, date_end, leagues):
    
    t = time.time()
    print("Extraction des liens...\n")
    
    start_date = datetime.strptime(date_start, '%Y-%m-%d')
    end_date = datetime.strptime(date_end, '%Y-%m-%d')
    links_day = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        url = f"https://fbref.com/fr/matchs/{date_str}"
        links_day.append(url)
        current_date += timedelta(days=1)
        
    links = []
    for i in range(len(links_day)):
        soup = page(links_day[i])
        matchs = soup.find_all("div", class_="table_wrapper tabbed")
        for j in range(len(matchs)):
            if matchs[j].find("a"):
                if matchs[j].find("a").text in leagues:
                    num_league = j
                    for k in range(len(matchs[num_league].find_all("a"))):
                        if "matchs" in matchs[num_league].find_all("a")[k].get("href") and "Rapport de match" in matchs[num_league].find_all("a")[k].text:
                            endlink = matchs[num_league].find_all("a")[k].get("href")
                            links.append('https://fbref.com' + endlink)
        print("Chargement :", round(((i+1)/(len(links_day)+1))*100), "%", end="\r")
        
    print("Chargement : 100 %")                    
    print("Extraction terminée en ", round((time.time() - t)/60, 2), "minutes")
    print(" ")
        
    return links