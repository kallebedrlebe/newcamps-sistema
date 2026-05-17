"""Ferramentas CrewAI para consulta de dados do e-CAC."""
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from automation.ecac.debitos import consultar_debitos


class ConsultaDebitosInput(BaseModel):
    empresa_id: int = Field(description="ID da empresa no banco de dados")


class ConsultaDebitosTool(BaseTool):
    name: str = "consultar_debitos_ecac"
    description: str = (
        "Consulta os débitos federais de uma empresa no portal e-CAC da Receita Federal. "
        "Retorna lista de débitos com código, competência e valor."
    )
    args_schema: type[BaseModel] = ConsultaDebitosInput

    def _run(self, empresa_id: int) -> dict:
        return consultar_debitos(empresa_id)
