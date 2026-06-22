"""
Dashboard de Orçamentos e Pedidos — Pedro (Diretor de Operações)
Executar: streamlit run app.py
"""
import json
import sqlite3

import pandas as pd
import streamlit as st

from database import DB_PATH, STATUS_VALIDOS, TIPO_CLIENTE_VALIDOS, inicializar

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Painel de Orçamentos | Pedro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa banco na primeira execução
inicializar()


# ── Carregamento de dados ─────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def carregar_dados() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM orcamentos ORDER BY data_orcamento DESC", conn)
    conn.close()
    df["data_orcamento"] = pd.to_datetime(df["data_orcamento"])
    df["margem_bruta"] = df["valor_total"] - df["custo_total_mp"]
    df["margem_pct"] = (df["margem_bruta"] / df["valor_total"] * 100).round(1)
    return df


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def expandir_mp(mp_json: str) -> str:
    try:
        itens = json.loads(mp_json)
        return "\n".join(f"• {i['item']}: {formatar_brl(i['valor'])}" for i in itens)
    except Exception:
        return mp_json


# ── Sidebar — Filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filtros")

    df_raw = carregar_dados()

    # Intervalo de datas
    data_min = df_raw["data_orcamento"].min().date()
    data_max = df_raw["data_orcamento"].max().date()
    intervalo = st.date_input(
        "Intervalo de datas",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

    # Tipo de cliente
    tipos = st.multiselect(
        "Tipo de Cliente",
        options=TIPO_CLIENTE_VALIDOS,
        default=TIPO_CLIENTE_VALIDOS,
    )

    # Status
    status_sel = st.multiselect(
        "Status",
        options=STATUS_VALIDOS,
        default=STATUS_VALIDOS,
    )

    # Busca textual
    busca = st.text_input("Buscar cliente / produto", placeholder="Ex: Caçapava, ACM...")

    st.divider()
    if st.button("Limpar cache e recarregar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ── Aplicar filtros ───────────────────────────────────────────────────────────
df = df_raw.copy()

if len(intervalo) == 2:
    d_ini, d_fim = intervalo
    df = df[
        (df["data_orcamento"].dt.date >= d_ini)
        & (df["data_orcamento"].dt.date <= d_fim)
    ]

if tipos:
    df = df[df["tipo_cliente"].isin(tipos)]

if status_sel:
    df = df[df["status"].isin(status_sel)]

if busca.strip():
    mask = df["nome_cliente"].str.contains(busca, case=False, na=False) | df[
        "descritivo_produto"
    ].str.contains(busca, case=False, na=False)
    df = df[mask]


# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("## 📊 Painel de Orçamentos e Pedidos")
st.caption(f"Exibindo **{len(df)}** de **{len(df_raw)}** registros | Base atualizada a cada 30s")
st.divider()


# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

valor_total = df["valor_total"].sum()
custo_total = df["custo_total_mp"].sum()
margem_total = df["margem_bruta"].sum()
margem_media_pct = (margem_total / valor_total * 100) if valor_total > 0 else 0
qtd_pipeline = df[df["status"].isin([
    "Orçamento gerado",
    "Orçamento aguardando aprovação Pedro",
    "Orçamento aguardando aprovação cliente",
    "Orçamento aprovado",
    "Pedido gerado",
    "Pedido em execução",
])]["valor_total"].sum()

col1.metric("Total em carteira", formatar_brl(valor_total))
col2.metric("Custo total MP", formatar_brl(custo_total))
col3.metric("Margem bruta", formatar_brl(margem_total), f"{margem_media_pct:.1f}%")
col4.metric("Pipeline ativo", formatar_brl(qtd_pipeline))
col5.metric("Registros", len(df))

st.divider()


# ── Abas ──────────────────────────────────────────────────────────────────────
aba_principal, aba_prefeituras, aba_clientes, aba_mp, aba_recusados = st.tabs([
    "📋 Todos os registros",
    "🏛 Prefeituras",
    "🏢 Clientes Diretos",
    "🔩 Matéria-Prima",
    "❌ Recusados",
])


def tabela_principal(frame: pd.DataFrame, key: str) -> None:
    if frame.empty:
        st.info("Nenhum registro encontrado para os filtros aplicados.")
        return

    exibir = frame[[
        "data_orcamento", "tipo_cliente", "nome_cliente",
        "descritivo_produto", "valor_total", "custo_total_mp",
        "margem_bruta", "margem_pct", "status", "motivo_recusa",
    ]].copy()

    exibir["data_orcamento"] = exibir["data_orcamento"].dt.strftime("%d/%m/%Y")
    exibir.columns = [
        "Data", "Tipo", "Cliente / Órgão", "Descritivo",
        "Valor Orçamento", "Custo MP", "Margem R$", "Margem %",
        "Status", "Motivo Recusa",
    ]

    st.dataframe(
        exibir,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor Orçamento": st.column_config.NumberColumn(format="R$ %.2f"),
            "Custo MP": st.column_config.NumberColumn(format="R$ %.2f"),
            "Margem R$": st.column_config.NumberColumn(format="R$ %.2f"),
            "Margem %": st.column_config.NumberColumn(format="%.1f%%"),
            "Descritivo": st.column_config.TextColumn(width="large"),
        },
        key=key,
    )


# ── Aba: Todos ────────────────────────────────────────────────────────────────
with aba_principal:
    # Gráfico de status
    contagem_status = df["status"].value_counts().reset_index()
    contagem_status.columns = ["Status", "Quantidade"]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Distribuição por Status")
        st.bar_chart(contagem_status.set_index("Status"), height=260)
    with c2:
        st.markdown("### Valor por Tipo de Cliente")
        por_tipo = df.groupby("tipo_cliente")["valor_total"].sum().reset_index()
        por_tipo.columns = ["Tipo", "Total"]
        st.dataframe(
            por_tipo.style.format({"Total": "R$ {:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Registros completos")
    tabela_principal(df, key="tab_todos")


# ── Aba: Prefeituras ──────────────────────────────────────────────────────────
with aba_prefeituras:
    df_pref = df[df["tipo_cliente"] == "Prefeitura"]
    st.markdown(f"### Prefeituras — {len(df_pref)} registros")

    if not df_pref.empty:
        por_pref = (
            df_pref.groupby("nome_cliente")
            .agg(
                Orçamentos=("id", "count"),
                Valor_Total=("valor_total", "sum"),
                Custo_MP=("custo_total_mp", "sum"),
            )
            .assign(Margem=lambda x: x["Valor_Total"] - x["Custo_MP"])
            .sort_values("Valor_Total", ascending=False)
        )
        por_pref.columns = ["Orçamentos", "Valor Total", "Custo MP", "Margem"]
        st.dataframe(
            por_pref.style.format({
                "Valor Total": "R$ {:,.2f}",
                "Custo MP": "R$ {:,.2f}",
                "Margem": "R$ {:,.2f}",
            }),
            use_container_width=True,
        )

    st.markdown("---")
    tabela_principal(df_pref, key="tab_pref")


# ── Aba: Clientes Diretos ─────────────────────────────────────────────────────
with aba_clientes:
    df_cli = df[df["tipo_cliente"] == "Cliente Direto"]
    st.markdown(f"### Clientes Diretos — {len(df_cli)} registros")

    if not df_cli.empty:
        por_cli = (
            df_cli.groupby("nome_cliente")
            .agg(
                Orçamentos=("id", "count"),
                Valor_Total=("valor_total", "sum"),
                Custo_MP=("custo_total_mp", "sum"),
            )
            .assign(Margem=lambda x: x["Valor_Total"] - x["Custo_MP"])
            .sort_values("Valor_Total", ascending=False)
        )
        por_cli.columns = ["Orçamentos", "Valor Total", "Custo MP", "Margem"]
        st.dataframe(
            por_cli.style.format({
                "Valor Total": "R$ {:,.2f}",
                "Custo MP": "R$ {:,.2f}",
                "Margem": "R$ {:,.2f}",
            }),
            use_container_width=True,
        )

    st.markdown("---")
    tabela_principal(df_cli, key="tab_cli")


# ── Aba: Matéria-Prima ────────────────────────────────────────────────────────
with aba_mp:
    st.markdown("### Rastreio de Matéria-Prima por Projeto")
    st.caption("Visão detalhada dos insumos adquiridos para cálculo de margem — exigência do Pedro.")

    if df.empty:
        st.info("Nenhum registro.")
    else:
        for _, row in df.iterrows():
            with st.expander(
                f"[{row['data_orcamento'].strftime('%d/%m/%Y')}] {row['nome_cliente']} "
                f"— {formatar_brl(row['valor_total'])} | Margem: {row['margem_pct']:.1f}%"
            ):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**Produto:** {row['descritivo_produto']}")
                    st.markdown(f"**Status:** `{row['status']}`")
                    if row.get("motivo_recusa"):
                        st.error(f"Motivo da recusa: {row['motivo_recusa']}")
                with col_b:
                    st.metric("Valor Orçamento", formatar_brl(row["valor_total"]))
                    st.metric("Custo MP", formatar_brl(row["custo_total_mp"]))
                    st.metric(
                        "Margem Bruta",
                        formatar_brl(row["margem_bruta"]),
                        f"{row['margem_pct']:.1f}%",
                    )

                st.markdown("**Insumos adquiridos:**")
                st.text(expandir_mp(row["materia_prima_json"]))


# ── Aba: Recusados ────────────────────────────────────────────────────────────
with aba_recusados:
    df_rec = df[df["status"] == "Orçamento recusado"]
    st.markdown(f"### Orçamentos Recusados — {len(df_rec)} registros")
    st.caption(f"Valor total de orçamentos perdidos: **{formatar_brl(df_rec['valor_total'].sum())}**")

    if df_rec.empty:
        st.success("Nenhum orçamento recusado nos filtros selecionados.")
    else:
        for _, row in df_rec.iterrows():
            st.error(
                f"**{row['nome_cliente']}** ({row['tipo_cliente']}) — "
                f"{formatar_brl(row['valor_total'])} | "
                f"{row['data_orcamento'].strftime('%d/%m/%Y')}\n\n"
                f"**Motivo:** {row['motivo_recusa']}"
            )
