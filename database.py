"""
Inicialização e seed do banco de dados SQLite para o sistema de orçamentos/pedidos.
"""
import sqlite3
import json
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


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            data_orcamento     TEXT    NOT NULL,
            tipo_cliente       TEXT    NOT NULL CHECK(tipo_cliente IN ('Cliente Direto', 'Prefeitura')),
            nome_cliente       TEXT    NOT NULL,
            descritivo_produto TEXT    NOT NULL,
            valor_total        REAL    NOT NULL,
            materia_prima_json TEXT    NOT NULL DEFAULT '[]',
            custo_total_mp     REAL    NOT NULL DEFAULT 0.0,
            status             TEXT    NOT NULL,
            motivo_recusa      TEXT
        )
    """)
    conn.commit()


def _mp(itens: list[dict]) -> tuple[str, float]:
    """Retorna (json_serializado, soma_dos_valores)."""
    total = sum(i["valor"] for i in itens)
    return json.dumps(itens, ensure_ascii=False), total


SEED_DATA = [
    # --- Clientes Diretos ---
    {
        "data_orcamento": "2026-01-15",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Construtora Horizonte Ltda",
        "descritivo_produto": "Fabricação de 200 esquadrias de alumínio linha 45 para residencial alto padrão",
        "valor_total": 87_500.00,
        "mp": [
            {"item": "Perfil alumínio linha 45", "valor": 32_000.00},
            {"item": "Vidro temperado 8mm", "valor": 15_000.00},
            {"item": "Acessórios e ferragens", "valor": 4_200.00},
        ],
        "status": "Pedido entregue",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-02-03",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Incorporadora Viva Mais S/A",
        "descritivo_produto": "Fornecimento e instalação de fachada em ACM para torre comercial — 4.200 m²",
        "valor_total": 312_000.00,
        "mp": [
            {"item": "Chapa ACM 4mm cinza grafite", "valor": 98_000.00},
            {"item": "Estrutura metálica galvanizada", "valor": 45_000.00},
            {"item": "Fixadores e selantes", "valor": 8_500.00},
        ],
        "status": "Pedido em execução",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-02-20",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Clínica São Lucas",
        "descritivo_produto": "Divisórias internas em drywall e vidro temperado — reforma da área administrativa",
        "valor_total": 28_900.00,
        "mp": [
            {"item": "Vidro temperado 10mm", "valor": 9_200.00},
            {"item": "Perfil drywall e chapas", "valor": 5_800.00},
            {"item": "Massa, fita e acabamentos", "valor": 1_100.00},
        ],
        "status": "Orçamento aprovado",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-03-10",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Auto Peças Saveiro ME",
        "descritivo_produto": "Cobertura metálica para pátio de estacionamento — 600 m²",
        "valor_total": 41_200.00,
        "mp": [
            {"item": "Telha metálica trapezoidal galvanizada", "valor": 14_500.00},
            {"item": "Estrutura tubular metálica", "valor": 11_000.00},
            {"item": "Calha e rufos", "valor": 2_300.00},
        ],
        "status": "Orçamento aguardando aprovação cliente",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-03-28",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Supermercado Bom Preço",
        "descritivo_produto": "Instalação de porta automática de vidro duplo na entrada principal",
        "valor_total": 19_800.00,
        "mp": [
            {"item": "Vidro duplo laminado", "valor": 7_500.00},
            {"item": "Motor automático Dorma", "valor": 4_800.00},
            {"item": "Perfil e trilho inox", "valor": 2_100.00},
        ],
        "status": "Orçamento recusado",
        "motivo_recusa": "Cliente optou por fornecedor local com preço 18% menor.",
    },
    {
        "data_orcamento": "2026-04-05",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Construtora Horizonte Ltda",
        "descritivo_produto": "Segunda fase: 150 portas de alumínio com vidro jateado — blocos B e C",
        "valor_total": 63_000.00,
        "mp": [
            {"item": "Perfil alumínio porta", "valor": 21_000.00},
            {"item": "Vidro jateado 6mm", "valor": 12_500.00},
            {"item": "Ferragens e dobradiças", "valor": 3_800.00},
        ],
        "status": "Pedido gerado",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-04-18",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Hotel Grand Palace",
        "descritivo_produto": "Fachada de vidro estrutural spider com perfis de aço inox — lobby e restaurante",
        "valor_total": 215_000.00,
        "mp": [
            {"item": "Vidro laminado 12mm estrutural", "valor": 72_000.00},
            {"item": "Spider e conectores inox 316L", "valor": 38_000.00},
            {"item": "Perfil inox e silicone estrutural", "valor": 14_000.00},
        ],
        "status": "Orçamento aguardando aprovação Pedro",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-05-02",
        "tipo_cliente": "Cliente Direto",
        "nome_cliente": "Colégio Objetivo",
        "descritivo_produto": "Substituição de 320 janelas basculantes por esquadrias de alumínio com veneziana integrada",
        "valor_total": 156_800.00,
        "mp": [
            {"item": "Perfil alumínio com veneziana integrada", "valor": 58_000.00},
            {"item": "Vidro temperado 6mm", "valor": 28_000.00},
            {"item": "Borrachas e vedação", "valor": 4_500.00},
        ],
        "status": "Orçamento gerado",
        "motivo_recusa": None,
    },

    # --- Prefeituras ---
    {
        "data_orcamento": "2026-01-22",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Caçapava",
        "descritivo_produto": "Reforma das janelas da UBS Central — 80 unidades em alumínio com vidro laminado",
        "valor_total": 52_000.00,
        "mp": [
            {"item": "Perfil alumínio anodizado 25 microns", "valor": 18_000.00},
            {"item": "Vidro laminado 6mm", "valor": 9_500.00},
            {"item": "Parafusos inox e silicone", "valor": 1_200.00},
        ],
        "status": "Pedido entregue",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-02-14",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Pindamonhangaba",
        "descritivo_produto": "Cobertura metálica para quadra poliesportiva da Escola Estadual João Pessoa — 1.200 m²",
        "valor_total": 198_000.00,
        "mp": [
            {"item": "Telha sanduíche 50mm EPS", "valor": 68_000.00},
            {"item": "Estrutura metálica tubular", "valor": 52_000.00},
            {"item": "Calhas, rufo e fechamentos", "valor": 12_000.00},
        ],
        "status": "Pedido em execução",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-03-05",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Câmara Municipal de Jacareí",
        "descritivo_produto": "Instalação de divisórias acústicas e vidros para sala de plenário — 340 m²",
        "valor_total": 89_500.00,
        "mp": [
            {"item": "Painel acústico divisória", "valor": 31_000.00},
            {"item": "Vidro laminado 8mm acústico", "valor": 22_000.00},
            {"item": "Perfis, acabamentos e instalação", "valor": 8_000.00},
        ],
        "status": "Orçamento aprovado",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-03-19",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Taubaté",
        "descritivo_produto": "Fornecimento de coberturas para 3 pontos de ônibus — estrutura em aço galvanizado e policarbonato",
        "valor_total": 34_500.00,
        "mp": [
            {"item": "Tubo aço galvanizado estrutural", "valor": 9_800.00},
            {"item": "Policarbonato alveolar 10mm UV", "valor": 7_200.00},
            {"item": "Parafusos inox e pintura epóxi", "valor": 1_800.00},
        ],
        "status": "Orçamento aguardando aprovação Pedro",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-04-02",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Caçapava",
        "descritivo_produto": "Ampliação do CRAS — fachada ACM e esquadrias de alumínio para nova ala",
        "valor_total": 127_000.00,
        "mp": [
            {"item": "Chapa ACM 4mm branco", "valor": 38_000.00},
            {"item": "Esquadrias alumínio linha 30", "valor": 27_000.00},
            {"item": "Vidro temperado 6mm", "valor": 11_000.00},
            {"item": "Estrutura e fixação", "valor": 9_500.00},
        ],
        "status": "Pedido gerado",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-04-25",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de São José dos Campos",
        "descritivo_produto": "Cobertura para estacionamento do Paço Municipal — 2.800 m² em estrutura metálica com telha termoacústica",
        "valor_total": 487_000.00,
        "mp": [
            {"item": "Telha termoacústica 50mm", "valor": 148_000.00},
            {"item": "Estrutura metálica treliçada", "valor": 132_000.00},
            {"item": "Calhas, rufos e águas pluviais", "valor": 28_000.00},
            {"item": "Pintura anticorrosiva estrutura", "valor": 18_000.00},
        ],
        "status": "Orçamento aguardando aprovação cliente",
        "motivo_recusa": None,
    },
    {
        "data_orcamento": "2026-05-08",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Lorena",
        "descritivo_produto": "Reforma geral das esquadrias da Secretaria de Saúde — 60 janelas e 20 portas",
        "valor_total": 38_200.00,
        "mp": [
            {"item": "Perfil alumínio natural", "valor": 13_500.00},
            {"item": "Vidro temperado 4mm", "valor": 7_800.00},
            {"item": "Ferragens e vedação", "valor": 2_100.00},
        ],
        "status": "Orçamento recusado",
        "motivo_recusa": "Processo licitatório cancelado pela câmara por irregularidade no edital.",
    },
    {
        "data_orcamento": "2026-05-20",
        "tipo_cliente": "Prefeitura",
        "nome_cliente": "Prefeitura Municipal de Guaratinguetá",
        "descritivo_produto": "Cobertura metálica para nova UPA — 950 m² com calhetão e iluminação zenital",
        "valor_total": 172_000.00,
        "mp": [
            {"item": "Telha metálica colorida galvanizada", "valor": 52_000.00},
            {"item": "Estrutura metálica", "valor": 44_000.00},
            {"item": "Domus de policarbonato (zenital)", "valor": 18_000.00},
            {"item": "Calhetão e rufos", "valor": 9_800.00},
        ],
        "status": "Orçamento gerado",
        "motivo_recusa": None,
    },
]


def popular_banco(conn: sqlite3.Connection) -> int:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orcamentos")
    if cursor.fetchone()[0] > 0:
        return 0

    inseridos = 0
    for row in SEED_DATA:
        mp_json, custo_mp = _mp(row["mp"])
        conn.execute(
            """
            INSERT INTO orcamentos
                (data_orcamento, tipo_cliente, nome_cliente, descritivo_produto,
                 valor_total, materia_prima_json, custo_total_mp, status, motivo_recusa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["data_orcamento"],
                row["tipo_cliente"],
                row["nome_cliente"],
                row["descritivo_produto"],
                row["valor_total"],
                mp_json,
                custo_mp,
                row["status"],
                row["motivo_recusa"],
            ),
        )
        inseridos += 1

    conn.commit()
    return inseridos


def inicializar() -> sqlite3.Connection:
    conn = get_connection()
    criar_tabelas(conn)
    n = popular_banco(conn)
    if n:
        print(f"[DB] {n} registros de seed inseridos.")
    return conn


if __name__ == "__main__":
    inicializar()
    print(f"[DB] Banco inicializado em: {DB_PATH}")
