from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

def create_rework_agent(reprovados_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    llm = LLM(
        model="gpt-4o",
        temperature=0.7,
        seed=0
    )

    current_date = datetime.now().strftime("%d-%m-%Y")
    start_date = (datetime.now() - timedelta(days=15)).strftime("%d-%m-%Y")

    rework_agent = Agent(
        role="Analista de Entrega Técnica",
        goal="Analisar padrões de conclusão e retrabalho apenas em cards específicos nos últimos **15 dias**",
        backstory="""Especialista em métricas de entrega ágil com ampla experiência em análise de sprints.
        Responsável por monitorar tanto as conclusões bem-sucedidas quanto os casos de retrabalho,
        garantindo a qualidade do processo de desenvolvimento e identificando oportunidades de melhoria.
        Com um olhar analítico, você se concentra na detecção de padrões de inconsistência e oportunidades
        de otimização no fluxo de trabalho, especialmente ao longo de períodos contínuos, como os últimos 15 dias.""",
        llm=llm,
        verbose=True
    )

    rework_task = Task(
        description=f"""
        ## Análise de Status de Cards - Período a ser analisado: {start_date} a {current_date}
        
        **Objetivo:**  
        - Analisar e identificar padrões de conclusão (Em produção, Em release e Em homologação) e reprovação nos últimos 15 dias nos dados fornecidos.
        - **ATENÇÃO**: Sempre que o responsável for um 'Estágiario', você **deve** utilizar o nome vinculado a 'desenvolvedor'
        - Analisar STRITAMENTE cards com alterações entre {start_date} e {current_date}
        - **CRITICO**: Verificar CADA 'data_mudanca' convertida (DD-MM-AAAA) antes de considerar
        - **CRITICO**: Ignorar COMPLETAMENTE qualquer registro fora do intervalo

        **Processamento:**  
        1. Acessar os dados brutos em 'reprovado_entries'
        2. Converter 'data_mudanca' para DD-MM-AAAA
             - MANTER APENAS registros onde:
                data_mudanca >= {start_date} 
                AND 
                data_mudanca <= {current_date}
            - DESCARTAR todos outros registros SEM EXCEÇÃO
        3. Regras de Classificação:
            - **REPROVAÇÕES VÁLIDAS**: 
                * Apenas alterações no status (status_novo'Reprovado') DENTRO do período
                * Se múltiplas reprovações no período, listar TODAS
                * Ignorar reprovações anteriores a {start_date}
        4. Classificar por status:
            - 'Em homologação' -> Conclusão válida
            - 'Em release' -> Conclusão válida
            - 'Em produção' -> Conclusão válida
            - 'Reprovado' -> Requer retrabalho
            - **ATENÇÃO**: Se um card tiver mais de um status de **conclusão**, considere  apenas o status que veio **primeiro**
            - - **ATENÇÃO**: Caso o card tenha mais de uma reprovação, considere apenas a reprovação que esteja dentro do périodo de análise.
        5. Agregar métricas por desenvolvedor e detectar recorrências
        6. Dos cards que **apresentarem um status de conclusão**, você **deve** exibir o Story Points do card (campo 'sp')
        
        **ATENÇÃO:**
        Dados a serem analisados a seguir:
        ---------------------
        {reprovados_data}
        ---------------------
        - Campo chave: 'data_mudanca' (timestamp ISO 8601)
        - Campo chave: 'status_novo': 'Em produção' (concluído)
        - Campo chave: 'status_novo': 'Em release' (concluído)
        - Campo chave: 'status_novo': 'Em homologação' (concluído)
        - Campo chave: 'status_novo': 'Reprovado' (reprovado)
        - Campo chave: 'sp': Story Points
        - Usar campo 'desenvolvedor' se 'responsavel' for 'Estagiarios'

        **CONTROLES CRÍTICOS:**
        ---------------------
        - NUNCA usar histórico completo dos cards
        - SEMPRE validar data_mudanca ENTRE {start_date}-{current_date}
        - REPROVAÇÕES: Excluir automaticamente se data_mudanca < {start_date}

        """,
        expected_output=f"""
        **Relatório Consolidado - Período obrigátorio dos cards: {start_date} a {current_date}**
        
        ### Dados Analisados
        - Período analisado: {start_date} a {current_date}
        
        ### Conclusões (Em produção, Em release e Em homologação)
        | Card              | Responsável          | Horário        | Story Points   |
        |-------------------|----------------------|----------------|----------------|
        | -                 | -                    | -              | -              |
        ### Reprovações
        | Card              | Responsável          | Reprovações | Horários        |
        |-------------------|----------------------|-------------|-----------------|
        | -                 | -                    | -           |    -            |
        
        **Métricas Chave:**
        - Total de cards concluídos: 0
        - Total de cards com reprovações: 0
        - Total de reprovações no período: 0
        """,
        agent=rework_agent,
    )

    try:
        df = pd.DataFrame(reprovados_data)

        df['data_mudanca'] = pd.to_datetime(df['data_mudanca']).dt.tz_localize(None)

        if 'desenvolvedor' in df.columns:
            df['desenvolvedor'] = df['desenvolvedor'].apply(
                lambda x: x['value'] if isinstance(x, dict) and 'value' in x else x
    )

        # Converter as datas de início e fim para Timestamp
        start_date = datetime.now() - timedelta(days=15)
        current_date = datetime.now()

        # Filtrar o DataFrame
        df_filtrado = df[(df['data_mudanca'] >= start_date) & (df['data_mudanca'] <= current_date)]


        print(df_filtrado)
        # Classificação dos dados
        conclusoes = df_filtrado[df_filtrado['status_novo'].isin(['Em produção', 'Em release', 'Em homologação'])]
        conclusoes = conclusoes.drop_duplicates(subset=['card_key'], keep='first')

        reprovacoes = df_filtrado[df_filtrado['status_novo'] == 'Reprovado']

        print(len(reprovacoes))

        crew = Crew(
        agents=[rework_agent],
        tasks=[rework_task],
        verbose=True
    )
        llm_result = crew.kickoff()
        # Criação do payload estruturado
        return {
            "llm_analysis": llm_result,  # Análise textual do CrewAI
            "charts_data": {
                "conclusoes": conclusoes.to_dict(orient='records'),
                "reprovacoes": reprovacoes.to_dict(orient='records'),
                "metrics": {
                    "total_concluidos": conclusoes['card_key'].nunique(),
                    "total_reprovados": reprovacoes['card_key'].nunique(),
                    "total_reprovações": len(reprovacoes)
                }
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "charts_data": {
                "conclusoes": [],
                "reprovacoes": [],
                "metrics": {
                    "total_concluidos": 0,
                    "total_reprovados": 0,
                    "total_reprovas": 0
                }
            }
        }
