from fastapi import APIRouter
from crewai import Task, Crew
from agents.retrabalho_agent import create_retrabalho_agent
from agents.story_points_agent import create_story_points_agent

router = APIRouter()

@router.get("/analyze")
def analyze():
    # Criando os agentes
    retrabalho_agent = create_retrabalho_agent()
    story_points_agent = create_story_points_agent()

    # Criando as tarefas
    retrabalho_task = Task(
        description="Analisar o número de alterações no status dos cards.",
        agent=retrabalho_agent
    )

    story_points_task = Task(
        description="Somar os valores de story points agrupados por dia ou semana.",
        agent=story_points_agent
    )

    # Criando a equipe (Crew)
    crew = Crew(
        agents=[retrabalho_agent, story_points_agent],
        tasks=[retrabalho_task, story_points_task],
        verbose=2
    )

    # Executando as tarefas
    result = crew.kickoff()

    return {"result": result}