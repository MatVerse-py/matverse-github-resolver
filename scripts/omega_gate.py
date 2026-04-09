#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MATVERSE Ω-GATE (Completo)
Governança | Admissibilidade | Decisão

Implementa o operador Ω completo do ecossistema MatVerse:
Ω = 0.4*Ψ + 0.3*Θ^ + 0.2*(1-CVaR) + 0.1*PoLE
"""

def compute_omega(psi: float, theta: float = 50.0, cvar: float = 0.01, pole: int = 1) -> float:
    """
    Calcula o score Ω baseado nos quatro pilares de confiança.
    
    Args:
        psi (float): Confiança intrínseca (0.0 a 1.0).
        theta (float): Temperatura/Incerteza (0 a 100).
        cvar (float): Conditional Value at Risk (0.0 a 1.0).
        pole (int): Polaridade/Alinhamento (0 ou 1).
    """
    # Normalização de Theta (Θ^)
    theta_hat = 1 / (1 + theta / 100.0)

    # Cálculo ponderado
    omega = (
        0.4 * psi +
        0.3 * theta_hat +
        0.2 * (1.0 - cvar) +
        0.1 * pole
    )
    
    return min(1.0, max(0.0, omega))


def omega_decision(omega: float, psi: float, cvar: float, threshold: float = 0.85) -> str:
    """
    Determina a decisão constitucional baseada no score Ω e restrições de segurança.
    """
    # Restrições de Segurança (Fail-Closed)
    if psi < 0.85:
        return "BLOCK"

    if cvar > 0.05:
        return "BLOCK"

    # Decisão baseada no Score
    if omega >= threshold:
        return "PASS"
    
    if omega >= 0.70:
        return "CONDITIONAL"

    return "BLOCK"

if __name__ == "__main__":
    # Teste rápido
    p, t, c, l = 0.98, 10.0, 0.01, 1
    score = compute_omega(p, t, c, l)
    decision = omega_decision(score, p, c)
    print(f"Ω-Gate Test: Ψ={p}, Θ={t}, CVaR={c}, PoLE={l} -> Ω={score:.4f} [{decision}]")
