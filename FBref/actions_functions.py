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
        text = c.text.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("for", " for").replace("Assist", " - Assist").replace("Tir au but—Substitute"," (Pen)—Goal score ").replace("Penalty Kick—", " (Pen)—Goal score ").replace("Penalty saved", " - Penalty saved")
        reg = re.match(r"(\d+\+?\d*[’'])(\d+:\d+)([^—]+)(?:—(.*))?", text)

        action_minute = sum([int(x) for x in reg.group(1).replace("’", "").split("+")])
        action_score = reg.group(2).strip()
        action_description = reg.group(3).strip().replace(":", " : ")
        if "Penalty saved" in action_description:
            action_type = "Penalty saved"
        else:
            action_type = reg.group(4).strip()
        match1 = re.match(r"([A-Za-z ]+)\s\d+:\d+", action_type)
        if match1:
            action_type = match1.group(1).strip()
        action_team = teams[0]
        action = [action_minute, action_score, action_description, action_type, action_team]

        game_actions.append(event + action)

    # Team 2
    code = soup.find_all("div", class_="event b")
    for c in code:
        text = c.text.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("for", " for").replace("Assist", " - Assist").replace("Tir au but—Substitute"," (Pen)—Goal score ").replace("Penalty Kick—", " (Pen)—Goal score ").replace("Penalty saved", " - Penalty saved")
        reg = re.match(r"(\d+\+?\d*[’'])(\d+:\d+)([^—]+)(?:—(.*))?", text)

        action_minute = sum([int(x) for x in reg.group(1).replace("’", "").split("+")])
        action_score = reg.group(2).strip()
        action_description = reg.group(3).strip().replace(":", " : ")
        if "Penalty saved" in action_description:
            action_type = "Penalty saved"
        else:
            action_type = reg.group(4).strip()
        match1 = re.match(r"([A-Za-z ]+)\s\d+:\d+", action_type)
        if match1:
            action_type = match1.group(1).strip()
        action_team = teams[1]
        action = [action_minute, action_score, action_description, action_type, action_team]

        game_actions.append(event + action)

    columns = ["league", "journey", "season", "date", "hours", "referee", "stadium", "team1", "team2", "action_minute", "action_score",
               "action_description", "action_type", "action_team"]
    data = pd.DataFrame(game_actions, columns=columns).sort_values(by="action_minute")
    
    return data


def get_actions_database(date_start, date_end, leagues, save, add):
    T = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    data = pd.DataFrame()

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)
        actions_match = get_actions_match(soup)
        data = pd.concat([data, actions_match])
        while time.time() - t <= 10:
            time.sleep(0.01)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")
    return data
