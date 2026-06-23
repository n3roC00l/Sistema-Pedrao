"""
Módulo central de métricas e KPIs — Painel Pedrão / Cilla Tech Park.
Toda lógica financeira passa por aqui. Nunca recalcule em outro lugar.
"""
import pandas as pd

# ── Funil de estágios ────────────────────────────────────────────────────────
ESTAGIOS: dict[str, list[str]] = {
    "aberto": [
        "Orçamento gerado",
        "Orçamento aguardando aprovação Pedro",
        "Orçamento aguardando aprovação cliente",
    ],
    "ganho": [
        "Orçamento aprovado",
        "Pedido gerado",
        "Pedido em execução",
        "Pedido entregue",
    ],
    "perdido": [
        "Orçamento recusado",
    ],
}

# Ponto único de configuração
AGING_ALERTA_DIAS: int = 30
LIMIAR_MARGEM_SAUDAVEL: float = 40.0  # % — verde acima
LIMIAR_MARGEM_ATENCAO: float = 25.0   # % — vermelho abaixo, âmbar entre

# Ordem canônica dos status no funil (para gráficos)
ORDEM_STATUS = [
    "Orçamento gerado",
    "Orçamento aguardando aprovação Pedro",
    "Orçamento aguardando aprovação cliente",
    "Orçamento aprovado",
    "Pedido gerado",
    "Pedido em execução",
    "Pedido entregue",
    "Orçamento recusado",
]

COR_ESTAGIO: dict[str, str] = {
    "aberto":       "#7DD3FC",  # sky-300   — dado semântico (nunca limão)
    "ganho":        "#34D399",  # emerald-400
    "perdido":      "#F87171",  # red-400
    "desconhecido": "#626B7A",  # neutral
}

# Probabilidade de fechamento por estágio (usada no pipeline ponderado)
PROBABILIDADE_STATUS: dict[str, float] = {
    "Orçamento gerado":                       0.20,
    "Orçamento aguardando aprovação Pedro":   0.35,
    "Orçamento aguardando aprovação cliente": 0.55,
    "Orçamento aprovado":                     0.85,
    "Pedido gerado":                          0.95,
    "Pedido em execução":                     1.00,
    "Pedido entregue":                        1.00,
    "Orçamento recusado":                     0.00,
}


def classificar_estagio(status: str) -> str:
    for estagio, statuses in ESTAGIOS.items():
        if status in statuses:
            return estagio
    return "desconhecido"


