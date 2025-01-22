from crewai import Agent, Task, Crew

def create_story_points_agent(story_data):
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
            Como resultado espero a soma do story point de cada desenvolvedor, separado por dia e semana.
        """,
        agent=story_agent
    )

    crew = Crew(
        name='Story Crew',
        agents=[story_agent],
        tasks=[story_agent_task],
        verbose= True
    )
    return crew.kickoff(inputs = {'data': story_data})
