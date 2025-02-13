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
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%d-%m-%Y")

    rework_agent = Agent(
        role="Analista de Entrega Técnica",
        goal="Analisar padrões de conclusão e retrabalho em cards específicos nos últimos 30 dias",
        backstory=f"""Especialista em métricas de entrega ágil com ampla experiência em análise de sprints.
        Responsável por monitorar tanto as conclusões bem-sucedidas quanto os casos de retrabalho,
        garantindo a qualidade do processo de desenvolvimento e identificando oportunidades de melhoria.
        Com um olhar analítico, você se concentra na detecção de padrões de inconsistência e oportunidades
        de otimização no fluxo de trabalho, especialmente ao longo de períodos contínuos, como os últimos 30 dias.""",
        llm=llm,
        verbose=True
    )

    rework_task = Task(
        description=f"""
        ## Análise de Status de Cards - Período {start_date} a {current_date}
        
        **Objetivo:**  
        Analisar {{reprovado_entries}} identificar padrões de conclusão e reprovação nos últimos 30 dias.
        
        **Processamento:**  
        1. Acessar os dados brutos em 'reprovado_entries'
        2. Converter datas para formato DD-MM-AAAA
        3. Filtrar registros entre {start_date} e {current_date}
        4. Classificar por status:
           - 'Em produção' -> Conclusão válida
           - 'Reprovado' -> Requer retrabalho
        5. Agregar métricas por desenvolvedor e detectar recorrências
        
        **ATENÇÃO:**
        Dados a serem analisados a seguir:
        ---------------------
        {{reprovado_entries}}
        ---------------------
        - Campo chave: 'data_mudanca' (timestamp ISO 8601)
        """,
        expected_output=f"""
        **Relatório Consolidado - Período {start_date} a {current_date}**
        
        ### Dados Analisados
        - Período analisado: {start_date} a {current_date}
        
        ### Conclusões (Em produção)
        | Card              | Responsável          | Horário        |
        |-------------------|----------------------|----------------|
        | -                 | -                    | -              |      
        ### Reprovações
        | Card              | Responsável          | Reprovações | Horários        |
        |-------------------|----------------------|-------------|-----------------|
        | -                 | -                    | -           |    -            |
        
        **Métricas Chave:**
        - Total de cards concluídos: 0
        - Total de cards com reprovações: 0
        - Total de reprovações no dia: 0
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
