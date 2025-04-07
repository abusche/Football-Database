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
    code2 = code.find_all("small")
    for i, small in enumerate(code2):
        if "Tribune" in small.text and i + 1 < len(code2):
            stadium = code2[i + 1].text.split(',')[0]
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
    return {"score_home": score_home, "score_away": score_away}


def get_xg(soup):
    code = soup.find_all("div", class_="score_xg")
    try:
        xg_home = float(code[0].text)
        xg_away = float(code[1].text)
    except (IndexError, ValueError):
        xg_home, xg_away = "NaN", "NaN" 
    return {"xg_home": xg_home, "xg_away": xg_away}


def get_possession(soup):
    code = soup.find_all('div', id='team_stats')[0].find_all("strong")
    possession = [float(code[0].text.strip('%'))/100,
                  float(code[1].text.strip('%'))/100]
    return possession


def get_global_stats(soup):
    stats = []
    code = soup.find_all('div', id='team_stats')[0].find_all("div")
    for i in range(len(code)):
        c2 = code[i].text.replace("\n", "").replace("\xa0—\xa0", " ")
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


def get_details_stats(soup):

    info_match = []
    code = soup.find_all('div', id='team_stats_extra')[0].find_all("div")

    for i in range(len(code)):
        c = code[i].text
        m1 = "Fautes"
        m2 = "Corners"
        m3 = "Centres"
        m4 = "Touches"
        if m1 in c and m2 in c and m3 in c and m4 in c:
            for k in list(re.findall(r'(\d+)\s*Fautes\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Corners\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Centres\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Touches\s*(\d+)', c)[0]):
                info_match.append(int(k))
        t1 = "Tacles"
        t2 = "Interceptions"
        t3 = "Duels aériens gagnés"
        t4 = "Dégagements"
        if t1 in c and t2 in c and t3 in c and t4 in c:
            for k in list(re.findall(r'(\d+)\s*Tacles\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Interceptions\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Duels aériens gagnés\s*(\d+)',
                                     c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Dégagements\s*(\d+)', c)[0]):
                info_match.append(int(k))
        h1 = "Hors-jeux"
        h2 = "Dégagements au six mètres"
        h3 = "Rentrée de touche"
        h4 = "Longs ballons"
        if h1 in c and h2 in c and h3 in c and h4 in c:
            for k in list(re.findall(r'(\d+)\s*Hors-jeux\s*(\d+)', c)[0]):
                info_match.append(int(k))
            for k in list(
                re.findall(r'(\d+)\s*Dégagements au six mètres\s*(\d+)',
                           c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Rentrée de touche\s*(\d+)',
                                     c)[0]):
                info_match.append(int(k))
            for k in list(re.findall(r'(\d+)\s*Longs ballons\s*(\d+)',
                                     c)[0]):
                info_match.append(int(k))

    return info_match


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


def get_stats(soup):
    stats = get_score(soup) + get_xg(soup) + get_possession(soup) + get_global_stats(soup) + get_details_stats(soup) + get_cards(soup)
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
    return coach


def get_compo(soup):
    code = soup.find_all("div", class_="lineup")
    compo = [
        c.find('tr').text.split(" (")[1].replace(")", "")
        for c in code
    ]
    return compo


def get_teams(soup):
    equipe1 = []
    equipe2 = []
    code = soup.find_all("div", class_="lineup")
    for i in range(len(code[0].find_all("a"))):
        equipe1.append(code[0].find_all("a")[i].text)

    for i in range(len(code[1].find_all("a"))):
        equipe2.append(code[1].find_all("a")[i].text)

    return [equipe1, equipe2]


def get_tactics(soup):
    tactics = get_coach(soup) + get_compo(soup) + get_teams(soup)
    return tactics


##############
# IV. Match  #
##############


def get_match(soup):
    match = get_event(soup) + get_stats(soup) + get_tactics(soup)
    return match


def get_match_database(date_start, date_end, leagues, save, add):
    T = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    var = ["Championnat", "Journée", "Saison", "Date", "Heure", "Arbitre",
           "Stade", "Equipe1", "Equipe2", "Score1", "Score2", "xG1", "xG2", 
           "Possession1", "Possession2", "Passes1", "Passes réussies1", 
           "% Passes réussies1", "Passes2", "Passes réussies2", 
           "% Passes réussies2", "Tirs1", "Tirs cadrés1",
           "% Tirs cadrés1", "Tirs2", "Tirs cadrés2", "% Tirs cadrés2",
           "Arrêts possibles1", "Arrêts1", "% Arrêts1", "Arrêts possibles2",
           "Arrêts2", "% Arrêts2", "Fautes1", "Fautes2", "Corners1",
           "Corners2", "Centres1", "Centres2", "Touches1", "Touches2",
           "Tacles1", "Tacles2", "Interceptions1", "Interceptions2",
           "Duels aériens gagnés1", "Duels aériens gagnés2", "Dégagements1",
           "Dégagements2", "Hors-jeux1", "Hors-jeux2",
           "Dégagements au six mètres1", "Dégagements au six mètres2",
           "Rentrée de touche1", "Rentrée de touche2", "Longs ballons1",
           "Longs ballons2", "Cartons jaunes1", "Cartons jaunes2",
           "Cartons rouges1", "Cartons rouges2", "Entraineur1", "Entraineur2", 
           "Dispositif1", "Dispositif2", "Composition1", "Composition2", "link"]
    data = []

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)
        match = get_match(soup) + [link]
        data.append(match)
        while time.time() - t <= 4.1:
            time.sleep(0.01)

    data = pd.DataFrame(data, columns=var)
    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")
    return data
