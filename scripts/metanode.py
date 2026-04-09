import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

@dataclass
class MNB:
    data: Dict[str, Any]
    psi: float
    timestamp: int
    hash: str

@dataclass
class State:
    data: dict
    psi: float
    hash: str

class MetaNode:
    def __init__(self, name: str):
        self.name = name

    def process(self, input_data: Any, prev_hash: str = "") -> MNB:
        # 1. Resolve Identidade (substituído pela lógica específica do nó)
        resolved_data = self.resolve(input_data)

        # 2. Calcula Ψ (simulado, deve ser implementado por cada nó)
        psi = self.compute_psi(resolved_data)

        # 3. Validação Ω (simplificada, deve ser implementada por cada nó)
        omega_score = self.validate_omega(psi)
        if omega_score < 0.85: # Exemplo de threshold
            raise ValueError(f"BLOCK: Ω-Gate falhou no nó {self.name} com score {omega_score}")

        # 4. Hash encadeado
        payload = json.dumps(resolved_data, sort_keys=True)
        current_hash = hashlib.sha256((payload + prev_hash).encode()).hexdigest()

        # 5. Emitir MNB
        return MNB(
            data=resolved_data,
            psi=psi,
            timestamp=int(time.time()),
            hash=current_hash
        )

    def resolve(self, x: Any) -> Any:
        # Deve ser sobrescrito por cada nó específico
        return x

    def compute_psi(self, x: Any) -> float:
        # Deve ser sobrescrito por cada nó específico
        return 0.9 # Valor padrão

    def validate_omega(self, psi: float, theta: float = 50.0) -> float:
        # Lógica Ω-Gate, pode ser sobrescrita
        theta_hat = 1 / (1 + theta / 100)
        return 0.7 * psi + 0.3 * theta_hat

# Funções de Ledger (simplificadas para este contexto)
LEDGER_PATH = "/home/ubuntu/matverse_ledger.jsonl"

def load_ledger() -> List[Dict[str, Any]]:
    if not os.path.exists(LEDGER_PATH):
        return []
    entries = []
    with open(LEDGER_PATH, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def append_ledger(mnb: MNB, omega: float, decision: str) -> Dict[str, Any]:
    ledger = load_ledger()
    prev_hash = ledger[-1]["hash"] if ledger else "GENESIS"

    content = f"{mnb.hash}-{prev_hash}-{omega}-{decision}"
    hash_val = hashlib.sha256(content.encode()).hexdigest()

    record = {
        "mnb_hash": mnb.hash,
        "prev_hash": prev_hash,
        "hash": hash_val,
        "omega": omega,
        "decision": decision,
        "timestamp": mnb.timestamp
    }

    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record

def get_last_omega() -> float:
    ledger = load_ledger()
    if not ledger:
        return 0.0
    return ledger[-1].get("omega", 0.0)
