"""Crew CrewAI para análise de situação fiscal no e-CAC."""
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from agents.tools.ecac_tools import ConsultaDebitosTool
from app.config import settings

_llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=settings.ANTHROPIC_API_KEY,
)

_consulta_tool = ConsultaDebitosTool()

analisador = Agent(
    role="Analista Fiscal",
    goal="Analisar a situação fiscal da empresa no e-CAC e identificar riscos e prioridades",
    backstory=(
        "Você é um contador especialista em tributos federais brasileiros. "
        "Conhece profundamente as regras da Receita Federal, parcelamentos e DARF."
    ),
    tools=[_consulta_tool],
    llm=_llm,
    verbose=True,
)

def analisar_empresa(empresa_id: int) -> str:
    tarefa = Task(
        description=(
            f"Consulte os débitos da empresa ID {empresa_id} no e-CAC. "
            "Analise os débitos encontrados: quais têm maior valor, quais estão vencidos, "
            "e recomende ações prioritárias (pagamento à vista, parcelamento, etc.)."
        ),
        expected_output=(
            "Relatório estruturado com: lista de débitos, análise de risco e recomendações."
        ),
        agent=analisador,
    )

    crew = Crew(
        agents=[analisador],
        tasks=[tarefa],
        process=Process.sequential,
        verbose=True,
    )
    return crew.kickoff()
