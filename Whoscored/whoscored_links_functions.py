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


def get_link_top_leagues(save=False):
    """
    Récupère les liens des principaux championnats (Top Leagues)
    depuis la page livescores de WhoScored.

    La fonction ouvre un navigateur Firefox puis extrait les liens
    des compétitions à l'aide de BeautifulSoup.

    Parameters
    ----------
    save : bool, optional (default=False)
        Si True, sauvegarde le résultat dans un fichier CSV
        à l'emplacement 'urls/data_link_top_leagues.csv'.

    Returns
    -------
    pd.DataFrame
        DataFrame contenant :
        - league : nom du championnat (extrait de l'URL)
        - lien   : URL complète vers la page du championnat
    """

    # --- Validation de l’argument ---
    if save not in [False, True]:
        print("L'argument 'save' doit prendre la valeur 'True' ou 'False'")
        return None

    # --- Configuration du navigateur Firefox en mode headless ---
    options = Options()
    options.add_argument("--headless")  # Exécution sans interface graphique
    options.add_argument("--disable-gpu")  # Désactivation GPU
    options.add_argument("--no-sandbox")

    # Installation automatique du driver Gecko
    service = Service(GeckoDriverManager().install())

    url = "https://fr.whoscored.com/livescores"
    link_leagues = []

    # Initialisation du driver
    driver = webdriver.Firefox(service=service, options=options)

    try:
        # --- Chargement de la page ---
        driver.get(url)

        time.sleep(2)  # Pause pour laisser le temps au JS de charger

        # --- Attente explicite du bouton des tournois principaux ---
        prev_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Premier-Tournois-btn"))
        )

        # Clic via JavaScript pour le retour en arrière
        driver.execute_script("arguments[0].click();", prev_button)

        # --- Récupération du HTML rendu dynamiquement ---
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extraction des liens des tournois
        code = soup.find_all(
            "a",
            class_="TournamentNavButton-module_clickableArea__ZFnBl"
        )

        for c in code:
            link_leagues.append("https://fr.whoscored.com" + c.get("href"))

    except Exception as e:
        # Gestion générique des erreurs Selenium / parsing
        print("Erreur :", e)

    finally:
        # Fermeture propre du navigateur
        driver.quit()

    # --- Construction du DataFrame résultat ---
    leagues = []

    # Extraction du nom du championnat depuis l’URL
    for link in link_leagues:
        leagues.append(link.split("/")[-1])

    top_leagues = pd.DataFrame({
        "league": leagues,
        "link": link_leagues
    })

    # --- Sauvegarde optionnelle ---
    if save is True:
        top_leagues.to_csv(
            "urls/data_link_top_leagues.csv",
            index=False
        )

    return top_leagues

# --------------------------------------------------
# II. Liens de toutes les saisons disponibles      -
# --------------------------------------------------


def get_link_historical_leagues(data_link_top_leagues, save=False):
    """
    Récupère l'ensemble des liens historiques (par saison) pour chaque
    championnat fourni en entrée.

    Pour chaque URL de ligue :
    - Ouvre la page Firefox
    - Clique sur le sélecteur de saisons
    - Extrait toutes les saisons disponibles
    - Construit un DataFrame contenant année, pays, ligue et lien associé

    Parameters
    ----------
    link_leagues : list
        Liste des URLs des championnats principaux.
    save : bool, optional (default=False)
        Si True, sauvegarde le résultat dans
        'urls/data_link_leagues.csv'.

    Returns
    -------
    pd.DataFrame
        DataFrame avec les colonnes :
        - annee  : saison (ex: 2023/2024)
        - pays   : pays du championnat
        - league : nom du championnat
        - lien   : URL vers la saison spécifique
    """

    # --- Validation de l’argument ---
    if save not in [False, True]:
        print("L'argument 'save' doit prendre la valeur 'True' ou 'False'")
        return None

    # --- Configuration Selenium (Firefox headless) ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    # DataFrame final cumulatif
    data_link_leagues = pd.DataFrame(
        columns=["season", "country", "league", "link"]
    )

    # --- Boucle sur chaque championnat ---
    for url in tqdm(list(data_link_top_leagues["link"])):

        driver = webdriver.Firefox(service=service, options=options)

        try:
            # Chargement de la page
            driver.get(url)
            time.sleep(3)

            # Attente du menu déroulant des saisons
            prev_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "seasons"))
            )

            # Clic via JS
            driver.execute_script("arguments[0].click();", prev_button)

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

        except Exception as e:
            print("Erreur :", e)

        finally:
            driver.quit()

        # --- Extraction des métadonnées depuis l’URL ---
        links = []

        # Extraction du pays depuis l’URL
        pays = url.split("/")[-1].split("-")[0]

        # Détermination de la saison courante
        if datetime.date.today().month > 8:
            annee1 = datetime.date.today().year
        else:
            annee1 = datetime.date.today().year - 1
        annee2 = annee1 + 1
        annee = str(annee1) + "/" + str(annee2)

        # Extraction du nom du championnat depuis l’URL
        league = (
            url.split("/")[-1]
            .replace(pays, "")
            .replace(str(annee1), "")
            .replace(str(annee2), "")
            .replace("-", " ")
            .strip()
        )

        # --- Récupération des saisons disponibles ---
        code = soup.find("select", id="seasons").find_all("option")

        for i in range(len(code)):
            link = "https://fr.whoscored.com" + code[i].get("value")
            links.append([annee, pays, league, link])

            # Décrémentation saison par saison
            if "/" in annee:
                annee1 -= 1
                annee2 -= 1
                annee = f"{annee1}/{annee2}"
            else:
                annee = str(int(annee) - 1)

        # DataFrame temporaire pour la ligue courante
        data = pd.DataFrame(
            links,
            columns=["season", "country", "league", "link"]
        )

        # Concaténation au DataFrame global
        data_link_leagues = pd.concat([data_link_leagues, data])

    data_link_leagues = data_link_leagues.reset_index(drop=True)

    if save is True:
        data_link_leagues.to_csv("urls/data_link_leagues.csv", index=False)

    return data_link_leagues

