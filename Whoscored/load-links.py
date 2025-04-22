import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import time


def get_link(soup):
    code = soup.find_all("a")
    for c in code:
        if "Centre du Match" in c.text:
            if c.get("href") != "#":
                link = c.get("href")
            else:
                link = "None"
            break

    return link


def split_by_year(chaine):
    # Regex qui capture soit une année seule soit une plage d'années
    match = re.search(r'\b(20\d{2}(?:-20\d{2})?)\b', chaine)
    if match:
        year = match.group(1)
        parts = chaine.split(year, 1)
        before = parts[0].strip('-')
        after = parts[1].strip('-')
        return before, year, after
    else:
        return None, None, None

def whoscored_link_traitement(df):
    df["num_lien"] = df["link"].str.split("/matches/").str[1].str.split("/live/").str[0]
    df["num_lien"] = pd.to_numeric(df["num_lien"], errors="coerce")
    
    match_slugs = df["link"].str.split("/matches/").str[1].str.split("/live/").str[1]
    split_results = match_slugs.apply(split_by_year)

    df["league"] = split_results.apply(lambda x: x[0])
    df["annee"] = split_results.apply(lambda x: x[1])
    df["equipes"] = split_results.apply(lambda x: x[2])
    return df


def whoscored_not_available_error_traitement(df):
    df['num_lien'] = df['link'].str.split("/").str[4]
    df["num_lien"] = pd.to_numeric(df["num_lien"], errors="coerce")
    return df


def get_link_whoscored(range_down, range_up, new):
    path = "urls/raw/"
    number_list = list(range(range_down, range_up + 1))
    pre_links = [f"https://fr.whoscored.com/matches/{el}" for el in number_list]

    if not new:
        all_matches = pd.read_csv(f"{path}links.csv")
        try:
            all_errors = pd.read_csv(f"{path}errors.csv")
        except:
            all_errors = pd.DataFrame(columns=["link"])
        all_not_availables = pd.read_csv(f"{path}not_availables.csv")
    else:
        all_matches = pd.DataFrame(columns=["link"])
        all_not_availables = pd.DataFrame(columns=["link"])
        all_errors = pd.DataFrame(columns=["link"])

    def traitement(links_batch, all_matches, all_not_availables, all_errors):
        links = []
        errors = []
        not_availables = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        try:
            for pre_link in tqdm(links_batch):
                try:
                    driver.get(pre_link)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    link = get_link(soup)
                    if link == "None":
                        not_availables.append(pre_link)
                    else:
                        links.append(link)

                except Exception as e:
                    print(f"❌ Erreur lors de la récupération de la page : {e}")
                    errors.append(pre_link)

                # Sauvegardes tous les 10
                if len(links) == 10:
                    all_matches = pd.concat([all_matches, pd.DataFrame(links, columns=["link"])])
                    all_matches.to_csv(f"{path}links.csv", index=False)
                    links = []

                if len(not_availables) == 10:
                    all_not_availables = pd.concat([all_not_availables, pd.DataFrame(not_availables, columns=["link"])])
                    all_not_availables.to_csv(f"{path}not_availables.csv", index=False)
                    not_availables = []

                if len(errors) == 10:
                    all_errors = pd.concat([all_errors, pd.DataFrame(errors, columns=["link"])])
                    all_errors.to_csv(f"{path}errors.csv", index=False)
                    errors = []

        finally:
            driver.quit()

        # Dernière sauvegarde en fin de traitement
        if links:
            all_matches = pd.concat([all_matches, pd.DataFrame(links, columns=["link"])])
        if not_availables:
            all_not_availables = pd.concat([all_not_availables, pd.DataFrame(not_availables, columns=["link"])])
        if errors:
            all_errors = pd.concat([all_errors, pd.DataFrame(errors, columns=["link"])])

        return all_matches, all_not_availables, all_errors

    # Traitement initial
    all_matches, all_not_availables, all_errors = traitement(pre_links, all_matches, all_not_availables, all_errors)

    # Boucle de reprise des erreurs
    previous_error_count = -1
    while len(all_errors) > 0 and len(all_errors) != previous_error_count:
        previous_error_count = len(all_errors)
        print(f"🔁 Retraitement de {len(all_errors)} erreurs...")

        to_retry = all_errors["link"].tolist()
        all_errors = pd.DataFrame(columns=["link"])  # reset
        all_matches, all_not_availables, all_errors = traitement(to_retry, all_matches, all_not_availables, all_errors)

    # Suppression des doublons
    all_matches.drop_duplicates(inplace=True)
    all_errors.drop_duplicates(inplace=True)
    all_not_availables.drop_duplicates(inplace=True)

    # Sauvegarde finale
    all_matches.to_csv(f"{path}links.csv", index=False)
    all_errors.to_csv(f"{path}errors.csv", index=False)
    all_not_availables.to_csv(f"{path}not_availables.csv", index=False)

    # Clean part
    all_matches = whoscored_link_traitement(all_matches)
    all_not_availables = whoscored_not_available_error_traitement(all_not_availables)
    all_errors = whoscored_not_available_error_traitement(all_errors)

    all_matches.to_csv("urls/clean/links.csv", index=False)
    all_errors.to_csv("urls/clean/errors.csv", index=False)
    all_not_availables.to_csv("urls/clean/not_availables.csv", index=False)


