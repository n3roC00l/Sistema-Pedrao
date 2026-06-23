"""
Painel de Operações — Cilla Tech Park
Diretor: Pedro | Executar: streamlit run app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from database import (
    DB_PATH,
    STATUS_VALIDOS,
    TIPO_CLIENTE_VALIDOS,
    TRANSICOES_VALIDAS,
    arquivar_orcamento,
    atualizar_cliente,
    atualizar_custo_realizado,
    atualizar_orcamento,
    atualizar_status,
    inicializar,
    inserir_orcamento,
)
from metrics import (
    AGING_ALERTA_DIAS,
    COR_ESTAGIO,
    LIMIAR_MARGEM_ATENCAO,
    LIMIAR_MARGEM_SAUDAVEL,
    ORDEM_STATUS,
    calcular_custo_vs_realizado,
    calcular_kpis,
    calcular_pipeline_ponderado,
    classificar_estagio,
    format_brl,
    format_pct,
)

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="CTP | Painel de Operações",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicializar()

# ── Logo (versão dark) ────────────────────────────────────────────────────────
# IMPORTANTE: assets/logo_dark.svg é um placeholder geométrico.
# Substituir pelo SVG oficial da Cilla Tech Park (hexágonos limão + wordmark branco).
_LOGO_PATH = Path(__file__).parent / "assets" / "logo_dark.svg"
if _LOGO_PATH.exists():
    st.logo(str(_LOGO_PATH))

# ── Autenticação ──────────────────────────────────────────────────────────────

_AUTH_FILE = Path(__file__).parent / "auth_config.yaml"
with open(_AUTH_FILE, encoding="utf-8") as _f:
    _auth_cfg = yaml.load(_f, Loader=SafeLoader)

_authenticator = stauth.Authenticate(
    _auth_cfg["credentials"],
    _auth_cfg["cookie"]["name"],
    _auth_cfg["cookie"]["key"],
    _auth_cfg["cookie"]["expiry_days"],
)

_authenticator.login(location="main")

if st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.stop()

_role = _auth_cfg["credentials"]["usernames"].get(
    st.session_state.get("username", ""), {}
).get("role", "vendedor")

# ── Sistema de design — CTP Dark (quase-preto + verde-limão da marca) ─────────
# Tokens centralizados aqui e no config.toml. Nenhum hex solto fora deste bloco
# ou das constantes abaixo.
#
# REGRA INEGOCIÁVEL: limão #9ACA3C aparece SOMENTE na moldura da marca
# (logo, aba ativa, botão primário, anel de foco). Nunca em dado.
# Verde de dado (#34D399 esmeralda) e verde de marca (limão) são cores distintas
# por propósito — permitem distinguir "aba ativa" de "negócio ganho" num relance.
st.markdown("""
<style>
/*
 * CTP Dark — Design Tokens
 * ─────────────────────────────────────────────────────────────────────────────
 * Base       #0A0B0F   Surface    #15171D   Elevated   #1E2129
 * Border:    sutil #20242E   padrão #2A2E38   forte #3A3F4C
 * Texto:     primary #F2F4F8   secondary #9AA3B2   tertiary #626B7A
 * Marca:     Limão #9ACA3C / hover #A9D94E  (SOMENTE moldura)
 * Semântica: ganho  #34D399 / bg #08352A
 *            atenção #FBBF24 / bg #3A2A08
 *            perda  #F87171 / bg #3A1414
 *            aberto #7DD3FC / bg #0C2E42
 */

/* ── Chrome do Streamlit ── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
[data-testid="stHeader"] { display: none !important; visibility: hidden !important; }

/* ── Tipografia global ── */
* { font-variant-numeric: tabular-nums; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #15171D;
    border-right: 1px solid #20242E;
}

