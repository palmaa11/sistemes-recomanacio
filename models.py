"""
models.py — Funcions de scoring dels models de recomanació.

Conté tres models:
  - score_engagement : replica el comportament de les xarxes socials comercials
  - score_etic       : model alternatiu que incorpora diversitat i penalitza repeticions
  - score_aleatori   : baseline de referència (selecció aleatòria)

Nota: tot el codi usa np.random per garantir que la llavor fixada a config.py
(np.random.seed) controla completament l'aleatorietat del sistema, assegurant
la reproductibilitat total dels resultats.
"""

import numpy as np
from collections import Counter
import config

# ── Paràmetres globals ───────────────────────────────────────────────────────
FINESTRA_RECENT = 5   # nombre d'interaccions recents que es consideren


# ── Funcions auxiliars ───────────────────────────────────────────────────────

def comptar_temes_recents(user, finestra=FINESTRA_RECENT):
    """Retorna un Counter amb els temes apareguts en les darreres 'finestra'
    interaccions de l'historial de l'usuari."""
    historial_recent = user["historial"][-finestra:]
    temes = [h["tema"] for h in historial_recent]
    return Counter(temes)


# ── Models de scoring ────────────────────────────────────────────────────────

def score_engagement(user, video):
    """
    Model orientat a maximitzar l'engagement.

    Combina la preferència de l'usuari pel tema del vídeo,
    l'impacte emocional i la qualitat. Tendeix a reforçar
    les preferències existents (feedback loop positiu).

    Pesos:
        0.50 · preferència_tema  +  0.30 · emoció  +  0.20 · qualitat
    """
    tema_score = user["preferencies"][video["tema"]]
    emocio     = video["emocio"]
    qualitat   = video["qualitat"]
    return 0.50 * tema_score + 0.30 * emocio + 0.20 * qualitat 


def score_etic(user, video):
    """
    Model ètic millorat.

    Introdueix tres mecanismes per contrarestar la concentració:
      1. Diversitat global  : penalitza temes amb preferència molt alta.
      2. Penalització per repetició recent : redueix el score si el tema
         ha aparegut molt en les darreres FINESTRA_RECENT iteracions.
      3. Qualitat intrínseca : premia contingut de qualitat independentment
         de la preferència.

    Nota sobre el disseny dels pesos:
        La combinació de tema_score (0.25) i diversitat_global (0.35)
        és deliberada: cap dels dos domina, cosa que crea un efecte de
        moderació. Un tema molt preferit (tema_score ≈ 1) obté
        diversitat_global ≈ 0, i viceversa, evitant extrems.

    Pesos finals:
        0.25 · tema_score  +  0.35 · (1 - tema_score)
        + 0.30 · qualitat  -  0.40 · penalització_repetició
    """
    tema       = video["tema"]
    tema_score = user["preferencies"][tema]
    qualitat   = video["qualitat"]

    diversitat_global      = 1 - tema_score
    temes_recents          = comptar_temes_recents(user)
    repeticions_recents    = temes_recents.get(tema, 0)
    penalitzacio_repeticio = repeticions_recents / FINESTRA_RECENT

    score = (  
        0.25 * tema_score
        + 0.35 * diversitat_global
        + 0.30 * qualitat
        - 0.40 * penalitzacio_repeticio
    )
    return score


def score_aleatori(user, video):
    """
    Model baseline: assigna un score aleatori uniforme a cada vídeo.

    Serveix com a punt de referència neutre per demostrar que:
      - El model engagement genera MÉS concentració que l'atzar.
      - El model ètic s'aproxima a la diversitat màxima sense ser aleatori.
    """
    return np.random.random()


# ── Selectors de vídeo ───────────────────────────────────────────────────────

def seleccionar_video_engagement(scored): 
    """Selecciona sempre el vídeo amb el score màxim (greedy)."""
    scored.sort(key=lambda x: x[1], reverse=True) 
    return scored[0][0]


def seleccionar_video_etic(scored):
    """
    Selecciona entre els TOP_K millors vídeos de forma ponderada.

    Amb probabilitat EXPLORACIO escull aleatòriament dins el top-k
    (exploració). Amb probabilitat 1-EXPLORACIO fa una selecció
    estocàstica proporcional als scores (explotació suavitzada).
    """
    scored.sort(key=lambda x: x[1], reverse=True)
    top_k = scored[:config.TOP_K]

    if np.random.random() < config.EXPLORACIO:
        idx = np.random.randint(len(top_k))
        return top_k[idx][0]

    scores = [max(0.01, s[1]) for s in top_k]
    total  = sum(scores)
    probs  = [s / total for s in scores]
    index  = np.random.choice(range(len(top_k)), p=probs)
    return top_k[index][0]


def seleccionar_video_aleatori(scored):
    """Selecciona un vídeo uniformement a l'atzar (ignora els scores)."""
    idx = np.random.randint(len(scored))
    return scored[idx][0]