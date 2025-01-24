from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
    rework_agent = Agent(
        role="Analista de Cards",
        goal="Identificar os desenvolvedores, listar os cards vinculados a eles e contar o número total de cards por desenvolvedor.",
        backstory="""
        Você é um especialista em análise de workflow de desenvolvimento. Seu objetivo é conectar-se ao JIRA, identificar os desenvolvedores, listar os cards vinculados a eles e fornecer o número total de cards associados a cada desenvolvedor.
        """,
        verbose=True,
        allow_delegation=False
    )

    rework_agent_task = Task(
        description="""
            Esta task conecta-se ao JIRA, extrai todos os cards do board e realiza a análise para identificar:
            1. O nome do desenvolvedor.
            2. Os cards vinculados a ele.
            3. A quantidade total de cards atribuída ao desenvolvedor.

            Dados a serem analisados:
            -----------------
            {data}
            -----------------
        """,
        expected_output="""
            O resultado final deve listar para cada desenvolvedor:
            - Nome do desenvolvedor e os cards vinculados a ele.
            - todas as informações vinculadas a todos os cards
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
    