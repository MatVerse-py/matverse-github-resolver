---
name: matverse-github-resolver
description: Resolvedor canônico de URLs e queries do GitHub para o ecossistema MatVerse/SymbiOS. Implementa a ontologia F → S → C (Filtro, Seleção, Resolução Canônica) e o Ω-Gate de validade para garantir acesso determinístico e auditável a recursos.
license: Complete terms in LICENSE.txt
---

# MatVerse GitHub Resolver (Certificado)

Esta skill fornece o workflow canônico para resolução de URLs e queries do GitHub dentro do ecossistema **MatVerse/SymbiOS**. Ela evoluiu para um **módulo canônico certificado**, integrando a ontologia **F → S → C**, o **Ω-Gate completo**, **Merkle Root no ledger**, e **receipts estruturados** para garantir prova pública e auditabilidade.

## Ontologia de Resolução de Identidade (F → S → C)

O problema de "abrir um repositório" é tratado como um problema formal de resolução de identidade, decomposto em três operadores fundamentais:

### 1. Filtro (F): Descoberta e Classificação
O operador $F(x) \rightarrow S$ projeta uma entrada arbitrária $x$ (query, string, URL parcial) sobre o universo de candidatos $S$.
- **Exemplo**: $F("admin:@me") \rightarrow \{r_1, r_2, ..., r_n\}$ (conjunto de repositórios administrativos).
- **Classes de Entrada**:
  - **Q (Query)**: `admin:@me`, `repos?q=...` (passa por F).
  - **R (Repo)**: `owner/repo` (identidade parcial, vai para C).
  - **U (URL)**: `https://github.com/...` (validação direta).
  - **I (Inválido)**: `admin:@mee` (BLOCK imediato).

### 2. Seleção (S): Escolha Determinística
O operador $S: S \rightarrow r^*$ escolhe o candidato ideal $r^*$ do conjunto $S$ baseado em matching semântico, ranking determinístico ou input explícito do usuário.

### 3. Resolução Canônica (C): Identidade Imutável
O operador $C(r^*) = u_c$ transforma o candidato selecionado na URL canônica determinística:
$$u_c = "https://github.com/" \oplus owner \oplus "/" \oplus repo \oplus "/tree/" \oplus branch \oplus "/" \oplus path$$

**Propriedade Crítica (Idempotência)**: $C(C(x)) = C(x)$. Se esta igualdade falhar, há um bug estrutural na resolução.

## Governança e Ω-Gate (Fail-Closed e Certificação)

Toda resolução é submetida ao **Ω-Gate**, que avalia a coerência sistêmica e a integridade da identidade resolvida. O Ω-Gate agora é completo, incorporando quatro pilares de confiança:

$$ \Omega = 0.4 \cdot \Psi + 0.3 \cdot \hat{\Theta} + 0.2 \cdot (1 - CVaR) + 0.1 \cdot PoLE $$

- **$\Psi$ (Psi)**: Confiança intrínseca na resolução (0.0 a 1.0).
- **$\hat{\Theta}$ (Theta-hat)**: Incerteza normalizada (0.0 a 1.0).
- **CVaR (Conditional Value at Risk)**: Risco de cauda (0.0 a 1.0).
- **PoLE (Polarity of Evidence)**: Alinhamento da evidência (0 ou 1).

O sistema opera em modo **fail-closed**: na dúvida ou em caso de ambiguidade semântica, a ação é bloqueada para evitar erros silenciosos ou acessos a recursos incorretos. A decisão do Ω-Gate pode ser `PASS`, `CONDITIONAL` ou `BLOCK`.

## Workflows e Scripts Production-Grade

A skill disponibiliza scripts Python em `scripts/` alinhados com a arquitetura **F → S → C** e a nova camada de certificação:

### 1. Resolvedor de Queries e Identidade (`github_query_resolver.py`)
Implementa o pipeline completo $\Pi(x) = C(S(F(x)))$. Classifica a entrada, tenta a seleção e resolve para a URL canônica.

**Uso:**
```bash
python /home/ubuntu/matverse-github-resolver/scripts/github_query_resolver.py "admin:@me"
```

### 2. Indexador e Mapeador Administrativo (`github_repo_indexer.py`)
Auxilia na fase de **Seleção (S)** ao transformar listagens administrativas brutas em um índice canônico auditável, permitindo a escolha determinística do repositório alvo.

**Uso:**
```bash
python /home/ubuntu/matverse-github-resolver/scripts/github_repo_indexer.py <repos.json>
```

### 3. Benchmark Formal (`github_resolver_benchmark.py`)
Um conjunto de testes para validação empírica e testes de regressão, garantindo a acurácia da classificação, status (Ω-Gate) e normalização.

**Uso:**
```bash
python /home/ubuntu/matverse-github-resolver/scripts/github_resolver_benchmark.py
```

### 4. MetaNode do Resolvedor (`matverse_resolver_node.py`)
Adaptação do GitHub Resolver como um `MetaNode`, integrando-o ao ledger. Este script utiliza o Ω-Gate completo e o Ledger V2 para registrar cada resolução como uma prova pública verificável.

**Uso:**
```bash
python /home/ubuntu/matverse-github-resolver/scripts/matverse_resolver_node.py
```

### 5. Ω-Gate Completo (`omega_gate.py`)
Implementa a função `compute_omega` e `omega_decision` com os quatro pilares de confiança ($\Psi$, $\hat{\Theta}$, CVaR, PoLE).

### 6. Ledger V2 (`ledger_v2.py`)
Implementa um ledger append-only com suporte a **Merkle Roots** e **Receipts Canônicos** estruturados, garantindo encadeamento causal, imutabilidade e auditabilidade externa. Suporta portabilidade via variável de ambiente `MATVERSE_LEDGER_PATH`.

## Ciclo Operacional Antifrágil

Para operações de alta criticidade, o módulo agora participa do ciclo:
**PROVA $\rightarrow$ ASSEGURA $\rightarrow$ PASSA $\rightarrow$ ATACA $\rightarrow$ PROVA**

1.  **PROVA**: Gera evidência verificável da identidade resolvida (via MNB e Receipt).
2.  **ASSEGURA**: Valida via Ω-Gate completo.
3.  **PASSA**: Propaga o estado apenas se válido.
4.  **ATACA**: Testa a resistência da identidade contra ambiguidades (Twin Adversarial).
5.  **PROVA (Novo)**: Mede a resistência e atualiza a verdade no ledger.

Este ciclo transforma o GitHub de uma plataforma de código em uma **fonte de verdade verificável** para o ecossistema MatVerse, com cada resolução sendo um **testemunho público auditável**.
