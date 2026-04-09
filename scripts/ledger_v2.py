#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MATVERSE LEDGER V2 (Certificado)
Merkle Root | Receipt Canônico | Causalidade

Implementa a persistência causal com suporte a Merkle Roots e Receipts estruturados,
garantindo que cada entrada seja uma prova pública verificável.
"""

import json
import hashlib
import os
import time
from typing import List, Dict, Any, Optional

# Portabilidade: permite configurar o caminho via variável de ambiente
LEDGER_PATH = os.getenv("MATVERSE_LEDGER_PATH", "/home/ubuntu/matverse_ledger_v2.jsonl")

def compute_merkle_root(hashes: List[str]) -> str:
    """Calcula a Merkle Root de uma lista de hashes SHA-256."""
    if not hashes:
        return ""

    layer = hashes[:]
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a
            combined = hashlib.sha256((a + b).encode()).hexdigest()
            next_layer.append(combined)
        layer = next_layer

    return layer[0]


def build_receipt(mnb_hash: str, omega: float, decision: str, prev_hash: str, timestamp: int) -> Dict[str, Any]:
    """Constrói um receipt canônico estruturado e seu hash de integridade."""
    payload = {
        "mnb_hash": mnb_hash,
        "omega": round(omega, 6),
        "decision": decision,
        "prev_hash": prev_hash,
        "timestamp": timestamp
    }

    # Hash do payload para garantir integridade do receipt
    payload_str = json.dumps(payload, sort_keys=True)
    receipt_hash = hashlib.sha256(payload_str.encode()).hexdigest()

    return {
        "payload": payload,
        "receipt_hash": receipt_hash
    }


def load_ledger() -> List[Dict[str, Any]]:
    """Carrega o histórico do ledger v2."""
    if not os.path.exists(LEDGER_PATH):
        return []

    entries = []
    with open(LEDGER_PATH, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def append_ledger(mnb_hash: str, omega: float, decision: str) -> Dict[str, Any]:
    """
    Adiciona uma nova entrada ao ledger v2 com receipt e encadeamento causal.
    """
    ledger = load_ledger()
    prev_hash = ledger[-1]["receipt_hash"] if ledger else "GENESIS"
    timestamp = int(time.time())

    # 1. Construir Receipt
    receipt = build_receipt(mnb_hash, omega, decision, prev_hash, timestamp)

    # 2. Calcular Merkle Root (incluindo o novo receipt e o anterior)
    # Em um sistema real, isso poderia incluir múltiplos artefatos do mesmo bloco
    m_root = compute_merkle_root([prev_hash, receipt["receipt_hash"]])

    # 3. Registro Final
    record = {
        "receipt": receipt["payload"],
        "receipt_hash": receipt["receipt_hash"],
        "merkle_root": m_root,
        "version": "2.0"
    }

    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record

if __name__ == "__main__":
    # Teste rápido
    m_hash = hashlib.sha256(b"test_mnb").hexdigest()
    res = append_ledger(m_hash, 0.885, "PASS")
    print(f"Ledger V2 Entry Created:\n{json.dumps(res, indent=2)}")
