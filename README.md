# MatVerse GitHub Resolver
Ferramenta de resolução canônica de URLs e queries do GitHub para o ecossistema MatVerse/SymbiOS.

## Estrutura
- `scripts/`: Contém os motores de resolução (F → S → C), scripts de indexação, o Ω-Gate completo, e a integração com a arquitetura MetaNode e Ledger V2.
  - `github_query_resolver.py`: Implementa o pipeline F → S → C.
  - `github_repo_indexer.py`: Auxilia na fase de Seleção (S).
  - `github_url_validator.py`: Validador de URLs GitHub.
  - `github_resolver_benchmark.py`: Script para validação empírica e testes de regressão.
  - `metanode.py`: Implementação da classe base MetaNode.
  - `omega_gate.py`: Implementação do Ω-Gate completo.
  - `ledger_v2.py`: Implementação do Ledger V2 com Merkle Root e Receipts Canônicos.
  - `matverse_resolver_node.py`: Adaptação do GitHub Resolver como um MetaNode, integrando-o ao Ledger V2.
- `SKILL.md`: Definição formal da ontologia F → S → C e do Ω-Gate evoluído.

## Uso

### Resolução Canônica (F → S → C)
```bash
python3 scripts/github_query_resolver.py "admin:@me"
```

### Execução do Benchmark
```bash
python3 scripts/github_resolver_benchmark.py
```

### Exemplo de MetaNode (com Ledger V2)
```bash
python3 scripts/matverse_resolver_node.py
```

### Variáveis de Ambiente
- `MATVERSE_LEDGER_PATH`: Define o caminho para o arquivo do ledger (ex: `/var/log/matverse_ledger.jsonl`). Se não definido, usa o padrão local.
