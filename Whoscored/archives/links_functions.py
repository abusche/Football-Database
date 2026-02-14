from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import pandas as pd
import time
import ace_tools_open as tools


###########################
# I. Current month        #
###########################

def get_link_current_month(url):

    options = Options()
    options.add_argument("--headless")  # Mode headless activé
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    all_links = []

    try:
        driver.get(url)
        
        # Accepter les cookies si la bannière apparaît
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qc-cmp-cleanslate"))
            )
            driver.execute_script("arguments[0].click();", accept_cookies)
            time.sleep(2)
        except Exception:
            print("Bannière de cookies non détectée.")
        
        time.sleep(2)  # Attendre le chargement de la page
        
        # Récupération du HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Extraction des liens
        code = soup.find_all("div", class_="Match-module_right_oddsOn__o-ux-")
        for c in code:
            if c.find("a") is not None:
                all_links.append("https://fr.whoscored.com" + c.find("a").get("href"))
            
    except Exception as e:
        print(e)
    finally:
        driver.quit()

    return all_links


###########################
# II. Old links           #
###########################

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

    df = df.sort_values(by='num_lien')

    return df


def whoscored_not_available_error_traitement(df):
    df['num_lien'] = df['link'].str.split("/").str[4]
    df["num_lien"] = pd.to_numeric(df["num_lien"], errors="coerce")
    df = df.sort_values(by='num_lien')
    return df


def traitement(links_batch, all_matches, all_not_availables, all_errors):

    path = "urls/raw/"

    links = []
    errors = []
    not_availables = []

    nb_links = 0
    nb_not_availables = 0
    nb_errors = 0

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
                    nb_not_availables += 1
                else:
                    links.append(link)
                    nb_links += 1

            except Exception as e:
                print(f"❌ Erreur lors de la récupération de la page : {e}")
                errors.append(pre_link)
                nb_errors += 1

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

    return all_matches, all_not_availables, all_errors, nb_links, nb_not_availables, nb_errors



def clean_links(message = False):
    path = "urls/raw/"
    all_matches = pd.read_csv(f"{path}links.csv")
    try:
        all_errors = pd.read_csv(f"{path}errors.csv")
    except:
        all_errors = pd.DataFrame(columns=["link"])
    all_not_availables = pd.read_csv(f"{path}not_availables.csv")

    nb_links_raw = len(all_matches["link"])
    nb_not_availables_raw = len(all_not_availables["link"])
    nb_errors_raw = len(all_errors["link"])

    all_matches = whoscored_link_traitement(all_matches)
    all_not_availables = whoscored_not_available_error_traitement(all_not_availables)
    all_errors = whoscored_not_available_error_traitement(all_errors)

    if message == True:
        print("Nouveaux liens traités :", len(all_matches["link"]) - nb_links_raw)
        print("Nouveaux liens traités pas applicables :", len(all_not_availables["link"]) - nb_not_availables_raw)
        print("Nouvelles erreurs :", len(all_errors["link"]) - nb_errors_raw)

    all_matches.to_csv("urls/clean/links.csv", index=False)
    all_errors.to_csv("urls/clean/errors.csv", index=False)
    all_not_availables.to_csv("urls/clean/not_availables.csv", index=False)



def get_link_whoscored(range_down, range_up, new = True):
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

    # Traitement initial
    all_matches, all_not_availables, all_errors, nb_links, nb_not_availables, nb_errors = traitement(pre_links, all_matches, all_not_availables, all_errors)

    # Suppression des doublons
    all_matches.drop_duplicates(inplace=True)
    all_errors.drop_duplicates(inplace=True)
    all_not_availables.drop_duplicates(inplace=True)

    # Sauvegarde finale
    all_matches.to_csv(f"{path}links.csv", index=False)
    all_errors.to_csv(f"{path}errors.csv", index=False)
    all_not_availables.to_csv(f"{path}not_availables.csv", index=False)

    print("Matchs trouvés :", nb_links)
    print("Non Applicables :", nb_not_availables)
    print("Erreurs :", nb_errors)

    # Clean part
    clean_links()

    # Traitement des erreurs
    nb_error = len(all_errors)
    i=1
    while nb_error != 0:
        print("Traitement des erreurs n°{i} \n")
        error_traitement()
        nb_error = len(pd.read_csv("urls/clean/errors.csv"))
        i+=1