# ------------------------------------
# III. Liens de tous les matchs      -
# ------------------------------------


def get_link_match(data_link_leagues, save=False):
    """
    Récupère l'ensemble des liens des matchs pour chaque saison de chaque
    championnat présent dans le DataFrame fourni.

    Pour chaque ligne du DataFrame :
    - Ouvre la page de la saison via Selenium
    - Récupère les liens des matchs affichés
    - Navigue jour par jour vers le passé jusqu'à épuisement des matchs
    disponibles
    - Évite les doublons
    - Construit un DataFrame final consolidé

    Parameters
    ----------
    data_link_leagues : pd.DataFrame
        DataFrame contenant :
        - annee  : saison
        - pays   : pays
        - league : nom du championnat
        - lien   : URL de la saison
    save : bool, optional (default=False)
        Si True, sauvegarde le résultat dans
        'urls/data_link_matches.csv'.

    Returns
    -------
    pd.DataFrame
        DataFrame contenant :
        - annee
        - pays
        - league
        - lien (URL du match)
    """

    # --- Validation de l’argument ---
    if save not in [False, True]:
        print("L'argument 'save' doit prendre la valeur 'True' ou 'False'")
        return None

    # --- Configuration Selenium (Firefox headless) ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    driver = webdriver.Firefox(service=service, options=options)

    # Liste pour éviter les doublons globaux
    all_links = []
    # Liste des données structurées pour le DataFrame final
    all_links_df = []

    try:

        # --- Boucle principale sur chaque saison de championnat ---
        for i in tqdm(range(len(data_link_leagues))):

            # Extraction des métadonnées
            annee = data_link_leagues["season"].iloc[i]
            pays = data_link_leagues["country"].iloc[i]
            league = data_link_leagues["league"].iloc[i]
            url = data_link_leagues["link"].iloc[i]

            try:

                driver.get(url)
                time.sleep(2)

                # Variable de contrôle pour parcourir les jours précédents
                stop = False

                while stop is False:

                    links1 = []  # Données structurées (avec métadonnées)
                    links2 = []  # Liens simples (contrôle doublons)

                    time.sleep(1)

                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                    # Extraction des blocs contenant les liens des matchs
                    code = soup.find_all(
                        "div",
                        class_="Match-module_right_oddsOn__o-ux-"
                    )

                    for c in code:
                        if c.find("a") is not None:
                            link_name = c.find_all("a")[-1].get("href")
                            link = "https://fr.whoscored.com" + link_name
                            if "/live/" in link:
                                # Évite les doublons globaux
                                if link not in all_links:
                                    links1.append([annee, pays, league, link])
                                    links2.append(link)

                    # Ajout aux structures globales
                    all_links_df = all_links_df + links1
                    all_links = all_links + links2

                    # Condition d’arrêt : si aucun nouveau lien trouvé
                    if links2 == []:
                        stop = True
                    else:
                        # Navigation vers le jour précédent
                        prev_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.ID, "dayChangeBtn-prev")
                            )
                        )

                        driver.execute_script(
                            "arguments[0].click();",
                            prev_button
                        )

            except Exception as e:
                print("Erreur :", e)

    finally:
        driver.quit()

    # --- Construction du DataFrame final ---
    all_links_df = pd.DataFrame(
        all_links_df,
        columns=["season", "country", "league", "link"]
    )

    # --- Sauvegarde automatique ---
    if save is True:
        all_links_df.to_csv("urls/data_link_matches.csv", index=False)

    return all_links_df

