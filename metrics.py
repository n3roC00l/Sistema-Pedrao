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
    "aberto":      "#60A5FA",  # blue-400
    "ganho":       "#10B981",  # emerald-500
    "perdido":     "#EF4444",  # red-500
    "desconhecido": "#94A3B8", # slate-400
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


def cor_margem(pct: float) -> str:
    if pct >= LIMIAR_MARGEM_SAUDAVEL:
        return "#10B981"
    if pct >= LIMIAR_MARGEM_ATENCAO:
        return "#F59E0B"
    return "#EF4444"


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
