# Diagnóstico — Sistema Pedrão (Cilla Tech Park)
**Data:** 22/06/2026 | **Versão analisada:** commit d2cf718

---

## Problemas críticos (lógica de negócio)

### KPI-01 — Margem bruta calculada sobre registros perdidos ❌
`app.py:33-34` e `app.py:122-123`:
```python
df["margem_bruta"] = df["valor_total"] - df["custo_total_mp"]  # calcula TODOS
margem_total = df["margem_bruta"].sum()                          # soma TODOS — inclui recusados
```
**Impacto:** Pedro vê margem inflada. Com os dados de seed: margem reportada ≠ margem real (recusados somam R$ 58.000 que nunca serão receita).

### KPI-02 — Faltam win rate, ticket médio e aging ❌
Nenhuma métrica de conversão ou tempo de pipeline está implementada.

---

## Problemas de dados

### DB-01 — `materia_prima_json` como TEXT desnormalizado
`database.py:39`: `materia_prima_json TEXT NOT NULL DEFAULT '[]'`
Impossível agregar "qual insumo pesa mais na margem", filtrar por item de MP, ou auditar sem parsear JSON em Python.

### DB-02 — Sem tabela `historico_status`
Sem timestamp de mudança de status, aging é estimado pela data do orçamento (impreciso) ou inexistente.

### DB-03 — `status` sem CHECK constraint real
A coluna `status TEXT NOT NULL` aceita qualquer string. Um typo (`"Orçamento Aprovado"` vs `"Orçamento aprovado"`) quebra todos os filtros silenciosamente.

---

## Problemas de formatação

### FMT-01 — Dois padrões de moeda coexistindo no mesmo app
- `formatar_brl()` → `R$ 172.000,00` (pt-BR correto)
- `column_config.NumberColumn(format="R$ %.2f")` → `R$ 172000.00` (americano)
- `por_tipo.style.format({"Total": "R$ {:,.2f}"})` → `R$ 172,000.00` (americano com vírgula)

Pedro pode encontrar 3 formatos diferentes ao cruzar números entre seções.

---

## Problemas visuais

### VIS-01 — Vermelho semântico queimado
Vermelho/salmon/bordas avermelhadas usados em decoração de UI → quando aparecer em dado (perda, alerta), Pedro não diferencia.

### VIS-02 — Gráfico de status quebrado
`app.py:194`: `st.bar_chart(contagem_status.set_index("Status"), height=260)` — labels cortados, todas as barras no mesmo tom azul default, sem valores, sem ordem lógica de funil.

### VIS-03 — Chrome do Streamlit visível
Menu hambúrguer, botão "Deploy", rodapé "Made with Streamlit" — parece demo, não produto.

---

## Números esperados (pós-correção)

Com os dados de seed, os KPIs corretos são:

| KPI | Valor |
|-----|-------|
| Pipeline aberto | R$ 1.106.500,00 |
| Valor ganho | R$ 957.900,00 |
| Custo MP (ganhos) | R$ 563.300,00 |
| Margem bruta | R$ 394.600,00 |
| Margem % | 41,2% |
| Valor perdido | R$ 58.000,00 |
| Win rate (valor) | 94,3% |
| Win rate (contagem) | 80,0% |
| Ticket médio ganho | R$ 119.737,50 |
| Negócios em aberto | 6 |
| Aging alertas (+30d) | 6 (todos parados) |

Se os KPIs no painel divergirem destes, há bug.
