import json
import time
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List
import hashlib
from github_query_resolver import run_pipeline, ResolutionResult

# Assuming metanode.py is in the same directory
from metanode import MetaNode, MNB, load_ledger, append_ledger, get_last_omega, LEDGER_PATH

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
        # PSI é a confiança na resolução. Baseado no omega_score do ResolutionResult.
        return resolved_data.resolution_result.get("omega_score", 0.0)

    def validate_omega(self, psi: float, theta: float = 50.0) -> float:
        # Reutiliza a lógica do omega_gate do github_query_resolver
        # Para este nó, o psi já é o omega_score da resolução anterior
        # Então, podemos simplificar ou usar um threshold direto
        if psi >= 0.85: # Threshold para PASS
            return psi
        return 0.0 # Falha no Ω-Gate

    def process(self, input_data: str, prev_hash: str = "") -> MNB:
        # 1. Resolve Identidade (usando a lógica do github_query_resolver)
        resolved_data_obj = self.resolve(input_data)
        resolved_data_dict = asdict(resolved_data_obj)

        # 2. Calcula Ψ
        psi = self.compute_psi(resolved_data_obj)

        # 3. Validação Ω
        omega_score = self.validate_omega(psi)
        
        status = resolved_data_obj.resolution_result.get("status", "BLOCK")
        if status == "BLOCK" or omega_score < 0.85:
            raise ValueError(f"BLOCK: Ω-Gate falhou no nó {self.name} com score {omega_score} ou status {status}")

        # 4. Hash encadeado
        payload = json.dumps(resolved_data_dict, sort_keys=True)
        current_hash = hashlib.sha256((payload + prev_hash).encode()).hexdigest()

        # 5. Emitir MNB
        mnb = MNB(
            data=resolved_data_dict,
            psi=psi,
            timestamp=int(time.time()),
            hash=current_hash
        )
        
        # 6. Ancorar no Ledger
        append_ledger(mnb, omega_score, status)

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

    print("\n--- Conteúdo do Ledger ---")
    print(json.dumps(load_ledger(), indent=2, ensure_ascii=False))
