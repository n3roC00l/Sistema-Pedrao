"""
Schema, migração e seed do banco SQLite — Painel Pedrão / Cilla Tech Park.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "orcamentos.db"

STATUS_VALIDOS = [
    "Orçamento gerado",
    "Orçamento aguardando aprovação Pedro",
    "Orçamento aguardando aprovação cliente",
    "Orçamento aprovado",
    "Orçamento recusado",
    "Pedido gerado",
    "Pedido em execução",
    "Pedido entregue",
]

TIPO_CLIENTE_VALIDOS = ["Cliente Direto", "Prefeitura"]

SCHEMA_VERSION = 2

# ── Dados de seed ────────────────────────────────────────────────────────────
SEED_DATA = [
    # Clientes Diretos
    {
        "data": "2026-01-15", "tipo": "Cliente Direto",
        "cliente": "Construtora Horizonte Ltda",
        "produto": "Fabricação de 200 esquadrias de alumínio linha 45 para residencial alto padrão",
        "valor": 87_500.00,
        "mp": [
            {"item": "Perfil alumínio linha 45", "valor": 32_000.00},
            {"item": "Vidro temperado 8mm", "valor": 15_000.00},
            {"item": "Acessórios e ferragens", "valor": 4_200.00},
        ],
        "status": "Pedido entregue", "motivo": None,
    },
    {
        "data": "2026-02-03", "tipo": "Cliente Direto",
        "cliente": "Incorporadora Viva Mais S/A",
        "produto": "Fornecimento e instalação de fachada em ACM para torre comercial — 4.200 m²",
        "valor": 312_000.00,
        "mp": [
            {"item": "Chapa ACM 4mm cinza grafite", "valor": 98_000.00},
            {"item": "Estrutura metálica galvanizada", "valor": 45_000.00},
            {"item": "Fixadores e selantes", "valor": 8_500.00},
        ],
        "status": "Pedido em execução", "motivo": None,
    },
    {
        "data": "2026-02-20", "tipo": "Cliente Direto",
        "cliente": "Clínica São Lucas",
        "produto": "Divisórias internas em drywall e vidro temperado — reforma da área administrativa",
        "valor": 28_900.00,
        "mp": [
            {"item": "Vidro temperado 10mm", "valor": 9_200.00},
            {"item": "Perfil drywall e chapas", "valor": 5_800.00},
            {"item": "Massa, fita e acabamentos", "valor": 1_100.00},
        ],
        "status": "Orçamento aprovado", "motivo": None,
    },
    {
        "data": "2026-03-10", "tipo": "Cliente Direto",
        "cliente": "Auto Peças Saveiro ME",
        "produto": "Cobertura metálica para pátio de estacionamento — 600 m²",
        "valor": 41_200.00,
        "mp": [
            {"item": "Telha metálica trapezoidal galvanizada", "valor": 14_500.00},
            {"item": "Estrutura tubular metálica", "valor": 11_000.00},
            {"item": "Calha e rufos", "valor": 2_300.00},
        ],
        "status": "Orçamento aguardando aprovação cliente", "motivo": None,
    },
    {
        "data": "2026-03-28", "tipo": "Cliente Direto",
        "cliente": "Supermercado Bom Preço",
        "produto": "Instalação de porta automática de vidro duplo na entrada principal",
        "valor": 19_800.00,
        "mp": [
            {"item": "Vidro duplo laminado", "valor": 7_500.00},
            {"item": "Motor automático Dorma", "valor": 4_800.00},
            {"item": "Perfil e trilho inox", "valor": 2_100.00},
        ],
        "status": "Orçamento recusado",
        "motivo": "Cliente optou por fornecedor local com preço 18% menor.",
    },
    {
        "data": "2026-04-05", "tipo": "Cliente Direto",
        "cliente": "Construtora Horizonte Ltda",
        "produto": "Segunda fase: 150 portas de alumínio com vidro jateado — blocos B e C",
        "valor": 63_000.00,
        "mp": [
            {"item": "Perfil alumínio porta", "valor": 21_000.00},
            {"item": "Vidro jateado 6mm", "valor": 12_500.00},
            {"item": "Ferragens e dobradiças", "valor": 3_800.00},
        ],
        "status": "Pedido gerado", "motivo": None,
    },
    {
        "data": "2026-04-18", "tipo": "Cliente Direto",
        "cliente": "Hotel Grand Palace",
        "produto": "Fachada de vidro estrutural spider com perfis de aço inox — lobby e restaurante",
        "valor": 215_000.00,
        "mp": [
            {"item": "Vidro laminado 12mm estrutural", "valor": 72_000.00},
            {"item": "Spider e conectores inox 316L", "valor": 38_000.00},
            {"item": "Perfil inox e silicone estrutural", "valor": 14_000.00},
        ],
        "status": "Orçamento aguardando aprovação Pedro", "motivo": None,
    },
    {
        "data": "2026-05-02", "tipo": "Cliente Direto",
        "cliente": "Colégio Objetivo",
        "produto": "Substituição de 320 janelas basculantes por esquadrias de alumínio com veneziana integrada",
        "valor": 156_800.00,
        "mp": [
            {"item": "Perfil alumínio com veneziana integrada", "valor": 58_000.00},
            {"item": "Vidro temperado 6mm", "valor": 28_000.00},
            {"item": "Borrachas e vedação", "valor": 4_500.00},
        ],
        "status": "Orçamento gerado", "motivo": None,
    },
    # Prefeituras
    {
        "data": "2026-01-22", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Caçapava",
        "produto": "Reforma das janelas da UBS Central — 80 unidades em alumínio com vidro laminado",
        "valor": 52_000.00,
        "mp": [
            {"item": "Perfil alumínio anodizado 25 microns", "valor": 18_000.00},
            {"item": "Vidro laminado 6mm", "valor": 9_500.00},
            {"item": "Parafusos inox e silicone", "valor": 1_200.00},
        ],
        "status": "Pedido entregue", "motivo": None,
    },
    {
        "data": "2026-02-14", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Pindamonhangaba",
        "produto": "Cobertura metálica para quadra poliesportiva da Escola Estadual João Pessoa — 1.200 m²",
        "valor": 198_000.00,
        "mp": [
            {"item": "Telha sanduíche 50mm EPS", "valor": 68_000.00},
            {"item": "Estrutura metálica tubular", "valor": 52_000.00},
            {"item": "Calhas, rufo e fechamentos", "valor": 12_000.00},
        ],
        "status": "Pedido em execução", "motivo": None,
    },
    {
        "data": "2026-03-05", "tipo": "Prefeitura",
        "cliente": "Câmara Municipal de Jacareí",
        "produto": "Instalação de divisórias acústicas e vidros para sala de plenário — 340 m²",
        "valor": 89_500.00,
        "mp": [
            {"item": "Painel acústico divisória", "valor": 31_000.00},
            {"item": "Vidro laminado 8mm acústico", "valor": 22_000.00},
            {"item": "Perfis, acabamentos e instalação", "valor": 8_000.00},
        ],
        "status": "Orçamento aprovado", "motivo": None,
    },
    {
        "data": "2026-03-19", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Taubaté",
        "produto": "Fornecimento de coberturas para 3 pontos de ônibus — estrutura em aço galvanizado e policarbonato",
        "valor": 34_500.00,
        "mp": [
            {"item": "Tubo aço galvanizado estrutural", "valor": 9_800.00},
            {"item": "Policarbonato alveolar 10mm UV", "valor": 7_200.00},
            {"item": "Parafusos inox e pintura epóxi", "valor": 1_800.00},
        ],
        "status": "Orçamento aguardando aprovação Pedro", "motivo": None,
    },
    {
        "data": "2026-04-02", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Caçapava",
        "produto": "Ampliação do CRAS — fachada ACM e esquadrias de alumínio para nova ala",
        "valor": 127_000.00,
        "mp": [
            {"item": "Chapa ACM 4mm branco", "valor": 38_000.00},
            {"item": "Esquadrias alumínio linha 30", "valor": 27_000.00},
            {"item": "Vidro temperado 6mm", "valor": 11_000.00},
            {"item": "Estrutura e fixação", "valor": 9_500.00},
        ],
        "status": "Pedido gerado", "motivo": None,
    },
    {
        "data": "2026-04-25", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de São José dos Campos",
        "produto": "Cobertura para estacionamento do Paço Municipal — 2.800 m² em estrutura metálica com telha termoacústica",
        "valor": 487_000.00,
        "mp": [
            {"item": "Telha termoacústica 50mm", "valor": 148_000.00},
            {"item": "Estrutura metálica treliçada", "valor": 132_000.00},
            {"item": "Calhas, rufos e águas pluviais", "valor": 28_000.00},
            {"item": "Pintura anticorrosiva estrutura", "valor": 18_000.00},
        ],
        "status": "Orçamento aguardando aprovação cliente", "motivo": None,
    },
    {
        "data": "2026-05-08", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Lorena",
        "produto": "Reforma geral das esquadrias da Secretaria de Saúde — 60 janelas e 20 portas",
        "valor": 38_200.00,
        "mp": [
            {"item": "Perfil alumínio natural", "valor": 13_500.00},
            {"item": "Vidro temperado 4mm", "valor": 7_800.00},
            {"item": "Ferragens e vedação", "valor": 2_100.00},
        ],
        "status": "Orçamento recusado",
        "motivo": "Processo licitatório cancelado pela câmara por irregularidade no edital.",
    },
    {
        "data": "2026-05-20", "tipo": "Prefeitura",
        "cliente": "Prefeitura Municipal de Guaratinguetá",
        "produto": "Cobertura metálica para nova UPA — 950 m² com calhetão e iluminação zenital",
        "valor": 172_000.00,
        "mp": [
            {"item": "Telha metálica colorida galvanizada", "valor": 52_000.00},
            {"item": "Estrutura metálica", "valor": 44_000.00},
            {"item": "Domus de policarbonato (zenital)", "valor": 18_000.00},
            {"item": "Calhetão e rufos", "valor": 9_800.00},
        ],
        "status": "Orçamento gerado", "motivo": None,
    },
]


# ── Conexão ──────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ── Schema v2 ─────────────────────────────────────────────────────────────────

def _status_check() -> str:
    vals = ", ".join(f"'{s}'" for s in STATUS_VALIDOS)
    return f"CHECK(status IN ({vals}))"


def _criar_schema_v2(conn: sqlite3.Connection) -> None:
    status_chk = _status_check()
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            data_orcamento     TEXT    NOT NULL,
            tipo_cliente       TEXT    NOT NULL CHECK(tipo_cliente IN ('Cliente Direto', 'Prefeitura')),
            nome_cliente       TEXT    NOT NULL,
            descritivo_produto TEXT    NOT NULL,
            valor_total        REAL    NOT NULL,
            custo_total_mp     REAL    NOT NULL DEFAULT 0.0,
            status             TEXT    NOT NULL {status_chk},
            motivo_recusa      TEXT
        );

        CREATE TABLE IF NOT EXISTS itens_materia_prima (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id  INTEGER NOT NULL REFERENCES orcamentos(id) ON DELETE CASCADE,
            descricao_item TEXT   NOT NULL,
            valor          REAL   NOT NULL CHECK(valor >= 0)
        );

        CREATE TABLE IF NOT EXISTS historico_status (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL REFERENCES orcamentos(id) ON DELETE CASCADE,
            status       TEXT    NOT NULL,
            timestamp    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            responsavel  TEXT
        );

        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );
    """)
    conn.commit()


