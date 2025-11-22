from base_functions import get_link_matchs, page
from shoot_functions import get_shoot
from player_functions import get_stats_player
from match_functions import get_match
from actions_functions import get_actions_match

from datetime import datetime, timedelta
import time
import pandas as pd
from tqdm import tqdm
import ace_tools_open as tools

def get_database(date_start, date_end, new = False):

    T = time.time()

    leagues = ["Ligue 1"]
    folder = "data"

    errors = []
    links = get_link_matchs(date_start, date_end, leagues)

    if new == True:
        matchs = pd.DataFrame()
        players = pd.DataFrame()
        shoots = pd.DataFrame()
        actions = pd.DataFrame()
    if new == False:
        matchs = pd.read_csv(f"{folder}/matchs.csv")
        players = pd.read_csv(f"{folder}/players.csv")
        shoots = pd.read_csv(f"{folder}/shoots.csv")
        actions = pd.read_csv(f"{folder}/actions.csv")

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        try:
            t = time.time()
            soup = page(link)

            match = pd.concat([get_match(soup), pd.DataFrame([link], columns=["link"])], axis=1)
            matchs = pd.concat([matchs, match])

            p = get_stats_player(soup)
            player = pd.concat([p, pd.DataFrame([link]*len(p), columns=["link"])], axis=1)
            players = pd.concat([players, player])

            shoot = pd.concat([get_shoot(soup), pd.DataFrame([link], columns=["link"])], axis=1)
            shoots = pd.concat([shoots, shoot])

            a = get_actions_match(soup)
            action = pd.concat([a, pd.DataFrame([link]*len(a), columns=["link"])], axis=1)
            actions = pd.concat([actions, action])
        
        except Exception as e:
            print(e)
            errors.append(link)

        while time.time() - t <= 10:
            time.sleep(0.01)

    errors = pd.DataFrame(errors)
    errors.to_csv(f"{folder}/errors.csv", index=False)
    matchs.to_csv(f"{folder}/matchs.csv", index=False)
    players.to_csv(f"{folder}/players.csv", index=False)
    shoots.to_csv(f"{folder}/shoots.csv", index=False)
    actions.to_csv(f"{folder}/actions.csv", index=False)
    
    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")


def update():

    T = time.time()

    folder = "data"
    leagues = ["Ligue 1"]

    matchs = pd.read_csv(f"{folder}/matchs.csv")
    players = pd.read_csv(f"{folder}/players.csv")
    shoots = pd.read_csv(f"{folder}/shoots.csv")
    actions = pd.read_csv(f"{folder}/actions.csv")
    

    last_date = pd.to_datetime(matchs[matchs["leagues"].isin(leagues)]['date'], format='%d/%m/%Y').max().strftime('%d/%m/%Y').split("/")
    date_str = last_date[2] + "-" + last_date[1] + "-" + last_date[0]
    last_date = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
    date_start = last_date.strftime("%Y-%m-%d")

    yesterday = datetime.today() - timedelta(days=1)
    date_end = yesterday.strftime("%Y-%m-%d")

    links = get_link_matchs(date_start, date_end, leagues)


    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)

        match = pd.concat([get_match(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        matchs = pd.concat([matchs, match])

        p = get_stats_player(soup)
        player = pd.concat([p, pd.DataFrame([link]*len(p), columns=["link"])], axis=1)
        players = pd.concat([players, player])

        shoot = pd.concat([get_shoot(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        shoots = pd.concat([shoots, shoot])

        a = get_actions_match(soup)
        action = pd.concat([a, pd.DataFrame([link]*len(a), columns=["link"])], axis=1)
        actions = pd.concat([actions, action])

        while time.time() - t <= 10:
            time.sleep(0.01)

    matchs.to_csv(f"{folder}/matchs.csv", index=False)
    players.to_csv(f"{folder}/players.csv", index=False)
    shoots.to_csv(f"{folder}/shoots.csv", index=False)
    actions.to_csv(f"{folder}/actions.csv", index=False)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")


def show_database():

    matchs = pd.read_csv("data/matchs.csv")

    leagues = list(matchs['leagues'].unique())

    max = pd.to_datetime(matchs[matchs["leagues"].isin(leagues)]['date'], format='%d/%m/%Y').max().strftime('%d/%m/%Y')
    min = pd.to_datetime(matchs[matchs["leagues"].isin(leagues)]['date'], format='%d/%m/%Y').min().strftime('%d/%m/%Y')

    print(leagues)
    print(min, "-", max)
    print("Nombre de matchs :", len(matchs), "\n\n")

    tools.display_dataframe_to_user("Matches :", pd.read_csv("data/matchs.csv"))
    tools.display_dataframe_to_user("Players :", pd.read_csv("data/players.csv"))
    tools.display_dataframe_to_user("Shoots :", pd.read_csv("data/shoots.csv"))
    tools.display_dataframe_to_user("Actions :", pd.read_csv("data/actions.csv"))