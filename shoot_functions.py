import pandas as pd
from base_functions import get_link_matchs, page
from match_functions import get_team, get_event_details

def get_shoot(soup):
    index = get_team(soup)[0] + "_" + get_team(soup)[1] + "_" + get_event_details(soup)[0] + "_" + get_event_details(soup)[1] + "_" + get_event_details(soup)[2]
    tirs = []
    var = ["Match_Index", "Minutes", "Joueur", "Equipe", "xG", "PSxG", "Résultats", "Distance", "Corps", "Notes", "AMT1Joueur", "AMT1Evenement", "AMT2Joueur", "AMT2Evenement"]
    minute = soup.find_all("div", class_="table_container tabbed current", id="div_shots_all")[0].find_all("th", class_="right")
    for k in range(len(minute)):
        if minute[k].text != "":
            tir = [index, minute[k].text]
            code = soup.find_all("div", class_="table_container tabbed current", id="div_shots_all")[0].find_all("tr")[2+k].find_all("td")
            for i in range(len(code)):
                tir.append(code[i].text)
            tirs.append(tir)
    tirs = pd.DataFrame(tirs, columns=var)
    return tirs