# ── Migração v1 → v2 ──────────────────────────────────────────────────────────

def _get_schema_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        return int(row[0]) if row[0] else 1
    except sqlite3.OperationalError:
        return 1


def _migrar_v1_para_v2(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # Lê todos os dados antigos antes de mexer no schema
    cursor.execute("""
        SELECT id, data_orcamento, tipo_cliente, nome_cliente, descritivo_produto,
               valor_total, materia_prima_json, custo_total_mp, status, motivo_recusa
        FROM orcamentos
    """)
    registros = cursor.fetchall()

    # Cria as novas tabelas auxiliares
    _criar_schema_v2(conn)

    # Cria tabela nova de orçamentos (sem materia_prima_json)
    status_chk = _status_check()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS orcamentos_v2 (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            data_orcamento     TEXT    NOT NULL,
            tipo_cliente       TEXT    NOT NULL CHECK(tipo_cliente IN ('Cliente Direto', 'Prefeitura')),
            nome_cliente       TEXT    NOT NULL,
            descritivo_produto TEXT    NOT NULL,
            valor_total        REAL    NOT NULL,
            custo_total_mp     REAL    NOT NULL DEFAULT 0.0,
            status             TEXT    NOT NULL {status_chk},
            motivo_recusa      TEXT
        )
    """)

    for row in registros:
        oid = row["id"]

        # Copia orçamento para a tabela nova
        cursor.execute("""
            INSERT INTO orcamentos_v2
                (id, data_orcamento, tipo_cliente, nome_cliente, descritivo_produto,
                 valor_total, custo_total_mp, status, motivo_recusa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (oid, row["data_orcamento"], row["tipo_cliente"], row["nome_cliente"],
              row["descritivo_produto"], row["valor_total"], row["custo_total_mp"],
              row["status"], row["motivo_recusa"]))

        # Migra itens de MP do JSON
        try:
            itens = json.loads(row["materia_prima_json"] or "[]")
            for item in itens:
                cursor.execute("""
                    INSERT INTO itens_materia_prima (orcamento_id, descricao_item, valor)
                    VALUES (?, ?, ?)
                """, (oid, item.get("item", ""), float(item.get("valor", 0))))
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

        # Cria o primeiro registro de histórico com a data do orçamento
        ts = row["data_orcamento"] + "T08:00:00"
        cursor.execute("""
            INSERT INTO historico_status (orcamento_id, status, timestamp)
            VALUES (?, ?, ?)
        """, (oid, row["status"], ts))

    # Substitui a tabela antiga
    cursor.execute("DROP TABLE orcamentos")
    cursor.execute("ALTER TABLE orcamentos_v2 RENAME TO orcamentos")

    cursor.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (2)")
    conn.commit()


# ── Seed ─────────────────────────────────────────────────────────────────────

def _popular_banco(conn: sqlite3.Connection) -> int:
    cursor = conn.cursor()
    if cursor.execute("SELECT COUNT(*) FROM orcamentos").fetchone()[0] > 0:
        return 0

    inseridos = 0
    for row in SEED_DATA:
        custo = sum(i["valor"] for i in row["mp"])
        cursor.execute("""
            INSERT INTO orcamentos
                (data_orcamento, tipo_cliente, nome_cliente, descritivo_produto,
                 valor_total, custo_total_mp, status, motivo_recusa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (row["data"], row["tipo"], row["cliente"], row["produto"],
              row["valor"], custo, row["status"], row["motivo"]))

        oid = cursor.lastrowid
        for item in row["mp"]:
            cursor.execute("""
                INSERT INTO itens_materia_prima (orcamento_id, descricao_item, valor)
                VALUES (?, ?, ?)
            """, (oid, item["item"], item["valor"]))

        ts = row["data"] + "T08:00:00"
        cursor.execute("""
            INSERT INTO historico_status (orcamento_id, status, timestamp)
            VALUES (?, ?, ?)
        """, (oid, row["status"], ts))

        inseridos += 1

    conn.commit()
    return inseridos


# ── Inicialização pública ─────────────────────────────────────────────────────

def inicializar() -> sqlite3.Connection:
    conn = get_connection()

    # Verifica se existe a tabela de orçamentos (pode ser schema antigo ou novo)
    tabelas = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}

    if "orcamentos" not in tabelas:
        # Banco vazio — cria schema v2 direto
        _criar_schema_v2(conn)
        conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (2)")
        conn.commit()
    elif _get_schema_version(conn) < SCHEMA_VERSION:
        # Schema v1 detectado — migra
        _migrar_v1_para_v2(conn)

    n = _popular_banco(conn)
    if n:
        print(f"[DB] {n} registros de seed inseridos.")
    return conn


if __name__ == "__main__":
    inicializar()
    print(f"[DB] Banco inicializado em: {DB_PATH}")
