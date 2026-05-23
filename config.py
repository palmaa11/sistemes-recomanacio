"""
config.py — Paràmetres globals de la simulació.
 
Centralitzar els hiperparàmetres aquí facilita l'anàlisi
de sensibilitat i la reproductibilitat dels experiments.
"""
 
# ── Reproductibilitat ────────────────────────────────────────────────────────
SEED = 42   
 
# ── Dimensions de la simulació ───────────────────────────────────────────────
NUM_VIDEOS   = 100   # mida del catàleg de continguts
ITERACIONS   = 50    # nombre d'iteracions per usuari
NUM_USUARIS  = 50    # usuaris per a la simulació multi-usuari
 
# ── Paràmetres dels models ───────────────────────────────────────────────────
# Aquests valors han estat escollits experimentalment (veure analisi_sensibilitat.py)
TOP_K      = 5    # candidats considerats pel model ètic   #segon a ensenyar
EXPLORACIO = 0.2  # taxa d'exploració aleatòria [0,1]    #tercer a ensenyar
 
# ── Distribució Beta per a la generació de contingut i preferències ──────────
# Beta(α, β) amb α=β=2 genera una distribució en forma de campana centrada
# a 0.5, més realista que la distribució uniforme.
# Valors recomanats: α=β=2 (campana suau), α=β=3 (campana més pronunciada)
BETA_EMOCIO_A    = 2   # paràmetre α de la distribució Beta per a emocio
BETA_EMOCIO_B    = 2   # paràmetre β de la distribució Beta per a emocio
BETA_QUALITAT_A  = 2   # paràmetre α de la distribució Beta per a qualitat
BETA_QUALITAT_B  = 2   # paràmetre β de la distribució Beta per a qualitat
BETA_PREF_A      = 2   # paràmetre α de la distribució Beta per a preferències
BETA_PREF_B      = 2   # paràmetre β de la distribució Beta per a preferències





