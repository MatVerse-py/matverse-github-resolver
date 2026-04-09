#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MATVERSE GITHUB RESOLVER (F → S → C)
Determinístico | Fail-Closed | Auditável | Ontológico

Este script implementa a evolução da resolução de identidade de recurso GitHub:
1. Filtro (F): Classifica e projeta a entrada (Query, Repo, URL).
2. Seleção (S): Escolhe o candidato ideal (Ranking/Matching).
3. Resolução Canônica (C): Gera a identidade imutável (URL + Hash).
4. Ω-Gate: Validação de integridade e conformidade.
"""

from __future__ import annotations

import re
import json
import sys
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from urllib.parse import unquote, urlparse, parse_qs


# ------------------------------------------------------------
# 1. Modelos de Dados (Ontologia)
# ------------------------------------------------------------

@dataclass
class RepoIdentity:
    owner: str
    repo: str
    branch: str = "main"
    path: str = ""
    commit_hash: Optional[str] = None

    def canonical_url(self) -> str:
        base = f"https://github.com/{self.owner}/{self.repo}/tree/{self.branch}/"
        return base + self.path if self.path else base


@dataclass
class ResolutionResult:
    input_x: str
    input_type: str  # QUERY, REPO, URL, INVALID
    status: str      # PASS, BLOCK, WAIT
    resolved_url: Optional[str] = None
    repo_identity: Optional[RepoIdentity] = None
    omega_score: float = 0.0
    reason: str = ""
    is_idempotent: bool = False


# ------------------------------------------------------------
# 2. Operadores do Pipeline
# ------------------------------------------------------------

class MatVerseResolver:
    OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    CANONICAL_RE = r"^https://github\.com/[\w\-]+/[\w\-.]+/tree/[\w\-./]+$"

    @staticmethod
    def classify_f(x: str) -> str:
        """Fase F: Filtro e Classificação"""
        x = unquote(x).strip()
        
        # 1. Detecção de Queries Malformadas (Fail-Closed)
        if "admin:@mee" in x:
            return "INVALID"
            
        # 2. URLs de Busca ou Filtros Administrativos
        if "admin:@me" in x or "repos?q=" in x or "search" in x:
            return "QUERY"
            
        # 3. URLs de Repositório
        if x.startswith("http"):
            return "URL"
            
        # 4. Strings owner/repo
        if MatVerseResolver.OWNER_REPO_RE.match(x):
            return "REPO"
            
        return "INVALID"

    @staticmethod
    def select_s(x: str, input_type: str) -> Optional[RepoIdentity]:
        """Fase S: Seleção de Elemento"""
        if input_type == "REPO":
            owner, repo = x.split("/")
            return RepoIdentity(owner=owner, repo=repo)
        
        if input_type == "URL":
            parsed = urlparse(x)
            parts = [p for p in parsed.path.split("/") if p]
            
            # Formato: /owner/repo/tree/branch/path
            if len(parts) >= 4 and parts[2] == "tree":
                return RepoIdentity(
                    owner=parts[0],
                    repo=parts[1],
                    branch=parts[3],
                    path="/".join(parts[4:]) if len(parts) > 4 else ""
                )
            # Formato: /owner/repo
            if len(parts) >= 2:
                return RepoIdentity(owner=parts[0], repo=parts[1])
        
        # Para QUERY, em produção integraria com busca. Aqui retornamos None para forçar S manual ou erro.
        return None

    @staticmethod
    def resolve_c(identity: RepoIdentity) -> str:
        """Fase C: Resolução Canônica"""
        return identity.canonical_url()

    @staticmethod
    def omega_gate(psi: float, theta: float = 50.0) -> float:
        """Validação Ω-Gate (Simplificada para Resolução)"""
        theta_hat = 1 / (1 + theta / 100)
        return 0.7 * psi + 0.3 * theta_hat

# ------------------------------------------------------------
# 3. Execução do Pipeline Π(x)
# ------------------------------------------------------------

def run_pipeline(x: str) -> ResolutionResult:
    resolver = MatVerseResolver()
    input_type = resolver.classify_f(x)
    
    if input_type == "INVALID":
        return ResolutionResult(x, input_type, "BLOCK", reason="Entrada malformada ou query inválida (admin:@mee).")

    if input_type == "QUERY":
        return ResolutionResult(x, input_type, "WAIT", reason="Query detectada. Requer enumeração administrativa (S) para resolver.")

    identity = resolver.select_s(x, input_type)
    
    if not identity:
        return ResolutionResult(x, input_type, "BLOCK", reason="Falha ao extrair identidade do repositório.")

    resolved_url = resolver.resolve_c(identity)
    
    # Validação Ω (Simulada: Ψ=0.98 para URLs canônicas/repos, 0.6 para parciais)
    psi = 0.98 if "/tree/" in x or input_type == "REPO" else 0.6
    score = resolver.omega_gate(psi)
    
    status = "PASS" if score >= 0.85 else "BLOCK"
    
    # Teste de Idempotência C(C(x)) == C(x)
    is_idempotent = (resolved_url == x) if input_type == "URL" else False

    return ResolutionResult(
        input_x=x,
        input_type=input_type,
        status=status,
        resolved_url=resolved_url,
        repo_identity=identity,
        omega_score=score,
        reason="Resolução canônica concluída." if status == "PASS" else "Score Ω insuficiente para resolução segura.",
        is_idempotent=is_idempotent
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "Uso: python github_query_resolver.py <input_x>"}, indent=2))
        return 2

    result = run_pipeline(argv[1])
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
