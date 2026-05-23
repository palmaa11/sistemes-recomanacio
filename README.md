# Simulador de Sistemes de Recomanació — TFG

Treball de Final de Grau (GEINF) — Universitat de Girona, 2026  
**Autor:** Aleix Palmada Teixidor

## Descripció

Simulador en Python que reprodueix el comportament dels algorismes de recomanació de plataformes de vídeo curt (TikTok, Instagram Reels, YouTube Shorts) i compara tres models:

- **Model Engagement** — replica la lògica comercial optimitzant la interacció
- **Model Ètic** — incorpora criteris de diversitat i penalitza la repetició recent
- **Model Aleatori** — referència neutra (baseline)

El projecte demostra que la formació de cambres d'eco és una conseqüència estructural dels sistemes orientats a engagement, i que és possible mantenir la personalització garantint diversitat informativa.

## Estructura del projecte
├── config.py                  # Hiperparàmetres centralitzats (SEED, TOP_K, EXPLORACIO...)
├── contingut.py               # Generació del catàleg de vídeos sintètics
├── usuari.py                  # Modelatge i actualització de perfils d'usuari
├── models.py                  # Els tres models de recomanació
├── simulacio.py               # Motor de simulació (un usuari / multi-usuari)
├── metriques.py               # Entropy, concentració, índex de Gini, tests estadístics
├── visualitzacio.py           # Generació de figures PNG
├── exportacio.py              # Exportació de resultats a CSV
├── analisi_sensibilitat.py    # Anàlisi de sensibilitat de TOP_K i EXPLORACIO
├── main.py                    # Punt d'entrada principal
└── resultats/                 # Figures PNG i fitxers CSV generats
## Requisits

- Python 3.8 o superior
- NumPy, Matplotlib, Pandas

```bash
pip install numpy matplotlib pandas
```

## Execució

**Simulació principal:**
```bash
python main.py
```
Genera 11 figures PNG i 4 fitxers CSV a la carpeta `resultats/`.

**Anàlisi de sensibilitat:**
```bash
python analisi_sensibilitat.py
```
Genera 2 figures i 1 CSV addicionals a `resultats/`.

## Resultats principals (50 usuaris, SEED=42)

| Mètrica | Engagement | Ètic | Aleatori |
|---|---|---|---|
| Entropy norm. | 0.003 ± 0.014 | 0.926 ± 0.015 | 0.932 ± 0.031 |
| Concentració | 0.995 ± 0.004 | 0.163 ± 0.016 | 0.205 ± 0.040 |
| Índex de Gini | 0.899 ± 0.004 | 0.257 ± 0.033 | 0.289 ± 0.064 |
