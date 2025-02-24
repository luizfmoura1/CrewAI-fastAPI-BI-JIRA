from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

def create_rework_agent(reprovados_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:

        df = pd.DataFrame(reprovados_data)
        df['data_mudanca'] = pd.to_datetime(df['data_mudanca']).dt.tz_localize(None)
        if 'desenvolvedor' in df.columns:
            df['desenvolvedor'] = df['desenvolvedor'].apply(
                lambda x: x['value'] if isinstance(x, dict) and 'value' in x else x
            )


        start_date_dt = datetime.now() - timedelta(days=15)
        current_date_dt = datetime.now()
        start_date_str = start_date_dt.strftime("%d-%m-%Y")
        current_date_str = current_date_dt.strftime("%d-%m-%Y")


        df_filtrado = df[(df['data_mudanca'] >= start_date_dt) & (df['data_mudanca'] <= current_date_dt)]
        print(df_filtrado)

        conclusoes = df_filtrado[df_filtrado['status_novo'].isin(['Em produção', 'Em release', 'Em Homologação'])]
        conclusoes = conclusoes.drop_duplicates(subset=['card_key'], keep='first')
        reprovacoes = df_filtrado[df_filtrado['status_novo'] == 'Reprovado']
        reprovacoes = reprovacoes.drop_duplicates(
            subset=['card_key', 'status_novo', 'responsavel', 'data_mudanca', 'sp'],
            keep='first'
        )
        print(len(reprovacoes))

        llm = LLM(
            model="gpt-4o",
            temperature=0.7,
            seed=0
        )

        rework_agent = Agent(
            role="Analista de Métricas Ágeis",
            goal="Calcular, a partir dos dados dos cards, o número de reprovações que os cards reprovados tiveram por desenvolvedor "
                 "e a soma dos Story Points dos cards que se encaixaram nos status de **concluídos** por cada desenvolvedor, fornecendo insights analíticos relevantes para a melhoria do processo de desenvolvimento.",
            backstory="Você é um especialista em métricas ágeis, com ampla experiência na análise de sprints e performance dos times. "
                      "Seu foco é identificar quais desenvolvedores estão enfrentando desafios frequentes (medidos pelo número de reprovações) e quais estão agregando maior valor (medidos pela soma dos Story Points dos cards concluídos). "
                      "Utilize os dados fornecidos para calcular essas métricas e, com base nos resultados, gerar insights que auxiliem na otimização dos processos de desenvolvimento.",
            llm=llm,
            verbose=True
        )

        rework_task = Task(
            description=f"""
            ## Análise de Métricas dos Cards - Período: {start_date_str} a {current_date_str}
            
            **Objetivo:**
            - Calcular o número de reprovações (status "Reprovado") para cada desenvolvedor.
            - Somar os Story Points dos cards **concluídos** (status "Em produção", "Em release" e "Em Homologação") para cada desenvolvedor.
            - Gerar insights analíticos relevantes com base nesses dados.
            
            **Processamento:**
            1. Filtrar os registros dos cards para o período entre {start_date_str} e {current_date_str}.
            2. Para os cards com status "Reprovado", contar o número de reprovações de cada um deles, separando por desenvolvedor.
            3. Para os cards com status "Em produção", "Em release" ou "Em Homologação", somar os Story Points (campo 'sp') de cada um deles separando por desenvolvedor. **ATENÇÃO** - Um card pode ter mais de um status de conclusão na changelog, mas deve ser contabilizado apenas uma vez.
            4. Agregar essas métricas por desenvolvedor e analisar a performance.
            5. Com base nos resultados, gerar insights que identifiquem gargalos ou oportunidades de melhoria.
    
            **ATENÇÃO:**
            Dados a serem analisados a seguir:
            ---------------------
            {df_filtrado.to_dict(orient='records')}
            ---------------------
            **ATENÇÃO**:
            - As reprovações devem ser análisadas com base na variavel {reprovacoes}
            - As conclusões devem ser analisadas com base na variavel {conclusoes} e a soma dos Story Points devem ser **apenas dos cards que estão nessa variavel**.
            - O número de reprovações devem chegar ao valor da variavel {len(reprovacoes)}.

            **Dados de Entrada:**
            - Lista de registros contendo:
              - 'card_key': Identificador do card.
              - 'responsavel': Nome do desenvolvedor.
              - 'status_novo': Novo status do card.
              - 'sp': Story Points do card.
              - 'data_mudanca': Data da mudança de status.
            
            **Saída Esperada:**
            - Relatório consolidado com:
              - Para cada desenvolvedor, o total de reprovações.
              - Para cada desenvolvedor, a soma dos Story Points dos cards que encaixaram nos status de concluído.
              - Insights analíticos relevantes, por exemplo, identificação de desenvolvedores com alta taxa de reprovação e sugestões para melhoria dos processos.
            """,
            expected_output=f"""
            **Relatório Consolidado - Período: {start_date_str} a {current_date_str}**
            
            ### Métricas por Desenvolvedor
            [Desenvolvedor 1]: Reprovações: [Total], Story Points Concluídos: [Total]
            [Desenvolvedor 2]: Reprovações: [Total], Story Points Concluídos: [Total]
            ...
            
            ### Insights Analíticos
            - [Insight 1]: ...
            - [Insight 2]: ...
            """,
            agent=rework_agent,
        )

        crew = Crew(
            agents=[rework_agent],
            tasks=[rework_task],
            verbose=True
        )
        llm_result = crew.kickoff()


        return {
            "llm_analysis": llm_result, 
            "charts_data": {
                "conclusoes": conclusoes.to_dict(orient='records'),
                "reprovacoes": reprovacoes.to_dict(orient='records'),
                "metrics": {
                    "total_concluidos": conclusoes['card_key'].nunique(),
                    "total_reprovados": reprovacoes['card_key'].nunique(),
                    "total_reprovas": len(reprovacoes)
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
