from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Analisar o número de alterações no status dos cards e identificar padrões de retrabalho.",
        backstory="Você é um especialista em análise de fluxo de trabalho e identifica padrões de retrabalho,individualmente para cada deselvolvedor, em um board no JIRA. Retrabalho é quando um **CARD**, se encontra na coluna Planejados/Reprovados, e está com o status 'Reprovado'.",
        verbose=True,
        allow_delegation=False
    )

    rework_agent_task = Task(
        description="""
            "Esta task conecta-se ao JIRA, extrai os cards na coluna Planejados/Reprovados com status 'Reprovado', "
            "analisa as mudanças de status ao longo do tempo e identifica padrões de retrabalho individualmente para cada desenvolvedor.",
            "Dados a serem analisados a seguir: 
            -----------------
            {data}
            -----------------
            "
        """,
        expected_output="""
            Como resultado quero os dados resultantes da sua análside individualmente para cada desenvolvedor
        """,
        agent=rework_agent  
    )

    crew = Crew(
        name='Rework Crew',
        agents=rework_agent,
        tasks=rework_agent_task,
        verbose= True
    )
    return crew.kickoff(inputs = {'data': rework_data})