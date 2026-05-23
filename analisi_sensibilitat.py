"""
analisi_sensibilitat.py — Justificació experimental dels hiperparàmetres.

Avalua com canvien les mètriques de diversitat (entropy_norm, concentracio)
en funció dels valors de TOP_K i EXPLORACIO, justificant les eleccions
fetes a config.py.

Genera:
  - fig_sensibilitat_topk.png
  - fig_sensibilitat_exploracio.png
  - resultats/sensibilitat.csv
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import copy
import numpy as np
import matplotlib.pyplot as plt
import csv

import models as M
from usuari import crear_usuari
from contingut import generar_videos
from simulacio import simular
from metriques import calcular_metriques
import config

OUTPUT_DIR = "resultats"
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(config.SEED)

# Catàleg fix per a tots els experiments
videos_base = generar_videos(config.NUM_VIDEOS)
N_USUARIS   = 30   # usuaris per punt de la graella (equilibri velocitat/precisió)


def simular_n_usuaris_etic(top_k, exploracio, n=N_USUARIS):
    """
    Executa n simulacions amb el model ètic per uns hiperparàmetres donats.
    Retorna la mitjana i desviació típica d'entropy_norm i concentracio.
    """
    # Sobreescrivim temporalment els paràmetres globals de config
    config.TOP_K      = top_k
    config.EXPLORACIO = exploracio

    entropies     = []
    concentracions = []

    for _ in range(n):
        u = crear_usuari()
        _, temes = simular(M.score_etic, videos_base,
                           copy.deepcopy(u), M.seleccionar_video_etic)
        m = calcular_metriques(temes)
        entropies.append(m["entropy_norm"])
        concentracions.append(m["concentracio"])

    return (np.mean(entropies),   np.std(entropies),
            np.mean(concentracions), np.std(concentracions))


# ── Experiment 1: variació de TOP_K ─────────────────────────────────────────

def analisi_topk(valors_topk=None):
    if valors_topk is None:
        valors_topk = [1, 2, 3, 5, 7, 10, 15, 20]

    print("Anàlisi de sensibilitat — TOP_K")
    ent_mitj, ent_std, conc_mitj, conc_std = [], [], [], []

    for k in valors_topk:
        em, es, cm, cs = simular_n_usuaris_etic(top_k=k,
                                                 exploracio=config.EXPLORACIO)
        ent_mitj.append(em);  ent_std.append(es)
        conc_mitj.append(cm); conc_std.append(cs)
        print(f"  TOP_K={k:2d}  entropy_norm={em:.3f}±{es:.3f}  "
              f"concentracio={cm:.3f}±{cs:.3f}")

    # Restaurar el valor original abans de generar la figura
    config.TOP_K = 5

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

    ax1.errorbar(valors_topk, ent_mitj, yerr=ent_std,
                 marker="o", color="#2A9D8F", capsize=4, linewidth=2)
    ax1.axvline(config.TOP_K, color="red", linestyle="--",
                label=f"Valor escollit (TOP_K={config.TOP_K})")
    ax1.set_title("Entropy normalitzada vs TOP_K")
    ax1.set_xlabel("TOP_K"); ax1.set_ylabel("Entropy norm.")
    ax1.set_ylim(0, 1); ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.errorbar(valors_topk, conc_mitj, yerr=conc_std,
                 marker="o", color="#E63946", capsize=4, linewidth=2)
    ax2.axvline(config.TOP_K, color="red", linestyle="--",
                label=f"Valor escollit (TOP_K={config.TOP_K})")
    ax2.set_title("Concentració vs TOP_K")
    ax2.set_xlabel("TOP_K"); ax2.set_ylabel("Concentració")
    ax2.set_ylim(0, 1); ax2.legend(); ax2.grid(True, alpha=0.3)

    fig.suptitle("Sensibilitat al hiperparàmetre TOP_K",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_sensibilitat_topk.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → Figura desada: {path}")

    return valors_topk, ent_mitj, ent_std, conc_mitj, conc_std


# ── Experiment 2: variació de EXPLORACIO ────────────────────────────────────

def analisi_exploracio(valors_expl=None):
    if valors_expl is None:
        valors_expl = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0]

    print("\nAnàlisi de sensibilitat — EXPLORACIO")
    ent_mitj, ent_std, conc_mitj, conc_std = [], [], [], []

    for e in valors_expl:
        em, es, cm, cs = simular_n_usuaris_etic(top_k=config.TOP_K,
                                                 exploracio=e)
        ent_mitj.append(em);  ent_std.append(es)
        conc_mitj.append(cm); conc_std.append(cs)
        print(f"  EXPLORACIO={e:.2f}  entropy_norm={em:.3f}±{es:.3f}  "
              f"concentracio={cm:.3f}±{cs:.3f}")

    # Restaurar el valor original abans de generar la figura
    config.EXPLORACIO = 0.2

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

    ax1.errorbar(valors_expl, ent_mitj, yerr=ent_std,
                 marker="o", color="#2A9D8F", capsize=4, linewidth=2)
    ax1.axvline(config.EXPLORACIO, color="red", linestyle="--",
                label=f"Valor escollit ({config.EXPLORACIO})")
    ax1.set_title("Entropy normalitzada vs EXPLORACIO")
    ax1.set_xlabel("Taxa d'exploració"); ax1.set_ylabel("Entropy norm.")
    ax1.set_ylim(0, 1); ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.errorbar(valors_expl, conc_mitj, yerr=conc_std,
                 marker="o", color="#E63946", capsize=4, linewidth=2)
    ax2.axvline(config.EXPLORACIO, color="red", linestyle="--",
                label=f"Valor escollit ({config.EXPLORACIO})")
    ax2.set_title("Concentració vs EXPLORACIO")
    ax2.set_xlabel("Taxa d'exploració"); ax2.set_ylabel("Concentració")
    ax2.set_ylim(0, 1); ax2.legend(); ax2.grid(True, alpha=0.3)

    fig.suptitle("Sensibilitat al hiperparàmetre EXPLORACIO",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_sensibilitat_exploracio.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → Figura desada: {path}")

    return valors_expl, ent_mitj, ent_std, conc_mitj, conc_std


# ── Exportació CSV ────────────────────────────────────────────────────────────

def exportar_csv(topk_data, expl_data):
    path = os.path.join(OUTPUT_DIR, "sensibilitat.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["experiment", "parametre", "valor",
                    "entropy_norm_mitj", "entropy_norm_std",
                    "concentracio_mitj", "concentracio_std"])
        vals_k, em_k, es_k, cm_k, cs_k = topk_data
        for i, k in enumerate(vals_k):
            w.writerow(["topk", "TOP_K", k,
                        em_k[i], es_k[i], cm_k[i], cs_k[i]])
        vals_e, em_e, es_e, cm_e, cs_e = expl_data
        for i, e in enumerate(vals_e):
            w.writerow(["exploracio", "EXPLORACIO", e,
                        em_e[i], es_e[i], cm_e[i], cs_e[i]])
    print(f"  → CSV desat: {path}")


if __name__ == "__main__":
    print("=== Anàlisi de sensibilitat dels hiperparàmetres ===\n")
    topk_data = analisi_topk()
    expl_data = analisi_exploracio()
    exportar_csv(topk_data, expl_data)
    print("\nAnàlisi completada.")