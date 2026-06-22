"""
Demo CLI — mostra os filtros que Pedro usará no dashboard.
"""
import json
import sqlite3
from datetime import date

import pandas as pd

from database import DB_PATH, inicializar


def brl(v: float) -> str:
    return f"R$ {v:>12,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sep(titulo: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print("="*70)


def carregar() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM orcamentos", conn)
    conn.close()
    df["data_orcamento"] = pd.to_datetime(df["data_orcamento"])
    df["margem_bruta"] = df["valor_total"] - df["custo_total_mp"]
    df["margem_pct"] = (df["margem_bruta"] / df["valor_total"] * 100).round(1)
    return df


def resumo(df: pd.DataFrame) -> None:
    print(f"  Registros    : {len(df)}")
    print(f"  Valor total  : {brl(df['valor_total'].sum())}")
    print(f"  Custo MP     : {brl(df['custo_total_mp'].sum())}")
    print(f"  Margem bruta : {brl(df['margem_bruta'].sum())}")
    if df["valor_total"].sum() > 0:
        pct = df["margem_bruta"].sum() / df["valor_total"].sum() * 100
        print(f"  Margem %     : {pct:.1f}%")


def tabela(df: pd.DataFrame, colunas: list) -> None:
    sub = df[colunas].copy()
    sub["data_orcamento"] = sub["data_orcamento"].dt.strftime("%d/%m/%Y")
    print(sub.to_string(index=False))


# ── Inicializar ───────────────────────────────────────────────────────────────
inicializar()
df = carregar()

print("\n" + "█"*70)
print("  SISTEMA DE RELATÓRIOS — PEDRO (Diretor de Operações)")
print("█"*70)

# ── Filtro 1: Visão geral ─────────────────────────────────────────────────────
sep("FILTRO 1 — Visão Geral (todos os registros)")
resumo(df)

# ── Filtro 2: Somente Prefeituras ─────────────────────────────────────────────
sep("FILTRO 2 — Tipo de Cliente: Prefeitura")
df_pref = df[df["tipo_cliente"] == "Prefeitura"]
resumo(df_pref)
print()
tabela(df_pref, ["data_orcamento", "nome_cliente", "valor_total", "margem_pct", "status"])

# ── Filtro 3: Somente Clientes Diretos ────────────────────────────────────────
sep("FILTRO 3 — Tipo de Cliente: Cliente Direto")
df_cli = df[df["tipo_cliente"] == "Cliente Direto"]
resumo(df_cli)
print()
tabela(df_cli, ["data_orcamento", "nome_cliente", "valor_total", "margem_pct", "status"])

# ── Filtro 4: Status — pedidos em execução ────────────────────────────────────
sep("FILTRO 4 — Status: 'Pedido em execução'")
df_exec = df[df["status"] == "Pedido em execução"]
resumo(df_exec)
print()
tabela(df_exec, ["data_orcamento", "tipo_cliente", "nome_cliente", "valor_total", "margem_pct"])

# ── Filtro 5: Aguardando aprovação do Pedro ───────────────────────────────────
sep("FILTRO 5 — Status: 'Orçamento aguardando aprovação Pedro'")
df_pedro = df[df["status"] == "Orçamento aguardando aprovação Pedro"]
resumo(df_pedro)
print()
tabela(df_pedro, ["data_orcamento", "tipo_cliente", "nome_cliente", "valor_total"])

# ── Filtro 6: Intervalo de datas (Q1 2026) ────────────────────────────────────
sep("FILTRO 6 — Intervalo de Datas: 01/01/2026 a 31/03/2026 (Q1)")
df_q1 = df[
    (df["data_orcamento"].dt.date >= date(2026, 1, 1))
    & (df["data_orcamento"].dt.date <= date(2026, 3, 31))
]
resumo(df_q1)
print()
tabela(df_q1, ["data_orcamento", "tipo_cliente", "nome_cliente", "valor_total", "status"])

# ── Filtro 7: Cruzamento — Prefeitura + Pedido gerado ou em execução ──────────
sep("FILTRO 7 — Prefeitura com pipeline ativo (Pedido gerado / em execução)")
df_cross = df[
    (df["tipo_cliente"] == "Prefeitura")
    & (df["status"].isin(["Pedido gerado", "Pedido em execução"]))
]
resumo(df_cross)
print()
tabela(df_cross, ["data_orcamento", "nome_cliente", "valor_total", "custo_total_mp", "margem_bruta", "status"])

# ── Filtro 8: Recusados — análise de perda ────────────────────────────────────
sep("FILTRO 8 — Orçamentos Recusados (análise de perda)")
df_rec = df[df["status"] == "Orçamento recusado"]
resumo(df_rec)
print()
for _, r in df_rec.iterrows():
    print(f"  [{r['data_orcamento'].strftime('%d/%m/%Y')}] {r['nome_cliente']}")
    print(f"    Valor   : {brl(r['valor_total'])}")
    print(f"    Motivo  : {r['motivo_recusa']}")

# ── Matéria-Prima: rastreio por projeto ───────────────────────────────────────
sep("RASTREIO DE MATÉRIA-PRIMA — Top 3 por custo")
top_mp = df.nlargest(3, "custo_total_mp")
for _, r in top_mp.iterrows():
    print(f"\n  {r['nome_cliente']} ({r['data_orcamento'].strftime('%d/%m/%Y')})")
    print(f"  Valor orçamento: {brl(r['valor_total'])} | Custo MP: {brl(r['custo_total_mp'])} | Margem: {r['margem_pct']:.1f}%")
    itens = json.loads(r["materia_prima_json"])
    for item in itens:
        print(f"    • {item['item']}: {brl(item['valor'])}")

print("\n" + "█"*70)
print("  Todos os filtros executados com sucesso.")
print("  Para o dashboard interativo: streamlit run app.py")
print("█"*70 + "\n")
