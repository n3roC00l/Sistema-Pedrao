# Sistema Pedrão — Painel de Orçamentos e Pedidos

> Sistema de controle e rastreabilidade do pipeline de vendas e execução de projetos, desenvolvido para o **Pedro (Diretor de Operações)**.

---

## O que é este sistema

O **Sistema Pedrão** é um painel interativo de gestão operacional que centraliza todos os orçamentos e pedidos da empresa em um único lugar. Ele foi construído para dar ao Pedro visibilidade total sobre:

- Quais propostas estão em negociação e em qual etapa
- Quais pedidos estão em execução ou já foram entregues
- Quanto cada projeto custa em matéria-prima e qual é a margem bruta real
- A separação clara entre **Clientes Diretos** (empresas e pessoas físicas) e **Prefeituras** (órgãos públicos licitantes), que possuem dinâmicas e riscos distintos

---

## Para que serve

| Necessidade do Pedro | Como o sistema resolve |
|---|---|
| Saber quais orçamentos precisam da sua aprovação | Filtro por status `Orçamento aguardando aprovação Pedro` |
| Acompanhar pedidos em andamento | Filtro por status `Pedido em execução` |
| Comparar performance entre Clientes Diretos e Prefeituras | Abas isoladas com KPIs por segmento |
| Rastrear custo de insumos por projeto | Aba "Matéria-Prima" com detalhamento item a item |
| Entender por que orçamentos foram perdidos | Aba "Recusados" com campo obrigatório de motivo |
| Analisar o pipeline por período | Filtro de intervalo de datas no sidebar |

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Banco de dados | SQLite (arquivo local `orcamentos.db`) |
| Manipulação de dados | Pandas |
| Dashboard interativo | Streamlit |
| Linguagem | Python 3.10+ |

---

## Estrutura do projeto

```
pedro_dashboard/
├── database.py        # Schema SQLite, seed de dados e conexão
├── app.py             # Dashboard Streamlit (interface principal)
├── demo_filtros.py    # Demonstração CLI de todos os filtros disponíveis
├── requirements.txt   # Dependências Python
├── .gitignore         # Exclui .db e cache do versionamento
└── README.md          # Este arquivo
```

---

## Schema do banco de dados

Tabela `orcamentos`:

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `data_orcamento` | TEXT (DATE) | Data de criação do orçamento |
| `tipo_cliente` | TEXT (ENUM) | `"Cliente Direto"` ou `"Prefeitura"` |
| `nome_cliente` | TEXT | Nome da empresa ou órgão público |
| `descritivo_produto` | TEXT | Escopo completo do projeto orçado |
| `valor_total` | REAL | Valor total do orçamento em R$ |
| `materia_prima_json` | TEXT (JSON) | Lista de insumos com item e valor individual |
| `custo_total_mp` | REAL | Soma calculada dos custos de matéria-prima |
| `status` | TEXT (ENUM) | Etapa atual do orçamento/pedido (ver abaixo) |
| `motivo_recusa` | TEXT (nullable) | Preenchido obrigatoriamente quando recusado |

### Status disponíveis (fluxo linear)

```
Orçamento gerado
    └─► Orçamento aguardando aprovação Pedro
            └─► Orçamento aguardando aprovação cliente
                    ├─► Orçamento aprovado
                    │       └─► Pedido gerado
                    │               └─► Pedido em execução
                    │                       └─► Pedido entregue
                    └─► Orçamento recusado  (exige motivo_recusa)
```

---

## Como rodar localmente

**1. Clone o repositório**
```bash
git clone https://github.com/n3roC00l/Sistema-Pedrao.git
cd Sistema-Pedrao
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Suba o dashboard**
```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador. O banco SQLite é criado e populado automaticamente na primeira execução.

**Opcional — demonstração dos filtros via terminal:**
```bash
python demo_filtros.py
```

---

## Filtros disponíveis no dashboard

- **Status** — qualquer combinação dos 8 status do pipeline
- **Tipo de Cliente** — visão isolada para Prefeituras ou Clientes Diretos
- **Intervalo de datas** — corte por período (útil para fechamento mensal/trimestral)
- **Busca textual** — pesquisa livre por nome de cliente ou descritivo do produto

Os KPIs (valor total, custo de MP, margem bruta e pipeline ativo) recalculam automaticamente conforme os filtros são aplicados.

---

## Próximos passos sugeridos

- [ ] Tela de cadastro/edição de orçamentos diretamente pelo Streamlit
- [ ] Exportação para Excel (`.xlsx`) via botão no dashboard
- [ ] Histórico de mudanças de status com timestamp e usuário responsável
- [ ] Autenticação por usuário (Pedro vs. equipe comercial vs. leitura)
- [ ] Alertas automáticos para orçamentos parados há mais de X dias
- [ ] Integração com sistema de NF-e para reconciliação de custos reais de MP

---

## Licença

Uso interno. Todos os direitos reservados.
