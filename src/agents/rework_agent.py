# rework_agent.py
# rework_agent.py
from crewai import Agent, Task, Crew
from typing import Dict, Any

def create_rework_agent(reprovados_data: list) -> Dict[str, Any]:
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Calcular o índice de retrabalho por desenvolvedor",
        backstory="Especialista em métricas de qualidade de desenvolvimento",
        verbose=True
    )

    rework_task = Task(
        description="""
        Analise os dados de reprovação para calcular:
        1. Quantas vezes cada desenvolvedor teve cards reprovados
        2. Ordenar do maior para o menor índice

        Instruções:
        1. Use exatamente os nomes dos desenvolvedores como recebidos
        2. Não generalize ou altere os nomes
        3. Mantenha a fidelidade absoluta aos dados de entrada
        5. Sempre que o responsável for um **Estagiário**, substituir pelo customfield_10172.
        6. 

        Dados a serem analisados a seguir:
        ---------------------
        {reprovado_entries}
        ---------------------
        """,
        expected_output="""
        - Tabela ordenada de desenvolvedores e contagem de reprovações
        - Key dos cards com reprovações e quantas reprovações cada um teve.
        - Lista com quantidade de reprovações de cada card.
        """,
        agent=rework_agent,
        inputs={'reprovado_entries': reprovados_data}  # ← Dados passados corretamente
    )

    crew = Crew(
        agents=[rework_agent],
        tasks=[rework_task],
        verbose=True
    )

    return crew.kickoff(inputs={'reprovado_entries': reprovados_data})