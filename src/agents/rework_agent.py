from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List
import datetime

def create_rework_agent(reprovados_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    llm = LLM(
        model="gpt-4o",
        temperature=0.7,
        seed=0
    )

    # Dados dinâmicos formatados
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    total_entries = len(reprovados_data)  # Nova métrica

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
        description=f"""
        ## Análise de Status de Cards - {current_date}
        
        **Objetivo:**  
        Analisar {total_entries} registros técnicos para identificar padrões de conclusão e reprovação.
        
        **Processamento:**  
        1. Acessar os dados brutos em 'reprovado_entries'
        2. Converter datas para formato DD-MM-AAAA
        3. Filtrar registros do dia {current_date}
        4. Classificar por status:
           - 'Em produção' -> Conclusão válida
           - 'Reprovado' -> Requer retrabalho
        5. Agregar métricas por desenvolvedor
        
        **Fonte de Dados:**
        - Entrada primária: Lista de dicionários com histórico de cards
        - Campo chave: 'data_mudanca' (timestamp ISO 8601)
        """,
        expected_output=f"""
        **Relatório Consolidado - {current_date}**
        
        ### Dados Analisados
        - Total de registros: {total_entries}
        - Período analisado: {current_date}
        
        ### Métricas Chave
        | Categoria           | Quantidade |
        |----------------------|------------|
        | Conclusões válidas   | 0          |
        | Reprovações          | 0          |
        | Cards problemáticos  | 0          |
        
        **Observações:**  
        Detalhamento por desenvolvedor disponível nos dados brutos.
        """,
        agent=rework_agent,
        inputs={'reprovado_entries': reprovados_data}  # Dados brutos separados
    )

    crew = Crew(
        agents=[rework_agent],
        tasks=[rework_task],
        verbose=True
    )

    return crew.kickoff()