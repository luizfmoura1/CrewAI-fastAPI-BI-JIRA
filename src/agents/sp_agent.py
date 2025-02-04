from crewai import Agent, Task, Crew

def create_story_agent(story_data):
    story_agent = Agent(
        role="Analista de Story Points",
        goal="Para cada desenvolvedor, somar os story points.",
        backstory="""Você é um especialista em métricas ágeis com expertise em JIRA. Suas análises ajudam times de desenvolvimento 
        a entenderem sua capacidade por sprint. Domina técnicas de data wrangling para extrair métricas de estruturas JSON complexas,
        identificando discrepâncias entre responsáveis e executores. Tem um olhar crítico para dados inconsistentes e sempre valida
        a origem das informações antes de calcular as métricas.""",
        verbose=True,
        allow_delegation=False
    )

    story_agent_task = Task(
        description="""
        ## Análise de Dados de Sprint
        
        **Estrutura dos Dados:**
        - JSON contendo issues do JIRA
        - Campos relevantes:
          * Story Points: issues.fields.customfield_10106
          * Responsável: issues.fields.assignee.displayName
          * Desenvolvedor: issues.fields.customfield_10172

        **Processamento:**
        1. Identificar o desenvolvedor correto:
           - Se responsável = "Estagiário", usar campo customfield_10172
           - Validar se nome do desenvolvedor existe
        2. Coletar story points:
           - Considerar 0 se campo estiver vazio
           - Registrar cards sem story points
        3. Agregar dados:
           - Agrupar cards por desenvolvedor
           - Somar pontos por desenvolvedor
           - Contar cards válidos/inválidos

        **Input:**
        ```json
        {data}
        ```
        """,
        expected_output="""
        **Relatório Consolidado:**
        - Total de cards analisados: [X]
        - Cards com story points: [Y]
        - Cards sem story points: [Z]

        **Desenvolvedores:**
        | Nome           | Story Points | Cards Atribuídos |
        |----------------|--------------|-------------------|
        | Desenvolvedor A | 13           | PROJ-123, PROJ-456|
        | Desenvolvedor B | 8            | PROJ-789          |

        **Listas:**
        - Cards sem story points: [PROJ-001, PROJ-002]
        - Cards com responsável inválido: [PROJ-003]
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