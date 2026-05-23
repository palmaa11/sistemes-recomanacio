"""
simulacio.py — Motor de simulació del feed de recomanació.

Executa el bucle principal: score → selecció → interacció → actualització.
"""

import copy
from config import ITERACIONS
from usuari import interactua, actualitzar, crear_usuari


def simular(model_func, videos, user, selector_func):
    """
    Executa la simulació per a un usuari i un model donats.

    En cada iteració:
      1. Calcula el score de cada vídeo amb model_func.
      2. Selecciona el vídeo a mostrar amb selector_func.
      3. Simula la interacció de l'usuari.
      4. Actualitza les preferències i l'historial.

    Args:
        model_func   : funció de scoring (user, video) → float
        videos       : llista de vídeos disponibles
        user         : perfil d'usuari (es modifica in-place)
        selector_func: funció de selecció (scored) → video

    Returns:
        historia       (list[dict]): snapshot de preferències per iteració
        temes_mostrats (list[str]) : tema del vídeo mostrat a cada iteració
    """
    historia       = []
    temes_mostrats = []

    for _ in range(ITERACIONS):   #dese a ensenyar
        scored            = [(video, model_func(user, video)) for video in videos]
        video_seleccionat = selector_func(scored)

        temes_mostrats.append(video_seleccionat["tema"])

        inter = interactua(user, video_seleccionat)
        actualitzar(user, video_seleccionat, inter)

        historia.append(copy.deepcopy(user["preferencies"]))

    return historia, temes_mostrats


def simular_multiples_usuaris(num_usuaris, model_func, videos,
                               selector_func, metriques_func):
    """
    Executa la simulació per a múltiples usuaris independents.

    Args:
        num_usuaris   : nombre d'usuaris a simular
        model_func    : funció de scoring
        videos        : catàleg de vídeos (compartit, no modificat)
        selector_func : funció de selecció
        metriques_func: funció (temes) → dict amb les mètriques desitjades

    Returns:
        llista de dicts amb les mètriques de cada usuari
    """
    resultats = []

    for _ in range(num_usuaris):
        usuari = crear_usuari()
        _, temes = simular(model_func, videos,
                           copy.deepcopy(usuari), selector_func)  
        resultats.append(metriques_func(temes))

    return resultats


def simular_multiples_usuaris_temes(num_usuaris, model_func, videos, selector_func):
    """
    Com simular_multiples_usuaris però retorna les seqüències de temes
    de cada usuari (no les mètriques), per calcular l'evolució temporal
    de l'entropy amb banda d'incertesa.

    Returns:
        llista de llistes de temes (una per usuari)
    """
    resultats = []
    for _ in range(num_usuaris):
        usuari = crear_usuari()
        _, temes = simular(model_func, videos, copy.deepcopy(usuari), selector_func)
        resultats.append(temes)
    return resultats