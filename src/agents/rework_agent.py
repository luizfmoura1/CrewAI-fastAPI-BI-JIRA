# src/agents/rework_agent.py

from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import logging

from src.utils.custom_llm import ChatDatabricks
import src.config.config as config

def create_workflow_analysis_agent(progression_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        if not progression_data:
            return {
                "llm_analysis": "Nenhum dado de progressão foi fornecido para análise.",
                "progression_data_for_display": []
            }

        llm = ChatDatabricks(
            endpoint_url=config.DATABRICKS_ENDPOINT,
            token=config.DATABRICKS_TOKEN,
            temperature=0.7,
        )

        workflow_analyst_agent = Agent(
            role="Analista de Fluxo de Trabalho Ágil (Agile Workflow Analyst)",
            goal="Analisar a linha do tempo de movimentação dos cards para identificar gargalos, ciclos de longa duração, movimentações inesperadas e fornecer insights para otimizar o fluxo de desenvolvimento.",
            backstory="Você é um especialista em otimização de processos Kanban e Scrum. Sua habilidade é transformar um histórico de movimentações de tarefas em um diagnóstico claro sobre a saúde do fluxo de trabalho. Você aponta onde o trabalho fica parado e sugere melhorias práticas.",
            llm=llm,
            verbose=True
        )

        workflow_analysis_task = Task(
            description=f"""
            ## Análise de Fluxo de Trabalho dos Cards
            ... (toda a descrição da tarefa continua a mesma) ...
            **Dados de Entrada (histórico de movimentação dos cards):**
            ---------------------
            {progression_data}
            ---------------------
            """,
            expected_output="""
            ... (toda a saída esperada continua a mesma) ...
            """,
            agent=workflow_analyst_agent,
        )

        crew = Crew(
            agents=[workflow_analyst_agent],
            tasks=[workflow_analysis_task],
            verbose=True
        )
        
        llm_result = crew.kickoff()

        return {
            "llm_analysis": llm_result,
            "progression_data_for_display": progression_data
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        # --- MUDANÇA PRINCIPAL AQUI ---
        # Em vez de uma mensagem genérica, vamos retornar o erro real.
        error_message = f"ERRO NO AGENTE DE IA: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {
            "error": str(e),
            "llm_analysis": error_message,
            "progression_data_for_display": progression_data  
        }