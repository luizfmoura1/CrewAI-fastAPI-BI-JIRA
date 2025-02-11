from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List

def create_rework_agent(reprovados_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    llm = LLM(
        model="gpt-4o",
        temperature=0.7,
        seed=0
    )
    
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Calcular o índice de retrabalho por desenvolvedor",
        backstory="""Especialista em análise de qualidade de código com experiência em métricas ágeis.
        Responsável por identificar padrões de retrabalho em cards do JIRA e propor melhorias no processo de desenvolvimento.""",
        llm=llm,
        verbose=True
    )

    rework_task = Task(
        description="""
        ## Análise de Cards Reprovados
        
        **Objetivo:**  
        Processar dados de reprovação para calcular métricas de retrabalho por desenvolvedor.
        
        **Processamento:**  
        1. Para cada entrada em 'reprovado_entries':
           - Identificar desenvolvedor responsável:
             - Se 'responsavel' for 'Estagiarios', usar o campo 'desenvolvedor' para identificar o desenvolvedor.
             - Caso contrário, usar o nome do 'responsavel'.
           - Coletar chave do card (card_key).
           - Para saber quantos cards foram encontrados, deve se contar quantos valores de car_key existem.
        
        2. Agregar dados:
           - Contar ocorrências de reprovações por desenvolvedor.
           - Contar quantos cards únicos foram reprovados por desenvolvedor.
           - Listar os cards associados a cada desenvolvedor.
        
        **Regras:**
        - Manter nomes originais sem normalização.
        - Todos os cards devem ser considerados, mesmo que não tenham reprovações.
        
        **Dados de Entrada:**
        {reprovado_entries}
        """,
        expected_output="""
        **Resultado Consolidado:**
        
        ### Desenvolvedores (ordem decrescente)
        | Desenvolvedor                     | Reprovações | Cards Associados                   |
        |-----------------------------------|-------------|------------------------------------|
        | [Nome do Desenvolvedor]           | [Número de Reprovações] | [Card(s) Associado(s)] |
        
        **Total de Cards Analisados:** [X]
        **Total de cards quem contém reprovações** [Y]
        

        ### Cards e quantidade de reprovações (ordem decrescente)
        | Key do card                    | Reprovações |
        |--------------------------------|-------------|
        | [Nome do Desenvolvedor]        | [Número de Reprovações]|

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