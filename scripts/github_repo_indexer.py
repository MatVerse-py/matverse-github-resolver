#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class RepoRecord:
    full_name: str
    owner: str
    repo: str
    visibility: str
    default_branch: str
    indexed: bool
    archived: bool
    canonical_url: str


def build_canonical_url(owner: str, repo: str, default_branch: str) -> str:
    branch = default_branch or "main"
    return f"https://github.com/{owner}/{repo}/tree/{branch}/"


def normalize_repo(raw: Dict[str, Any]) -> RepoRecord:
    full_name = raw.get("repository_full_name", f"{raw.get('owner', {}).get('login', 'unknown')}/{raw.get('name', 'unknown')}")
    owner = raw.get("owner", {}).get("login", "unknown")
    repo = raw.get("name", "unknown")
    visibility = raw.get("visibility", "unknown")
    default_branch = raw.get("default_branch") or "main"
    indexed = bool(raw.get("is_code_search_indexed", False))
    archived = bool(raw.get("archived", False))

    return RepoRecord(
        full_name=full_name,
        owner=owner,
        repo=repo,
        visibility=visibility,
        default_branch=default_branch,
        indexed=indexed,
        archived=archived,
        canonical_url=build_canonical_url(owner, repo, default_branch),
    )


def build_index(repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
    records = [normalize_repo(r) for r in repositories]

    return {
        "total_repositories": len(records),
        "indexed_count": sum(1 for r in records if r.indexed),
        "private_count": sum(1 for r in records if r.visibility == "private"),
        "public_count": sum(1 for r in records if r.visibility == "public"),
        "archived_count": sum(1 for r in records if r.archived),
        "repositories": [asdict(r) for r in records],
    }


def filter_indexed(records: List[RepoRecord]) -> List[RepoRecord]:
    return [r for r in records if r.indexed and not r.archived]


def group_by_owner(records: List[RepoRecord]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        out.setdefault(r.owner, []).append(asdict(r))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            json.dumps(
                {
                    "error": "Uso: python github_repo_indexer.py <caminho_para_json_repositorios>"
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    file_path = argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"Erro ao ler arquivo: {str(e)}"}, ensure_ascii=False, indent=2))
        return 1

    # Suporta tanto uma lista direta quanto um objeto com a chave "repositories"
    repos_list = data.get("repositories", data) if isinstance(data, dict) else data
    
    if not isinstance(repos_list, list):
        print(json.dumps({"error": "Formato JSON inválido. Esperado uma lista de repositórios ou um objeto com a chave 'repositories'."}, ensure_ascii=False, indent=2))
        return 1

    records = [normalize_repo(r) for r in repos_list]
    result = {
        "summary": build_index(repos_list),
        "indexed_active_by_owner": group_by_owner(filter_indexed(records)),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
