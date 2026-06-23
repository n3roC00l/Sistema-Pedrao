"""
Notificador de aging — Painel Pedrão / Cilla Tech Park
Enviar: python notificador.py
Agendar: Windows Task Scheduler ou cron rodando diariamente.

Variáveis de ambiente (.env):
    SMTP_HOST      ex: smtp.gmail.com
    SMTP_PORT      ex: 587
    SMTP_USER      ex: seuemail@gmail.com
    SMTP_PASS      senha de app do Gmail (não a senha normal)
    NOTIFY_TO      destinatário, ex: pedro@cillatechpark.com.br
"""
import os
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).parent / "orcamentos.db"
AGING_ALERTA_DIAS = 30


def buscar_alertas() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT
            o.nome_cliente, o.valor_total, o.status,
            CAST(
                JULIANDAY(DATE('now')) -
                JULIANDAY(DATE(COALESCE(h.ultima_mudanca, o.data_orcamento)))
            AS INTEGER) AS aging_dias
        FROM orcamentos o
        LEFT JOIN (
            SELECT orcamento_id, MAX(timestamp) AS ultima_mudanca
            FROM historico_status GROUP BY orcamento_id
        ) h ON h.orcamento_id = o.id
        WHERE o.arquivado = 0
          AND o.status NOT IN ('Orçamento recusado', 'Pedido entregue')
          AND CAST(
                JULIANDAY(DATE('now')) -
                JULIANDAY(DATE(COALESCE(h.ultima_mudanca, o.data_orcamento)))
              AS INTEGER) > ?
        ORDER BY aging_dias DESC
    """, (AGING_ALERTA_DIAS,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def formatar_brl(v: float) -> str:
    return f"R$ {v:_.2f}".replace(".", ",").replace("_", ".")


def montar_email(alertas: list[dict]) -> tuple[str, str]:
    linhas_html = ""
    linhas_txt = ""
    for a in alertas:
        cor = "#EF4444" if a["aging_dias"] > 60 else "#F59E0B"
        linhas_html += (
            f"<tr>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #334155'>{a['nome_cliente']}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #334155'>{formatar_brl(a['valor_total'])}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #334155'>{a['status']}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #334155;color:{cor};font-weight:700'>{a['aging_dias']}d</td>"
            f"</tr>"
        )
        linhas_txt += f"  • {a['nome_cliente']} | {formatar_brl(a['valor_total'])} | {a['status']} | {a['aging_dias']} dias\n"

    html = f"""
    <html><body style="font-family:Inter,sans-serif;background:#0F172A;color:#F1F5F9;padding:24px">
    <h2 style="color:#C2892B;margin-bottom:4px">Cilla Tech Park — Alertas de Aging</h2>
    <p style="color:#64748B;margin-top:0">{len(alertas)} negócio(s) parado(s) há mais de {AGING_ALERTA_DIAS} dias</p>
    <table style="width:100%;border-collapse:collapse;background:#1E293B;border-radius:8px;overflow:hidden">
      <thead>
        <tr style="background:#0F172A">
          <th style="padding:10px 12px;text-align:left;color:#94A3B8;font-size:0.75rem;text-transform:uppercase">Cliente</th>
          <th style="padding:10px 12px;text-align:left;color:#94A3B8;font-size:0.75rem;text-transform:uppercase">Valor</th>
          <th style="padding:10px 12px;text-align:left;color:#94A3B8;font-size:0.75rem;text-transform:uppercase">Status</th>
          <th style="padding:10px 12px;text-align:left;color:#94A3B8;font-size:0.75rem;text-transform:uppercase">Parado</th>
        </tr>
      </thead>
      <tbody>{linhas_html}</tbody>
    </table>
    <p style="margin-top:20px;color:#475569;font-size:0.8rem">Acesse o painel para tomar ação.</p>
    </body></html>
    """
    texto = (
        f"Cilla Tech Park — Alertas de Aging\n"
        f"{len(alertas)} negócio(s) parado(s) há mais de {AGING_ALERTA_DIAS} dias:\n\n"
        + linhas_txt
    )
    return texto, html


def enviar(alertas: list[dict]) -> None:
    host  = os.environ["SMTP_HOST"]
    port  = int(os.environ.get("SMTP_PORT", 587))
    user  = os.environ["SMTP_USER"]
    pwd   = os.environ["SMTP_PASS"]
    dest  = os.environ["NOTIFY_TO"]

    texto, html = montar_email(alertas)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[CTP] {len(alertas)} negócio(s) parado(s) — ação necessária"
    msg["From"]    = user
    msg["To"]      = dest
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))

    with smtplib.SMTP(host, port) as s:
        s.ehlo()
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, dest, msg.as_string())
    print(f"[notificador] E-mail enviado para {dest} — {len(alertas)} alerta(s).")


if __name__ == "__main__":
    alertas = buscar_alertas()
    if not alertas:
        print("[notificador] Nenhum alerta de aging. Nenhum e-mail enviado.")
    else:
        enviar(alertas)
