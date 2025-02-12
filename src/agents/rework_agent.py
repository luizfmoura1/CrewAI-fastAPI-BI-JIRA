from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List

def create_rework_agent(reprovados_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    llm = LLM(
        model="gpt-4o",
        temperature=0.7,
        seed=0
    )
    
    rework_agent = Agent(
        role="Analista de Entrega Técnica",
        goal="Identificar padrões de conclusão e retrabalho em cards específicos",
        backstory="""Especialista em métricas de entrega ágil com ampla experiência em análise de sprints.
        Responsável por monitorar tanto as conclusões bem-sucedidas quanto os casos de retrabalho,
        garantindo a qualidade do processo de desenvolvimento e identificando oportunidades de melhoria.""",
        llm=llm,
        verbose=True
    )

    rework_task = Task(
        description="""
        ## Análise de Status de Cards - 02/01/2025
        
        **Objetivo:**  
        Identificar cards concluídos (Em produção) e reprovações ocorridas na data específica.
        
        **Processamento:**  
        1. Para cada entrada em 'reprovado_entries':
           - Extrair a data do campo 'data_mudanca' (parte antes do 'T')
           - Converter para formato DD-MM-AAAA (ex: 02-01-2025)
           - Filtrar apenas registros onde a data é 02-01-2025
           - Classificar por tipo de status:
             * 'Em produção' -> Conclusão bem-sucedida
             * 'Reprovado' -> Registrar contagem de reprovações
           - Identificar responsável:
             - Usar 'responsavel' se diferente de 'Estagiarios'
             - Caso contrário, usar 'desenvolvedor'
        
        2. Agregar dados:
           - Contar ocorrências de cada status por desenvolvedor
           - Identificar cards únicos com múltiplas reprovações
           - Listar cards concluídos sem reprovações
        
        **Regras:**
        - Considerar apenas a parte da data antes do 'T' (YYYY-MM-DD)
        - Ignorar milissegundos e offset timezone
        - Formato final da hora: HH:mm (ex: 11:54)
        """,
        expected_output="""
        **Relatório Consolidado - 02/01/2025**
        
        ### Conclusões (Em produção)
        | Card              | Responsável          | Horário        |
        |-------------------|----------------------|----------------|
        | [Nenhum registro encontrado]          | -     | -          |
        
        ### Reprovações
        | Card              | Responsável          | Reprovações | Horários        |
        |-------------------|----------------------|-------------|-----------------|
        | [Nenhum registro encontrado]        | -     | -           | -    |
        
        **Métricas Chave:**
        - Total de cards concluídos: 0
        - Total de cards com reprovações: 0
        - Total de reprovações no dia: 0
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