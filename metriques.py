"""
metriques.py — Càlcul de mètriques quantitatives de diversitat.

Mètriques principals:
  - Distribució de temes   : proporció de cada tema en el feed
  - Entropy de Shannon     : mesura de diversitat [0, log2(N_temes)]
  - Concentració (max)     : pes del tema dominant [0, 1]
  - Índex de Gini          : desigualtat en la distribució [0, 1]
"""

import math
from collections import Counter
from itertools import combinations
from scipy.stats import mannwhitneyu
from usuari import TEMES


# ── Distribució ──────────────────────────────────────────────────────────────

def calcular_distribucio(temes):
    """
    Calcula la distribució normalitzada dels temes mostrats.

    Returns:
        dict {tema: proporció}  — suma = 1.0
    """
    counter = Counter(temes)
    total   = len(temes)
    return {k: v / total for k, v in counter.items()}


# ── Entropy de Shannon ───────────────────────────────────────────────────────

def calcular_entropy(distribucio):    
    """
    Calcula l'entropy de Shannon de la distribució (en bits).

    Interpretació:
      - entropy = 0          → un sol tema (concentració total)
      - entropy = log2(n)    → distribució completament uniforme
      - Per 10 temes, màxim = log2(10) = 2.0 bits

    Args:
        distribucio (dict): {tema: proporció}

    Returns:
        float: entropy en bits
    """
    entropy = 0.0
    for p in distribucio.values():
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def entropy_maxima():
    """Retorna l'entropy màxima possible per al nombre de temes definits."""
    return math.log2(len(TEMES))


# ── Concentració ─────────────────────────────────────────────────────────────

def concentracio(distribucio):  
    """
    Retorna la proporció del tema dominant (màxim de la distribució).

    Valors propers a 1 indiquen alta concentració (efecte cambra d'eco).
    """
    return max(distribucio.values()) if distribucio else 0.0


def tema_dominant(distribucio):
    """Retorna el nom del tema amb major proporció."""
    return max(distribucio, key=distribucio.get) if distribucio else None


# ── Índex de Gini ────────────────────────────────────────────────────────────

def gini(distribucio):   
    """
    Calcula l'índex de Gini de la distribució de temes.

    El Gini mesura la desigualtat de la distribució:
      - Gini = 0 → distribució perfectament uniforme
      - Gini = 1 → un sol tema rep tota l'atenció

    Complementa l'entropy permetent una validació creuada de la diversitat.
    """
    valors = sorted(distribucio.get(t, 0.0) for t in TEMES)
    n      = len(valors)
    if n == 0 or sum(valors) == 0:
        return 0.0
    numerador = sum((2 * (i + 1) - n - 1) * v
                    for i, v in enumerate(valors))
    return numerador / (n * sum(valors))


# ── Funció resum ─────────────────────────────────────────────────────────────

def _significancia(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return "ns"


def tests_estadistics(resultats_per_model):   
    """
    Tests de Mann-Whitney U entre tots els parells de models.

    No assumeix normalitat, adequat per a distribucions de mètriques simulades.
    Compara entropy_norm, concentracio i gini.

    Returns:
        dict {metrica: {parell: {"U": float, "p": float, "sig": str}}}
    """
    metriques = ["entropy_norm", "concentracio", "gini"]
    models    = list(resultats_per_model.keys())
    out       = {}

    for metrica in metriques:
        out[metrica] = {}
        for m1, m2 in combinations(models, 2):
            v1 = [r[metrica] for r in resultats_per_model[m1]]
            v2 = [r[metrica] for r in resultats_per_model[m2]]
            stat, p = mannwhitneyu(v1, v2, alternative="two-sided")
            out[metrica][f"{m1} vs {m2}"] = {
                "U":   round(stat, 1),
                "p":   round(p, 4),
                "sig": _significancia(p)
            }

    return out


def calcular_metriques(temes):
    """
    Calcula totes les mètriques per a una llista de temes mostrats.

    Args:
        temes (list[str]): seqüència de temes del feed simulat.

    Returns:
        dict amb:
          distribucio, entropy, entropy_norm, concentracio,
          tema_dominant, gini
    """
    dist  = calcular_distribucio(temes)
    ent   = calcular_entropy(dist)
    ent_n = ent / entropy_maxima() if entropy_maxima() > 0 else 0.0

    return {
        "distribucio":    dist,
        "entropy":        round(ent,   4),
        "entropy_norm":   round(ent_n, 4),   # [0,1] per facilitar comparació
        "concentracio":   round(concentracio(dist), 4),
        "tema_dominant":  tema_dominant(dist),
        "gini":           round(gini(dist), 4)
    }
