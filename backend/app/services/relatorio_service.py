from fastapi import HTTPException
from app.models.tarefa import Tarefa


def gerar_pdf_tarefa(tarefa: Tarefa) -> bytes:
    try:
        from weasyprint import HTML
    except OSError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"WeasyPrint indisponível neste ambiente (GTK ausente): {exc}",
        )
    resultado = tarefa.resultado or {}
    html = _render_html(tarefa, resultado)
    return HTML(string=html).write_pdf()


def _render_html(tarefa: Tarefa, resultado: dict) -> str:
    linhas = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in resultado.items()
    )
    return f"""
    <html><head><meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; padding: 40px; }}
      h1 {{ color: #1a1a1a; }}
      table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
      td, th {{ border: 1px solid #ddd; padding: 8px 12px; }}
      th {{ background: #f4f4f4; }}
    </style></head>
    <body>
      <h1>NewCamps Sistema</h1>
      <h2>Relatório — Tarefa #{tarefa.id}</h2>
      <p><b>Tipo:</b> {tarefa.tipo} &nbsp; <b>Status:</b> {tarefa.status}</p>
      <p><b>Empresa ID:</b> {tarefa.empresa_id} &nbsp; <b>Criado em:</b> {tarefa.criado_em}</p>
      <table><tr><th>Campo</th><th>Valor</th></tr>{linhas}</table>
    </body></html>
    """
