import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional

# Configuração da página (deve ser o primeiro comando)
st.set_page_config(
    page_title="JIRA Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS para melhorar a apresentação dos cards de métricas
st.markdown("""
    <style>
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def format_metric(value: int, title: str) -> str:
    return f"""
    <div class="metric-box">
        <h3 style="color: #2c3e50; margin-bottom: 8px;">{title}</h3>
        <p style="font-size: 24px; color: #3498db; margin: 0;">{value}</p>
    </div>
    """

def plot_responsavel_performance(df: pd.DataFrame, title: str) -> Optional[plt.Figure]:
    try:
        if df.empty or 'responsavel' not in df.columns:
            return None

        counts = df['responsavel'].value_counts()
        
        # Verifica se há dados para plotar
        if counts.empty:
            return None

        fig, ax = plt.subplots(figsize=(20, 15))
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(counts)))
        counts.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Quantidade', fontsize=21)
        ax.set_ylabel('Responsável', fontsize=21)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.tight_layout()
        return fig

    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None


def process_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """
    Processa um DataFrame garantindo a coluna 'responsavel'. Caso seja necessário,
    utiliza a coluna 'desenvolvedor' para corrigir valores (ex: estagiário(s)).
    """
    if not df.empty:
        # Verifica se a coluna 'desenvolvedor' existe
        tem_desenvolvedor = 'desenvolvedor' in df.columns

        # Procura as colunas possíveis para 'responsavel'
        possible_columns = ['responsavel', 'Responsável', 'assignee']
        for col in possible_columns:
            if col in df.columns:
                df['responsavel'] = df[col]
                break
        else:
            st.warning(f"Coluna 'responsavel' não encontrada em {df_name}")
            df['responsavel'] = 'Não definido'

        df['responsavel'] = (
            df['responsavel']
            .fillna('Não definido')
            .replace({'': 'Não definido'})
        )

        if tem_desenvolvedor:
            possiveis_estagiario = ['estagiario', 'estagiário', 'estagiarios', 'estagiários']
            mask = df['responsavel'].str.lower().str.strip().isin(possiveis_estagiario)
            df.loc[mask, 'responsavel'] = df.loc[mask, 'desenvolvedor']
    else:
        df['responsavel'] = pd.Series(dtype=str)
        
    return df

# ============================================================================
# Funções para obter dados dos endpoints do FastAPI
# Utilize st.cache_data para armazenar os resultados (TTL de 1 hora)
# ============================================================================

@st.cache_data(ttl=3600, show_spinner="Carregando boards...")
def fetch_boards():
    from app import list_boards  # Importa a função do FastAPI
    boards_data = list_boards()   # Retorna um dict com a chave "boards"
    return boards_data.get("boards", [])

@st.cache_data(ttl=3600, show_spinner="Carregando sprints...")
def fetch_sprints(board_id: str):
    from app import list_sprints
    sprints_data = list_sprints(board_id)  # Retorna dict com chave "sprints"
    return sprints_data.get("sprints", [])

@st.cache_data(ttl=3600, show_spinner="Carregando dados do Jira...")
def fetch_data(board_id: str, sprint_id: str) -> dict:
    from app import get_analitycs_with_changelogs
    return get_analitycs_with_changelogs(board_id, sprint_id)

import requests
import streamlit as st

@st.cache_data(ttl=3600, show_spinner="Carregando dados do Jira para todos os boards e sprints...")
def fetch_all_data() -> dict:
    url = "http://127.0.0.1:8000/JIRA_all_analytics"  # Endpoint correto
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta exceção para erros HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição: {str(e)}")
        return {}
    except ValueError as e:
        st.error(f"Resposta inválida da API: {response.text}")
        return {}


# ============================================================================
# Interface do Sidebar para configuração da consulta
# ============================================================================

with st.sidebar:
    st.title("Configurações")
    
    modo = st.radio("Selecione o modo de consulta:", options=["Consulta Específica", "Todos Boards e Sprints"])
    
    if modo == "Consulta Específica":
        # Busca os boards dinamicamente
        boards = fetch_boards()
        # Cria um dicionário: key = id do board (como string) e value = nome (ou "Board {id}" se não houver nome)
        board_options = {str(board.get("id")): board.get("name", f"Board {board.get('id')}") for board in boards}
        selected_board_id = st.selectbox("Selecione o Board", options=list(board_options.keys()),
                                         format_func=lambda x: board_options[x])
        # Após selecionar o board, busca os sprints dele
        sprints = fetch_sprints(selected_board_id)
        sprint_options = {str(sprint.get("id")): sprint.get("name", f"Sprint {sprint.get('id')}") for sprint in sprints}
        selected_sprint_id = st.selectbox("Selecione a Sprint", options=list(sprint_options.keys()),
                                          format_func=lambda x: sprint_options[x])
    else:
        st.info("A consulta será realizada em TODOS os boards e sprints.")
    
    run_query = st.button("Run")

# ============================================================================
# Execução da consulta e apresentação dos resultados
# ============================================================================

if run_query:
    if modo == "Consulta Específica":
        try:
            with st.spinner("Obtendo dados do Jira..."):
                data = fetch_data(str(selected_board_id), str(selected_sprint_id))

            if 'error' in data:
                st.error(f"Erro na API: {data['error']}")
                st.stop()

            analysis = data.get('analysis', {})
            charts_data = analysis.get('charts_data', {})

            # Processa os dados para conclusões e reprovações
            concl_df = process_dataframe(
                pd.DataFrame(charts_data.get('conclusoes', [])),
                "Conclusões"
            )
            reprov_df = process_dataframe(
                pd.DataFrame(charts_data.get('reprovacoes', [])),
                "Reprovações"
            )

            metrics = charts_data.get('metrics', {})

            st.title("📊 Análise de Performance - OPPEM")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(format_metric(metrics.get('total_concluidos', 0), "Concluídos"),
                            unsafe_allow_html=True)
            with col2:
                st.markdown(format_metric(metrics.get('total_reprovados', 0), "Reprovados"),
                            unsafe_allow_html=True)
            with col3:
                st.markdown(format_metric(metrics.get('total_reprovas', 0), "Reprovações"),
                            unsafe_allow_html=True)

            st.header("Performance por Responsável")
            col1, col2 = st.columns(2)
            with col1:
                fig = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
                if fig:
                    st.pyplot(fig)
                else:
                    st.info("Sem dados de conclusões")
            with col2:
                fig = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
                if fig:
                    st.pyplot(fig)
                else:
                    st.info("Sem dados de reprovações")

            st.header("Insights Analíticos")
            with st.expander("Ver Análise Detalhada"):
                llm_analysis = analysis.get('llm_analysis', 'Análise não disponível')
                st.markdown(f"```\n{llm_analysis}\n```")

            st.header("Dados Detalhados")
            tab1, tab2 = st.tabs(["Conclusões", "Reprovações"])
            with tab1:
                st.dataframe(concl_df, hide_index=True, use_container_width=True,
                             column_config={"card_key": "Card", "responsavel": "Responsável"})
            with tab2:
                st.dataframe(reprov_df, hide_index=True, use_container_width=True,
                             column_config={"card_key": "Card", "responsavel": "Responsável"})

        except Exception as e:
            st.error(f"Erro crítico: {str(e)}")
            st.exception(e)
    else:
        try:
            with st.spinner("Obtendo dados do Jira para todos os boards e sprints..."):
                all_data = fetch_all_data()
            # all_data deve conter um dicionário com a chave "results", que é uma lista de análises
            results = all_data.get("results", [])
            st.title("📊 Análise de Performance - Todos os Boards e Sprints")
            if not results:
                st.info("Nenhum dado encontrado.")
            else:
                # Exibe um resumo em tabela
                summary_data = []
                for result in results:
                    board_id = result.get("board_id")
                    sprint_id = result.get("sprint_id")
                    summary_data.append({"Board": board_id, "Sprint": sprint_id})
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df)

                # Permite expandir os detalhes de cada board/sprint
                for result in results:
                    with st.expander(f"Detalhes para Board {result.get('board_id')} - Sprint {result.get('sprint_id')}"):
                        st.json(result)
        except Exception as e:
            st.error(f"Erro crítico: {str(e)}")
            st.exception(e)
else:
    st.info("Clique em **Run** para buscar os dados do Jira.")
