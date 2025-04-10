from shoot_functions import get_shoot
from player_functions import get_stats_player
from match_functions import get_match
from base_functions import get_link_matchs, page
import time
import pandas as pd

def get_database(date_start, date_end, leagues, folder):
    
    t = time.time()
    secs = []
    
    links = get_link_matchs(date_start, date_end, leagues)
    
    var = ["Championnat", "Journée", "Saison", "Equipe1", "Equipe2", "Score1", "Score2", "xG1", "xG2", "Possession1", "Possession2", "Passes1", "Passes réussies1", "% Passes réussies1", "Passes2", "Passes réussies2", "% Passes réussies2", "Tirs1", "Tirs cadrés1", "% Tirs cadrés1", "Tirs2", "Tirs cadrés2", "% Tirs cadrés2", "Arrêts possibles1", "Arrêts1", "% Arrêts1", "Arrêts possibles2", "Arrêts2", "% Arrêts2", "Fautes1" , "Fautes2", "Corners1", "Corners2", "Centres1", "Centres2", "Touches1", "Touches2", "Tacles1", "Tacles2", "Interceptions1", "Interceptions2", "Duels aériens gagnés1", "Duels aériens gagnés2", "Dégagements1", "Dégagements2", "Hors-jeux1","Hors-jeux2", "Dégagements au six mètres1", "Dégagements au six mètres2", "Rentrée de touche1", "Rentrée de touche2", "Longs ballons1", "Longs ballons2", "Cartons jaunes1", "Cartons jaunes2", "Cartons rouges1", "Cartons rouges2", "Date", "Heure", "Arbitre", "Affluence", "Stade", "Entraineur1", "Entraineur2", "Dispositif1", "Dispositif2", "Composition1", "Composition2"]
    matchs = []
    players = pd.DataFrame()
    shoots = pd.DataFrame()
    
    z=0 # Initialisation d'un compteur
    print("Chargement de la base de données...")
    print(" ")
    
    for link in links:
        z+=1
        soup = page(link)
        
        print("Chargement : ", round((z/len(links))*100), "%", end="\r")
        print(link, end = "\r")
        test = time.time()
        
        shoot = get_shoot(soup)
        shoots = pd.concat([shoots, shoot])
        
        player = get_stats_player(soup)
        players = pd.concat([players, player])
        
        match = get_match(soup)
        matchs.append(match)
        
        secs.append(time.time() - test)
        
    matchs = pd.DataFrame(matchs, columns=var)
    
    matchs.to_csv(f"{folder}/matchs.csv", index=False)
    players.to_csv(f"{folder}/players.csv", index=False)
    shoots.to_csv(f"{folder}/shoots.csv", index=False)
    
    print("Extraction terminée en ", round((time.time() - t)/60, 2), "minutes")
    
    return secs