/* ── KPI via st.metric (fallback / abas secundárias) ── */
[data-testid="metric-container"] {
    background: #15171D;
    border: 1px solid #2A2E38;
    border-radius: 10px;
    padding: 16px 20px 14px;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #9AA3B2 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: #F2F4F8 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid #2A2E38; }
[data-testid="stTabs"] button[role="tab"] {
    font-size: 0.82rem;
    font-weight: 600;
    color: #626B7A;
    padding: 10px 16px;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-bottom-color 0.2s;
}
[data-testid="stTabs"] button[role="tab"]:hover { color: #9AA3B2; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #9ACA3C;
    border-bottom: 2px solid #9ACA3C;
    background: transparent;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrame"] [role="gridcell"] { white-space: nowrap; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #15171D;
    border: 1px solid #2A2E38;
    border-radius: 8px;
    margin-bottom: 6px;
}

/* ── Dividers ── */
hr { border-color: #20242E !important; }

/* ── Elevated layer — dialogs/modais ganham profundidade ── */
[data-testid="stModal"] > div,
div[role="dialog"],
[data-baseweb="dialog"] { background: #1E2129 !important; }

/* ── Badges de status (views de detalhe / expanders) ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-ganho   { background: #08352A; color: #34D399; }
.badge-aberto  { background: #0C2E42; color: #7DD3FC; }
.badge-pedro   { background: #3A2A08; color: #FBBF24; }
.badge-perdido { background: #3A1414; color: #F87171; }

/* ── Aging ── */
.aging-alert { color: #F87171; font-weight: 600; }
.aging-warn  { color: #FBBF24; }

/* ── KPI section label ── */
.kpi-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #626B7A;
    margin-bottom: 8px;
    margin-top: 4px;
}

/* ── Barra de ação contextual (tabela) ── */
.action-bar {
    background: #1E2129;
    border: 1px solid #2A2E38;
    border-radius: 8px;
    padding: 10px 16px;
    margin-top: 6px;
}
.action-bar-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #F2F4F8;
}
.action-bar-sub {
    font-size: 0.72rem;
    color: #626B7A;
    margin-top: 2px;
}

/* ──────────────────── MOTION ─────────────────────────────────────────────── */
/* Princípio: movimento carrega informação, não decora.
   Toda animação é coberta pela trava de movimento reduzido abaixo. */

/* ── KPI flash (mudança de valor no refresh) ── */
@keyframes kpiFlash { 0% { background: #1B2417; } 100% { background: #15171D; } }
.kpi-flash { animation: kpiFlash 0.6s ease-out; }

/* ── Aging pulse dot ── */
@keyframes pulseAging { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }
.aging-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
    animation: pulseAging 1.9s ease-in-out infinite;
}
.aging-dot-warn  { background: #FBBF24; }
.aging-dot-alert { background: #F87171; }

/* ── Skeleton shimmer (refresh) ── */
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}
.skeleton {
    background: #15171D;
    background-image: linear-gradient(90deg, #15171D 0%, #1E2129 50%, #15171D 100%);
    background-size: 800px 100%;
    animation: shimmer 1.2s infinite linear;
    border-radius: 6px;
    height: 14px;
    margin-bottom: 6px;
}

/* ── Entrada em cascata (só 1ª carga, controlada por session_state) ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0);   }
}
.kpi-enter   { animation: fadeUp 0.35s ease-out both; }
.kpi-enter-1 { animation-delay: 0.04s; }
.kpi-enter-2 { animation-delay: 0.10s; }
.kpi-enter-3 { animation-delay: 0.17s; }
.kpi-enter-4 { animation-delay: 0.24s; }

/* ── Sublinhado de aba deslizante ── */
/* Transição já coberta por border-bottom-color 0.2s na regra das tabs acima.
   Fallback: se o seletor do indicador interno mudar entre versões do Streamlit,
   a cor de aba ativa em limão mantém a identidade sem o deslize. */

/* ── Timeline de status (dialog de detalhe) ── */
.tl-wrap { padding: 8px 0; }
.tl-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    opacity: 0;
    animation: fadeUp 0.3s ease-out both;
}
.tl-dot-wrap { display: flex; flex-direction: column; align-items: center; min-width: 16px; }
.tl-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    border: 2px solid #2A2E38;
    background: #1E2129;
    flex-shrink: 0;
    margin-top: 3px;
}
.tl-dot.done  { background: #34D399; border-color: #34D399; }
.tl-dot.atual { background: #9ACA3C; border-color: #9ACA3C; box-shadow: 0 0 6px #9ACA3C55; }
.tl-dot.perdido { background: #F87171; border-color: #F87171; }
@keyframes growDown { from { transform: scaleY(0); } to { transform: scaleY(1); } }
.tl-line {
    width: 2px;
    background: #2A2E38;
    flex-grow: 1;
    min-height: 20px;
    transform-origin: top;
    animation: growDown 0.25s ease-out both;
}
.tl-content { padding-bottom: 16px; }
.tl-status { font-size: 0.82rem; font-weight: 600; color: #F2F4F8; }
.tl-meta   { font-size: 0.72rem; color: #626B7A; margin-top: 3px; }

/* ── Trava de movimento reduzido — obrigatória, cobre TODO o motion acima ── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ── Formulário: novo orçamento ────────────────────────────────────────────────

@st.dialog("Novo Orçamento", width="large")
def dialog_novo_orcamento() -> None:
    if "_mp" not in st.session_state:
        st.session_state["_mp"] = [{"item": "", "valor": 0.0}]

    from datetime import date

    col_a, col_b = st.columns(2)
    data_orc = col_a.date_input(
        "Data do orçamento", value=date.today(), format="DD/MM/YYYY"
    )
    tipo = col_b.selectbox("Tipo de cliente", TIPO_CLIENTE_VALIDOS)

    nome = st.text_input("Cliente / Órgão", placeholder="Ex: Construtora XYZ Ltda")
    descritivo = st.text_area(
        "Descritivo do produto / serviço",
        placeholder="Descreva o escopo do projeto orçado…",
        height=90,
    )

    col_v, col_s = st.columns(2)
    valor = col_v.number_input(
        "Valor total (R$)", min_value=0.01, step=1000.0, format="%.2f"
    )
    status_ini = col_s.selectbox(
        "Status inicial",
        STATUS_VALIDOS,
        index=0,
    )

    motivo = None
    if status_ini == "Orçamento recusado":
        motivo = st.text_area("Motivo da recusa", placeholder="Descreva o motivo…")

    st.markdown("**Itens de Matéria-Prima**")
    itens = st.session_state["_mp"]
    for i, it in enumerate(itens):
        c1, c2, c3 = st.columns([4, 2, 1])
        itens[i]["item"]  = c1.text_input("Insumo",    value=it["item"],  key=f"_mp_n{i}", label_visibility="collapsed", placeholder=f"Insumo {i+1}")
        itens[i]["valor"] = c2.number_input("Valor R$", value=it["valor"], key=f"_mp_v{i}", label_visibility="collapsed", min_value=0.0, step=500.0, format="%.2f")
        if c3.button("✕", key=f"_mp_r{i}", help="Remover", disabled=len(itens) == 1):
            itens.pop(i)
            st.rerun()

    custo_atual = sum(i["valor"] for i in itens if i["valor"] > 0)
    col_add, col_custo = st.columns([1, 2])
    col_add.button(
        "+ Adicionar insumo",
        on_click=lambda: st.session_state["_mp"].append({"item": "", "valor": 0.0}),
    )
    if custo_atual > 0:
        margem_prev = valor - custo_atual if valor > 0 else 0
        cor = "#34D399" if margem_prev >= 0 else "#F87171"
        col_custo.markdown(
            f'<div style="text-align:right;padding-top:8px;font-size:0.82rem;color:#9AA3B2">'
            f'Custo MP: <b style="color:#F2F4F8">{format_brl(custo_atual)}</b> &nbsp;·&nbsp; '
            f'Margem prévia: <b style="color:{cor}">{format_brl(margem_prev)}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    erros = []
    if not nome.strip():
        erros.append("Informe o nome do cliente.")
    if not descritivo.strip():
        erros.append("Informe o descritivo do produto.")
    if valor <= 0:
        erros.append("Valor total deve ser maior que zero.")
    if status_ini == "Orçamento recusado" and not (motivo or "").strip():
        erros.append("Motivo da recusa é obrigatório quando o status é Recusado.")

    col_btn, col_aviso = st.columns([1, 3])
    salvar = col_btn.button("Salvar", type="primary", width="stretch")

    if salvar:
        if erros:
            for e in erros:
                st.error(e)
        else:
            mp_validos = [i for i in itens if i["item"].strip() and i["valor"] > 0]
            if not mp_validos:
                st.warning("Nenhum item de MP válido — o custo ficará zerado.")
            inserir_orcamento(
                data_orcamento   = str(data_orc),
                tipo_cliente     = tipo,
                nome_cliente     = nome.strip(),
                descritivo_produto = descritivo.strip(),
                valor_total      = valor,
                status           = status_ini,
                motivo_recusa    = motivo,
                mp_itens         = itens,
            )
            st.toast(f"Orçamento de {nome.strip()} criado com sucesso", icon="✅")
            st.cache_data.clear()
            del st.session_state["_mp"]
            st.rerun()


@st.dialog("Editar Orçamento", width="large")
def dialog_editar_orcamento(orcamento_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM orcamentos WHERE id = ?", (orcamento_id,)).fetchone()
    itens_db = conn.execute(
        "SELECT descricao_item, valor FROM itens_materia_prima WHERE orcamento_id = ? ORDER BY valor DESC",
        (orcamento_id,),
    ).fetchall()
    conn.close()

    if not row:
        st.error("Orçamento não encontrado.")
        return

    key = f"_edit_mp_{orcamento_id}"
    if key not in st.session_state:
        st.session_state[key] = [{"item": r["descricao_item"], "valor": r["valor"]} for r in itens_db] or [{"item": "", "valor": 0.0}]

    from datetime import date as date_type
    col_a, col_b = st.columns(2)
    tipo = col_a.selectbox("Tipo de cliente", TIPO_CLIENTE_VALIDOS,
                           index=TIPO_CLIENTE_VALIDOS.index(row["tipo_cliente"]))
    nome = col_b.text_input("Cliente / Órgão", value=row["nome_cliente"])
    descritivo = st.text_area("Descritivo", value=row["descritivo_produto"], height=80)
    valor = st.number_input("Valor total (R$)", value=float(row["valor_total"]),
                            min_value=0.01, step=1000.0, format="%.2f")

    st.markdown("**Itens de Matéria-Prima**")
    itens = st.session_state[key]
    for i, it in enumerate(itens):
        c1, c2, c3 = st.columns([4, 2, 1])
        itens[i]["item"]  = c1.text_input("Insumo",    value=it["item"],  key=f"{key}_n{i}", label_visibility="collapsed")
        itens[i]["valor"] = c2.number_input("Valor R$", value=it["valor"], key=f"{key}_v{i}", label_visibility="collapsed", min_value=0.0, step=500.0, format="%.2f")
        if c3.button("✕", key=f"{key}_r{i}", disabled=len(itens) == 1):
            itens.pop(i); st.rerun()

    st.button("+ Adicionar insumo", on_click=lambda: st.session_state[key].append({"item": "", "valor": 0.0}))
    st.divider()

    if st.button("Salvar alterações", type="primary"):
        erros = []
        if not nome.strip():
            erros.append("Informe o nome do cliente.")
        if not descritivo.strip():
            erros.append("Informe o descritivo.")
        if valor <= 0:
            erros.append("Valor deve ser maior que zero.")
        if erros:
            for e in erros: st.error(e)
        else:
            atualizar_orcamento(
                orcamento_id,
                nome_cliente=nome.strip(),
                descritivo_produto=descritivo.strip(),
                valor_total=valor,
                tipo_cliente=tipo,
                mp_itens=itens,
            )
            st.toast("Orçamento atualizado com sucesso", icon="✅")
            st.cache_data.clear()
            del st.session_state[key]
            st.rerun()


@st.dialog("Alterar Status", width="small")
def dialog_alterar_status(orcamento_id: int, status_atual: str, nome_cliente: str) -> None:
    proximos = TRANSICOES_VALIDAS.get(status_atual, [])
    if not proximos:
        st.info(f"**{status_atual}** é um status terminal. Nenhuma alteração permitida.")
        return

    st.markdown(f"**{nome_cliente}**")
    st.caption(f"Status atual: {status_atual}")

    novo = st.selectbox("Próximo status", proximos)
    motivo = None
    custo_real = None

    if novo == "Orçamento recusado":
        motivo = st.text_area("Motivo da recusa", placeholder="Descreva o motivo…")
    if novo == "Pedido entregue":
        custo_real = st.number_input(
            "Custo real de MP (R$) — opcional",
            min_value=0.0, step=500.0, format="%.2f",
            help="Registre o custo real de materiais para comparar com o orçado.",
        )

    if st.button("Confirmar", type="primary"):
        try:
            atualizar_status(orcamento_id, novo, responsavel="Pedro", motivo_recusa=motivo)
            if novo == "Pedido entregue" and custo_real and custo_real > 0:
                atualizar_custo_realizado(orcamento_id, custo_real)
            st.toast(f"Status atualizado para **{novo}**", icon="✅")
            st.cache_data.clear()
            st.rerun()
        except ValueError as e:
            st.error(str(e))


@st.dialog("Detalhes do Orçamento", width="large")
def dialog_detalhe(orcamento_id: int) -> None:
    """Mostra resumo + timeline animada do histórico de status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM orcamentos WHERE id = ?", (orcamento_id,)).fetchone()
    historico = conn.execute(
        """SELECT status_novo, responsavel, motivo_recusa, timestamp
           FROM historico_status WHERE orcamento_id = ?
           ORDER BY timestamp ASC""",
        (orcamento_id,),
    ).fetchall()
    conn.close()

    if not row:
        st.error("Orçamento não encontrado.")
        return

    # ── Resumo ────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([3, 2, 2])
    c1.markdown(f"**{row['nome_cliente']}**  \n{row['tipo_cliente']}")
    c2.markdown(f"**Valor:** {format_brl(row['valor_total'])}")
    c3.markdown(f"**Status atual:** {badge_status(row['status'])}", unsafe_allow_html=True)
    st.caption(row["descritivo_produto"])
    st.divider()

    if not historico:
        st.info("Nenhuma transição de status registrada ainda.")
        return

    # ── Timeline animada ──────────────────────────────────────────────────────
    # Cada item aparece com fadeUp escalonado (CSS da Fase 1).
    # prefers-reduced-motion já está na trava global do CSS — os itens ficam
    # visíveis imediatamente sem animação.
    st.markdown("**Histórico de status**")

    # Calcula dias em cada etapa
    from datetime import datetime as _dt

    def _parse_ts(ts: str) -> _dt:
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return _dt.strptime(ts, fmt)
            except ValueError:
                continue
        return _dt.now()

    ts_list = [_parse_ts(h["timestamp"]) for h in historico]

    linhas = []
    for i, h in enumerate(historico):
        is_last = i == len(historico) - 1
        estagio = classificar_estagio(h["status_novo"])
        dot_cls = (
            "tl-dot perdido" if estagio == "perdido"
            else ("tl-dot atual" if is_last else "tl-dot done")
        )
        if i < len(historico) - 1:
            delta_dias = (ts_list[i + 1] - ts_list[i]).days
            duracao = f"{delta_dias}d neste estágio"
        else:
            delta_dias = ((_dt.now() - ts_list[i]).days)
            duracao = f"{delta_dias}d (atual)"

        resp = f" · {h['responsavel']}" if h["responsavel"] else ""
        motivo = f"<div class='tl-meta' style='color:#F87171'>↳ {h['motivo_recusa']}</div>" if h["motivo_recusa"] else ""
        delay = f"{0.06 + i * 0.08:.2f}s"
        line_delay = f"{0.08 + i * 0.08:.2f}s"
        line_html = (
            f'<div class="tl-line" style="animation-delay:{line_delay}"></div>'
            if not is_last else ""
        )
        linhas.append(
            f'<div class="tl-item" style="animation-delay:{delay}">'
            f'  <div class="tl-dot-wrap">'
            f'    <div class="{dot_cls}"></div>'
            f'    {line_html}'
            f'  </div>'
            f'  <div class="tl-content">'
            f'    <div class="tl-status">{h["status_novo"]}</div>'
            f'    <div class="tl-meta">{ts_list[i].strftime("%d/%m/%Y %H:%M")}{resp} · {duracao}</div>'
            f'    {motivo}'
            f'  </div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="tl-wrap">{"".join(linhas)}</div>',
        unsafe_allow_html=True,
    )


# ── Funções de carregamento ───────────────────────────────────────────────────

@st.cache_data(ttl=30)
def carregar_dados() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            o.*,
            COALESCE(h.ultima_mudanca, o.data_orcamento) AS ultima_mudanca,
            CAST(
                JULIANDAY(DATE('now')) -
                JULIANDAY(DATE(COALESCE(h.ultima_mudanca, o.data_orcamento)))
            AS INTEGER) AS aging_dias
        FROM orcamentos o
        LEFT JOIN (
            SELECT orcamento_id, MAX(timestamp) AS ultima_mudanca
            FROM historico_status
            GROUP BY orcamento_id
        ) h ON h.orcamento_id = o.id
        WHERE o.arquivado = 0
        ORDER BY o.data_orcamento DESC
    """, conn)
    conn.close()
    df["data_orcamento"] = pd.to_datetime(df["data_orcamento"])
    df["estagio"] = df["status"].map(classificar_estagio)
    return df


@st.cache_data(ttl=30)
def carregar_clientes() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            c.id, c.nome, c.cnpj, c.tipo_cliente,
            c.contato_nome, c.contato_email, c.contato_telefone,
            COUNT(o.id)                                         AS total_negocios,
            COALESCE(SUM(CASE WHEN o.status IN (
                'Orçamento aprovado','Pedido gerado',
                'Pedido em execução','Pedido entregue'
            ) THEN o.valor_total ELSE 0 END), 0)               AS valor_ganho,
            COALESCE(SUM(CASE WHEN o.status = 'Orçamento recusado'
                THEN o.valor_total ELSE 0 END), 0)             AS valor_perdido,
            COALESCE(SUM(o.custo_total_mp), 0)                 AS custo_mp
        FROM clientes c
        LEFT JOIN orcamentos o ON o.cliente_id = c.id AND o.arquivado = 0
        GROUP BY c.id
        ORDER BY valor_ganho DESC
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=30)
def carregar_mp() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            o.id, o.data_orcamento, o.tipo_cliente, o.nome_cliente,
            o.descritivo_produto, o.valor_total, o.custo_total_mp,
            o.status, o.motivo_recusa,
            i.descricao_item, i.valor AS valor_item
        FROM orcamentos o
        JOIN itens_materia_prima i ON i.orcamento_id = o.id
        ORDER BY o.data_orcamento DESC, i.valor DESC
    """, conn)
    conn.close()
    df["data_orcamento"] = pd.to_datetime(df["data_orcamento"])
    return df


# ── Helpers de UI ────────────────────────────────────────────────────────────

def badge_status(status: str) -> str:
    estagio = classificar_estagio(status)
    if status == "Orçamento aguardando aprovação Pedro":
        cls = "badge-pedro"
    elif estagio == "ganho":
        cls = "badge-ganho"
    elif estagio == "perdido":
        cls = "badge-perdido"
    else:
        cls = "badge-aberto"
    return f'<span class="badge {cls}">{status}</span>'


def plotly_base_layout(**kwargs) -> dict:
    return {
        "paper_bgcolor": "#0A0B0F",
        "plot_bgcolor":  "#15171D",
        "font": {"color": "#F2F4F8", "family": "Inter, system-ui, sans-serif"},
        "margin": {"l": 10, "r": 150, "t": 30, "b": 10},
        **kwargs,
    }


def grafico_pipeline(df: pd.DataFrame) -> go.Figure:
    """Barras horizontais do funil: ordem canônica de cima p/ baixo, cores semânticas."""
    status_vals = df.groupby("status")["valor_total"].sum().reset_index()
    status_vals["estagio"] = status_vals["status"].map(classificar_estagio)
    status_vals["ordem"] = status_vals["status"].map(
        {s: i for i, s in enumerate(ORDEM_STATUS)}
    )
    # Ordem decrescente para que o primeiro status canônico apareça no topo
    status_vals = status_vals.sort_values("ordem", ascending=False)
    status_vals = status_vals[status_vals["valor_total"] > 0]

    cores = status_vals["estagio"].map(COR_ESTAGIO).tolist()
    textos = [format_brl(v) for v in status_vals["valor_total"]]

    fig = go.Figure(go.Bar(
        x=status_vals["valor_total"],
        y=status_vals["status"],
        orientation="h",
        marker_color=cores,
        text=textos,
        textposition="outside",
        textfont={"size": 11, "color": "#9AA3B2"},
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    ))
    fig.update_layout(
        **plotly_base_layout(height=320),
        xaxis={"showgrid": False, "showticklabels": False, "zeroline": False, "range": [0, status_vals["valor_total"].max() * 1.45]},
        yaxis={"gridcolor": "#15171D", "tickfont": {"size": 11}},
        title={"text": "Valor por Estágio do Funil", "font": {"size": 13, "color": "#9AA3B2"}},
        bargap=0.4,
    )
    return fig


def grafico_tipo_cliente(df: pd.DataFrame) -> go.Figure:
    por_tipo = df.groupby("tipo_cliente")["valor_total"].sum().reset_index()
    fig = go.Figure(go.Pie(
        labels=por_tipo["tipo_cliente"],
        values=por_tipo["valor_total"],
        hole=0.52,
        marker_colors=["#7DD3FC", "#9AA3B2"],  # categórico — nunca limão nem verde de ganho
        textinfo="label+percent",
        textfont={"size": 11},
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **plotly_base_layout(height=320),
        showlegend=False,
        title={"text": "Valor por Tipo de Cliente", "font": {"size": 13, "color": "#9AA3B2"}},
    )
    return fig


# ── KPI iframe — CSS e JS (strings fixas; sem f-string para evitar escape) ───
# Trade-off documentado: faixa de KPIs vira iframe isolado (components.html).
# Vantagem: JS de count-up não reinicia a cada rerun do Streamlit; anima delta.
# Custo: sem tooltips nativos do st.metric; paleta CTP Dark fixada no HTML.

_KPI_CSS = """<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,system-ui,sans-serif;font-variant-numeric:tabular-nums}
body{background:transparent;padding:0 2px 6px}
.kpi-sl{font-size:.67rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#626B7A;margin:0 0 8px}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.kpi-card{background:#15171D;border:1px solid #2A2E38;border-radius:10px;padding:14px 18px}
.kpi-card.flash{animation:kpiFlash .6s ease-out}
@keyframes kpiFlash{0%{background:#1B2417}100%{background:#15171D}}
.kpi-label{font-size:.67rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#9AA3B2;margin-bottom:8px}
.kpi-value{font-size:1.42rem;font-weight:700;color:#F2F4F8;line-height:1.1;display:flex;align-items:center;gap:5px}
.kpi-delta{font-size:.7rem;color:#626B7A;margin-top:5px}
.aging-dot{display:inline-block;width:7px;height:7px;border-radius:50%;flex-shrink:0;animation:pulse 1.9s ease-in-out infinite}
.aging-dot-warn{background:#FBBF24}.aging-dot-alert{background:#F87171}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.kpi-enter{animation:fadeUp .35s ease-out both}
.kpi-enter-1{animation-delay:.04s}.kpi-enter-2{animation-delay:.10s}
.kpi-enter-3{animation-delay:.17s}.kpi-enter-4{animation-delay:.24s}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>"""

_KPI_JS = """<script>
(function(){
  var data=__ANIM_DATA__;
  var rm=window.matchMedia&&window.matchMedia("(prefers-reduced-motion:reduce)").matches;
  function fBRL(v){
    if(v==null||isNaN(v))return"—";
    return"R$ "+Math.abs(v).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
  }
  function fPct(v){
    if(v==null||isNaN(v))return"—";
    return v.toLocaleString("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1})+"%";
  }
  function fInt(v){return Math.round(v).toString();}
  function ease(p){return 1-Math.pow(1-p,3);}
  data.forEach(function(d){
    var el=document.getElementById(d.id);
    if(!el)return;
    var fmt=d.fmt==="brl"?fBRL:d.fmt==="pct"?fPct:fInt;
    if(rm||Math.abs(d.to-(d.from||0))<0.005){el.textContent=fmt(d.to);return;}
    var from=d.from||0,to=d.to,dur=900,t0=performance.now();
    (function step(t){
      var p=Math.min((t-t0)/dur,1);
      el.textContent=fmt(from+(to-from)*ease(p));
      if(p<1)requestAnimationFrame(step);else el.textContent=fmt(to);
    })(t0);
  });
})();
</script>"""


def _build_kpi_html(prev: dict, curr: dict, first_load: bool, is_admin: bool) -> str:
    import json as _json

    n_ag      = int(curr.get("n_aging", 0) or 0)
    aging_lim = int(curr.get("aging_lim", AGING_ALERTA_DIAS))
    n_ganho   = int(curr.get("n_ganho",   0) or 0)
    n_perdido = int(curr.get("n_perdido", 0) or 0)
    pond_fmt  = format_brl(curr.get("pipeline_pond", 0) or 0)

    def _chg(k: str) -> bool:
        pv = prev.get(k)
        return pv is not None and abs((pv or 0) - (curr.get(k) or 0)) > 0.01

    def _fl(k: str) -> str:
        return "flash" if _chg(k) else ""

    def _en(n: int) -> str:
        return f"kpi-enter kpi-enter-{n}" if first_load else ""

    def _fr(k: str) -> float:
        return float(prev.get(k) or 0)

    def _to(k: str) -> float:
        return float(curr.get(k) or 0)

    # Aging pulse dot
    aging_dot = ""
    if n_ag > 0:
        dc = "aging-dot-alert" if n_ag > 3 else "aging-dot-warn"
        aging_dot = f'<span class="aging-dot {dc}"></span>'

    # Aging delta text
    aging_delta = (
        f"{n_ag} parado{'s' if n_ag != 1 else ''} &gt; {aging_lim}d"
        if n_ag > 0 else f"Todos ativos &le; {aging_lim}d"
    )

    # Margem % color
    mpct = curr.get("margem_pct", 0) or 0
    mc = "#34D399" if mpct >= LIMIAR_MARGEM_SAUDAVEL else ("#FBBF24" if mpct >= LIMIAR_MARGEM_ATENCAO else "#F87171")

    # Animation data list for JS
    anim = [
        {"id": "kv-pipeline",  "from": _fr("pipeline"),     "to": _to("pipeline"),     "fmt": "brl"},
        {"id": "kv-ganho",     "from": _fr("valor_ganho"),  "to": _to("valor_ganho"),  "fmt": "brl"},
        {"id": "kv-perdido",   "from": _fr("valor_perdido"),"to": _to("valor_perdido"),"fmt": "brl"},
        {"id": "kv-aging",     "from": _fr("n_aging"),      "to": _to("n_aging"),      "fmt": "int"},
    ]
    if is_admin:
        anim += [
            {"id": "kv-margem-b", "from": _fr("margem_bruta"), "to": _to("margem_bruta"), "fmt": "brl"},
            {"id": "kv-margem-p", "from": _fr("margem_pct"),   "to": _to("margem_pct"),   "fmt": "pct"},
            {"id": "kv-winrate",  "from": _fr("win_rate"),     "to": _to("win_rate"),     "fmt": "pct"},
            {"id": "kv-ticket",   "from": _fr("ticket_medio"), "to": _to("ticket_medio"), "fmt": "brl"},
        ]

    def _card(c_id, label, delta, extra_cls, val_prefix=""):
        return (
            f'<div class="kpi-card {extra_cls}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val_prefix}<span id="{c_id}"></span></div>'
            f'<div class="kpi-delta">{delta}</div>'
            f'</div>'
        )

    row1 = (
        _card("kv-pipeline", "Pipeline Aberto",
              f"Ponderado: {pond_fmt}", _fl("pipeline") + " " + _en(1))
        + _card("kv-ganho", "Valor Ganho",
                f"{n_ganho} negócio{'s' if n_ganho != 1 else ''}",
                _fl("valor_ganho") + " " + _en(2))
        + _card("kv-perdido", "Valor Perdido",
                f"{n_perdido} recusado{'s' if n_perdido != 1 else ''}",
                _fl("valor_perdido") + " " + _en(3))
        + _card("kv-aging", "Negócios Parados", aging_delta,
                _fl("n_aging") + " " + _en(4), val_prefix=aging_dot)
    )

    row2_block = ""
    if is_admin:
        row2 = (
            _card("kv-margem-b", "Margem Bruta",
                  "Valor ganho &minus; Custo MP", _fl("margem_bruta") + " " + _en(1))
            + f'<div class="kpi-card {_fl("margem_pct")} {_en(2)}">'
            + f'<div class="kpi-label">Margem %</div>'
            + f'<div class="kpi-value"><span id="kv-margem-p" style="color:{mc}"></span></div>'
            + f'<div class="kpi-delta">Meta &ge; {LIMIAR_MARGEM_SAUDAVEL:.0f}%</div></div>'
            + _card("kv-winrate", "Win Rate (Valor)",
                    "Ganho &divide; (ganho + perdido)", _fl("win_rate") + " " + _en(3))
            + _card("kv-ticket", "Ticket Médio Ganho",
                    f"{n_ganho} negócio{'s' if n_ganho != 1 else ''}",
                    _fl("ticket_medio") + " " + _en(4))
        )
        row2_block = f'<div class="kpi-sl" style="margin-top:14px">Rentabilidade e Eficiência</div><div class="kpi-row">{row2}</div>'

    js = _KPI_JS.replace("__ANIM_DATA__", _json.dumps(anim))

    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>{_KPI_CSS}</head>"
        f"<body>"
        f'<div class="kpi-sl">Comercial</div>'
        f'<div class="kpi-row">{row1}</div>'
        f"{row2_block}"
        f"{js}"
        f"</body></html>"
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Cilla Tech Park")
    st.markdown('<div style="color:#9ACA3C;font-size:0.75rem;margin-top:-12px;margin-bottom:8px;letter-spacing:0.05em">PAINEL DE OPERAÇÕES</div>', unsafe_allow_html=True)
    _user_display = st.session_state.get("name", st.session_state.get("username", ""))
    _role_label = "Admin" if _role == "admin" else "Vendedor"
    st.markdown(f'<div style="font-size:0.72rem;color:#626B7A;margin-bottom:12px">{_user_display} · {_role_label}</div>', unsafe_allow_html=True)
    _authenticator.logout("Sair", location="sidebar")

    if st.button("＋ Novo Orçamento", width="stretch", type="primary"):
        if "_mp" in st.session_state:
            del st.session_state["_mp"]
        dialog_novo_orcamento()

    st.divider()

    df_raw = carregar_dados()

    data_min = df_raw["data_orcamento"].min().date()
    data_max = df_raw["data_orcamento"].max().date()
    intervalo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY",
    )

    tipos = st.multiselect(
        "Tipo de cliente",
        options=TIPO_CLIENTE_VALIDOS,
        default=TIPO_CLIENTE_VALIDOS,
    )

    status_sel = st.multiselect(
        "Status",
        options=STATUS_VALIDOS,
        default=STATUS_VALIDOS,
    )

    busca = st.text_input("Buscar", placeholder="Cliente, órgão ou produto…")

    st.divider()
    if st.button("↺ Recarregar dados", width="stretch"):
        st.cache_data.clear()
        st.rerun()


# ── Aplicar filtros ───────────────────────────────────────────────────────────

df = df_raw.copy()

if len(intervalo) == 2:
    d_ini, d_fim = intervalo
    df = df[(df["data_orcamento"].dt.date >= d_ini) & (df["data_orcamento"].dt.date <= d_fim)]

if tipos:
    df = df[df["tipo_cliente"].isin(tipos)]

if status_sel:
    df = df[df["status"].isin(status_sel)]

if busca.strip():
    mask = (
        df["nome_cliente"].str.contains(busca, case=False, na=False)
        | df["descritivo_produto"].str.contains(busca, case=False, na=False)
    )
    df = df[mask]


# ── KPIs ──────────────────────────────────────────────────────────────────────

kpis          = calcular_kpis(df)
pipeline_pond = calcular_pipeline_ponderado(df)
n_ag          = kpis["n_aging_alertas"]

# Cabeçalho
st.markdown(
    '<h1 style="font-size:1.5rem;font-weight:700;color:#F2F4F8;margin-bottom:2px">'
    'Painel de Operações</h1>'
    '<div style="color:#626B7A;font-size:0.8rem;margin-bottom:16px">'
    f'Cilla Tech Park · {len(df)} de {len(df_raw)} registros · atualizado a cada 30s'
    '</div>',
    unsafe_allow_html=True,
)

# ── Faixa de KPIs via components.html ─────────────────────────────────────────
# Controles de animação:
#   kpi_entered — True após 1ª carga; impede que fadeUp rode em todo rerun
#   kpis_prev   — valores da rodada anterior; count-up anima de prev → curr
_kpi_first = not st.session_state.get("kpi_entered", False)
st.session_state["kpi_entered"] = True
_kpi_prev = st.session_state.get("kpis_prev", {})

_kpi_curr = {
    "pipeline":       kpis["pipeline"],
    "pipeline_pond":  pipeline_pond,
    "valor_ganho":    kpis["valor_ganho"],
    "n_ganho":        kpis["n_ganho"],
    "valor_perdido":  kpis["valor_perdido"],
    "n_perdido":      kpis["n_perdido"],
    "n_aging":        n_ag,
    "aging_lim":      AGING_ALERTA_DIAS,
    "margem_bruta":   kpis["margem_bruta"],
    "margem_pct":     kpis["margem_pct"],
    "win_rate":       kpis["win_rate_valor"] * 100,
    "ticket_medio":   kpis["ticket_medio"],
}

_kpi_height = 250 if _role == "admin" else 132
components.html(
    _build_kpi_html(_kpi_prev, _kpi_curr, _kpi_first, _role == "admin"),
    height=_kpi_height,
    scrolling=False,
)

# Atualiza prev APÓS renderizar — próximo rerun recebe o delta correto
st.session_state["kpis_prev"] = _kpi_curr

st.divider()


# ── Abas ──────────────────────────────────────────────────────────────────────

aba_visao, aba_todos, aba_pref, aba_cli, aba_mp, aba_perdidos, aba_clientes = st.tabs([
    "Visão Geral",
    "Todos os Registros",
    "Prefeituras",
    "Clientes Diretos",
    "Matéria-Prima",
    "Perdidos",
    "Clientes",
])


# ── Helper: tabela de orçamentos ─────────────────────────────────────────────
# Renderiza via Styler (coloração semântica de células) + on_select → barra de
# ação contextual. A lista vertical de botões por linha foi removida.

def tabela_orcamentos(frame: pd.DataFrame, key: str, mostrar_aging: bool = True) -> None:
    if frame.empty:
        st.info("Nenhum registro encontrado com os filtros aplicados.")
        return

    frame = frame.reset_index(drop=True)
    _sel_key = f"{key}_sel"

    # ── Display DF ────────────────────────────────────────────────────────────
    display_cols = ["data_orcamento", "tipo_cliente", "nome_cliente",
                    "descritivo_produto", "valor_total"]
    if _role == "admin":
        display_cols += ["custo_total_mp"]
    display_cols += ["status"]
    if mostrar_aging:
        display_cols += ["aging_dias"]
    display_cols += ["motivo_recusa"]

    exibir = frame[display_cols].copy()

    if _role == "admin":
        exibir["margem_pct"] = (
            (frame["valor_total"] - frame["custo_total_mp"])
            / frame["valor_total"].replace(0, float("nan")) * 100
        ).round(1)

    exibir["data_orcamento"] = exibir["data_orcamento"].dt.strftime("%d/%m/%Y")

    exibir.rename(columns={
        "data_orcamento":     "Data",
        "tipo_cliente":       "Tipo",
        "nome_cliente":       "Cliente",
        "descritivo_produto": "Descritivo",
        "valor_total":        "Valor",
        "custo_total_mp":     "Custo MP",
        "margem_pct":         "Margem %",
        "aging_dias":         "Aging",
        "status":             "Status",
        "motivo_recusa":      "Motivo",
    }, inplace=True)

    # ── Styler — coloração semântica de células ───────────────────────────────
    def _style_status(val: str) -> str:
        if pd.isna(val):
            return ""
        estagio = classificar_estagio(str(val))
        if val == "Orçamento aguardando aprovação Pedro":
            return "background-color:#3A2A08;color:#FBBF24;font-weight:600"
        if estagio == "ganho":
            return "background-color:#08352A;color:#34D399;font-weight:600"
        if estagio == "perdido":
            return "background-color:#3A1414;color:#F87171;font-weight:600"
        return "background-color:#0C2E42;color:#7DD3FC;font-weight:600"

    def _style_aging(val) -> str:
        if pd.isna(val):
            return ""
        v = float(val)
        if v > 60:
            return "color:#F87171;font-weight:700"
        if v > AGING_ALERTA_DIAS:
            return "color:#FBBF24;font-weight:600"
        return ""

    def _style_margem(val) -> str:
        if pd.isna(val):
            return ""
        v = float(val)
        if v >= LIMIAR_MARGEM_SAUDAVEL:
            return "color:#34D399;font-weight:600"
        if v >= LIMIAR_MARGEM_ATENCAO:
            return "color:#FBBF24;font-weight:600"
        return "color:#F87171;font-weight:600"

    styler = exibir.style.map(_style_status, subset=["Status"])
    if "Aging" in exibir.columns:
        styler = styler.map(_style_aging, subset=["Aging"])
    if "Margem %" in exibir.columns:
        styler = styler.map(_style_margem, subset=["Margem %"])

    # Formata valores monetários e percentuais via Styler.format (não pré-converte)
    fmt: dict = {
        "Valor": lambda v: format_brl(float(v)) if pd.notna(v) else "—",
    }
    if "Custo MP" in exibir.columns:
        fmt["Custo MP"] = lambda v: format_brl(float(v)) if pd.notna(v) else "—"
    if "Margem %" in exibir.columns:
        fmt["Margem %"] = lambda v: format_pct(float(v)) if pd.notna(v) else "—"
    styler = styler.format(fmt).hide(axis=0)

    # ── Column config ─────────────────────────────────────────────────────────
    col_cfg: dict = {
        "Descritivo": st.column_config.TextColumn(width="medium"),
        "Motivo":     st.column_config.TextColumn(width="small"),
    }
    if "Aging" in exibir.columns:
        col_cfg["Aging"] = st.column_config.NumberColumn(
            help=f"Dias sem mudança de status. Alerta > {AGING_ALERTA_DIAS}d.",
            format="%d",
        )
    if "Margem %" in exibir.columns:
        col_cfg["Margem %"] = st.column_config.TextColumn(
            help=f"Verde ≥ {LIMIAR_MARGEM_SAUDAVEL:.0f}% | Âmbar ≥ {LIMIAR_MARGEM_ATENCAO:.0f}%.",
        )

    # ── Render com seleção ────────────────────────────────────────────────────
    event = st.dataframe(
        styler,
        key=f"{key}_tbl",
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        column_config=col_cfg,
    )

    sel_rows = (event.selection.rows if event and hasattr(event, "selection") else [])
    if sel_rows:
        st.session_state[_sel_key] = sel_rows[0]
    sel_idx = st.session_state.get(_sel_key)

    # ── Barra de ação contextual ──────────────────────────────────────────────
    if sel_idx is not None and 0 <= sel_idx < len(frame):
        row = frame.iloc[sel_idx]
        oid = int(row["id"])
        terminal = not TRANSICOES_VALIDAS.get(row["status"], [])
        descr_prev = (row["descritivo_produto"][:70] + "…") if len(row["descritivo_produto"]) > 70 else row["descritivo_produto"]

        st.markdown(
            f'<div class="action-bar">'
            f'<div class="action-bar-label">{row["nome_cliente"]}</div>'
            f'<div class="action-bar-sub">{descr_prev}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        extra_btn = 1 if _role == "admin" else 0
        btn_cols = st.columns([1, 1, 1] + [1] * extra_btn + [3])
        if btn_cols[0].button("✎ Editar", key=f"{key}_act_ed_{oid}", use_container_width=True):
            dialog_editar_orcamento(oid)
        if btn_cols[1].button(
            "→ Status", key=f"{key}_act_st_{oid}",
            use_container_width=True, disabled=terminal,
            help="Status terminal — nenhuma transição possível." if terminal else None,
        ):
            dialog_alterar_status(oid, row["status"], row["nome_cliente"])
        if btn_cols[2].button("🔍 Detalhes", key=f"{key}_act_det_{oid}", use_container_width=True):
            dialog_detalhe(oid)
        if _role == "admin" and btn_cols[3].button("🗑 Arquivar", key=f"{key}_act_arc_{oid}", use_container_width=True):
            st.session_state[f"_confirm_arc_{oid}"] = True

        if st.session_state.get(f"_confirm_arc_{oid}"):
            st.warning(f"Arquivar **{row['nome_cliente']}** — {format_brl(row['valor_total'])}? Esta ação oculta o registro.")
            c_ok, c_no = st.columns(2)
            if c_ok.button("Confirmar", key=f"{key}_arc_ok_{oid}", type="primary"):
                arquivar_orcamento(oid)
                st.toast(f"{row['nome_cliente']} arquivado", icon="🗑️")
                st.cache_data.clear()
                del st.session_state[f"_confirm_arc_{oid}"]
                st.session_state.pop(_sel_key, None)
                st.rerun()
            if c_no.button("Cancelar", key=f"{key}_arc_no_{oid}"):
                del st.session_state[f"_confirm_arc_{oid}"]
                st.rerun()
    else:
        st.caption("↑ Selecione uma linha para ver as ações disponíveis.")


# ── Aba: Visão Geral ──────────────────────────────────────────────────────────

with aba_visao:
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        st.plotly_chart(grafico_pipeline(df), width="stretch")
    with col_g2:
        st.plotly_chart(grafico_tipo_cliente(df), width="stretch")

    # Legenda de cores semânticas
    st.markdown(
        '<div style="display:flex;gap:20px;margin-top:4px;margin-bottom:16px">'
        '<span><span style="color:#7DD3FC">●</span> <span style="color:#626B7A;font-size:0.78rem">Em aberto</span></span>'
        '<span><span style="color:#34D399">●</span> <span style="color:#626B7A;font-size:0.78rem">Ganho</span></span>'
        '<span><span style="color:#F87171">●</span> <span style="color:#626B7A;font-size:0.78rem">Perdido</span></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Alertas de aging
    df_alertas = df[(df["estagio"] == "aberto") & (df["aging_dias"] > AGING_ALERTA_DIAS)]
    if not df_alertas.empty:
        st.markdown(f"**{len(df_alertas)} negócio(s) em aberto parado(s) há mais de {AGING_ALERTA_DIAS} dias:**")
        for _, row in df_alertas.sort_values("aging_dias", ascending=False).iterrows():
            dias = int(row["aging_dias"])
            cor = "#F87171" if dias > 60 else "#FBBF24"
            dot_cls = "aging-dot aging-dot-alert" if dias > 60 else "aging-dot aging-dot-warn"
            st.markdown(
                f'<div style="background:#15171D;border-left:3px solid {cor};'
                f'padding:10px 14px;border-radius:4px;margin-bottom:6px">'
                f'<span style="color:{cor};font-weight:600">'
                f'<span class="{dot_cls}"></span>{dias}d parado</span> · '
                f'<b style="color:#F2F4F8">{row["nome_cliente"]}</b> · {format_brl(row["valor_total"])} · '
                f'<span style="color:#626B7A">{row["status"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("Nenhum negócio em aberto parado além do prazo.")


# ── Aba: Todos os Registros ───────────────────────────────────────────────────

with aba_todos:
    tabela_orcamentos(df, key="tab_todos")


# ── Aba: Prefeituras ──────────────────────────────────────────────────────────

with aba_pref:
    df_pref = df[df["tipo_cliente"] == "Prefeitura"]
    kpis_pref = calcular_kpis(df_pref)

    st.markdown(f"**{len(df_pref)} registros** · Ganho: {format_brl(kpis_pref['valor_ganho'])} · Margem: {format_pct(kpis_pref['margem_pct'])} · Win rate: {format_pct(kpis_pref['win_rate_valor'] * 100)}")

    if not df_pref.empty:
        por_pref = (
            df_pref.groupby("nome_cliente")
            .agg(
                Contratos=("id", "count"),
                Valor=("valor_total", "sum"),
                Custo_MP=("custo_total_mp", "sum"),
            )
            .assign(Margem=lambda x: x["Valor"] - x["Custo_MP"])
            .assign(Margem_Pct=lambda x: (x["Margem"] / x["Valor"] * 100).round(1))
            .sort_values("Valor", ascending=False)
            .reset_index()
        )
        por_pref.rename(columns={"nome_cliente": "Prefeitura / Câmara", "Custo_MP": "Custo MP"}, inplace=True)
        # Formata moeda
        for col in ["Valor", "Custo MP", "Margem"]:
            por_pref[col] = por_pref[col].map(format_brl)
        por_pref["Margem %"] = por_pref["Margem_Pct"].map(lambda v: format_pct(v))
        por_pref.drop(columns=["Margem_Pct"], inplace=True)

        st.dataframe(por_pref, width="stretch", hide_index=True)

    st.divider()
    tabela_orcamentos(df_pref, key="tab_pref")


# ── Aba: Clientes Diretos ─────────────────────────────────────────────────────

with aba_cli:
    df_cli = df[df["tipo_cliente"] == "Cliente Direto"]
    kpis_cli = calcular_kpis(df_cli)

    st.markdown(f"**{len(df_cli)} registros** · Ganho: {format_brl(kpis_cli['valor_ganho'])} · Margem: {format_pct(kpis_cli['margem_pct'])} · Win rate: {format_pct(kpis_cli['win_rate_valor'] * 100)}")

    if not df_cli.empty:
        por_cli = (
            df_cli.groupby("nome_cliente")
            .agg(
                Contratos=("id", "count"),
                Valor=("valor_total", "sum"),
                Custo_MP=("custo_total_mp", "sum"),
            )
            .assign(Margem=lambda x: x["Valor"] - x["Custo_MP"])
            .assign(Margem_Pct=lambda x: (x["Margem"] / x["Valor"] * 100).round(1))
            .sort_values("Valor", ascending=False)
            .reset_index()
        )
        por_cli.rename(columns={"nome_cliente": "Cliente", "Custo_MP": "Custo MP"}, inplace=True)
        for col in ["Valor", "Custo MP", "Margem"]:
            por_cli[col] = por_cli[col].map(format_brl)
        por_cli["Margem %"] = por_cli["Margem_Pct"].map(lambda v: format_pct(v))
        por_cli.drop(columns=["Margem_Pct"], inplace=True)

        st.dataframe(por_cli, width="stretch", hide_index=True)

    st.divider()
    tabela_orcamentos(df_cli, key="tab_cli")


# ── Aba: Matéria-Prima ────────────────────────────────────────────────────────

with aba_mp:
    st.markdown("Insumos por projeto — base para análise de composição de custo.")

    df_mp = carregar_mp()

    # Aplica filtros de cliente/tipo ao df_mp
    if tipos:
        df_mp = df_mp[df_mp["tipo_cliente"].isin(tipos)]
    if busca.strip():
        df_mp = df_mp[
            df_mp["nome_cliente"].str.contains(busca, case=False, na=False)
            | df_mp["descritivo_produto"].str.contains(busca, case=False, na=False)
        ]

    if df_mp.empty:
        st.info("Nenhum insumo encontrado com os filtros aplicados.")
    else:
        # Top insumos por valor (visão agregada)
        top_mp = (
            df_mp.groupby("descricao_item")["valor_item"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_mp.columns = ["Insumo", "Valor Total"]
        top_mp["Valor Total"] = top_mp["Valor Total"].map(format_brl)

        with st.expander("Top 10 insumos por valor total na carteira", expanded=False):
            st.dataframe(top_mp, width="stretch", hide_index=True)

        st.divider()

        # Detalhe por projeto
        for oid, grupo in df_mp.groupby("id"):
            row0 = grupo.iloc[0]
            margem = row0["valor_total"] - row0["custo_total_mp"]
            margem_pct = (margem / row0["valor_total"] * 100) if row0["valor_total"] > 0 else 0
            estagio = classificar_estagio(row0["status"])

            titulo = (
                f"{row0['data_orcamento'].strftime('%d/%m/%Y')} · "
                f"{row0['nome_cliente']} · "
                f"{format_brl(row0['valor_total'])} · "
                f"Margem {format_pct(margem_pct)}"
            )
            with st.expander(titulo, expanded=False):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"**Produto:** {row0['descritivo_produto']}")
                    st.markdown(
                        f"**Status:** {badge_status(row0['status'])}",
                        unsafe_allow_html=True,
                    )
                    if row0.get("motivo_recusa"):
                        st.warning(f"Motivo da recusa: {row0['motivo_recusa']}")

                    itens_df = grupo[["descricao_item", "valor_item"]].copy()
                    itens_df["valor_item"] = itens_df["valor_item"].map(format_brl)
                    itens_df.columns = ["Insumo", "Valor"]
                    st.dataframe(itens_df, width="stretch", hide_index=True)
                with cb:
                    st.metric("Valor Orçamento", format_brl(row0["valor_total"]))
                    st.metric("Custo MP (orçado)", format_brl(row0["custo_total_mp"]))
                    custo_real = row0.get("custo_realizado_mp")
                    if custo_real and not pd.isna(custo_real):
                        delta_custo = custo_real - row0["custo_total_mp"]
                        st.metric(
                            "Custo MP (realizado)",
                            format_brl(custo_real),
                            f"{'+' if delta_custo >= 0 else ''}{format_brl(delta_custo)}",
                            delta_color="inverse",
                            help="Diferença entre custo real e orçado de matéria-prima.",
                        )
                    st.metric(
                        "Margem Bruta",
                        format_brl(margem) if estagio == "ganho" else "—",
                        format_pct(margem_pct) if estagio == "ganho" else f"Estágio: {estagio}",
                        help="Margem calculada apenas para negócios no estágio Ganho.",
                    )


# ── Aba: Perdidos ─────────────────────────────────────────────────────────────

with aba_perdidos:
    df_rec = df[df["status"] == "Orçamento recusado"]
    total_perdido = df_rec["valor_total"].sum()

    if df_rec.empty:
        st.success("Nenhum orçamento recusado nos filtros selecionados.")
    else:
        st.markdown(
            f"**{len(df_rec)} orçamento(s) recusado(s)** · "
            f"Valor total: **{format_brl(total_perdido)}**"
        )
        st.markdown("")

        for _, row in df_rec.sort_values("data_orcamento", ascending=False).iterrows():
            st.markdown(
                f'<div style="background:#15171D;border-left:3px solid #F87171;'
                f'padding:12px 16px;border-radius:4px;margin-bottom:8px">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                f'<div>'
                f'<b style="color:#F2F4F8">{row["nome_cliente"]}</b> '
                f'<span style="color:#626B7A;font-size:0.8rem">({row["tipo_cliente"]})</span><br>'
                f'<span style="color:#9AA3B2;font-size:0.82rem">{row["descritivo_produto"]}</span>'
                f'</div>'
                f'<div style="text-align:right;white-space:nowrap">'
                f'<b style="color:#F87171">{format_brl(row["valor_total"])}</b><br>'
                f'<span style="color:#626B7A;font-size:0.78rem">{row["data_orcamento"].strftime("%d/%m/%Y")}</span>'
                f'</div>'
                f'</div>'
                f'<div style="margin-top:8px;color:#9AA3B2;font-size:0.82rem">'
                f'<b style="color:#626B7A">Motivo:</b> {row["motivo_recusa"] or "—"}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Aba: Clientes ─────────────────────────────────────────────────────────────

with aba_clientes:
    df_clientes = carregar_clientes()

    if df_clientes.empty:
        st.info("Nenhum cliente cadastrado.")
    else:
        # Tabela resumo de clientes
        resumo = df_clientes.copy()
        resumo["win_rate"] = resumo.apply(
            lambda r: (r["valor_ganho"] / (r["valor_ganho"] + r["valor_perdido"]) * 100)
            if (r["valor_ganho"] + r["valor_perdido"]) > 0 else 0,
            axis=1,
        )
        resumo["margem_pct"] = resumo.apply(
            lambda r: ((r["valor_ganho"] - r["custo_mp"]) / r["valor_ganho"] * 100)
            if r["valor_ganho"] > 0 else 0,
            axis=1,
        )

        exibir_res = resumo[["nome", "cnpj", "tipo_cliente", "contato_nome", "contato_email",
                              "contato_telefone", "total_negocios", "valor_ganho", "win_rate", "margem_pct"]].copy()
        exibir_res["valor_ganho"] = exibir_res["valor_ganho"].map(format_brl)
        exibir_res["win_rate"]    = exibir_res["win_rate"].map(lambda v: format_pct(v))
        exibir_res["margem_pct"]  = exibir_res["margem_pct"].map(lambda v: format_pct(v))
        exibir_res = exibir_res.fillna("—")
        exibir_res.rename(columns={
            "nome": "Cliente", "cnpj": "CNPJ", "tipo_cliente": "Tipo",
            "contato_nome": "Contato", "contato_email": "E-mail",
            "contato_telefone": "Telefone", "total_negocios": "Negócios",
            "valor_ganho": "Valor Ganho", "win_rate": "Win Rate", "margem_pct": "Margem %",
        }, inplace=True)
        st.dataframe(exibir_res, width="stretch", hide_index=True)

        st.divider()
        st.markdown('<div class="kpi-section-title" style="margin-top:8px">Editar dados de contato</div>', unsafe_allow_html=True)

        for _, cli in df_clientes.iterrows():
            with st.expander(f"{cli['nome']} ({cli['tipo_cliente']})", expanded=False):
                cc1, cc2 = st.columns(2)
                cnpj_val     = cc1.text_input("CNPJ",     value=cli["cnpj"] or "",     key=f"cli_cnpj_{cli['id']}")
                contato_val  = cc2.text_input("Contato",  value=cli["contato_nome"] or "", key=f"cli_ctnom_{cli['id']}")
                email_val    = cc1.text_input("E-mail",   value=cli["contato_email"] or "", key=f"cli_email_{cli['id']}")
                tel_val      = cc2.text_input("Telefone", value=cli["contato_telefone"] or "", key=f"cli_tel_{cli['id']}")

                if st.button("Salvar contato", key=f"cli_save_{cli['id']}"):
                    atualizar_cliente(
                        int(cli["id"]),
                        cnpj=cnpj_val.strip() or None,
                        contato_nome=contato_val.strip() or None,
                        contato_email=email_val.strip() or None,
                        contato_telefone=tel_val.strip() or None,
                    )
                    st.cache_data.clear()
                    st.rerun()
