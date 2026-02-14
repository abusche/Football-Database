# Importation des packages
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time
import datetime

# --------------------------------------
# I. Liens Top Leagues                 -
# --------------------------------------


def get_link_top_leagues():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    url = "https://fr.whoscored.com/livescores"

    link_leagues = []

    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)

        time.sleep(2)

        prev_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Premier-Tournois-btn"))
        )

        driver.execute_script("arguments[0].click();", prev_button)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        code = soup.find_all("a", class_="TournamentNavButton-module_clickableArea__ZFnBl")
        for c in code:
            link_leagues.append("https://fr.whoscored.com" + c.get("href"))

    except Exception as e:
        print("Erreur :", e)

    finally:
        driver.quit()

    top_leagues = pd.DataFrame()
    leagues = []
    for link in link_leagues:
        leagues.append(link.split("/")[-1])

    top_leagues["league"] = leagues
    top_leagues["lien"] = link_leagues

    top_leagues.to_csv("urls/data_link_top_leagues.csv", index=False)

    return top_leagues

# --------------------------------------------------
# II. Liens de toutes les saisons disponibles      -
# --------------------------------------------------


def get_link_historical_leagues(link_leagues):

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    data_link_leagues = pd.DataFrame(columns=["annee", "pays", "league", "lien"])

    for url in tqdm(link_leagues):

        driver = webdriver.Firefox(service=service, options=options)

        try:
            driver.get(url)

            time.sleep(2)

            prev_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "seasons"))
            )

            driver.execute_script("arguments[0].click();", prev_button)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

        except Exception as e:
            print("Erreur :", e)

        finally:
            driver.quit()

        links = []

        pays = url.split("/")[-1].split("-")[0]

        if datetime.date.today().month > 8:
            annee1 = datetime.date.today().year
        else:
            annee1 = datetime.date.today().year - 1
        annee2 = annee1 + 1
        annee = str(annee1) + "/" + str(annee2)

        league = url.split("/")[-1].replace(pays, "").replace(str(annee1), "").replace(str(annee2), "").replace("-", " ").strip()

        code = soup.find("select", id = "seasons").find_all("option")

        for i in range(len(code)):
            link = "https://fr.whoscored.com" + code[i].get("value")
            links.append([annee, pays, league, link])
            if "/" in annee:
                annee1 += -1
                annee2 += -1
                annee = str(annee1) + "/" + str(annee2)
            else:
                annee = int(annee)
                annee += -1
                annee = str(annee)

        data = pd.DataFrame(links, columns=["annee", "pays", "league", "lien"])

        data_link_leagues = pd.concat([data_link_leagues, data])

    data_link_leagues.to_csv("urls/data_link_leagues.csv", index=False)

    return data_link_leagues

# ------------------------------------
# III. Liens de tous les matchs      -
# ------------------------------------


def get_link_match(data_link_leagues):

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    all_links = []
    all_links_df = []

    for i in tqdm(range(len(data_link_leagues))):

        driver = webdriver.Firefox(service=service, options=options)

        annee = data_link_leagues["annee"].iloc[i]
        pays = data_link_leagues["pays"].iloc[i]
        league = data_link_leagues["league"].iloc[i]
        url = data_link_leagues["lien"].iloc[i]

        try:
            driver.get(url)

            time.sleep(2)

            stop=False

            while stop == False:
                links1 = []
                links2 = []
                time.sleep(1)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                code = soup.find_all("div", class_="Match-module_right_oddsOn__o-ux-")
                for c in code:
                    if c.find("a") is not None:
                        link_name = c.find("a").get("href")
                        link = "https://fr.whoscored.com" + link_name
                        if link not in all_links:
                            links1.append([annee, pays, league, link])
                            links2.append(link)

                all_links_df = all_links_df + links1
                all_links = all_links + links2

                if links2 == []:
                    stop = True
                else:
                    prev_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "dayChangeBtn-prev"))
                    )

                    driver.execute_script("arguments[0].click();", prev_button)

        except Exception as e:
            print("Erreur :", e)

        finally:
            driver.quit()

    all_links_df = pd.DataFrame(all_links_df, columns=["annee", "pays", "league", "lien"])

    all_links_df.to_csv("urls/data_link_matches.csv", index=False)

    return all_links_df

# ------------------------------------
# IV. updates des liens des matchs   -
# ------------------------------------


def update_match_link():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    data_link_matches = pd.read_csv("urls/data_link_matches.csv")
    data_link_leagues = pd.read_csv("urls/data_link_leagues.csv")

    data_link_leagues = data_link_leagues[data_link_leagues["annee"] == data_link_leagues["annee"].max()]
    all_links = list(data_link_matches[data_link_matches["annee"] == data_link_matches["annee"].max()]["lien"])
    all_links_df = []

    driver = webdriver.Firefox(service=service, options=options)

    try:
        for i in tqdm(range(len(data_link_leagues))):

            annee = data_link_leagues["annee"].iloc[i]
            pays = data_link_leagues["pays"].iloc[i]
            league = data_link_leagues["league"].iloc[i]
            url = data_link_leagues["lien"].iloc[i]

            driver.get(url)

            time.sleep(2)

            stop=False

            while stop == False:
                links1 = []
                links2 = []
                time.sleep(1)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                code = soup.find_all("div", class_="Match-module_right_oddsOn__o-ux-")
                for c in code:
                    if c.find("a") is not None:
                        link_name = c.find("a").get("href")
                        link = "https://fr.whoscored.com" + link_name
                        if link not in all_links:
                            links1.append([annee, pays, league, link])
                            links2.append(link)

                all_links_df = all_links_df + links1
                all_links = all_links + links2

                if links2 == []:
                    stop = True
                else:
                    prev_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "dayChangeBtn-prev"))
                    )

                    driver.execute_script("arguments[0].click();", prev_button)

            all_links_df_live = []
            for link in all_links_df:
                if "/live/" in link[3]:
                    all_links_df_live.append(link)

            all_links_df_live = pd.DataFrame(all_links_df_live, columns=["annee", "pays", "league", "lien"])

    except Exception as e:
        print("Erreur :", e)

    finally:
        driver.quit()

    data_link_matches = pd.concat([data_link_matches, all_links_df_live])

    data_link_matches = data_link_matches.sort_values(["annee", "pays"], ascending=False)
    data_link_matches = data_link_matches.reset_index(drop = True)

    if all_links_df_live.empty:
        print("Aucun autre lien de match trouvé")
    else:
        print("Nombre de nouveau lien :", len(all_links_df_live))
        data_link_matches.to_csv("urls/data_link_matches.csv", index = False)

    return data_link_matches
