from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, empresas, ecac, fgts, tron, tarefas, relatorios

app = FastAPI(title="NewCamps Sistema", version="0.1.0", docs_url="/docs", redoc_url="/redoc", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(empresas.router, prefix="/empresas", tags=["empresas"])
app.include_router(ecac.router, prefix="/ecac", tags=["ecac"])
app.include_router(fgts.router, prefix="/fgts", tags=["fgts"])
app.include_router(tron.router, prefix="/tron", tags=["tron"])
app.include_router(tarefas.router, prefix="/tarefas", tags=["tarefas"])
app.include_router(relatorios.router, prefix="/relatorios", tags=["relatorios"])


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}
