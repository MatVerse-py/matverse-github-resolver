# MatVerse GitHub Resolver
Ferramenta de resolução canônica de URLs e queries do GitHub para o ecossistema MatVerse/SymbiOS.

## Estrutura
- `scripts/`: Motores de resolução e indexação, incluindo a implementação do pipeline F → S → C e a integração com a arquitetura MetaNode.
- `SKILL.md`: Definição formal da ontologia F → S → C e do Ω-Gate.
- `scripts/github_resolver_benchmark.py`: Script para validação empírica e testes de regressão do resolvedor.
- `scripts/metanode.py`: Implementação da classe base MetaNode para integração em meta-pipelines.
- `scripts/matverse_resolver_node.py`: Adaptação do GitHub Resolver como um MetaNode, integrando-o ao ledger.

## Uso

### Resolução Canônica (F → S → C)
```bash
python3 scripts/github_query_resolver.py "admin:@me"
```

### Execução do Benchmark
```bash
python3 scripts/github_resolver_benchmark.py
```

### Exemplo de MetaNode (com Ledger)
```bash
python3 scripts/matverse_resolver_node.py
```
