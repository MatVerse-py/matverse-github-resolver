import json
import time
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List
import hashlib

from github_query_resolver import run_pipeline, ResolutionResult
from metanode import MetaNode, MNB # Keep MetaNode and MNB base classes
from omega_gate import compute_omega, omega_decision # New Ω-Gate
from ledger_v2 import load_ledger, append_ledger, LEDGER_PATH # New Ledger V2

@dataclass
class GitHubResolverMNBData:
    input_x: str
    resolution_result: Dict[str, Any]

class GitHubResolverNode(MetaNode):
    def __init__(self, name: str = "github_resolver_node"):
        super().__init__(name)

    def resolve(self, input_data: str) -> GitHubResolverMNBData:
        # Use the existing run_pipeline from github_query_resolver.py
        resolution_result = run_pipeline(input_data)
        return GitHubResolverMNBData(
            input_x=input_data,
            resolution_result=asdict(resolution_result)
        )

    def compute_psi(self, resolved_data: GitHubResolverMNBData) -> float:
        # PSI é a confiança intrínseca na resolução, baseada no omega_score do ResolutionResult.
        # Usamos o omega_score do resolvedor como PSI para o Ω-Gate externo.
        return resolved_data.resolution_result.get("omega_score", 0.0)

    def process(self, input_data: str, prev_hash: str = "") -> MNB:
        # 1. Resolve Identidade (usando a lógica do github_query_resolver)
        resolved_data_obj = self.resolve(input_data)
        resolved_data_dict = asdict(resolved_data_obj)

        # Extrai PSI do resultado da resolução
        psi = self.compute_psi(resolved_data_obj)
        
        # Simula valores para theta, cvar, pole (em produção, viriam de sensores/config)
        theta = 10.0 # Exemplo: baixa incerteza
        cvar = 0.01  # Exemplo: baixo risco
        pole = 1     # Exemplo: alinhamento positivo

        # 2. Calcula Ω-Gate completo
        omega_score = compute_omega(psi, theta, cvar, pole)
        decision = omega_decision(omega_score, psi, cvar)
        
        if decision == "BLOCK":
            raise ValueError(f"BLOCK: Ω-Gate falhou no nó {self.name} com score {omega_score} e decisão {decision}")

        # 3. Hash encadeado
        payload = json.dumps(resolved_data_dict, sort_keys=True)
        current_hash = hashlib.sha256((payload + prev_hash).encode()).hexdigest()

        # 4. Emitir MNB
        mnb = MNB(
            data=resolved_data_dict,
            psi=psi,
            timestamp=int(time.time()),
            hash=current_hash
        )
        
        # 5. Ancorar no Ledger V2 (com Merkle Root e Receipt)
        append_ledger(mnb.hash, omega_score, decision)

        return mnb


# Exemplo de uso do nó
if __name__ == "__main__":
    # Limpar ledger para teste
    if os.path.exists(LEDGER_PATH):
        os.remove(LEDGER_PATH)

    github_node = GitHubResolverNode()

    test_inputs = [
        "matverse/core",
        "https://github.com/matverse/core/tree/main/",
        "admin:@me",
        "admin:@mee", # Este deve falhar
        "invalid_input_string_123"
    ]

    prev_hash = ""
    for i, input_x in enumerate(test_inputs):
        print(f"\n--- Processando entrada: {input_x} ---")
        try:
            mnb_output = github_node.process(input_x, prev_hash)
            print(f"MNB Output:\n{json.dumps(asdict(mnb_output), indent=2, ensure_ascii=False)}")
            prev_hash = mnb_output.hash
        except ValueError as e:
            print(f"Erro no processamento: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    print("\n--- Conteúdo do Ledger V2 ---")
    print(json.dumps(load_ledger(), indent=2, ensure_ascii=False))
