import time
import pandas as pd
from tqdm import tqdm

from base_functions import get_link_matchs, page
from match_functions import get_event

# Résumé
def get_summary(soup):

    var = ["league", "journey", "season", "date", "hours", "referee", "stadium", "team1", "team2", "name","shirtnumber","nationality","position","age","minutes","goals","assists","pens_made",
           "pens_att","shots","shots_on_target","cards_yellow","cards_red","touches","tackles","interceptions","blocks","xg","npxg","xg_assist","sca","gca","passes_completed","passes",
           "passes_pct","progressive_passes","carries","progressive_carries","take_ons","take_ons_won"]
    index = get_event(soup) + ["NaN"] * 31
    summary = pd.DataFrame(columns=var)

    try:
        code = soup.find_all("div", class_="table_container tabbed current")[0].find_all('th', class_="left")
        for i in range(len(code)-2):
            summary_player = pd.DataFrame([index], columns=var)
            summary_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed current")[0].find_all('tr')[i+2].find_all("td")
            for col in summary_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        summary_player[f"{col}"] = [c2.text]
            summary = pd.concat([summary, summary_player])

        code = soup.find_all("div", class_="table_container tabbed current")[1].find_all('th', class_="left")
        for i in range(len(code)-2):
            summary_player = pd.DataFrame([index], columns=var)
            summary_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed current")[1].find_all('tr')[i+2].find_all("td")
            for col in summary_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        summary_player[f"{col}"] = [c2.text]
            summary = pd.concat([summary, summary_player])
    finally:
        return summary

# Passes
def get_passes(soup):
    var = ["name","shirtnumber","nationality","position","age","minutes","passes_completed","passes","passes_pct",
        "passes_total_distance","passes_progressive_distance","passes_completed_short","passes_short",
        "passes_pct_short","passes_completed_medium","passes_medium","passes_pct_medium",
        "passes_completed_long","passes_long","passes_pct_long","assists","xg_assist","pass_xa","assisted_shots",
        "passes_into_final_third","passes_into_penalty_area","crosses_into_penalty_area","progressive_passes"]

    passes = pd.DataFrame(columns=var)
    try:
        code = soup.find_all("div", class_="table_container tabbed")[0].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[0].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])

        code = soup.find_all("div", class_="table_container tabbed")[5].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[5].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])
    finally:
        return passes


# Type de passe
def get_passes_type(soup):
    var = ["name","shirtnumber","nationality","position","age","minutes","passes","passes_live","passes_dead",
           "passes_free_kicks","through_balls","passes_switches","crosses","throw_ins","corner_kicks",
           "corner_kicks_in","corner_kicks_out","corner_kicks_straight","passes_completed",
           "passes_offsides","passes_blocked"]

    passes = pd.DataFrame(columns=var)
    try:
        code = soup.find_all("div", class_="table_container tabbed")[1].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[1].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])

        code = soup.find_all("div", class_="table_container tabbed")[6].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[6].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])
    finally:
        return passes


# Action défensive
def get_defensive_action(soup):
    var = ["name","shirtnumber","nationality","position","age","minutes","tackles","tackles_won",
           "tackles_def_3rd","tackles_mid_3rd","tackles_att_3rd","challenge_tackles","challenges",
           "challenge_tackles_pct","challenges_lost","blocks","blocked_shots","blocked_passes","interceptions",
           "tackles_interceptions","clearances","errors"]

    passes = pd.DataFrame(columns=var)
    try:
        code = soup.find_all("div", class_="table_container tabbed")[2].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[2].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])

        code = soup.find_all("div", class_="table_container tabbed")[7].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[7].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])
    finally:
        return passes


# Possession
def get_possession(soup):
    var = ["name","shirtnumber","nationality","position","age","minutes","touches","touches_def_pen_area",
           "touches_def_3rd","touches_mid_3rd","touches_att_3rd","touches_att_pen_area","touches_live_ball",
           "take_ons","take_ons_won","take_ons_won_pct","take_ons_tackled","take_ons_tackled_pct","carries",
           "carries_distance","carries_progressive_distance","progressive_carries","carries_into_final_third",
           "carries_into_penalty_area","miscontrols","dispossessed","passes_received",
           "progressive_passes_received"]

    passes = pd.DataFrame(columns=var)
    try:
        code = soup.find_all("div", class_="table_container tabbed")[3].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[3].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])

        code = soup.find_all("div", class_="table_container tabbed")[8].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[8].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])
    finally:
        return passes


