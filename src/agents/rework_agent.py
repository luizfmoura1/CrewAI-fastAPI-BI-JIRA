from crewai import Agent, Task, Crew
from typing import Dict, Any

def create_rework_agent(reprovados_data: list) -> Dict[str, Any]:
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Calcular o índice de retrabalho por desenvolvedor",
        backstory="""Especialista em análise de qualidade de código com experiência em métricas ágeis.
        Responsável por identificar padrões de retrabalho em cards do JIRA e propor melhorias no processo de desenvolvimento.""",
        verbose=True
    )

    rework_task = Task(
        description="""
        ## Análise de Cards Reprovados
        
        **Objetivo:**  
        Processar dados de reprovação para calcular métricas de retrabalho por desenvolvedor
        
        **Processamento:**  
        1. Para cada entrada em 'reprovado_entries':
           - Identificar desenvolvedor responsável:
             - Usar campo 'desenvolvedor' se 'responsavel' for 'Estagiarios'
             - Manter nome original do 'responsavel' nos demais casos
           - Coletar chave do card (card_key)
        
        2. Agregar dados:
           - Contar ocorrências por desenvolvedor
           - Contar reprovações por card
           - Listar cards associados a cada desenvolvedor
        
        **Regras:**
        - Manter nomes originais sem normalização
        - Cards sem informação clara devem ser registrados separadamente
        - Priorizar dados explícitos do campo 'desenvolvedor'
        
        **Dados de Entrada:**
        {reprovado_entries}
        """,
        expected_output="""
        **Resultado Consolidado:**
        
        ### Desenvolvedores (ordem decrescente)
        | Desenvolvedor    | Reprovações | Cards Associados          |
        |------------------|-------------|---------------------------|
        | [Nome]           | [N]         | [GER-123, GER-456]        |
        

        
        **Total de Cards Analisados:** [X]
        **Total de cards com no mínimo 1 reprovação:** [Y]
        """,
        agent=rework_agent,
        inputs={'reprovado_entries': reprovados_data}
    )

    crew = Crew(
        agents=[rework_agent],
        tasks=[rework_task],
        verbose=True
    )

    return crew.kickoff(inputs={'reprovado_entries': reprovados_data})