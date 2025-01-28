from crewai import Agent, Task, Crew

def create_retrabalho_agent(rework_data):
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

        - Sempre que o responsável pelo card for um **Estagiário** você deve substituir o nome do responsável pelo desenvolvedor presente na customfield_10172.
        
        """,
        expected_output="""
            Como resultado final, deve ser separada a soma de story points de cada desenvolvedor.
        """,
        agent=story_agent
    )

    crew = Crew(
        name='Story Crew',
        agents=[story_agent],
        tasks=[story_agent_task],
        verbose=True
    )

    return crew.kickoff(inputs={'data': rework_data})