# Statistiques diverses
def get_divers_stats(soup):
    var = ["name","shirtnumber","nationality","position","age","minutes","cards_yellow","cards_red","cards_yellow_red","fouls","fouled","offsides","crosses","interceptions","tackles_won",
           "pens_won","pens_conceded","own_goals","ball_recoveries","aerials_won","aerials_lost","aerials_won_pct"]

    passes = pd.DataFrame(columns=var)
    try:
        code = soup.find_all("div", class_="table_container tabbed")[4].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[4].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])

        code = soup.find_all("div", class_="table_container tabbed")[9].find_all('th', class_="left")
        for i in range(len(code)-2):
            passes_player = pd.DataFrame(columns=var)
            passes_player["name"] = [code[i+1].text]
            code2 = soup.find_all("div", class_="table_container tabbed")[9].find_all('tr')[i+2].find_all("td")
            for col in passes_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        passes_player[f"{col}"] = [c2.text]
            passes = pd.concat([passes, passes_player])
    finally:
        return passes


def keep_uppercase(input_string):
    return ''.join([char for char in input_string if char.isupper()])


def get_stat_goal(soup):

    var = ["name","nationality","age","minutes","gk_shots_on_target_against","gk_goals_against","gk_saves","gk_save_pct","gk_psxg","gk_passes_completed_launched","gk_passes_launched",
           "gk_passes_pct_launched","gk_passes","gk_passes_throws","gk_pct_passes_launched","gk_passes_length_avg","gk_goal_kicks","gk_pct_goal_kicks_launched","gk_goal_kick_length_avg",
           "gk_crosses","gk_crosses_stopped","gk_crosses_stopped_pct","gk_def_actions_outside_pen_area","gk_avg_distance_def_actions"]

    GK = pd.DataFrame(columns=var)

    try:
        code = soup.find_all("div", class_="table_container")[6].find_all("th", class_="left")[1:]
        code2 = soup.find_all("div", class_="table_container")[6].find_all("td")
        for i in range(len(code)):
            GK_player = pd.DataFrame(columns=var)
            GK_player["name"] = [code[i].text]
            for col in GK_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        GK_player[f"{col}"] = [c2.text]
            GK = pd.concat([GK, GK_player])
            
        code = soup.find_all("div", class_="table_container")[13].find_all("th", class_="left")[1:]
        code2 = soup.find_all("div", class_="table_container")[13].find_all("td")
        for i in range(len(code)):
            GK_player = pd.DataFrame(columns=var)
            GK_player["name"] = [code[i].text]
            for col in GK_player.columns:
                for c2 in code2:
                    if col == c2.get("data-stat"):
                        GK_player[f"{col}"] = [c2.text]
            GK = pd.concat([GK, GK_player])

    finally:
        return GK


def get_stats_player(soup):

    df = get_summary(soup).merge(get_passes(soup), on=["name","shirtnumber","nationality","position","age","minutes"], how='left')
    df2 = df.merge(get_passes_type(soup), on=["name","shirtnumber","nationality","position","age","minutes"], how='left')
    df3 = df2.merge(get_defensive_action(soup), on=["name","shirtnumber","nationality","position","age","minutes"], how='left')
    df4 = df3.merge(get_possession(soup), on=["name","shirtnumber","nationality","position","age","minutes"], how='left')
    df5 = df4.merge(get_divers_stats(soup), on=["name","shirtnumber","nationality","position","age","minutes"], how='left')
    df6 = df5.merge(get_stat_goal(soup), on=["name","nationality","age","minutes"], how='left')
    df6["nationality"] = df6["nationality"].apply(keep_uppercase)
    return df6


def get_player_database(date_start, date_end, leagues, save, add):
    T = time.time()
    links = get_link_matchs(date_start, date_end, leagues)
    data = pd.DataFrame()

    for link in tqdm(links, desc="Extraction des données des matchs", unit="Matchs", colour="green"):
        t=time.time()
        soup = page(link)

        info = get_stats_player(soup)
        data = pd.concat([data, info])

        while time.time() - t <= 4.1:
            time.sleep(0.01)

    print("Extraction terminée en ", round((time.time() - T)/60, 2), "minutes")
    return data
