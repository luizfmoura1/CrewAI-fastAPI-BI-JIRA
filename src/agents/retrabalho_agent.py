from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
    rework_agent = Agent(
        role="Analista de Cards",
        goal="Retornar o changelog do card mais recente.",
        backstory="""
        Você é um especialista em análise de workflow de desenvolvimento. Seu objetivo é identificar o card mais antigo e retornar seu changelog.
        """,
        verbose=True,
        allow_delegation=False
    )

    rework_agent_task = Task(
        description="""
            Esta task analisa os dados fornecidos e retorna o changelog do card mais antigo.

            Dados a serem analisados:
            -----------------
            {data}
            -----------------
        """,
        expected_output="""
            O changelog do card mais antigo.
        """,
        agent=rework_agent
    )

    crew = Crew(
        name='Rework Crew',
        agents=[rework_agent],
        tasks=[rework_agent_task],
        verbose=True
    )

    return crew.kickoff(inputs={'data': rework_data})