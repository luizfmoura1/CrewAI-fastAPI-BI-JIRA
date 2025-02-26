from crewai import Agent, Task, Crew, LLM
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

def create_rework_agent(reprovados_data: List[Dict[str, Any]], start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(reprovados_data)
        df['data_mudanca'] = pd.to_datetime(df['data_mudanca']).dt.tz_localize(None)
        if 'desenvolvedor' in df.columns:
            df['desenvolvedor'] = df['desenvolvedor'].apply(
                lambda x: x['value'] if isinstance(x, dict) and 'value' in x else x
            )
        # Se não informados, o padrão é os últimos 15 dias
        if start_date is None:
            start_date_dt = datetime.now() - timedelta(days=15)
        else:
            start_date_dt = start_date
        if end_date is None:
            end_date_dt = datetime.now()
        else:
            end_date_dt = end_date

        start_date_str = start_date_dt.strftime("%d-%m-%Y")
        end_date_str = end_date_dt.strftime("%d-%m-%Y")

        df_filtrado = df[(df['data_mudanca'] >= start_date_dt) & (df['data_mudanca'] <= end_date_dt)]
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
            goal="Analisar os dados dos cards para extrair insights analíticos relevantes, identificando padrões, tendências e oportunidades de melhoria no processo de desenvolvimento.",
            backstory="Você é um especialista em métricas ágeis, com vasta experiência em transformar dados em insights estratégicos. Seu foco é analisar os registros dos cards para identificar oportunidades de melhoria e gargalos no desempenho dos desenvolvedores, apresentando apenas os insights analíticos que realmente importam, sem expor os cálculos brutos.",
            llm=llm,
            verbose=True
        )

        rework_task = Task(
            description=f"""
            ## Insights Analíticos Relevantes - Período: {start_date_str} a {end_date_str}
            
            **Objetivo:**
            - Extrair insights analíticos relevantes a partir da análise dos dados dos cards, evidenciando padrões e oportunidades de melhoria no desempenho dos desenvolvedores, sem apresentar os números brutos.
            
            **Processamento:**
            1. Filtrar os registros dos cards para o período entre {start_date_str} e {end_date_str}.
            2. Analisar os registros para identificar padrões de reprovações e a acumulação de Story Points nos cards concluídos.
            3. Agregar as informações por desenvolvedor e identificar tendências que possam indicar gargalos ou oportunidades de otimização.
            4. Gerar insights analíticos que orientem melhorias no processo de desenvolvimento, apresentando somente as conclusões estratégicas.
            
            **ATENÇÃO:**
            Utilize os dados a seguir para derivar insights analíticos, sem expor os valores brutos:
            ---------------------
            {df_filtrado.to_dict(orient='records')}
            ---------------------
            - Considere as reprovações conforme a variável {reprovacoes}.
            - Considere as conclusões e a soma dos Story Points conforme a variável {conclusoes}, contabilizando apenas os cards indicados.
            - O total de reprovações deve corresponder à variável {len(reprovacoes)}.
            
            **Dados de Entrada:**
            - Lista de registros contendo:
            - 'card_key': Identificador do card.
            - 'responsavel': Nome do desenvolvedor.
            - 'status_novo': Novo status do card.
            - 'sp': Story Points do card.
            - 'data_mudanca': Data da mudança de status.
            
            **Saída Esperada:**
            - Relatório final contendo apenas os insights analíticos relevantes, destacando:
            - Padrões e tendências de desempenho entre os desenvolvedores.
            - Recomendações e oportunidades de melhoria para otimização do processo de desenvolvimento.
            - O resultado final deve ser uma análise visualmente limpa, sem a utilização de asteriscos e hashtags, tente montar uma estrutura clara, objetiva e organizada.
            """,
            expected_output=f"""
            Relatório Consolidado - Período: {start_date_str} a {end_date_str}
            
            Insights Analíticos Relevantes
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
