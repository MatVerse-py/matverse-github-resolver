#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MATVERSE GITHUB RESOLVER BENCHMARK
Validação Empírica | Regressão | Acurácia

Este script executa um conjunto de testes (Test Suite) sobre o motor de resolução
para garantir que a ontologia F → S → C e o Ω-Gate operem com o rigor exigido.
"""

import json
import sys
from dataclasses import dataclass
from typing import List, Optional
from github_query_resolver import run_pipeline

@dataclass(frozen=True)
class TestCase:
    input_x: str
    expected_type: str
    expected_status: str
    expected_normalized_contains: Optional[str] = None

def run_benchmark(tests: List[TestCase]) -> dict:
    total = len(tests)
    type_ok = 0
    status_ok = 0
    norm_ok = 0
    failures = []

    for t in tests:
        result = run_pipeline(t.input_x)
        
        this_type_ok = (result.input_type == t.expected_type)
        this_status_ok = (result.status == t.expected_status)
        
        # Verifica se a URL resolvida contém o esperado (se houver)
        this_norm_ok = True
        if t.expected_normalized_contains:
            if result.resolved_url:
                this_norm_ok = (t.expected_normalized_contains in result.resolved_url)
            else:
                this_norm_ok = False

        if this_type_ok: type_ok += 1
        if this_status_ok: status_ok += 1
        if this_norm_ok: norm_ok += 1

        if not (this_type_ok and this_status_ok and this_norm_ok):
            failures.append({
                "input": t.input_x,
                "got": {
                    "type": result.input_type,
                    "status": result.status,
                    "resolved_url": result.resolved_url,
                    "reason": result.reason
                },
                "expected": {
                    "type": t.expected_type,
                    "status": t.expected_status,
                    "normalized_contains": t.expected_normalized_contains
                }
            })

    return {
        "summary": {
            "total": total,
            "type_accuracy": type_ok / total if total else 0.0,
            "status_accuracy": status_ok / total if total else 0.0,
            "normalization_accuracy": norm_ok / total if total else 0.0,
            "all_passed": len(failures) == 0
        },
        "failures": failures
    }

if __name__ == "__main__":
    test_suite = [
        TestCase("admin:@me", "QUERY", "WAIT", None),
        TestCase("admin:@mee", "INVALID", "BLOCK", None),
        TestCase("matverse/core", "REPO", "PASS", "https://github.com/matverse/core/tree/main/"),
        TestCase("https://github.com/matverse/core/tree/main/", "URL", "PASS", "https://github.com/matverse/core/tree/main/"),
        TestCase("https://github.com/repos?q=matverse", "QUERY", "WAIT", None),
        TestCase("invalid_input_string_123", "INVALID", "BLOCK", None)
    ]

    report = run_benchmark(test_suite)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    if not report["summary"]["all_passed"]:
        sys.exit(1)
    sys.exit(0)
