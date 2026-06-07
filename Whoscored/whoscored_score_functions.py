import re
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

from whoscored_links_functions import update_match_link


def get_event(soup):
    code = soup.find_all("a", class_="team-link")
    team_dom = code[0].text
    team_ext = code[1].text

    c = soup.find_all(
        "div",
        class_="info-block cleared"
    )
    c = c[2].text.replace("Coup d'envoi:", "").split(", ")
    date_str = c[1]
    date_obj = datetime.strptime(date_str, '%d-%b-%y')
    formatted_date = date_obj.strftime('%d/%m/%Y')
    date = formatted_date
    heure = c[0].split("Date")[0]

    try:
        stade = soup.find_all("span", class_="value")[0].text
        affluence = soup.find_all("span", class_="value")[1]
        affluence = int(affluence.text.replace(",", ""))

    except Exception as e:
        print(f"❌ Erreur get_event : {e}")
        stade = "NaN"
        affluence = "NaN"
        soup.find_all("a", class_="team-link")
        team_dom = code[0].text
        team_ext = code[2].text

    return date, heure, team_dom, team_ext, affluence, stade


def get_rate(soup, link):

    date, heure, team_dom, team_ext, affluence, stade = get_event(soup)

    try:
        team1 = soup.find_all("div", class_="pitch-field")[0]
        bench1 = soup.find_all("div", class_="bench")[0]

        team2 = soup.find_all("div", class_="pitch-field")[1]
        bench2 = soup.find_all("div", class_="bench")[1]

        rates_team1 = [c.text.strip() if c.text.strip() else "NaN" for c in team1.find_all("span", class_="player-stat-value")] + [c.text.strip() if c.text.strip() else "NaN" for c in bench1.find_all("span", class_="player-stat-value")]
        name_team1 = [c.text.strip() if c.text.strip() else "NaN" for c in team1.find_all("span", class_="player-name")] + [c.text.strip() if c.text.strip() else "NaN" for c in bench1.find_all("span", class_="player-name")]
        rates_team2 = [c.text.strip() if c.text.strip() else "NaN" for c in team2.find_all("span", class_="player-stat-value")] + [c.text.strip() if c.text.strip() else "NaN" for c in bench2.find_all("span", class_="player-stat-value")]
        name_team2 = [c.text.strip() if c.text.strip() else "NaN" for c in team2.find_all("span", class_="player-name")] + [c.text.strip() if c.text.strip() else "NaN" for c in bench2.find_all("span", class_="player-name")]

        rates = rates_team1 + rates_team2
        player = name_team1 + name_team2
        rates_team1_label = [team_dom] * len(name_team1)
        rates_team2_label = [team_ext] * len(name_team2)
        label = rates_team1_label + rates_team2_label

        player = player[:len(rates)]
        n = len(player)
        nt1 = len(rates_team1)
        nt2 = len(rates_team2)
        rates_team1_label = [team_dom] * nt1
        rates_team2_label = [team_ext] * nt2
        label = rates_team1_label + rates_team2_label

    except Exception as e:
        n = 0

    if n == 0:
        n = 1
        player = "NaN"
        rates = "NaN"
        label = "NaN"
    # Event
    match = re.search(r'/live/[^/-]+-([^/]+)-(\d{4}-\d{4})', link)
    championnat = [match.group(1).replace('-', ' ').title()] * n
    saison = [match.group(2)] * n

    date = [date] * n
    heure = [heure] * n
    team_dom = [team_dom] * n
    team_ext = [team_ext] * n
    affluence = [affluence] * n
    stade = [stade] * n

    index = championnat[0].lower().replace(" ", "_") + "_"
    index = index + saison[0].lower().replace("-", "_") + "_"
    index = index + date[0].lower().replace("/", "_") + "_"
    index = index + team_dom[0].lower().replace(" ", "_") + "_"
    index = index + team_ext[0].lower().replace(" ", "_")

    df_rate = pd.DataFrame({'index': index, 'league': championnat,
                            'season': saison, 'date': date, 'hour': heure,
                            'stadium': stade, 'home_team': team_dom,
                            'away_team': team_ext, 'affluence': affluence,
                            'player_team': label, 'player': player,
                            'rate': rates, 'link': link})

    return df_rate


def get_rates_database(links, save=False, add=False):

    links = list(links["link"])

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    rates = pd.DataFrame(
        columns=[
            "index", "league", "season", "date", "hour", "stadium",
            "home_team", "away_team", "affluence", "player_team", "player",
            "rate", "link"
        ]
    )

    try:
        for link in tqdm(links):
            try:
                driver.get(link)
                time.sleep(1.2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                rates = pd.concat([rates, get_rate(soup, link)])
            except Exception as e:
                print(f"❌ Erreur : {e}")

    finally:
        driver.quit()

    new_rates = rates
    if save is True:
        if add is True:
            all_rates = pd.read_csv("rates/rates.csv")
            rates = pd.concat([all_rates, rates])
            rates["date"] = pd.to_datetime(rates["date"], format="%d/%m/%Y")
            rates = rates.sort_values("date", ascending=False).reset_index(drop=True)
        rates.to_csv("rates/rates.csv", index=False)

    return new_rates


def update_rates_database(save=False):
    print("Update des liens :")
    new_data_link_matches = update_match_link(save)
    if new_data_link_matches.empty:
        return pd.DataFrame(columns=[
            "index", "league", "season", "date", "hour", "stadium",
            "home_team", "away_team", "affluence", "player_team", "player",
            "rate", "link"
        ])
    else:
        print("Update des notes des joueurs :")
        new_rates = get_rates_database(new_data_link_matches, save=save, add=save)
        return new_rates
