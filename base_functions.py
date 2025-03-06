from datetime import datetime, timedelta
import functools
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
import cloudscraper


@functools.cache
def page_old(urlpage):
    """
    Récupération du HTML d'un site internet via Beautifulsoup
    """
    user_agent = {
        'User-Agent':
        ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        }
    time.sleep(3)
    res = requests.get(urlpage, headers=user_agent)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

@functools.cache
def page(urlpage):
    """
    Récupération du HTML d'un site internet en prenant des précautions contre le blocage.
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    ]
    
    headers = {'User-Agent': random.choice(user_agents)}
    
    # Attendre un délai aléatoire pour éviter d'être détecté comme un bot
    time.sleep(random.uniform(3, 7))
    
    scraper = cloudscraper.create_scraper()
    
    try:
        res = scraper.get(urlpage, headers=headers, timeout=10)
        res.raise_for_status()  # Vérifie s'il y a une erreur HTTP (ex: 403, 500, etc.)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la page : {e}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')
    return soup



def get_link_matchs(date_start, date_end, leagues):

    print("Extraction des liens...\n")
    start_date = datetime.strptime(date_start, '%Y-%m-%d')
    end_date = datetime.strptime(date_end, '%Y-%m-%d')
    links_day = []
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        url = f"https://fbref.com/fr/matchs/{date_str}"
        links_day.append(url)
        current_date += timedelta(days=1)

    links = []
    for link_day in tqdm(links_day):
        soup = page(link_day)
        matchs = soup.find_all("div", class_="table_wrapper tabbed")
        for match in matchs:
            if match.find("a"):
                if match.find("a").text in leagues:
                    m = match.find_all("a")
                    for k in m:
                        href = k.get("href")
                        if "matchs" in href and "Rapport de match" in k.text:
                            links.append('https://fbref.com' + k.get("href"))

    return links
