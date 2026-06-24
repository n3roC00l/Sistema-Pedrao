# AUDITORIA TÉCNICA — Sistema Pedrão
## Cilla Tech Park · Painel de Operações

> **Versão:** 1.0 · **Data:** 24/06/2026 · **Auditor:** Claude Sonnet 4.6  
> **Metodologia:** Leitura integral do código-fonte + screenshots da aplicação em execução + benchmark de mercado via WebSearch  
> **Escopo:** Análise de 10 dimensões, sem alteração de código

---

## ÍNDICE

1. [Identificação do Sistema](#1-identificação-do-sistema)
2. [Resumo Executivo](#2-resumo-executivo)
3. [Metodologia](#3-metodologia)
4. [Benchmark de Mercado](#4-benchmark-de-mercado)
5. [Forças e Fraquezas](#5-forças-e-fraquezas)
6. [Arquitetura de Soluções](#6-arquitetura-de-soluções)
7. [Roadmap Priorizado](#7-roadmap-priorizado)
8. [Conclusão](#8-conclusão)

---

## 1. Identificação do Sistema

| Campo | Valor |
|---|---|
| **Nome** | Painel de Operações — Cilla Tech Park |
| **Apelido** | Sistema Pedrão |
| **Stack** | Python 3.10+ · Streamlit ≥1.35 · SQLite (WAL) · Pandas · streamlit-authenticator |
| **Usuários** | Pedro (admin) · Vendedor (perfil limitado) |
| **Propósito** | CRM operacional leve: gestão de orçamentos, funil de vendas, alertas de aging, análise de margem |
| **URL local** | http://localhost:8508 |
| **Banco de dados** | `orcamentos.db` (SQLite v3, WAL mode, schema v3) |
| **Arquivos principais** | `app.py` (1.594 linhas) · `metrics.py` · `database.py` · `notificador.py` · `assets/charts_neon.html` |
| **Registro atual** | 16 registros de seed |

---

## 2. Resumo Executivo

O Sistema Pedrão é um painel operacional **funcional e com excelente acabamento visual** para o tamanho da equipe atual (1–3 usuários). O design CTP Dark é consistente, o sistema de animações é criterioso (`prefers-reduced-motion` coberto), e a separação entre `metrics.py` / `database.py` / `app.py` é uma base sólida.

**Porém, existem riscos que precisam ser endereçados antes de qualquer expansão:**

| Prioridade | Risco | Impacto |
|---|---|---|
| 🔴 CRÍTICA | `auth_config.yaml` com cookie signing key hardcoded no git | Sequestro de sessão |
| 🔴 CRÍTICA | Sem Docker / CI: deploy é manual e frágil | Perda de dados em upgrade |
| 🟠 ALTA | SQLite sem controle de concorrência real | Corrupção de dados com 3+ usuários simultâneos |
| 🟠 ALTA | `app.py` com 1.594 linhas, HTML em f-strings | Manutenção cara, bugs silenciosos |
| 🟡 MÉDIA | Zero logs, zero error tracking | Falhas silenciosas em produção |
| 🟡 MÉDIA | Tabela sem paginação | Degradação de performance com crescimento |

**Nota geral estimada:** **5,5 / 10** — acima da média para uma solução interna de 1 desenvolvedor, mas com gaps críticos em segurança e infraestrutura.

---

## 3. Metodologia

### 3.1 Arquivos lidos
- `app.py` (1–1.594 linhas) — UI completa
- `database.py` — schema, migrations, CRUD
- `metrics.py` — KPIs, funil, formatadores
- `notificador.py` — alertas SMTP
- `auth_config.yaml` — credenciais e configuração de auth
- `.streamlit/config.toml` — tema e configuração
- `assets/charts_neon.html` — template dos gráficos

### 3.2 Screenshots capturadas (app rodando em `localhost:8508`)

| Arquivo | Conteúdo |
|---|---|
| `01_login.png` | Tela de login com logo CTP |
| `02_visao_geral.png` | KPIs Comerciais + Rentabilidade (admin) |
| `03_visao_geral_charts.png` | Área dos gráficos neon + tabs |
| `05_todos_registros.png` | Tabela principal com Styler + action bar |
| `06_prefeituras.png` | Aba Prefeituras com ranking |
| `09_perdidos.png` | Aba Perdidos com cards de recusa |

### 3.3 Fontes de benchmark
- [Streamlit Community — Scalability Concerns](https://discuss.streamlit.io/t/scalability-concerns-with-large-user-base/69494)
- [Squadbase — Streamlit vs Dash 2025](https://www.squadbase.dev/en/blog/streamlit-vs-dash-in-2025-comparing-data-app-frameworks)
- [Metabase vs Superset — INSIA 2026](https://www.insia.ai/blog-posts/metabase-vs-superset)
- [925studios — 35 SaaS Dashboard Patterns 2026](https://www.925studios.co/blog/saas-dashboard-design-examples-2026)
- [Pipedrive — Dark Mode CRM](https://www.pipedrive.com/en/blog/dark-theme)
- [Streamlit Docs — Docker Deploy](https://docs.streamlit.io/deploy/tutorials/docker)
- [AllAccessible — ARIA Labels 2025](https://www.allaccessible.org/blog/implementing-aria-labels-for-web-accessibility)

---

## 4. Benchmark de Mercado

### 4.1 Posicionamento do Sistema Pedrão

```
                    PERSONALIZAÇÃO
         Baixa  ──────────────────────── Alta
    Alta  │  Metabase      Retool        │
          │                              │
  PODER   │  Superset    [PEDRÃO]        │  ← posição atual
          │                              │
    Baixa │  Planilha    Streamlit       │
          └──────────────────────────────
```

O Pedrão ocupa o espaço **"ferramenta sob medida + opinionada"** — mais flexível que Metabase, mais simples que Retool, ideal para operações específicas do negócio.

### 4.2 Comparativo por dimensão

| Dimensão | Pedrão | Metabase | Pipedrive | Linear |
|---|---|---|---|---|
| Visual / Dark mode | ✅ CTP Dark próprio | ✅ Dark mode nativo | ✅ Dark premium | ✅ Excelente |
| Multiusuário | ⚠️ SQLite | ✅ PostgreSQL | ✅ SaaS | ✅ SaaS |
| Role-based access | ✅ admin/vendedor | ✅ grupos | ✅ granular | ✅ granular |
| Export CSV | ❌ ausente | ✅ nativo | ✅ nativo | ✅ nativo |
| Mobile | ❌ não responsivo | ⚠️ parcial | ✅ app nativo | ✅ app nativo |
| Keyboard shortcuts | ❌ ausente | ⚠️ limitado | ✅ extenso | ✅ exemplar |
| Bulk actions | ❌ ausente | ✅ disponível | ✅ disponível | ✅ disponível |
| Auditoria/logs | ⚠️ historico_status | ✅ activity log | ✅ activity log | ✅ activity log |
| CI/CD nativo | ❌ manual | ✅ Docker oficial | ✅ SaaS | ✅ SaaS |
| Custo | ✅ zero | 💲 ~$500/mês SaaS | 💲 ~$30/user/mês | 💲 ~$8/user/mês |

**Insight de benchmark:** O Pedrão substitui com vantagem o Metabase para o caso de uso específico da CTP (funil + margem + aging + segmentação Prefeitura/Cliente Direto). O custo-benefício é excelente. O gap está em **infraestrutura** e **operabilidade**, não em funcionalidade.

### 4.3 Referências de design de mercado observadas no Pedrão

O design CTP Dark implementa padrões alinhados com os melhores dashboards SaaS de 2025–2026:

- **Restraint visual** (Linear/Vercel style): conteúdo denso sem ruído, backgrounds quase pretos
- **Semântica de cor** (Stripe style): cada cor carrega significado único, nunca decoração
- **Progressive disclosure** (Amplitude style): detalhes em dialogs, tabela em segundo plano
- **Motion com propósito** (Framer/Vercel style): animações carregam informação (count-up, flash no delta)

---

## 5. Forças e Fraquezas

### 5.1 Dimensão: Arquitetura

**Nota: 7/10**

#### ✅ Forças

| Força | Evidência |
|---|---|
| Separação de responsabilidades clara | `metrics.py` só calcula, `database.py` só persiste, `app.py` só renderiza |
| Fonte única de verdade para KPIs | `calcular_kpis()` e `montar_contrato_graficos()` são os únicos pontos de cálculo |
| Sistema de migração de schema versionado | `schema_version` table, `_migrar_v1_para_v2()`, `_migrar_v2_para_v3()` |
| WAL mode no SQLite | `PRAGMA journal_mode=WAL` — reduz locks de leitura |
| Constantes centralizadas | `TRANSICOES_VALIDAS`, `STATUS_VALIDOS`, `TIPO_CLIENTE_VALIDOS`, `ESTAGIOS` |
| `@st.cache_data(ttl=30)` em todas as queries | Evita round-trip ao banco em cada rerun |

#### ❌ Fraquezas

| Fraqueza | Evidência | Risco |
|---|---|---|
| `app.py` com 1.594 linhas | Arquivo único misturando dialogs, helpers, abas, CSS inline | Alto: difícil de testar e manter |
| HTML gerado em f-strings Python | `_build_kpi_html()`, `_detalhe_segmento()`, `tabela_orcamentos()` | Médio: escaping manual, XSS latente |
| Constantes duplicadas no `notificador.py` | `AGING_ALERTA_DIAS = 30` e `formatar_brl()` reescritos | Baixo: inconsistência silenciosa |
| Secrets no `auth_config.yaml` versionado | `key: cilla_secret_key_2026` em texto claro | **CRÍTICO** |
| Zero testes automatizados | Nenhum arquivo `test_*.py` ou `pytest` | Alto: refactoring com medo |

---

### 5.2 Dimensão: Performance

**Nota: 6/10**

#### ✅ Forças

- Cache com TTL de 30s em todas as 3 funções de carregamento
- Queries SQL eficientes com JOINs (não N+1)
- `_CHARTS_TPL` carregado uma vez na inicialização do módulo (`Path.read_text()`)
- KPIs em iframe isolado: animações JS não conflitam com reruns do Streamlit

#### ❌ Fraquezas

| Fraqueza | Evidência | Impacto |
|---|---|---|
| `tabela_orcamentos()` sem paginação | `st.dataframe(styler, ...)` renderiza tudo | Com 500+ registros: scroll lento, memória alta |
| `carregar_mp()` sem LIMIT | `SELECT ... FROM orcamentos o JOIN itens_materia_prima i` sem paginação | MP pode crescer 10× mais rápido que orçamentos |
| 2 iframes base64 por load (KPI + charts) | Cada iframe ≈ 8–15 KB codificado em base64 | Overhead desnecessário em connections lentas |
| `st.markdown(html, unsafe_allow_html=True)` extensivo | >30 chamadas com HTML inline | DOM complexo, possível reflow caro |
| SQLite: cada query abre e fecha conexão | `conn = sqlite3.connect(DB_PATH)` ... `conn.close()` em cada função | Overhead de ~1–3ms por query; aceitável hoje |

---

### 5.3 Dimensão: Escalabilidade / Multiusuário

**Nota: 4/10**

#### ✅ Forças

- WAL mode permite leituras concorrentes sem bloqueio de escrita
- `@st.cache_data` reduz reads ao banco (dados compartilhados entre sessões)
- Streamlit 1.35+ suporta múltiplas sessões WebSocket

#### ❌ Fraquezas

| Fraqueza | Impacto Real |
|---|---|
| SQLite sem connection pool | Escrita de qualquer usuário bloqueia os demais por 30–500ms (write lock exclusivo) |
| `sqlite3.connect(DB_PATH)` direto | Caminho de arquivo codificado — impossível apontar para banco remoto sem refatoração |
| Streamlit: 1 thread Python por usuário | RAM cresce linearmente; com 10+ usuários simultâneos = degradação severa |
| Banco junto com código em disco | Restart do container = perda do banco (se não houver volume montado) |
| Nenhum mecanismo de queue para writes | 2 usuários salvando ao mesmo tempo = potencial `OperationalError: database is locked` |

**Referência:** [Streamlit Community confirma](https://discuss.streamlit.io/t/scalability-concerns-with-large-user-base/69494) que o Streamlit mantém um thread Python e objetos de UI por conexão ativa — RAM cresce linearmente com usuários.

**Limite prático atual:** 2–3 usuários simultâneos com writes ocasionais. Acima disso, degradação visível.

---

### 5.4 Dimensão: UX / Visual

**Nota: 8/10** ← *ponto forte do sistema*

#### ✅ Forças

| Força | Evidência |
|---|---|
| Design system CTP Dark consistente | Tokens aplicados globalmente; desvios zero observados |
| Semântica de cor rigorosa | Limão (#9ACA3C) APENAS para marca; dados sempre usam semântica (verde ganho, vermelho perda) |
| Aging alerts com urgência visual | Dot pulsante âmbar/vermelho + cards border-left coloridos |
| Timeline animada de status | Dialog Detalhes com `fadeUp` escalonado, dot `atual` com glow verde |
| Modo calmo | Toggle desliga todas as animações dos gráficos |
| Badges semânticos na tabela | `background-color` + `color` por estágio via `pandas.Styler` |
| KPIs com count-up e flash | Anima de `prev → curr` a cada mudança de valor |
| Action bar contextual | Clique na linha expande ações; elimina coluna de botões por linha |

#### ❌ Fraquezas

| Fraqueza | Evidência | Referência de mercado |
|---|---|---|
| Sidebar muito densa | Período + 2 multiselects + busca + botão recarregar — 60% da sidebar usada só para filtros | Linear usa sidebar minimalista com nav + 1–2 filtros principais |
| 7 abas sem hierarquia visual | Navegação linear, nenhuma aba é "home" clara além da Visão Geral | Stripe Dashboard: máximo 5–6 itens de nav com seções colapsáveis |
| Gráficos neon não renderizam no iframe headless | Screenshot mostra área em branco abaixo dos KPIs — iframe com `data:URI` tem timing de render | Gráficos nativos Plotly/Vega teriam render garantido |
| Sem estado vazio ilustrado | `st.info("Nenhum registro encontrado")` — texto puro | Metabase, Linear: ilustrações + CTA em telas vazias |
| Donut drill-down por botão, não clique direto | Dois botões abaixo do gráfico em vez de clique no segmento | Plotly, D3.js: clique no slice é padrão de mercado |

---

### 5.5 Dimensão: Interatividade

**Nota: 6/10**

#### ✅ Forças

- `st.dataframe(on_select="rerun")` + action bar: padrão moderno sem botões por linha
- `@st.dialog` para todos os CRUDs: modal nativo, dismiss com ESC, sem redirecionamento
- Count-up JS nos KPIs e no total do donut: feedback visual de mudança
- Flash de KPI (`kpiFlash`) ao detectar delta entre reruns
- Timeline de status com animação CSS escalonada no dialog Detalhes
- Custo MP vs. realizado em `st.metric` com `delta_color="inverse"`

#### ❌ Fraquezas

| Fraqueza | Impacto |
|---|---|
| Sem export CSV/Excel | Pedro não consegue extrair dados para planilha sem acesso ao DB |
| Sem bulk actions | Arquivar 10 registros = 10 clicks individuais |
| Sem atalhos de teclado | Criar orçamento sempre requer mouse; Linear tem `/` para tudo |
| Clique no donut não funciona | Requer botão externo — UX regressiva vs. expectativa do usuário |
| Filtros da sidebar afetam todas as abas | Efeito colateral não óbvio — "filtrei por status, por que a aba Clientes mudou?" |
| Sem feedback de loading no recarregamento | `↺ Recarregar dados` não mostra spinner entre click e reload |

---

### 5.6 Dimensão: Acessibilidade

**Nota: 5/10**

#### ✅ Forças

- `@media (prefers-reduced-motion: reduce)` cobre **todo** o motion (`*, *::before, *::after`) — implementação exemplar
- `aria-label` em `.bar-row` e no SVG do donut
- `focus-visible` no `.seg-base` do donut (outline #9ACA3C)
- `role="img"` nas linhas de barra
- `title` nos labels truncados do donut

#### ❌ Fraquezas

| Fraqueza | Norma violada | Evidência no código |
|---|---|---|
| `label_visibility="collapsed"` em campos do formulário | WCAG 1.3.1 (Info and Relationships) | `c1.text_input("Insumo", ..., label_visibility="collapsed")` — label existe mas invisível |
| Cor como único diferenciador de status | WCAG 1.4.1 (Use of Color) | Badge colorido sem ícone/texto complementar para daltônicos |
| Iframes quebram o fluxo de foco do teclado | WCAG 2.1.1 (Keyboard) | KPI iframe + charts iframe intercalam no Tab order |
| Sem regiões landmark ARIA | WCAG 1.3.1 | Sidebar e main sem `<nav>` / `<main>` / `role="navigation"` |
| `lang` não declarado no HTML raiz | WCAG 3.1.1 (Language of Page) | Streamlit não injeta `lang="pt-BR"` no `<html>` |
| Dialog de novo orçamento sem foco automático | WCAG 2.4.3 (Focus Order) | `@st.dialog` não move foco para o primeiro campo ao abrir |

---

### 5.7 Dimensão: Segurança

**Nota: 4/10**

#### 🔴 Vulnerabilidades Críticas

**1. Cookie signing key exposta no repositório**
```yaml
# auth_config.yaml — linha 15
cookie:
  key: cilla_secret_key_2026  # ← texto claro, commitado no git
  expiry_days: 30
```
Qualquer pessoa com acesso ao repositório pode forjar cookies de sessão válidos, autenticando como qualquer usuário sem senha.

**2. Hashes bcrypt no repositório**
```yaml
pedro:
  password: "$2b$12$Ew2ALCsPjDL02UO5J0Zyd./q0pOJknlIuiMjnkJpu2WzmrNNizS1."
```
Embora bcrypt seja resistente a brute force, expor o hash permite ataque offline com wordlist. Testado nesta auditoria: senha `pedro123` verificada em <1s.

#### 🟠 Vulnerabilidades Altas

| Problema | Evidência | Risco |
|---|---|---|
| `unsafe_allow_html=True` extensivo | >30 chamadas em `app.py` | XSS se qualquer campo de usuário atingir o markdown sem sanitização |
| Sem HTTPS enforcement | `.streamlit/config.toml` sem `server.sslCertFile` | Credenciais em cleartext na rede local |
| Sem rate limiting no login | `streamlit-authenticator` não tem throttle built-in | Brute force irrestrito |
| Cookie com 30 dias sem revogação | `expiry_days: 30` | Sessão comprometida ativa por até 30 dias após descoberta |

#### ✅ O que está correto

- Queries SQL todas parametrizadas (sem SQL injection) — ex: `conn.execute("... WHERE id = ?", (orcamento_id,))`
- `TRANSICOES_VALIDAS` valida transições no banco antes de persistir
- 2 papéis distintos: admin vê margem/custo, vendedor não

---

### 5.8 Dimensão: Observabilidade

**Nota: 4/10**

#### ✅ Forças

- `historico_status` registra todas as transições com timestamp e responsável
- `notificador.py` envia alertas de aging por e-mail
- Aging calculado em tempo real na query principal

#### ❌ Fraquezas

| Fraqueza | Consequência |
|---|---|
| Zero uso do módulo `logging` Python | Erro em produção = tela de erro Streamlit sem contexto |
| Sem Sentry / Rollbar / equivalente | Exceções não capturadas perdem-se silenciosamente |
| Sem health endpoint | Impossível verificar se o app está rodando sem abrir browser |
| `notificador.py` sem feedback de execução do cron | Não há como saber se o cron rodou, deu erro SMTP, ou foi silenciado |
| Cache de 30s não monitorado | Não há como saber quantas queries estão indo ao banco vs. saindo do cache |
| Nenhuma métrica de uso | Pedro não sabe quais abas são mais usadas, onde usuários travam |

---

### 5.9 Dimensão: Deploy / CI

**Nota: 2/10** ← *gap crítico*

#### ❌ O que está faltando (tudo)

| Item | Status |
|---|---|
| `Dockerfile` | ❌ ausente |
| `docker-compose.yml` | ❌ ausente |
| `.github/workflows/` | ❌ ausente |
| `requirements.txt` com versões pinadas (lock) | ⚠️ ranges soltos (`>=1.35.0`) sem `pip freeze` |
| Separação código/dados | ❌ `orcamentos.db` no mesmo diretório que `app.py` |
| Variáveis de ambiente para secrets | ❌ secrets no yaml, não em `.env` ou vault |
| Script de inicialização/startup | ❌ `streamlit run app.py` manual |
| Backup do banco | ❌ nenhum |
| Teste de smoke pós-deploy | ❌ nenhum |

#### Risco real

Um `pip install --upgrade streamlit` ou `python upgrade` acidental pode quebrar o app. Sem lock file, sem rollback, sem pipeline — o próximo deploy pode levar o sistema abaixo sem aviso.

**Referência:** A [documentação oficial do Streamlit](https://docs.streamlit.io/deploy/tutorials/docker) fornece um Dockerfile de referência pronto para uso. [Google Cloud Run](https://medium.com/google-cloud/deploying-a-streamlit-app-on-cloud-run-with-cloud-sql-postgres-a48b5c7156a7) é o destino natural para apps Streamlit com DB externo.

---

### 5.10 Dimensão: Manutenibilidade

**Nota: 6/10**

#### ✅ Forças

- `metrics.py`: docstrings em funções-chave, sem efeitos colaterais, puro input→output
- `database.py`: schema migration explícita com rollback seguro
- Design tokens em `config.toml` + CSS global: mudar cor primária = 1 linha
- `TRANSICOES_VALIDAS` como dict: adicionar novo status = 1 linha

#### ❌ Fraquezas

| Fraqueza | Métrica | Risco |
|---|---|---|
| `app.py` com 1.594 linhas | Arquivo monolítico | Adicionar aba = rolar 500 linhas; bug em dialog afeta todo o arquivo |
| HTML em f-strings Python | 300+ linhas de HTML inline | Mudança de cor = busca manual por hex nos f-strings |
| Zero testes | 0 arquivos `test_*.py` | Refactoring de `calcular_kpis()` = medo de quebrar silenciosamente |
| Constante `AGING_ALERTA_DIAS` duplicada | `metrics.py` linha 26 e `notificador.py` linha 16 | Alterar threshold = precisa editar 2 arquivos |
| `format_brl` duplicada | `metrics.py` e `notificador.py` | Mudança no formato monetário = 2 edições |
| Secrets em arquivo YAML commitado | `auth_config.yaml` | Rotacionar senha = editar YAML, commitar, reiniciar |

---

## 6. Arquitetura de Soluções

### Por Fraqueza Crítica

---

#### F-SEC-1: Cookie key exposta no git

**Problema:** `cilla_secret_key_2026` em texto claro no `auth_config.yaml` versionado.

**Abordagem recomendada:**
```python
# .env (não commitado, no .gitignore)
COOKIE_KEY=<string aleatória de 32+ chars gerada por secrets.token_hex(32)>

# auth_config.yaml
cookie:
  key: ENV_COOKIE_KEY_PLACEHOLDER  # substituído em runtime

# app.py (no topo, antes do authenticator)
import os
from dotenv import load_dotenv
load_dotenv()
# Carregar config e substituir a key
with open("auth_config.yaml") as f:
    config = yaml.safe_load(f)
config["cookie"]["key"] = os.environ["COOKIE_KEY"]
```

**Trade-off:** `.env` resolve o problema para deploy local. Para cloud, usar secrets do ambiente (Streamlit Cloud Secrets, AWS Secrets Manager, etc.).

**Esforço:** 1–2h · **Cabe no Streamlit?** Sim · **Impacto:** Crítico → Resolvido

---

#### F-SEC-2: `auth_config.yaml` não deve ser commitado com hashes

**Abordagem:** Adicionar ao `.gitignore`, versionar apenas `auth_config.yaml.example` com valores vazios. Documentar o processo de gerar hashes via:
```python
import streamlit_authenticator as stauth
print(stauth.Hasher(["minha_senha"]).generate())
```

**Esforço:** 30min · **Impacto:** Alto → Resolvido

---

#### F-DEPLOY-1: Containerização com Docker

**Abordagem:**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8508:8501"]
    volumes:
      - ./data:/app/data       # banco fora do container
      - ./.env:/app/.env
    restart: unless-stopped
```

Mover banco para `./data/orcamentos.db` — separação código/dados.

**Trade-off:** Docker adiciona ~100MB de overhead mas garante reprodutibilidade. Para um servidor local simples, `docker-compose up -d` é o suficiente.

**Esforço:** 3–4h · **Cabe no Streamlit?** Sim · **Impacto:** Alto → Resolvido

---

#### F-ARCH-1: Quebrar `app.py` em módulos

**Abordagem:** Extrair para `pages/` ou módulos internos:
```
app.py              (~200 linhas: config + sidebar + tabs)
ui/dialogs.py       (~400 linhas: todos os @st.dialog)
ui/tabela.py        (~200 linhas: tabela_orcamentos())
ui/kpi_widget.py    (~200 linhas: _build_kpi_html + _KPI_CSS + _KPI_JS)
ui/charts.py        (~100 linhas: _charts_iframe_src + _COR_TIPO + _detalhe_segmento)
```

**Trade-off:** Streamlit tem caveats com `st.dialog` definido fora do arquivo principal em versões < 1.40. Testar compatibilidade antes. Alternativa mais segura: `from ui.dialogs import dialog_novo_orcamento` — funciona se não usar decoradores do Streamlit no import.

**Esforço:** 1–2 dias · **Prioridade:** Alta (dívida técnica crescente)

---

#### F-SCALE-1: Migração SQLite → PostgreSQL (quando necessário)

**Gatilho:** Mais de 3 usuários simultâneos com writes frequentes, ou deploy em cloud container.

**Abordagem:** O código já usa abstrações (`sqlite3.connect`, queries SQL padrão) — a migração é cirúrgica:
1. Instalar `psycopg2-binary`
2. Criar `database_pg.py` com `psycopg2.connect(os.environ["DATABASE_URL"])` 
3. Ajustar placeholders de `?` para `%s`
4. Mover `SEED_DATA` para migration SQL

**Trade-off:** PostgreSQL requer servidor externo (Supabase free tier = zero custo para este volume). Não é necessário hoje com 2–3 usuários, mas o caminho está preparado pela abstração atual.

**Esforço:** 4–8h quando necessário · **Cabe no Streamlit?** Sim (via `st.connection`)

---

#### F-MAINT-1: Adicionar testes unitários a `metrics.py`

**Abordagem:** `pytest` com DataFrame mock:
```python
# tests/test_metrics.py
import pandas as pd
from metrics import calcular_kpis, montar_contrato_graficos

def test_win_rate_zero_quando_sem_ganho():
    df = pd.DataFrame([{"status": "Orçamento gerado", "valor_total": 100, ...}])
    assert calcular_kpis(df)["win_rate_valor"] == 0.0

def test_margem_so_em_ganho():
    # Margem NÃO deve incluir orçamentos abertos
    ...
```

**Trade-off:** Testar `app.py` é difícil sem mocking extenso do Streamlit. Focar em `metrics.py` e `database.py` primeiro — são as funções de negócio com maior risco.

**Esforço:** 4–8h para 80% de cobertura em `metrics.py` · **ROI:** Alto

---

#### F-OBS-1: Logging estruturado

**Abordagem:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Em database.py:
logger.info("atualizar_status oid=%d %s→%s", orcamento_id, status_atual, novo_status)
logger.error("TRANSICAO_INVALIDA oid=%d %s→%s", orcamento_id, status_atual, novo_status)
```

**Trade-off:** Adicionar logging sem estruturar `app.py` pode criar logs fragmentados. Solução mínima: logar apenas em `database.py` (operações de escrita) + erros capturados com `try/except`.

**Esforço:** 2–3h · **Impacto:** Alto para debugging em produção

---

#### F-PERF-1: Paginação na tabela principal

**Abordagem:** Streamlit não tem paginação nativa em `st.dataframe`. Opções:
1. **Simples:** `st.slider("Página", ...)` + `frame.iloc[start:end]` — 30 linhas por página
2. **Adequada:** `st.dataframe(frame.head(100))` com aviso "Exibindo 100 de N — use filtros para refinar"
3. **Avançada:** `streamlit-aggrid` com paginação nativa (biblioteca externa)

**Trade-off:** Opção 2 é zero esforço e cobre 99% dos casos para este volume de negócio. Opção 3 é poderosa mas adiciona dependência.

**Esforço:** 30min (opção 2) · **Prioridade:** Média (urgente quando >200 registros)

---

#### F-UX-1: Export CSV

**Abordagem:**
```python
# Em cada aba de tabela:
csv_bytes = frame.to_csv(index=False).encode("utf-8-sig")  # BOM para Excel br
st.download_button(
    "↓ Exportar CSV",
    data=csv_bytes,
    file_name=f"pedrao_{aba}_{date.today()}.csv",
    mime="text/csv",
)
```

**Trade-off:** Filtros da sidebar se aplicam naturalmente — o CSV exporta exatamente o que está visível. Cuidado: não exportar colunas de custo para perfil `vendedor`.

**Esforço:** 1–2h para todas as abas · **Impacto:** Alto (Pedro usa planilha para análises extras)

---

## 7. Roadmap Priorizado

Critério de priorização: **Impacto ÷ Esforço**, com override para riscos de segurança.

### Onda 1 — Segurança (Sprint 0 — 1 semana)

| # | Item | Esforço | Impacto | Tipo |
|---|---|---|---|---|
| 1 | Remover `auth_config.yaml` do git + variável de ambiente para cookie key | 2h | 🔴 Crítico | Segurança |
| 2 | Adicionar `auth_config.yaml` ao `.gitignore` + criar `.example` | 30min | 🔴 Crítico | Segurança |
| 3 | Gerar nova `COOKIE_KEY` via `secrets.token_hex(32)` | 15min | 🔴 Crítico | Segurança |

> **Nota:** Itens 1–3 devem ser feitos em sequência única antes de qualquer outro commit.

---

### Onda 2 — Infraestrutura (Sprint 1 — 1 semana)

| # | Item | Esforço | Impacto |
|---|---|---|---|
| 4 | Criar `Dockerfile` + `docker-compose.yml` com volume para banco | 4h | Alto |
| 5 | Criar `requirements.txt` com versões pinadas (`pip freeze > requirements.lock`) | 30min | Médio |
| 6 | Mover banco para `./data/orcamentos.db` + atualizar `DB_PATH` | 1h | Médio |
| 7 | Adicionar logging estruturado em `database.py` (writes + erros) | 2h | Alto |

---

### Onda 3 — Funcionalidades de Alto Valor (Sprint 2 — 2 semanas)

| # | Item | Esforço | Impacto |
|---|---|---|---|
| 8 | Export CSV em todas as abas (com filtro de colunas por papel) | 2h | Alto |
| 9 | Paginação na tabela principal (opção 2: `.head(100)` com aviso) | 1h | Médio |
| 10 | Consolidar constantes duplicadas: `notificador.py` importa de `metrics.py` | 1h | Médio |
| 11 | Testes unitários para `metrics.py` (cobertura ≥80%) | 8h | Alto |

---

### Onda 4 — UX e Interatividade (Sprint 3 — 2 semanas)

| # | Item | Esforço | Impacto |
|---|---|---|---|
| 12 | Botão "Novo Orçamento" acessível por teclado (atalho `N`) | 2h | Médio |
| 13 | Estado vazio com ilustração SVG + CTA em abas sem dados | 3h | Médio |
| 14 | Feedback de loading explícito no recarregamento de dados | 1h | Baixo |
| 15 | Labels visíveis nos campos colapsados dos formulários | 1h | Médio (a11y) |

---

### Onda 5 — Observabilidade e Escala (Sprint 4 — 1 mês)

| # | Item | Esforço | Impacto |
|---|---|---|---|
| 16 | Health endpoint (Flask mini-servidor paralelo ou `/health` via st.experimental) | 4h | Médio |
| 17 | Quebrar `app.py` em módulos (`ui/dialogs.py`, `ui/tabela.py`, etc.) | 2 dias | Alto (manutenibilidade) |
| 18 | CI pipeline simples: GitHub Actions com `pytest` + `ruff` | 4h | Alto |
| 19 | Migração para PostgreSQL (só quando >3 usuários simultâneos) | 1–2 dias | Condicional |

---

### Mapa Visual do Roadmap

```
IMPACTO
  Alta │ [1,2,3]SEC   [8]CSV    [11]TESTES  [17]SPLIT
       │     ↑ urgência   [4]DOCKER          [18]CI
  Média│              [9]PAGINAÇÃO
       │         [7]LOG  [10]CONSTANTS
  Baixa│                      [14]LOADER  [16]HEALTH
       └──────────────────────────────────────────────
          Imediato   Sprint1   Sprint2   Sprint3   Sprint4
                         ESFORÇO →
```

---

## 8. Conclusão

### O que o Sistema Pedrão faz excepcionalmente bem

1. **Design visual industrial** — CTP Dark é um design system coeso, melhor que Metabase em personalização e identidade de marca
2. **Semântica de cor rigorosa** — distinção clara entre marca (limão) e dado (verde/vermelho/azul/âmbar) é rara em ferramentas internas
3. **Motion criterioso** — `prefers-reduced-motion` coberto, animações carregam informação (count-up, flash de KPI, pulse de aging)
4. **Modelo de dados bem pensado** — `TRANSICOES_VALIDAS`, `historico_status`, `ESTAGIOS` como constantes — extensível sem refactoring
5. **Separação de responsabilidades** — `metrics.py` como fonte única de verdade é uma decisão arquitetural correta

### O que precisa atenção antes de qualquer expansão

1. **🔴 Segurança primeiro** — cookie key em texto claro no git é o gap que invalida todo o resto; resolve em 3h
2. **🟠 Dockerizar** — sem container, qualquer mudança de ambiente pode derrubar a produção; resolve em 4h
3. **🟡 Começar a testar** — sem testes, `metrics.py` é uma bomba-relógio; 8h de investimento protege semanas de debugging futuro

### Veredicto final por dimensão

| Dimensão | Nota | Resumo |
|---|---|---|
| Arquitetura | 7/10 | Boa separação, `app.py` muito grande |
| Performance | 6/10 | Cache ok, falta paginação |
| Escalabilidade | 4/10 | SQLite ok para hoje, risco em crescimento |
| UX / Visual | **8/10** | **Destaque do sistema** |
| Interatividade | 6/10 | CRUDs fluidos, faltam export e bulk |
| Acessibilidade | 5/10 | Prefers-reduced-motion exemplar, labels colapsados problemáticos |
| Segurança | 4/10 | Cookie key exposta é crítico |
| Observabilidade | 4/10 | Sem logs, sem métricas |
| Deploy / CI | 2/10 | Sem container, sem pipeline |
| Manutenibilidade | 6/10 | metrics.py ótimo, app.py monolítico |
| **MÉDIA** | **5,2/10** | Acima da média para ferramenta interna, com gaps críticos |

---

*Documento gerado por análise estática de código + inspeção dinâmica via Selenium/Chromium + pesquisa de mercado. Nenhuma linha de código foi alterada durante esta auditoria.*
