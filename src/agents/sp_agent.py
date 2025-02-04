from crewai import Agent, Task, Crew

def create_story_agent(story_data):
    story_agent = Agent(
        role="Analista de Story Points",
        goal="Para cada desenvolvedor, somar os story points.",
        backstory="Você é um analista de story points, responsável por calcular os story points de cada desenvolvedor.",
        verbose=True,
        allow_delegation=False
    )

    story_agent_task = Task(
        description="""
        "Esta task é responsável por medir a soma do story points de todos os cards, separados por desenvolvedores individualmente."
        
        Dados a serem analisados a seguir:
        ---------------------
        {data}
        ---------------------
        ""
        Analise cuidadosamente a estrutura JSON dos dados.
        - Story Points estão em issues.fields.customfield_10106
        - Responsável está em issues.fields.assignee.displayName
        - Desenvolvedor está em issues.fields.customfield_10172
        ""

        **ATENÇÃO**

        -# Em sp_agente.py
        - Sempre que o responsável for um **Estagiário**, substituir pelo customfield_10172.
        
        """,
        expected_output="""
        - Tabela ordenada de desenvolvedores e contagem de story points.
        - Key dos cards com story points
        - Lista de quais cards pertencem a cada desenvolvedor.
        - Contagem total de cards encontrados na análise.
        - Contagem total de cards com story points.
        """,
        agent=story_agent
    )

    crew = Crew(
        name='Story Crew',
        agents=[story_agent],
        tasks=[story_agent_task],
        verbose=True
    )

    return crew.kickoff(inputs={'data': story_data})
