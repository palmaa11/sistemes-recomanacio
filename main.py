"""
main.py — Punt d'entrada principal del simulador.
 
Executa la simulació completa:
  1. Simulació d'un sol usuari (3 models)
  2. Simulació de múltiples usuaris (3 models)
  3. Exportació de resultats a CSV
  4. Generació de totes les figures
 
Ús:
    python main.py
"""
 
import copy
import numpy as np

# ── Configuració ─────────────────────────────────────────────────────────────
import config
np.random.seed(config.SEED)  
 
# ── Mòduls del projecte ───────────────────────────────────────────────────────
from contingut      import generar_videos
from usuari         import crear_usuari
from simulacio      import simular, simular_multiples_usuaris, simular_multiples_usuaris_temes
from metriques      import calcular_metriques, tests_estadistics
from exportacio     import exportar_un_usuari, exportar_multi_usuari, exportar_resum
import visualitzacio as viz
 
from models import (
    score_engagement,    seleccionar_video_engagement,
    score_etic,          seleccionar_video_etic,
    score_aleatori,      seleccionar_video_aleatori
)
 
# ── Definició dels models ─────────────────────────────────────────────────────
MODELS = {
    "Engagement": (score_engagement, seleccionar_video_engagement),
    "Ètic":       (score_etic,       seleccionar_video_etic),
    "Aleatori":   (score_aleatori,   seleccionar_video_aleatori)
}
 
 
def main():
    print("=" * 60)
    print("  SIMULADOR DE SISTEMES DE RECOMANACIÓ — TFG")
    print("=" * 60)
 
    # ── Generació de dades compartides ────────────────────────────────────────
    videos     = generar_videos(config.NUM_VIDEOS)
    usuari_base = crear_usuari()
 
    # ────────────────────────────────────────────────────────────────────────
    # BLOC 1 — Simulació d'un sol usuari
    # ────────────────────────────────────────────────────────────────────────
    print("\n[1/3] Simulació d'un sol usuari...")
 
    historials         = {}
    temes_per_model    = {}
    metriques_per_model = {}
 
    for nom, (score_fn, selector_fn) in MODELS.items():
        usuari = copy.deepcopy(usuari_base)
        hist, temes = simular(score_fn, videos, usuari, selector_fn)
        m = calcular_metriques(temes)
 
        historials[nom]          = hist
        temes_per_model[nom]     = temes
        metriques_per_model[nom] = m
 
        print(f"\n  ── Model {nom} ──")
        print(f"     Distribució    : { {k: round(v,3) for k,v in m['distribucio'].items()} }")
        print(f"     Entropy        : {m['entropy']:.4f} bits  "
              f"(norm. {m['entropy_norm']:.4f})")
        print(f"     Concentració   : {m['concentracio']:.4f}")
        print(f"     Gini           : {m['gini']:.4f}")
        print(f"     Tema dominant  : {m['tema_dominant']}")
 
    # ────────────────────────────────────────────────────────────────────────
    # BLOC 2 — Simulació de múltiples usuaris
    # ────────────────────────────────────────────────────────────────────────
    print(f"\n[2/3] Simulació de {config.NUM_USUARIS} usuaris per model...")
 
    resultats_multi = {}
    for nom, (score_fn, selector_fn) in MODELS.items():
        resultats = simular_multiples_usuaris(
            config.NUM_USUARIS, score_fn, videos,
            selector_fn, calcular_metriques
        )
        resultats_multi[nom] = resultats
 
        entropies      = [r["entropy_norm"]  for r in resultats]
        concentracions = [r["concentracio"]  for r in resultats]
        ginis          = [r["gini"]          for r in resultats]
 
        print(f"\n  ── Model {nom} ({config.NUM_USUARIS} usuaris) ──")
        print(f"     Entropy norm.  : {np.mean(entropies):.4f} "
              f"± {np.std(entropies):.4f}")
        print(f"     Concentració   : {np.mean(concentracions):.4f} "
              f"± {np.std(concentracions):.4f}")
        print(f"     Gini           : {np.mean(ginis):.4f} "
              f"± {np.std(ginis):.4f}")
 
    # ────────────────────────────────────────────────────────────────────────
    # BLOC 2b — Tests estadístics (Mann-Whitney U)
    # ────────────────────────────────────────────────────────────────────────
    print("\n[Tests estadístics Mann-Whitney U]")
    tests = tests_estadistics(resultats_multi)
    for metrica, comparacions in tests.items():
        print(f"\n  {metrica}:")
        for parell, res in comparacions.items():
            print(f"    {parell:35s}  U={res['U']:7.1f}  p={res['p']:.4f}  {res['sig']}")

    # ────────────────────────────────────────────────────────────────────────
    # BLOC 3 — Exportació i visualització
    # ────────────────────────────────────────────────────────────────────────
    print("\n[3/3] Exportant resultats i generant figures...")
 
    # CSV
    exportar_un_usuari(historials, temes_per_model, metriques_per_model)
    exportar_multi_usuari(resultats_multi)
    exportar_resum(resultats_multi)
 
    # Figures
    distribucions = {nom: metriques_per_model[nom]["distribucio"]
                     for nom in MODELS}
    viz.plot_evolucio_preferencies(historials)
    viz.plot_distribucio_temes(distribucions)
    # L'Engagement s'exclou dels histogrames comparatius: el seu valor extrem
    # (entropy ≈ 0, concentracio ≈ 1) aplasta visualment Ètic i Aleatori,
    # que son els models d'interès per a la comparació.
    resultats_sense_engagement = {k: v for k, v in resultats_multi.items()
                                  if k != "Engagement"}
    viz.plot_histogrames_multiusuari(resultats_sense_engagement, "entropy_norm",
                                     "Distribució de l'entropy normalitzada",
                                     "Entropy norm.")
    viz.plot_histogrames_multiusuari(resultats_sense_engagement, "concentracio",
                                     "Distribució de la concentració",
                                     "Concentració")
    viz.plot_histogrames_multiusuari(resultats_sense_engagement, "gini",
                                     "Distribució de l'índex de Gini",
                                     "Índex de Gini")
    viz.plot_resum_comparatiu(resultats_multi)

    temes_multi_per_model = {
        nom: simular_multiples_usuaris_temes(
            config.NUM_USUARIS, score_fn, videos, selector_fn
        )
        for nom, (score_fn, selector_fn) in MODELS.items()
    }
    viz.plot_evolucio_entropy(temes_multi_per_model)
 
    print("\n" + "=" * 60)
    print("  Simulació completada. Resultats a la carpeta 'resultats/'")
    print("=" * 60)
 
 
if __name__ == "__main__":
    main()