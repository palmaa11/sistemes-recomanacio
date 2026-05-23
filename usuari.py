"""
usuari.py — Gestió dels perfils d'usuari simulats.
 
Cada usuari té:
  - preferencies : dict {tema: float [0,1]} que evoluciona amb les interaccions
  - historial    : llista d'interaccions passades (tema, video_id, resultat)
"""
 
import numpy as np
import config
 
TEMES = ["esport", "politica", "humor", "tecnologia",
         "ciencia", "cultura", "salut", "economia", "viatges", "moda"]
 
# Taxes d'actualització de preferències
DELTA_POSITIU = 0.08   # increment si l'usuari interactua  
DELTA_NEGATIU = 0.03   # decrement si no interactua      
 
 
def crear_usuari():
    """
    Crea un nou usuari amb preferències inicials aleatòries
    seguint una distribució Beta(α, β) escalada a [0.2, 0.8].
 
    L'ús de la distribució Beta en lloc de la uniforme genera preferències
    inicials més realistes: la majoria d'usuaris tindran preferències
    moderades (al voltant de 0.5), i serà menys freqüent trobar usuaris
    amb preferències molt extremes en totes les temàtiques.
    Els paràmetres α i β es configuren a config.py.
    """
    prefs = {
        tema: float(0.2 + 0.6 * np.random.beta(config.BETA_PREF_A,
                                                config.BETA_PREF_B))
        for tema in TEMES
    }
    return {
        "preferencies": prefs,
        "historial": []
    }
 
 
def interactua(user, video):
    """
    Simula si l'usuari interactua amb el vídeo.
 
    La probabilitat d'interacció combina la preferència pel tema (70%)
    i l'impacte emocional del contingut (30%), limitada a [0, 1].
 
    Returns:
        bool — True si hi ha interacció, False altrament.
    """
    base   = user["preferencies"][video["tema"]]
    emocio = video["emocio"]
    prob   = 0.7 * base + 0.3 * emocio
    prob   = max(0.0, min(1.0, prob))
    return np.random.random() < prob
 
 
def actualitzar(user, video, interact):
    """
    Actualitza les preferències de l'usuari en funció de la interacció.
 
    Si hi ha interacció, la preferència pel tema augmenta (DELTA_POSITIU).
    Si no n'hi ha, disminueix lleugerament (DELTA_NEGATIU).
    El valor resultant es clipa a [0, 1].
 
    Nota: l'asimetria (0.08 vs 0.03) és deliberada i reflecteix
    que les plataformes reals reforcen preferències més ràpidament
    del que les debiliten, modelitzant un biaix de confirmació.
    """
    tema = video["tema"]
    if interact:
        user["preferencies"][tema] += DELTA_POSITIU
    else:
        user["preferencies"][tema] -= DELTA_NEGATIU
    user["preferencies"][tema] = max(0.0, min(1.0, user["preferencies"][tema]))  
 
    user["historial"].append({
        "video_id":   video["id"],
        "tema":       tema,
        "interaccio": interact
    })