"""
exportacio.py — Exportació dels resultats a CSV per a anàlisi externa.

Genera fitxers CSV a la carpeta 'resultats/' amb:
  - resultats_un_usuari.csv   : mètriques detallades de la simulació principal
  - resultats_multi_usuari.csv: mètriques per usuari en la simulació massiva
  - resum_models.csv          : taula comparativa resum per als tres models
"""

import os
import csv
import numpy as np

OUTPUT_DIR = "resultats"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def exportar_un_usuari(historials, temes_per_model, metriques_per_model):
    """
    Exporta les mètriques de la simulació d'un sol usuari.

    Args:
        historials        (dict): {nom_model: llista_snapshots_preferencies}
        temes_per_model   (dict): {nom_model: llista_temes}
        metriques_per_model(dict): {nom_model: dict_metriques}
    """
    # ── Evolució de preferències per iteració ────────────────────────────────
    from usuari import TEMES
    path = os.path.join(OUTPUT_DIR, "resultats_evolucio.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "iteracio"] + TEMES)
        for nom, hist in historials.items():
            for i, snap in enumerate(hist):
                w.writerow([nom, i] + [snap[t] for t in TEMES])
    print(f"  → CSV desat: {path}")

    # ── Mètriques resum d'un usuari ──────────────────────────────────────────
    path2 = os.path.join(OUTPUT_DIR, "resultats_un_usuari.csv")
    with open(path2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "entropy", "entropy_norm", "concentracio",
                    "gini", "tema_dominant"] + TEMES)
        for nom, m in metriques_per_model.items():
            dist = m["distribucio"]
            w.writerow([nom, m["entropy"], m["entropy_norm"],
                        m["concentracio"], m["gini"], m["tema_dominant"]]
                       + [dist.get(t, 0) for t in TEMES])
    print(f"  → CSV desat: {path2}")


def exportar_multi_usuari(resultats_per_model):
    """
    Exporta les mètriques de tots els usuaris per a cada model.

    Args:
        resultats_per_model (dict): {nom_model: llista_de_dicts_metriques}
    """
    from usuari import TEMES
    path = os.path.join(OUTPUT_DIR, "resultats_multi_usuari.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "usuari_id", "entropy", "entropy_norm",
                    "concentracio", "gini", "tema_dominant"] + TEMES)
        for nom, resultats in resultats_per_model.items():
            for i, m in enumerate(resultats):
                dist = m["distribucio"]
                w.writerow([nom, i, m["entropy"], m["entropy_norm"],
                            m["concentracio"], m["gini"], m["tema_dominant"]]
                           + [dist.get(t, 0) for t in TEMES])
    print(f"  → CSV desat: {path}")


def exportar_resum(resultats_per_model):
    """
    Exporta la taula comparativa resum (mitjana ± std) per a tots els models.

    Args:
        resultats_per_model (dict): {nom_model: llista_de_dicts_metriques}
    """
    path = os.path.join(OUTPUT_DIR, "resum_models.csv")
    metriques_keys = ["entropy", "entropy_norm", "concentracio", "gini"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        capçalera = ["model"]
        for mk in metriques_keys:
            capçalera += [f"{mk}_mitj", f"{mk}_std"]
        w.writerow(capçalera)

        for nom, resultats in resultats_per_model.items():
            fila = [nom]
            for mk in metriques_keys:
                valors = [r[mk] for r in resultats]
                fila += [round(np.mean(valors), 4), round(np.std(valors), 4)]
            w.writerow(fila)
    print(f"  → CSV desat: {path}")