from datetime import datetime
from tqdm import tqdm
import re
import time
import pandas as pd
import dateparser
from base_functions import get_link_matchs, page


##############
# I. Events  #
##############


def get_teams_name(soup):
    code = soup.find("div", class_="scorebox").find_all("a")
    teams_name = [c.text for c in code if "equipes" in c.get("href")]
    return teams_name


def get_event_details(soup):

    code = soup.find("div", class_="scorebox_meta")

    urls = code.find_all("a")
    league = urls[1].text  # League
    raw_date_text = urls[0].text
    date_obj = dateparser.parse(raw_date_text, languages=['fr'])
    date_str = date_obj.strftime("%d/%m/%Y")  # Date

    # Season
    if date_obj.month >= 7:
        season = f"{date_obj.year}/{date_obj.year + 1}"
    else:
        season = f"{date_obj.year - 1}/{date_obj.year}"

    # Journey
    journey_match = re.search(r'Journée \d+', code.text)
    journey = journey_match.group(0) if journey_match else "NaN"

    # Hours
    hours_raw = soup.find("span", class_="venuetime").text
    hours = re.sub(r'\s*\([^)]*\)', '', hours_raw)

    # Referee
    referee = "NaN"
    for span in code.find_all("span"):
        if "Arbitre" in span.text:
            referee = span.text.replace("\xa0", " ").replace(" (Arbitre)", "")
            break

    # Stadium
    stadium = "NaN"
    small_tags = code.find_all("small")
    for i, small in enumerate(small_tags):
        if "Tribune" in small.text and i + 1 < len(small_tags):
            stadium = small_tags[i + 1].text.split(',')[0]
            break

    return [league, journey, season, date_str, hours, referee, stadium]


def get_event(soup):
    event = get_event_details(soup) + get_teams_name(soup)
    return event


##############
# II. Stats  #
##############


def get_score(soup):
    code = soup.find_all("div", class_="score")
    try:
        score_home = int(code[0].text)
        score_away = int(code[1].text)
    except (IndexError, ValueError):
        score_home, score_away = "NaN", "NaN" 
    return pd.DataFrame([{"score_home": score_home, "score_away": score_away}])


def get_xg(soup):
    code = soup.find_all("div", class_="score_xg")
    try:
        xg_home = float(code[0].text)
        xg_away = float(code[1].text)
    except (IndexError, ValueError):
        xg_home, xg_away = "NaN", "NaN" 
    return pd.DataFrame([{"xg_home": xg_home, "xg_away": xg_away}])


def get_stat_perc(soup):

    data = pd.DataFrame(columns=['Possession_home', 'Possession_away', 'S_Pourcentage de passes réussies_home', 'SR_Pourcentage de passes réussies_home', 'Pourcentage de passes réussies_home', 
                                 'S_Pourcentage de passes réussies_away', 'SR_Pourcentage de passes réussies_away', 'Pourcentage de passes réussies_away', 
                                 'S_Tirs cadrés_home', 'SR_Tirs cadrés_home', 'Tirs cadrés_home', 'S_Tirs cadrés_away', 'SR_Tirs cadrés_away', 'Tirs cadrés_away', 
                                 'S_Arrêts_home', 'SR_Arrêts_home', 'Arrêts_home', 'S_Arrêts_away', 'SR_Arrêts_away', 'Arrêts_away'])

    code = soup.find('div', id='team_stats')

    col_name = []
    for c in code.find_all("th"):
        if c.get("colspan") == "2":
            col_name.append(f"{c.text}_home")
            col_name.append(f"{c.text}_away")

    for col in data.columns:
        for i in range(len(col_name)):
            if col == col_name[i]:
                stats = code.find_all("td")[i].text.replace("\n", "")

                if "of" in stats:
                    for stat in stats.split("\xa0—\xa0"):
                          if "of" in stat:
                              stat1 = stat.split(" of ")[0]
                              stat2 = stat.split(" of ")[1]
                          else:
                              perc = stat
                    data[f"S_{col}"] = [int(stat1)]
                    data[f"SR_{col}"] = [int(stat2)]
                    if perc.replace("%", "") != "":
                        data[f"{col}"] = [float(perc.replace("%", ""))/100]
                    else:
                        data[f"{col}"] = [float(0)]
                else:
                    if code.find_all("td")[i].text.replace("\n", "").replace("%", "") != "":
                        data[f"{col}"] = [float(code.find_all("td")[i].text.replace("\n", "").replace("%", ""))/100]
                    else:
                        data[f"{col}"] = [float(0)]

    return data


