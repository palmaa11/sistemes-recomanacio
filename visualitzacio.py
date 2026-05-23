"""
visualitzacio.py — Generació de totes les gràfiques del projecte.

Genera i desa (en PNG) les figures necessàries per a la memòria del TFG:
  1. Evolució de preferències (per model)
  2. Distribució de temes (per model)
  3. Distribució d'entropy (multi-usuari)
  4. Distribució de concentració (multi-usuari)
  5. Distribució de Gini (multi-usuari)
  6. Anàlisi de sensibilitat dels hiperparàmetres
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

from usuari import TEMES

# ── Directori de sortida ──────────────────────────────────────────────────────
OUTPUT_DIR = "resultats"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS_TEMES = {
    "esport":      "#E63946",
    "politica":    "#457B9D",
    "humor":       "#F4A261",
    "tecnologia":  "#2A9D8F",
    "ciencia":     "#8338EC",
    "cultura":     "#FB5607",
    "salut":       "#06D6A0",
    "economia":    "#118AB2",
    "viatges":     "#FFD166",
    "moda":        "#EF476F",
}

COLORS_MODELS = {
    "Engagement": "#E63946",
    "Ètic":       "#2A9D8F",
    "Aleatori":   "#8338EC"
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _desa(nom):
    path = os.path.join(OUTPUT_DIR, nom)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  → Figura desada: {path}")
    plt.close()


# ── Figura 1: Evolució de preferències ───────────────────────────────────────

def plot_evolucio_preferencies(historials_per_model):
    """
    Genera una figura independent per a cada model amb l'evolució de les
    preferències per tema al llarg de les iteracions.

    Args:
        historials_per_model (dict): {nom_model: llista_de_snapshots}
    """
    for nom, hist in historials_per_model.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        for tema in TEMES:
            values = [h[tema] for h in hist]
            ax.plot(values, label=tema,
                    color=COLORS_TEMES[tema], linewidth=2)
        ax.set_title(f"Evolució de les preferències per tema — Model {nom}",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Iteració")
        ax.set_ylabel("Preferència")
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        nom_fitxer = f"fig1_evolucio_preferencies_{nom.replace(' ', '_')}.png"
        _desa(nom_fitxer)


# ── Figura 2: Distribució de temes ───────────────────────────────────────────

def plot_distribucio_temes(distribucions_per_model):
    """
    Genera una figura independent per a cada model amb la distribució
    final de temes en forma de gràfic de barres.

    Args:
        distribucions_per_model (dict): {nom_model: dict_distribucio}
    """
    ref = 1 / len(TEMES)
    for nom, dist in distribucions_per_model.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        valors = [dist.get(t, 0) for t in TEMES]
        bars   = ax.bar(TEMES, valors,
                        color=[COLORS_TEMES[t] for t in TEMES],
                        edgecolor="white", linewidth=0.8)
        ax.set_title(f"Distribució final de temes — Model {nom}",
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Tema")
        ax.set_ylabel("Proporció")
        ax.set_ylim(0, 1)
        ax.tick_params(axis="x", rotation=45)
        ax.axhline(ref, color="gray", linestyle="--",
                   linewidth=1, label="Distribució uniforme")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis="y")
        for bar, v in zip(bars, valors):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + 0.02, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        nom_fitxer = f"fig2_distribucio_temes_{nom.replace(' ', '_')}.png"
        _desa(nom_fitxer)


# ── Figura 3: Histogrames multi-usuari ───────────────────────────────────────

def plot_histogrames_multiusuari(resultats_per_model, metrica, titol, xlabel):
    """
    Histogrames superposats de la mètrica indicada per a múltiples models.

    Args:
        resultats_per_model (dict): {nom_model: llista_de_dicts_metriques}
        metrica (str): clau del dict de mètriques a representar
        titol   (str): títol del gràfic
        xlabel  (str): etiqueta de l'eix X
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    for nom, resultats in resultats_per_model.items():
        valors = [r[metrica] for r in resultats]
        mu     = np.mean(valors)
        sigma  = np.std(valors)
        ax.hist(valors, alpha=0.6, bins=12,
                color=COLORS_MODELS.get(nom, "gray"),
                label=f"{nom}  μ={mu:.3f} ± {sigma:.3f}",
                edgecolor="white")

    ax.set_title(titol, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Nombre d'usuaris")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    nom_fitxer = f"fig_{metrica}_multiusuari.png"
    _desa(nom_fitxer)


# ── Figura 4: Resum comparatiu de mètriques ──────────────────────────────────

def plot_resum_comparatiu(resultats_per_model):
    """
    Gràfic de barres horitzontals amb la mitjana ± std de les principals
    mètriques per a cada model, facilitant la comparació global.
    """
    metriques_keys  = ["entropy_norm", "concentracio", "gini"]
    metriques_noms  = ["Entropy norm.", "Concentració", "Índex de Gini"]
    models          = list(resultats_per_model.keys())
    n_metriques     = len(metriques_keys)
    n_models        = len(models)
    x               = np.arange(n_metriques)
    amplada         = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, nom in enumerate(models):
        resultats = resultats_per_model[nom]
        medies    = [np.mean([r[m] for r in resultats]) for m in metriques_keys]
        stds      = [np.std([r[m]  for r in resultats]) for m in metriques_keys]
        offset    = (i - n_models / 2 + 0.5) * amplada
        bars      = ax.bar(x + offset, medies, amplada,
                           yerr=stds, capsize=4,
                           color=COLORS_MODELS.get(nom, "gray"),
                           label=nom, alpha=0.85, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(metriques_noms, fontsize=11)
    ax.set_ylabel("Valor mitjà")
    ax.set_ylim(0, 1.15)
    ax.set_title("Comparació global de mètriques (mitjana ± desv. típica)",
                 fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    _desa("fig_resum_comparatiu.png")


# ── Figura 5: Evolució de l'entropy del feed ──────────────────────────────────

def plot_evolucio_entropy(temes_per_model_multi):
    """
    Mostra l'evolució de l'entropy normalitzada acumulada del feed al llarg
    de les iteracions, com a mitjana ± desviació típica sobre tots els usuaris.

    Permet visualitzar si el model Engagement col·lapsa progressivament cap
    a una sola temàtica mentre el model Ètic manté diversitat, amb la banda
    d'incertesa demostrant que el resultat és robust i no un cas aïllat.

    Args:
        temes_per_model_multi (dict): {nom_model: llista_de_seqüències_per_usuari}
    """
    from metriques import calcular_distribucio, calcular_entropy, entropy_maxima

    max_ent = entropy_maxima()
    fig, ax = plt.subplots(figsize=(9, 4))

    for nom, llista_temes in temes_per_model_multi.items():
        n_iter = len(llista_temes[0])
        matriu = np.array([
            [calcular_entropy(calcular_distribucio(temes[:i + 1])) / max_ent
             for i in range(n_iter)]
            for temes in llista_temes
        ])
        mitj  = matriu.mean(axis=0)
        std   = matriu.std(axis=0)
        x     = range(1, n_iter + 1)
        color = COLORS_MODELS.get(nom, "gray")
        ax.plot(x, mitj, label=nom, color=color, linewidth=2)
        ax.fill_between(x, mitj - std, mitj + std, alpha=0.2, color=color)

    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1,
               label="Màxim teòric (distribució uniforme)")
    n_usuaris = len(next(iter(temes_per_model_multi.values())))
    ax.set_title(f"Evolució de l'entropy del feed (mitjana ± desv. típica, n={n_usuaris})",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Iteració")
    ax.set_ylabel("Entropy normalitzada")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    _desa("fig_evolucio_entropy.png")