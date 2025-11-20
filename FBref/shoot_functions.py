import pandas as pd
from base_functions import get_link_matchs, page
from match_functions import get_event
from tqdm import tqdm
import time

def get_shoot(soup):
    var = ["league", "journey", "season", "date", "hours", "referee", "stadium", "team1", "team2",
           "minutes","player","team","xg_shot","psxg_shot","outcome","distance","body_part","notes","sca_1_player","sca_1_type","sca_2_player","sca_2_type"]
    index = get_event(soup) + ["NaN"] * 13
    data = pd.DataFrame(columns=var)

    try:
        code = soup.find_all("div", class_="table_container tabbed current", id="div_shots_all")[0].find_all("th", class_="right")
        for k in range(len(code)):
            if code[k].text != "":
                shoot = pd.DataFrame([index],columns=var)
                shoot["minutes"] = [code[k].text]
                code2 = soup.find_all("div", class_="table_container tabbed current", id="div_shots_all")[0].find_all("tr")[2+k].find_all("td")
                for col in shoot.columns:
                    for c2 in code2:
                        if col == c2.get("data-stat"):
                            shoot[f"{col}"] = [c2.text]
                data = pd.concat([data, shoot])
    finally:
        return data


def get_shoot_database(date_start, date_end, leagues):
    T = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    data = pd.DataFrame()

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t = time.time()
        soup = page(link)
        shoot_match = get_shoot(soup)
        data = pd.concat([data, shoot_match])

        while time.time() - t <= 10:
            time.sleep(0.01)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")
    return data