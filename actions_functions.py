import re
import pandas as pd
from match_functions import get_event, get_teams_name
from base_functions import get_link_matchs, page
import time
from tqdm import tqdm


def get_actions_match(soup):

    game_actions = []
    teams = get_teams_name(soup)
    event = get_event(soup)

    # Team 1
    code = soup.find_all("div", class_="event a")
    for c in code:
        text = c.text.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("pour", " pour").replace("Passe", " Passe").replace("Tir au but—Substitute"," (Pen)—Goal score ").replace("Tir au but—", " (Pen)—Goal score ")
        m1 = re.search(r'\d+:\d+', text)
        m1 = m1.group()
        reg = re.match(r"([\d+’]+)\d+:\d+([^—]+)—(.+)", text.replace("score", m1))

        action_minute = sum([int(x) for x in reg.group(1).replace("’", "").split("+")])
        action_description = reg.group(2).strip().replace(":", " : ")
        if "Pénalty arrêté" in action_description:
            action_type = "Pénalty arrêté"
        else:
            action_type = reg.group(3).strip()
        action_team = teams[0]
        action = [action_minute, action_description, action_type, action_team]

        game_actions.append(event + action)

    # Team 2
    code = soup.find_all("div", class_="event b")
    for c in code:
        text = c.text.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("pour", " pour").replace("Passe", " Passe").replace("Tir au but—Substitute"," (Pen)—Goal score ").replace("Tir au but—", " (Pen)—Goal score ").replace("Pénalty arrêté", " Pénalty arrêté")
        m1 = re.search(r'\d+:\d+', text)
        m1 = m1.group()
        reg = re.match(r"([\d+’]+)\d+:\d+([^—]+)—(.+)", text.replace("score", m1))

        action_minute = sum([int(x) for x in reg.group(1).replace("’", "").split("+")])
        action_description = reg.group(2).strip().replace(":", " : ")
        if "Pénalty arrêté" in action_description:
            action_type = "Pénalty arrêté"
        else:
            action_type = reg.group(3).strip()
        action_team = teams[1]
        action = [action_minute, action_description, action_type, action_team]

        game_actions.append(event + action)

    columns = ["championnat", "journée", "saison", "date", "heure", "arbitre", "stade", "equipe1", "equipe2", "action_minute", 
            "action_description", "action_type", "action_team"]
    data = pd.DataFrame(game_actions, columns=columns).sort_values(by="action_minute")
    
    return data


def get_actions_database(date_start, date_end, leagues, save, add):
    t = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    print("Chargement de la base de données...\n")
    data = pd.DataFrame()
    for link in tqdm(links):
        soup = page(link)
        actions_match = get_actions_match(soup)
        data = pd.concat([data, actions_match])

    print("Extraction terminée en ", round((time.time() - t)/60, 2), "minutes")
    return data
