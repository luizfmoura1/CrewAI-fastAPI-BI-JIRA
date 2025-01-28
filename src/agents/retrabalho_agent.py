from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
    story_agent = Agent(
        role="Analista de Story Points",
        goal="Para cada desenvolvedor, somar os story points por dia e por semana.",
        backstory="Você é um analista de story points, responsável por calcular os story points de cada desenvolvedor, por dia e por semana.",
        verbose=True,
        allow_delegation=False
    )

    story_agent_task = Task(
        description="""
    "Esta task é responsável por medir a soma do story points de todos os cards separados por desenvolvedores individualmente."
    "Story point se refere a estrutura do JSON, 'priority' -> 'id'."
    "Dados a serem analisados a seguir:
    ---------------------
    {data}
    ---------------------
    "
    """,
    expected_output="""
            Como resultado final, deve ser separado a soma de story points de cada desenvolvedor por dia mencinando a data, e por semana.
        """,
        agent=story_agent
    )

    crew = Crew(
        name='Story Crew',
        agents=[story_agent],
        tasks=[story_agent_task],
        verbose= True
    )

    return crew.kickoff(inputs={'data': rework_data})

    