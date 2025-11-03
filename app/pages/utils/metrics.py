from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Weights:
    w_D: float = 0.50
    w_AM: float = 0.25
    w_S: float = 0.15
    w_AF: float = 0.10

@dataclass
class Params:
    alpha1: float = 0.05
    alpha2: float = 0.25
    c3: float = 0.30
    c4: float = 0.60
    p3: float = 1.6
    p4: float = 1.6
    mQS_min: float = 0.85
    mQS_max: float = 1.25

def clip(x, lo=0, hi=10): return max(lo, min(hi, x))

def f_D(D, p):
    if D <= 3.5: return p.alpha1 * D
    f1 = p.alpha1 * 3.5
    if D <= 6: return f1 + p.alpha2 * (D - 3.5)
    f2 = f1 + p.alpha2 * (6 - 3.5)
    if D <= 10: return f2 + p.c3 * (D - 6)**p.p3
    f3 = f2 + p.c3 * (10 - 6)**p.p.p3
    return f3 + p.c4 * (D - 10)**p.p4

def score_fatigue(D, QS, AM, S, AF, A, weights=Weights(), params=Params()):
    m_QS = max(params.mQS_min, min(params.mQS_max, 1.25 - 0.04 * QS))
    m_A = 0.85 + 0.065 * A
    mS_D = 1 + 0.30 * (10 - S) / 10
    mS_AM = 1 + 0.20 * (10 - S) / 10
    PD_base = f_D(D, params)
    P_D = PD_base * m_QS * m_A * mS_D
    P_AM = (10 - AM) * mS_AM
    P_S = (10 - S)
    P_AF = (10 - AF)
    total_penalty = (
        weights.w_D * P_D +
        weights.w_AM * P_AM +
        weights.w_S * P_S +
        weights.w_AF * P_AF
    )
    return clip(10 - total_penalty)

def motivometro(EB, AUT, EMO, CLA, REL, APO, REC, VAL, PRO):
    w = dict(EB=0.05, AUT=0.15, EMO=0.10, CLA=0.15, REL=0.15,
             APO=0.10, REC=0.10, VAL=0.10, PRO=0.10)
    g_tarea = (REL * CLA) / 100.0
    g_ident = (VAL * PRO) / 100.0
    bonus = min(0.5 * g_tarea + 0.5 * g_ident, 1.0)
    base = sum([
        EB * w['EB'], AUT * w['AUT'], EMO * w['EMO'], CLA * w['CLA'],
        REL * w['REL'], APO * w['APO'], REC * w['REC'], VAL * w['VAL'], PRO * w['PRO']
    ])
    return clip(base + bonus)