# ------------------------------------
# IV. updates des liens des matchs   -
# ------------------------------------


def update_match_link(save=False):
    """
    Met à jour le fichier des liens de matchs en récupérant
    les nouveaux matchs de la saison la plus récente.

    La fonction :
    - Charge les fichiers CSV existants (leagues + matches)
    - Identifie la saison la plus récente
    - Scrape uniquement cette saison
    - Récupère les nouveaux liens non encore présents
    - Filtre les liens contenant "/live/"
    - Met à jour le dataset global

    Parameters
    ----------
    save : bool, optional (default=False)
        Si True, sauvegarde le fichier mis à jour
        dans 'urls/data_link_matches.csv'.

    Returns
    -------
    pd.DataFrame
        DataFrame mis à jour contenant l'ensemble des liens de matchs.
    """

    # --- Validation de l’argument ---
    if save not in [False, True]:
        print("L'argument 'save' doit prendre la valeur 'True' ou 'False'")
        return None

    # --- Configuration Selenium (Firefox headless) ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())

    # --- Chargement des données existantes ---
    data_link_matches = pd.read_csv("urls/data_link_matches.csv")
    data_link_leagues = pd.read_csv("urls/data_link_leagues.csv")

    # On ne garde que la saison la plus récente
    current_season = data_link_leagues["season"].max()
    data_link_leagues = data_link_leagues[
        data_link_leagues["season"] == current_season
    ]

    # Liste des liens déjà existants (évite doublons)
    all_links = list(
        data_link_matches[
            data_link_matches["season"] ==
            data_link_matches["season"].max()
        ]["link"]
    )

    all_links_df = []

    driver = webdriver.Firefox(service=service, options=options)

    try:
        # --- Boucle sur chaque championnat de la saison courante ---
        for i in tqdm(range(len(data_link_leagues))):

            annee = data_link_leagues["season"].iloc[i]
            pays = data_link_leagues["country"].iloc[i]
            league = data_link_leagues["league"].iloc[i]
            url = data_link_leagues["link"].iloc[i]

            driver.get(url)
            time.sleep(2)

            prev_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, "dayChangeBtn-prev")
                )
            )

            driver.execute_script("arguments[0].click();", prev_button)

            stop = False

            # --- Navigation jour par jour ---
            while stop is False:

                links1 = []
                links2 = []

                time.sleep(1)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # code = soup.find_all(
                #    "div",
                #    class_="Match-module_right_oddsOn__o-ux-"
                # )
                code = soup.find_all(
                    "a", class_="Match-module_statsBtn__O2q4H")

                # for c in code:
                #    if c.find("a") is not None:
                #        link_name = c.find_all("a")[-1].get("href")
                #        link = "https://fr.whoscored.com" + link_name

                for c in code:
                    if c.get("href") is not None:
                        link_name = c.get("href")
                        link = "https://fr.whoscored.com" + link_name

                        # Ajout uniquement si lien nouveau
                        if link not in all_links:
                            links1.append([annee, pays, league, link])
                            links2.append(link)

                all_links_df = all_links_df + links1
                all_links = all_links + links2

                # Condition d’arrêt
                if links2 == []:
                    stop = True
                else:
                    prev_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.ID, "dayChangeBtn-prev")
                        )
                    )

                    driver.execute_script("arguments[0].click();", prev_button)

            # --- Filtrage des liens "live" uniquement ---
            all_links_df_live = []
            for link in all_links_df:
                if "/live/" in link[3]:
                    all_links_df_live.append(link)

            all_links_df_live = pd.DataFrame(
                all_links_df_live,
                columns=["season", "country", "league", "link"]
            )

    except Exception as e:
        print("Erreur :", e)
        all_links_df_live = pd.DataFrame(
            columns=["season", "country", "league", "link"]
        )

    finally:
        driver.quit()

    # --- Fusion avec dataset existant ---
    data_link_matches = pd.concat([data_link_matches, all_links_df_live])

    data_link_matches = data_link_matches.sort_values(
        ["season", "country"], ascending=False)
    data_link_matches = data_link_matches.reset_index(drop=True)

    # --- Reporting + sauvegarde optionnelle ---
    if all_links_df_live.empty:
        print("Aucun autre lien de match trouvé")
    else:
        print("Nombre de nouveau lien :", len(all_links_df_live))
        if save is True:
            data_link_matches.to_csv("urls/data_link_matches.csv", index=False)

    return all_links_df_live
