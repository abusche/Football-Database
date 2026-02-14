import re
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime
import time


def get_event(soup):
    code = soup.find_all("a", class_="team-link")
    team_dom = code[0].text
    team_ext = code[1].text

    c = soup.find_all("div", class_="info-block cleared")[2].text.replace("Coup d'envoi:", "").split(", ")
    date_str = c[1]
    date_obj = datetime.strptime(date_str, '%d-%b-%y')
    formatted_date = date_obj.strftime('%d/%m/%Y')
    date = formatted_date
    heure = c[0].split("Date")[0]
    stade = soup.find_all("span", class_="value")[0].text
    # arbitre = soup.find_all("span", class_="value")[2].text.split(". ")[1]
    affluence = int(soup.find_all("span", class_="value")[1].text.replace(",", ""))

    return date, heure, team_dom, team_ext, affluence, stade


def get_rate(soup, link):

    # Extraction des notes
    rate = [c.text.strip() if c.text.strip() else "NaN" for c in soup.find_all("span", class_="player-stat-value")]

    # Extraction des noms des joueurs
    player = [c.text.strip() for c in soup.find_all("span", class_="player-name")][:len(rate)]
    n = len(player)

    # Event
    match = re.search(r'/live/[^/-]+-([^/]+)-(\d{4}-\d{4})', link)
    championnat = [match.group(1).replace('-', ' ').title()] * n
    saison = [match.group(2)] * n

    date, heure, team_dom, team_ext, affluence, stade = get_event(soup)

    date = [date] * n
    heure = [heure] * n
    team_dom = [team_dom] * n
    team_ext = [team_ext] * n
    affluence = [affluence] * n
    stade = [stade] * n

    df_rate = pd.DataFrame({'championnat': championnat, 'saison': saison,
                            'date': date, 'heure': heure, 'stade': stade,
                            'Equipe1': team_dom, 'Equipe2': team_ext,
                            'affluence': affluence, 'joueur': player,
                            'rate': rate})

    return df_rate


def get_rates_database(links):
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    rates = pd.DataFrame(columns=["championnat", "saison", "date", "heure", "stade", "Equipe1", "Equipe2", "affluence", "joueur", "rate"])

    try:
        for link in tqdm(links):
            try:
                driver.get(link)
                time.sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                rates = pd.concat([rates, get_rate(soup, link)])
            except Exception as e:
                print(f"❌ Erreur : {e}")

    finally:
        driver.quit()

    return rates
