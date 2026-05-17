from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tarefa import Tarefa
from app.services.relatorio_service import gerar_pdf_tarefa

router = APIRouter()


@router.get("/{tarefa_id}/pdf")
def pdf_tarefa(tarefa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.status != "CONCLUIDA":
        raise HTTPException(status_code=409, detail="Tarefa ainda não concluída")
    pdf_bytes = gerar_pdf_tarefa(tarefa)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tarefa_{tarefa_id}.pdf"},
    )
