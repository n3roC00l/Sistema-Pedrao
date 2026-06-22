# Sistema Pedrão — Painel de Operações

> Painel interno de gestão do pipeline comercial e execução de projetos da **Cilla Tech Park** — empresa de esquadrias, fachadas e coberturas metálicas.

Desenvolvido para o **Pedro (Diretor de Operações)**. O objetivo é decisão rápida: o que precisa de aprovação, o que está travado, quanto está ganhando de verdade, o que perdeu e por quê.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Banco de dados | SQLite (`orcamentos.db`) |
| Dados | Pandas |
| Dashboard | Streamlit ≥ 1.35 |
| Gráficos | Plotly |
| Linguagem | Python 3.10+ |

---

## Como rodar

```bash
git clone https://github.com/n3roC00l/Sistema-Pedrao.git
cd Sistema-Pedrao
pip install -r requirements.txt
streamlit run app.py
```

Acesse `http://localhost:8501`. O banco SQLite é criado e populado automaticamente na primeira execução — nenhuma configuração manual necessária.

Para rodar em segundo plano:

```bash
nohup streamlit run app.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
```

---

## Estrutura do projeto

```
Sistema-Pedrao/
├── app.py              # UI principal (Streamlit)
├── metrics.py          # KPIs e lógica financeira — fonte de verdade única
├── database.py         # Schema v2, migração automática e seed
├── requirements.txt    # Dependências
├── DIAGNOSTICO.md      # Relatório técnico da refatoração
├── .streamlit/
│   └── config.toml     # Tema e configurações do Streamlit
└── orcamentos.db       # Banco SQLite (gerado automaticamente)
```

---

## KPIs do painel

### Linha comercial
| KPI | Definição |
|---|---|
| **Pipeline Aberto** | Valor total em negociação (não decidido) |
| **Valor Ganho** | Soma dos orçamentos aprovados + pedidos em andamento/entregues |
| **Valor Perdido** | Soma dos orçamentos recusados (nunca entra em margem) |
| **Negócios Parados** | Itens em aberto sem mudança de status há mais de 30 dias |

### Linha de rentabilidade
| KPI | Definição |
|---|---|
| **Margem Bruta** | Valor ganho − custo de MP dos negócios ganhos |
| **Margem %** | Margem bruta ÷ valor ganho |
| **Win Rate (valor)** | Valor ganho ÷ (ganho + perdido) |
| **Ticket Médio Ganho** | Valor ganho ÷ número de negócios ganhos |

> **Regra fundamental:** margem bruta e margem % incidem somente sobre o estágio **Ganho**. Orçamentos perdidos ou em aberto nunca entram no cálculo de margem.

---

## Funil de status

```
Orçamento gerado  ──────────────────────────────── ABERTO
Orçamento aguardando aprovação Pedro  ──────────── ABERTO
Orçamento aguardando aprovação cliente  ────────── ABERTO
    │
    ├── Orçamento aprovado  ──────────────────────── GANHO
    │       └── Pedido gerado
    │               └── Pedido em execução
    │                       └── Pedido entregue
    │
    └── Orçamento recusado  ───────────────────── PERDIDO
```

---

## Schema do banco (v2)

### `orcamentos`
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `data_orcamento` | TEXT (DATE) | Data de criação |
| `tipo_cliente` | TEXT CHECK | `"Cliente Direto"` ou `"Prefeitura"` |
| `nome_cliente` | TEXT | Empresa ou órgão |
| `descritivo_produto` | TEXT | Escopo do projeto |
| `valor_total` | REAL | Valor em R$ |
| `custo_total_mp` | REAL | Soma dos itens de MP (denormalizado) |
| `status` | TEXT CHECK | Enum — 8 valores válidos |
| `motivo_recusa` | TEXT | Preenchido quando recusado |

### `itens_materia_prima`
Relação 1:N com `orcamentos`. Cada insumo é um registro: `orcamento_id`, `descricao_item`, `valor`.

### `historico_status`
Rastreabilidade de mudanças: `orcamento_id`, `status`, `timestamp`, `responsavel`. Viabiliza o cálculo de aging.

> Bancos no schema v1 (com `materia_prima_json`) são migrados automaticamente na primeira inicialização — sem perda de dados.

---

## Segmentos de cliente

- **Cliente Direto** — empresas e pessoas físicas, dinâmica comercial padrão
- **Prefeitura** — órgãos públicos licitantes, processo e risco distintos

Cada segmento tem aba própria com KPIs isolados (margem, win rate, valor por órgão).

---

## Próximos passos sugeridos

- [ ] Tela de cadastro e edição de orçamentos no próprio Streamlit
- [ ] Exportação para Excel via botão no painel
- [ ] Autenticação (Pedro vs. equipe comercial vs. leitura)
- [ ] Integração com NF-e para reconciliação de custos reais de MP

---

## Licença

Uso interno — Cilla Tech Park. Todos os direitos reservados.