def error_traitement():

    path = "urls/raw/"

    errors = pd.read_csv("urls/clean/errors.csv")
    retry = list(errors["link"])

    from links_functions import traitement, whoscored_link_traitement, whoscored_not_available_error_traitement
    all_matches = pd.read_csv("urls/clean/links.csv")
    all_not_availables = pd.read_csv("urls/clean/not_availables.csv")
    all_errors = pd.DataFrame(columns=["link"])

    all_matches, all_not_availables, all_errors, nb_links, nb_not_availables, nb_errors = traitement(retry, all_matches, all_not_availables, all_errors)

    # Suppression des doublons
    all_matches.drop_duplicates(inplace=True)
    all_errors.drop_duplicates(inplace=True)
    all_not_availables.drop_duplicates(inplace=True)

    # Sauvegarde finale
    all_matches.to_csv(f"{path}links.csv", index=False)
    all_errors.to_csv(f"{path}errors.csv", index=False)
    all_not_availables.to_csv(f"{path}not_availables.csv", index=False)

    # Clean part
    clean_links()


def update_link(num, order):
    path = "urls/clean/"
    all_matches = pd.read_csv(f"{path}links.csv")
    all_not_availables = pd.read_csv(f"{path}not_availables.csv")
    try:
        all_errors = pd.read_csv(f"{path}errors.csv")
    except:
        all_errors = pd.DataFrame(columns=["link"])
    
    ma = int(max([int(all_matches["num_lien"].max()), float(all_not_availables["num_lien"].max())]))
    mi = int(min([int(all_matches["num_lien"].min()), float(all_not_availables["num_lien"].min())]))

    number_list = []
    if order == "asc":
        number_list = list(range(ma + 1, ma + num + 1))
    if order == "desc":
        number_list = list(range(mi - num, mi))

    pre_links = [f"https://fr.whoscored.com/matches/{el}" for el in number_list]

    all_matches, all_not_availables, all_errors, nb_links, nb_not_availables, nb_errors = traitement(pre_links, all_matches, all_not_availables, all_errors)

    print("Matchs trouvés :", nb_links)
    print("Non Applicables :", nb_not_availables)
    print("Erreurs :", nb_errors)

    clean_links()



    # Traitement des erreurs
    nb_error = len(all_errors)
    i=1
    while nb_error != 0:
        print("Traitement des erreurs n°{i} \n")
        error_traitement()
        nb_error = len(pd.read_csv("urls/clean/errors.csv"))
        i+=1



###################
# IV. Vizu       #
###################

def show_links():
    links = pd.read_csv("urls/clean/links.csv")
    not_available = pd.read_csv("urls/clean/not_availables.csv")
    try:
        error = pd.read_csv("urls/clean/errors.csv")
    except:
        error = pd.DataFrame()

    links_raw = pd.read_csv("urls/raw/links.csv")
    not_available_raw = pd.read_csv("urls/raw/not_availables.csv")
    try:
        error_raw = pd.read_csv("urls/raw/errors.csv")
    except:
        error = pd.DataFrame()

    print("Données transformées :")
    print("Intervalle des données :", int(links["num_lien"].min()), max([int(links["num_lien"].max()), float(not_available["num_lien"].max())]))
    print("Links :", len(links["num_lien"]))
    print("Not availables :", len(not_available["num_lien"]))
    print("Errors :", len(error["num_lien"]))
    print("Nombre d'observation :", len(links) + len(not_available),"\n")

    print("Données brutes :")
    print("Intervalle des données :", int(links_raw["num_lien"].min()), max([int(links_raw["num_lien"].max()), float(not_available_raw["num_lien"].max())]))
    print("Links :", len(links_raw["num_lien"]))
    print("Not availables :", len(not_available_raw["num_lien"]))
    print("Errors :", len(error_raw["link"]))
    print("Nombre d'observation :", len(links_raw) + len(not_available_raw),"\n")
    tools.display_dataframe_to_user("Links :", links_raw)
    tools.display_dataframe_to_user("Not availables :", not_available_raw)
    tools.display_dataframe_to_user("Errors :", error)
    tools.display_dataframe_to_user("NA's :", links[links_raw["num_lien"].isna()])