def get_details_stats(soup):
    stats = pd.DataFrame(columns=['Fautes_home', 'Fautes_away', 'Corners_home', 'Corners_away', 'Centres_home', 'Centres_away', 'Touches_home', 'Touches_away', 'Tacles_home', 'Tacles_away', 'Interceptions_home', 'Interceptions_away', 'Duels aériens gagnés_home',
                                     'Duels aériens gagnés_away', 'Dégagements_home', 'Dégagements_away', 'Hors-jeux_home', 'Hors-jeux_away', 'Dégagements au six mètres_home', 'Dégagements au six mètres_away', 'Rentrée de touche_home', 'Rentrée de touche_away', 
                                     'Longs ballons_home', 'Longs ballons_away'])

    code = soup.find_all('div', id='team_stats_extra')[0].find_all("div")

    stats_patterns = {
        "Fautes": r'(\d+)\s*Fautes\s*(\d+)',
        "Corners": r'(\d+)\s*Corners\s*(\d+)',
        "Centres": r'(\d+)\s*Centres\s*(\d+)',
        "Touches": r'(\d+)\s*Touches\s*(\d+)',
        "Tacles": r'(\d+)\s*Tacles\s*(\d+)',
        "Interceptions": r'(\d+)\s*Interceptions\s*(\d+)',
        "Duels aériens gagnés": r'(\d+)\s*Duels aériens gagnés\s*(\d+)',
        "Dégagements": r'(\d+)\s*Dégagements\s*(\d+)',
        "Hors-jeux": r'(\d+)\s*Hors-jeux\s*(\d+)',
        "Dégagements au six mètres": r'(\d+)\s*Dégagements au six mètres\s*(\d+)',
        "Rentrée de touche": r'(\d+)\s*Rentrée de touche\s*(\d+)',
        "Longs ballons": r'(\d+)\s*Longs ballons\s*(\d+)'
    }

    for div in code:
            text = div.text
            for stat_name, pattern in stats_patterns.items():
                match = re.findall(pattern, text)
                if match:
                    home, away = map(int, match[0])
                    if f'{stat_name}_home' in stats.columns:
                        stats[f'{stat_name}_home'] = [int(home)]
                    if f'{stat_name}_away' in stats.columns:
                        stats[f'{stat_name}_away'] = [int(away)]

    return stats


def get_cards(soup):

    cards = pd.DataFrame(columns=["yellow_card_dom", "yellow_card_ext", "red_card_dom", "red_card_ext"])

    code = soup.find_all("div", class_="cards")

    dom = code[0].find_all("span")
    yellow_card_dom, red_card_dom = 0,0
    for d in dom:
        if "yellow" in re.findall(r'["\'](.*?)["\']', str(d))[0]:
            yellow_card_dom += 1
        if "red" in re.findall(r'["\'](.*?)["\']', str(d))[0]:
            red_card_dom += 1
    cards["yellow_card_dom"] = [yellow_card_dom]
    cards["red_card_dom"] = [red_card_dom]

    ext = code[1].find_all("span")
    yellow_card_ext, red_card_ext = 0,0
    for e in ext:
        if "yellow" in re.findall(r'["\'](.*?)["\']', str(e))[0]:
            yellow_card_ext += 1
        if "red" in re.findall(r'["\'](.*?)["\']', str(e))[0]:
            red_card_ext += 1
    cards["yellow_card_ext"] = [int(yellow_card_ext)]
    cards["red_card_ext"] = [int(red_card_ext)]

    return cards


def get_stats(soup):
    stats = pd.concat([get_score(soup), get_xg(soup), get_stat_perc(soup), get_details_stats(soup), get_cards(soup)], axis=1)
    return stats

#################
# III. Tactics  #
#################


def get_coach(soup):

    code = soup.find_all("div", class_="datapoint")

    coach = [
        c.text.replace("\xa0", " ").split(": ")[1]
        for c in code
        if "Entraineur" in c.text.replace("\xa0", " ").split(": ")[0]
    ]

    capitaine = [
        c.text.replace("\xa0", " ").split(": ")[1]
        for c in code
        if "Capitaine" in c.text.replace("\xa0", " ").split(": ")[0]
    ]

    return pd.DataFrame([coach + capitaine], columns=["Entraineur_home", "Entraineur_away", "Capitaine_home", "Capitaine_away"])


def get_compo(soup):

    code = soup.find_all("div", class_="lineup")

    compo = [
        c.find('tr').text.split(" (")[1].replace(")", "")
        for c in code
    ]

    equipe1 = []
    equipe2 = []

    for i in range(len(code[0].find_all("a"))):
        equipe1.append(code[0].find_all("a")[i].text)

    for i in range(len(code[1].find_all("a"))):
        equipe2.append(code[1].find_all("a")[i].text)

    return pd.DataFrame([compo + [equipe1, equipe2]], columns=["Compo_home", "Compo_away", "Teams_home", "Teams_away"])


def get_tactics(soup):
    tactics = pd.concat([get_coach(soup), get_compo(soup)], axis=1)
    return tactics


##############
# IV. Match  #
##############


def get_match(soup):
    event = pd.DataFrame([get_event(soup)], columns=["leagues", "journey", "season", "date", "hours", "referee", "stadium", "team_name_home", "team_name_away"])
    match = pd.concat([event, get_stats(soup), get_tactics(soup)], axis=1)
    return match


def get_match_database(date_start, date_end, leagues, save, add):
    T = time.time()

    links = get_link_matchs(date_start, date_end, leagues)

    data = pd.DataFrame()

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)
        match = pd.concat([get_match(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        data = pd.concat([data, match])
        while time.time() - t <= 4.1:
            time.sleep(0.01)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")
    return data
