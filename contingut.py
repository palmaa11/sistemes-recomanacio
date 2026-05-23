"""
contingut.py — Generació del catàleg de vídeos simulats.
 
Cada vídeo té:
  - id      : identificador únic
  - tema    : categoria temàtica (esport, política, humor, tecnologia)
  - emocio  : nivell d'impacte emocional [0, 1]
  - qualitat: qualitat intrínseca del contingut [0, 1]
 
Els atributs emocio i qualitat es generen amb una distribució Beta(α, β),
més realista que la uniforme: concentra els valors al voltant de 0.5
i redueix la freqüència de valors extrems (propers a 0 o a 1).
Els paràmetres α i β es configuren a config.py.
"""
 
import numpy as np
from usuari import TEMES
import config
 
 
def generar_videos(n):
    """
    Genera un catàleg de n vídeos amb atributs aleatoris.
 
    La temàtica s'assigna amb distribució uniforme entre les quatre categories.
    Els atributs emocio i qualitat es generen amb distribució Beta(α, β)
    definida a config.py, que produeix una distribució en forma de campana
    centrada a 0.5, més representativa de contingut real que la uniforme.
 
    Args:
        n (int): nombre de vídeos a generar.
 
    Returns:
        list[dict]: llista de vídeos.
    """
    videos = []
    for i in range(n):
        video = {
            "id":      i,
            "tema":    np.random.choice(TEMES),
            "emocio":  float(np.random.beta(config.BETA_EMOCIO_A,
                                            config.BETA_EMOCIO_B)),
            "qualitat": float(np.random.beta(config.BETA_QUALITAT_A,
                                             config.BETA_QUALITAT_B))
        }
        videos.append(video)
    return videos