def format_brl(valor: float | None) -> str:
    """Formata valor monetário em pt-BR. Única função de formatação no sistema."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "—"
    return f"R$ {valor:_.2f}".replace(".", ",").replace("_", ".")


def format_pct(valor: float | None, casas: int = 1) -> str:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "—"
    return f"{valor:.{casas}f}%".replace(".", ",")


def calcular_pipeline_ponderado(df: pd.DataFrame) -> float:
    """Soma valor_total × probabilidade apenas para o estágio aberto."""
    if df.empty:
        return 0.0
    aberto = df[df["status"].map(classificar_estagio) == "aberto"].copy()
    if aberto.empty:
        return 0.0
    aberto["peso"] = aberto["status"].map(PROBABILIDADE_STATUS).fillna(0.0)
    return float((aberto["valor_total"] * aberto["peso"]).sum())


def calcular_custo_vs_realizado(df: pd.DataFrame) -> dict:
    """Compara custo_total_mp (orçado) com custo_realizado_mp nos pedidos entregues."""
    entregues = df[
        (df["status"] == "Pedido entregue") & df["custo_realizado_mp"].notna()
    ] if "custo_realizado_mp" in df.columns else pd.DataFrame()

    if entregues.empty:
        return {"orcado": 0.0, "realizado": 0.0, "delta": 0.0, "delta_pct": 0.0, "n": 0}

    orcado    = float(entregues["custo_total_mp"].sum())
    realizado = float(entregues["custo_realizado_mp"].sum())
    delta     = realizado - orcado
    delta_pct = (delta / orcado * 100) if orcado > 0 else 0.0
    return {"orcado": orcado, "realizado": realizado, "delta": delta, "delta_pct": delta_pct, "n": len(entregues)}


def montar_contrato_graficos(df: pd.DataFrame) -> dict:
    """Monta o contrato de dados para o componente neon de gráficos (Visão Geral)."""
    _empty_tipo = lambda: {"total": 0.0, "negocios": 0, "valor_ganho": 0.0, "win_rate": 0.0, "margem_pct": 0.0, "top": []}
    _tipos_vazios = {"Prefeitura": _empty_tipo(), "Cliente Direto": _empty_tipo()}

    if df.empty:
        return {"total_carteira": 0.0, "funil": [], "tipos": _tipos_vazios}

    sv = df.groupby("status")["valor_total"].sum().reset_index()
    sv["grupo"] = sv["status"].map(classificar_estagio)
    sv["ordem"] = sv["status"].map({s: i for i, s in enumerate(ORDEM_STATUS)})
    sv = sv[sv["valor_total"] > 0].sort_values("ordem", ascending=False)
    funil = [
        {
            "status": r["status"],
            "label":  LABEL_CURTO.get(r["status"], r["status"]),
            "valor":  float(r["valor_total"]),
            "grupo":  r["grupo"],
        }
        for _, r in sv.iterrows()
    ]

    tipos: dict = {}
    for tipo in ("Prefeitura", "Cliente Direto"):
        sub = df[df["tipo_cliente"] == tipo]
        kpis = calcular_kpis(sub)
        top = (
            sub.nlargest(3, "valor_total")[["nome_cliente", "valor_total"]].to_dict("records")
            if not sub.empty else []
        )
        tipos[tipo] = {
            "total":       float(sub["valor_total"].sum()) if not sub.empty else 0.0,
            "negocios":    len(sub),
            "valor_ganho": kpis["valor_ganho"],
            "win_rate":    round(kpis["win_rate_valor"] * 100, 1),
            "margem_pct":  round(kpis["margem_pct"], 1),
            "top":         [{"nome": r["nome_cliente"], "valor": float(r["valor_total"])} for r in top],
        }

    return {"total_carteira": float(df["valor_total"].sum()), "funil": funil, "tipos": tipos}


def cor_margem(pct: float) -> str:
    if pct >= LIMIAR_MARGEM_SAUDAVEL:
        return "#10B981"
    if pct >= LIMIAR_MARGEM_ATENCAO:
        return "#F59E0B"
    return "#EF4444"


LABEL_CURTO: dict[str, str] = {
    "Orçamento gerado":                       "Orc. gerado",
    "Orçamento aguardando aprovação Pedro":   "Aguarda Pedro",
    "Orçamento aguardando aprovação cliente": "Aguarda cliente",
    "Orçamento aprovado":                     "Orc. aprovado",
    "Pedido gerado":                          "Ped. gerado",
    "Pedido em execução":                     "Em execução",
    "Pedido entregue":                        "Entregue",
    "Orçamento recusado":                     "Recusado",
}


def calcular_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula todos os KPIs a partir do DataFrame filtrado.

    Regra: margem bruta e margem % incidem SOMENTE sobre estágio 'ganho'.
    Orçamentos perdidos e abertos nunca entram em cálculo de margem.
    """
    if df.empty:
        return {k: 0 for k in (
            "valor_ganho", "custo_ganho", "margem_bruta", "margem_pct",
            "valor_perdido", "pipeline", "n_ganho", "n_perdido", "n_aberto",
            "win_rate_valor", "win_rate_contagem", "ticket_medio",
            "total_registros", "n_aging_alertas",
        )}

    df = df.copy()
    df["estagio"] = df["status"].map(classificar_estagio)

    df_ganho   = df[df["estagio"] == "ganho"]
    df_perdido = df[df["estagio"] == "perdido"]
    df_aberto  = df[df["estagio"] == "aberto"]

    valor_ganho  = float(df_ganho["valor_total"].sum())
    custo_ganho  = float(df_ganho["custo_total_mp"].sum())
    margem_bruta = valor_ganho - custo_ganho
    margem_pct   = (margem_bruta / valor_ganho * 100) if valor_ganho > 0 else 0.0

    valor_perdido = float(df_perdido["valor_total"].sum())
    pipeline      = float(df_aberto["valor_total"].sum())

    n_ganho    = len(df_ganho)
    n_perdido  = len(df_perdido)
    n_aberto   = len(df_aberto)
    n_decidido = n_ganho + n_perdido

    win_rate_valor    = valor_ganho / (valor_ganho + valor_perdido) if (valor_ganho + valor_perdido) > 0 else 0.0
    win_rate_contagem = n_ganho / n_decidido if n_decidido > 0 else 0.0
    ticket_medio      = valor_ganho / n_ganho if n_ganho > 0 else 0.0

    n_aging = 0
    if "aging_dias" in df_aberto.columns and not df_aberto.empty:
        n_aging = int((df_aberto["aging_dias"] > AGING_ALERTA_DIAS).sum())

    return {
        "valor_ganho":        valor_ganho,
        "custo_ganho":        custo_ganho,
        "margem_bruta":       margem_bruta,
        "margem_pct":         margem_pct,
        "valor_perdido":      valor_perdido,
        "pipeline":           pipeline,
        "n_ganho":            n_ganho,
        "n_perdido":          n_perdido,
        "n_aberto":           n_aberto,
        "win_rate_valor":     win_rate_valor,
        "win_rate_contagem":  win_rate_contagem,
        "ticket_medio":       ticket_medio,
        "total_registros":    len(df),
        "n_aging_alertas":    n_aging,
    }
