#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validador e normalizador de URLs GitHub para conectores com formato estrito.

Objetivo:
1. Detectar URLs inválidas para abertura de repositórios/paths.
2. Extrair owner, repo, branch e path quando possível.
3. Sugerir uma URL canônica no formato:
   https://github.com/{owner}/{repo}/tree/{branch}/{path}

Uso:
    python github_url_validator.py "https://github.com/openai/codex/tree/main/docs"

Saída:
    JSON estruturado com status, tipo da URL, componentes e sugestão.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlparse, parse_qs


GITHUB_HOSTS = {"github.com", "www.github.com"}


@dataclass
class GitHubURLAnalysis:
    input_url: str
    is_github: bool
    classification: str
    owner: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None
    path: Optional[str] = None
    is_valid_for_strict_connector: bool = False
    canonical_url: Optional[str] = None
    reason: Optional[str] = None
    search_query_hint: Optional[str] = None


def _normalize_path(path: str) -> str:
    return re.sub(r"/+", "/", path.strip())


def analyze_github_url(url: str) -> GitHubURLAnalysis:
    parsed = urlparse(url)

    if parsed.netloc not in GITHUB_HOSTS:
        return GitHubURLAnalysis(
            input_url=url,
            is_github=False,
            classification="non_github_url",
            reason="Host não é github.com"
        )

    path = _normalize_path(parsed.path)
    parts = [p for p in path.split("/") if p]

    # Caso 1: URL de busca
    if parts and parts[0] in {"search", "repos"}:
        qs = parse_qs(parsed.query)
        query = qs.get("q", [None])[0]
        return GitHubURLAnalysis(
            input_url=url,
            is_github=True,
            classification="search_url",
            is_valid_for_strict_connector=False,
            reason="URL de busca não é aceita como URL canônica de repositório",
            search_query_hint=query
        )

    # Caso 2: formato owner/repo/tree/branch/path...
    if len(parts) >= 4 and parts[2] == "tree":
        owner = parts[0]
        repo = parts[1]
        branch = parts[3]
        subpath = "/".join(parts[4:]) if len(parts) > 4 else ""
        canonical = f"https://github.com/{owner}/{repo}/tree/{branch}/"
        if subpath:
            canonical += subpath

        return GitHubURLAnalysis(
            input_url=url,
            is_github=True,
            classification="repo_tree_url",
            owner=owner,
            repo=repo,
            branch=branch,
            path=subpath,
            is_valid_for_strict_connector=True,
            canonical_url=canonical,
            reason="URL compatível com conector estrito"
        )

    # Caso 3: owner/repo sem tree
    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1]
        suggested = f"https://github.com/{owner}/{repo}/tree/main/"
        return GitHubURLAnalysis(
            input_url=url,
            is_github=True,
            classification="repo_root_url",
            owner=owner,
            repo=repo,
            is_valid_for_strict_connector=False,
            canonical_url=suggested,
            reason="Repositório identificado, mas falta /tree/{branch}/{path}"
        )

    return GitHubURLAnalysis(
        input_url=url,
        is_github=True,
        classification="unknown_github_url",
        is_valid_for_strict_connector=False,
        reason="Formato GitHub não reconhecido para resolução segura"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            json.dumps(
                {
                    "error": "Uso: python github_url_validator.py <github_url>"
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    url = argv[1]
    analysis = analyze_github_url(url)
    print(json.dumps(asdict(analysis), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
