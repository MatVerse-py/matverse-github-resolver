---
name: matverse-github-resolver
description: Resolvedor canônico de URLs e queries do GitHub para o ecossistema MatVerse/SymbiOS. Implementa a ontologia F → S → C (Filtro, Seleção, Resolução Canônica) e o Ω-Gate de validade para garantir acesso determinístico e auditável a recursos.
license: Complete terms in LICENSE.txt
---

# MatVerse GitHub Resolver (Evoluído)

Esta skill fornece o workflow canônico para resolução de URLs e queries do GitHub dentro do ecossistema **MatVerse/SymbiOS**. Ela evoluiu de um simples normalizador para um sistema formal de resolução de identidade de recurso, operando sob o invariante fundamental de não ambiguidade e auditabilidade.

## Ontologia de Resolução de Identidade

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

## Governança e Ω-Gate (Fail-Closed)

Toda resolução é submetida ao **Ω-Gate**, que avalia a coerência sistêmica e a integridade da identidade resolvida.
- **V(u_c) = 1**: Formato válido e acessível $\rightarrow$ **PASS**.
- **V(u_c) = 0**: Formato inválido ou inacessível $\rightarrow$ **BLOCK**.

O sistema opera em modo **fail-closed**: na dúvida ou em caso de ambiguidade semântica, a ação é bloqueada para evitar erros silenciosos ou acessos a recursos incorretos.

## Workflows e Scripts Production-Grade

A skill disponibiliza scripts Python em `scripts/` alinhados com a arquitetura **F → S → C**:

### 1. Resolvedor de Queries e Identidade (`github_query_resolver.py`)
Implementa o pipeline completo $\Pi(x) = C(S(F(x)))$. Classifica a entrada, tenta a seleção e resolve para a URL canônica, aplicando o Ω-Gate.

**Uso:**
```bash
python /home/ubuntu/skills/matverse-github-resolver/scripts/github_query_resolver.py "admin:@me"
```

### 2. Indexador e Mapeador Administrativo (`github_repo_indexer.py`)
Auxilia na fase de **Seleção (S)** ao transformar listagens administrativas brutas em um índice canônico auditável, permitindo a escolha determinística do repositório alvo.

**Uso:**
```bash
python /home/ubuntu/skills/matverse-github-resolver/scripts/github_repo_indexer.py <repos.json>
```

## Ciclo Operacional Antifrágil

Para operações de alta criticidade, siga o ciclo:
**PROVA $\rightarrow$ ASSEGURA $\rightarrow$ PASSA $\rightarrow$ ATACA $\rightarrow$ PROVA**

1. **PROVA**: Gera evidência verificável da identidade resolvida.
2. **ASSEGURA**: Valida via Ω-Gate.
3. **PASSA**: Propaga o estado apenas se válido.
4. **ATACA**: Testa a resistência da identidade contra ambiguidades (Twin Adversarial).
5. **PROVA (Novo)**: Mede a resistência e atualiza a verdade no ledger.

Este ciclo transforma o GitHub de uma plataforma de código em uma **fonte de verdade verificável** para o ecossistema MatVerse.
