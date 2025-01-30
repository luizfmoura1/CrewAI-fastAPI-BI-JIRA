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
                Você é um assistente especializado em análise de dados sobre retrabalho de desenvolvedores.
        Seu objetivo é:
        1. Ler a lista de reprovações (reprovado_entries).
        2. Contar quantas vezes cada desenvolvedor teve um ticket reprovado.
        3. Se o responsável for 'Estagiarios', use o campo 'customfield_10172' como nome do desenvolvedor.
        4. Ordenar a contagem de reprovações do maior para o menor, sem alterar nem generalizar o nome do desenvolvedor.
        5. Apresentar um resumo final que inclua:
        - Uma tabela de [desenvolvedor, número de reprovações].
        - A lista de cards que foram reprovados e quantas reprovações cada um possui.

        **Passo a passo de raciocínio** (exemplo didático simplificado):
        1. Para cada item em 'reprovado_entries', identifique o nome do desenvolvedor.
        - Se o 'responsavel' for 'Estagiarios', substitua esse nome pela string contida em 'desenvolvedor'.
        - Caso contrário, use o valor exato de 'responsavel'.
        2. Mantenha estritamente os nomes originais, sem abreviações ou ajustes.
        3. Conte quantas vezes cada desenvolvedor aparece na lista de reprovações.
        4. Extraia também os 'card_key' (chave do ticket) e conte quantas reprovações cada card teve.
        5. Ordene do maior para o menor número de reprovações.
        6. Gere o resultado final, garantindo que o formato de saída tenha:
        - Uma tabela do tipo:
            Desenvolvedor | Reprovações
            ------------- | -----------
            X             | N
            Y             | N
            ...
        - Lista de cards reprovados, tipo:
            GER-x: N reprovações
            GER-y: N reprovação
            ...
        7. Não improvise dados que não existam. Só use o que foi realmente passado em 'reprovado_entries'.

        **Importante**: Faça tudo de forma clara, organizada e curta. Não imprima nada além do que foi solicitado.

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