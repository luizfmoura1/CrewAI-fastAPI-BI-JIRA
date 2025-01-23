from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Analisar o número de alterações no status dos cards e identificar padrões de retrabalho.",
        backstory="""Você é um especialista em análise de fluxo de trabalho e identifica padrões de retrabalho,individualmente para cada deselvolvedor, em um board no JIRA. Retrabalho é quando um **CARD**, se encontra na coluna Planejados/Reprovados, e está com o status 'Reprovado'.
        **ATENÇÃO**
            - Sempre que um card estiver viculado a um 'Estagiário' você deve procurar pelo nome verdadeiro desse estágiario no tópico 'Desenvolvedor'.
            - Um card pode ser reprovado N vezes, ou seja retrabalho = N.
        """,
        verbose=True,
        allow_delegation=False
    )

    rework_agent_task = Task(
        description="""
            "Esta task conecta-se ao JIRA, extrai todos os cards do board e ao fim separa os casos de retrabalho separado por desenvolvedor."
            "Deve ser analisado todos os issues do board, e a resposta final deve ser o a soma de índice de retrabalho de cada desenvolvedor.",
            "Caso um desenvolvedor tenha 0 de indice de retrabalho, ele *deve* ser incluido na resposta final.",
            "Dados a serem analisados a seguir: 
            -----------------
            {data}
            -----------------
            "
            """,
        expected_output="""
            Como resultado quero a soma de retrabalho para cada desenvolvedor.
        """,
        agent=rework_agent  
    )

    crew = Crew(
        name='Rework Crew',
        agents=[rework_agent],
        tasks=[rework_agent_task],
        verbose= True
    )
    return crew.kickoff(inputs = {'data': rework_data})