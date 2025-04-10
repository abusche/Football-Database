from base_functions import get_link_matchs, page
from shoot_functions import get_shoot
from player_functions import get_stats_player
from match_functions import get_match
from actions_functions import get_actions_match
import time
import pandas as pd
from tqdm import tqdm


def get_database(date_start, date_end, leagues, folder = "data", save = True, add = False):

    T = time.time()

    links = get_link_matchs(date_start, date_end, leagues)

    if add == True:
        matchs = pd.read_csv(f"{folder}/matchs.csv")
        players = pd.read_csv(f"{folder}/players.csv")
        shoots = pd.read_csv(f"{folder}/shoots.csv")
        actions = pd.read_csv(f"{folder}/actions.csv")
    elif add == False:
        matchs = pd.DataFrame()
        players = pd.DataFrame()
        shoots = pd.DataFrame()
        actions = pd.DataFrame()
    else:
        raise ValueError("Le paramètre 'add' doit être True ou False")


    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)

        match = pd.concat([get_match(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        matchs = pd.concat([matchs, match])

        player = pd.concat([get_stats_player(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        players = pd.concat([players, player])

        shoot = pd.concat([get_shoot(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        shoots = pd.concat([shoots, shoot])

        action = pd.concat([get_actions_match(soup), pd.DataFrame([link], columns=["link"])], axis=1)
        actions = pd.concat([actions, action])

        while time.time() - t <= 4.1:
            time.sleep(0.01)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")

    if save == True:
        matchs.to_csv(f"{folder}/matchs.csv", index=False)
        players.to_csv(f"{folder}/players.csv", index=False)
        shoots.to_csv(f"{folder}/shoots.csv", index=False)
        actions.to_csv(f"{folder}/actions.csv", index=False)
    elif save == False:
        return matchs, players, shoots, actions
