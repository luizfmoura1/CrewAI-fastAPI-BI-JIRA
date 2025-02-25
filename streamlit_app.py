import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional
import io

# Configuração da página
st.set_page_config(
    page_title="JIRA Analytics",
    page_icon="📊",
    layout="wide"
)

# CSS customizado para os cards de métricas
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
        if counts.empty:
            return None
        fig, ax = plt.subplots(figsize=(15, 11))
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

def plot_sp_conclusions(df: pd.DataFrame, title: str) -> Optional[plt.Figure]:
    try:
        if df.empty or 'responsavel' not in df.columns or 'sp' not in df.columns:
            return None
        df['sp'] = pd.to_numeric(df['sp'], errors='coerce').fillna(0)
        sp_sum = df.groupby('responsavel')['sp'].sum().sort_values(ascending=False)
        if sp_sum.empty:
            return None
        fig, ax = plt.subplots()
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(sp_sum)))
        sp_sum.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Total Story Points', fontsize=7)
        ax.set_ylabel('Responsável', fontsize=7)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        for i, value in enumerate(sp_sum):
            ax.text(value, i, f' {value}', va='center', ha='left', fontsize=8)
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Erro ao gerar gráfico de Story Points: {str(e)}")
        return None

def process_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """
    Garante que exista a coluna 'responsavel'. Se houver a coluna 'desenvolvedor',
    utiliza-a para corrigir casos como de estagiários.
    """
    if not df.empty:
        tem_desenvolvedor = 'desenvolvedor' in df.columns
        possible_columns = ['responsavel', 'Responsável', 'assignee']
        for col in possible_columns:
            if col in df.columns:
                df['responsavel'] = df[col]
                break
        else:
            st.warning(f"Coluna 'responsavel' não encontrada em {df_name}")
            df['responsavel'] = 'Não definido'
        df['responsavel'] = df['responsavel'].fillna('Não definido').replace({'': 'Não definido'})
        if tem_desenvolvedor:
            possiveis_estagiario = ['estagiario', 'estagiário', 'estagiarios', 'estagiários']
            mask = df['responsavel'].str.lower().str.strip().isin(possiveis_estagiario)
            df.loc[mask, 'responsavel'] = df.loc[mask, 'desenvolvedor']
    else:
        df['responsavel'] = pd.Series(dtype=str)
    return df

# ============================================================================
# Funções para obter dados dos endpoints do FastAPI
# ============================================================================
@st.cache_data(ttl=3600, show_spinner="Carregando dados para consulta específica (15 dias)...")
def fetch_specific_15days(board_id: str, sprint_id: str):
    from app import get_analitycs_with_changelogs
    return get_analitycs_with_changelogs(board_id, sprint_id)

@st.cache_data(ttl=3600, show_spinner="Carregando dados para consulta específica (diária)...")
def fetch_specific_daily(board_id: str, sprint_id: str):
    from app import get_analitycs_daily
    return get_analitycs_daily(board_id, sprint_id)

@st.cache_data(ttl=3600, show_spinner="Carregando dados para todos os boards e sprints (15 dias)...")
def fetch_all_15days(num_sprints: int):
    from app import get_all_analytics 
    try:
        return get_all_analytics(num_sprints=num_sprints)
    except Exception as e:
        st.error(f"Erro ao obter analytics: {str(e)}")
        return {}

@st.cache_data(ttl=3600, show_spinner="Carregando dados para todos os boards e sprints (diária)...")
def fetch_all_daily(num_sprints: int):
    from app import get_daily_all_analytics
    return get_daily_all_analytics(num_sprints=num_sprints)

# ============================================================================
# Sidebar: opções de modo e período
# ============================================================================
with st.sidebar:
    st.title("Configurações")
    
    modo_consulta = st.radio("Selecione o modo de consulta:", 
                              options=["Consulta Específica", "Todos Boards e Sprints"])
    periodo = st.radio("Selecione o período:", 
                       options=["Diário", "15 dias"])
    
    if modo_consulta == "Consulta Específica":
        boards = None
        try:
            from app import list_boards
            boards_data = list_boards()
            boards = boards_data.get("boards", [])
        except Exception as e:
            st.error(f"Erro ao carregar boards: {e}")
        if boards:
            board_options = {str(board.get("id")): board.get("name", f"Board {board.get('id')}") for board in boards}
            selected_board_id = st.selectbox("Selecione o Board", options=list(board_options.keys()),
                                             format_func=lambda x: board_options[x])
            try:
                from app import list_sprints
                sprints_data = list_sprints(selected_board_id)
                sprints = sprints_data.get("sprints", [])
            except Exception as e:
                st.error(f"Erro ao carregar sprints: {e}")
                sprints = []
            if sprints:
                sprint_options = {str(sprint.get("id")): sprint.get("name", f"Sprint {sprint.get('id')}") for sprint in sprints}
                selected_sprint_id = st.selectbox("Selecione a Sprint", options=list(sprint_options.keys()),
                                                  format_func=lambda x: sprint_options[x])
    else:  # Todos Boards e Sprints
        st.info("A consulta será realizada em TODOS os boards e sprints.")
        num_sprints = st.number_input("Número de últimas sprints para análise", min_value=1, value=2, step=1)
    
    run_query = st.button("Run")

# ============================================================================
# Execução da consulta e apresentação dos resultados
# ============================================================================
if run_query:
    if modo_consulta == "Consulta Específica":
        if periodo == "15 dias":
            try:
                with st.spinner("Obtendo dados do Jira (Consulta Específica, 15 dias)..."):
                    data = fetch_specific_15days(str(selected_board_id), str(selected_sprint_id))
                # Exibe a análise completa (conforme endpoint /JIRA_analitycs)
                analysis = data.get('analysis', {})
                charts_data = analysis.get('charts_data', {})
                metrics = charts_data.get('metrics', {})
                
                st.title("📊 Consulta Específica (15 dias)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(format_metric(metrics.get('total_concluidos', 0), "Concluídos"), unsafe_allow_html=True)
                with col2:
                    st.markdown(format_metric(metrics.get('total_reprovados', 0), "Reprovados"), unsafe_allow_html=True)
                with col3:
                    st.markdown(format_metric(metrics.get('total_reprovas', 0), "Reprovações"), unsafe_allow_html=True)
                
                concl_df = process_dataframe(pd.DataFrame(charts_data.get('conclusoes', [])), "Conclusões")
                reprov_df = process_dataframe(pd.DataFrame(charts_data.get('reprovacoes', [])), "Reprovações")
                
                st.header("Performance por Responsável")
                col1, col2, col3 = st.columns(3)
                with col1:
                    fig1 = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
                    if fig1:
                        st.pyplot(fig1)
                    else:
                        st.info("Sem dados de conclusões")
                with col2:
                    fig2 = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
                    if fig2:
                        st.pyplot(fig2)
                    else:
                        st.info("Sem dados de reprovações")
                with col3:
                    fig3 = plot_sp_conclusions(concl_df, "Story Points - Conclusões")
                    if fig3:
                        st.pyplot(fig3)
                    else:
                        st.info("Sem dados para Story Points")
                
                st.header("Insights Analíticos")
                with st.expander("Ver Análise Detalhada"):
                    llm_analysis = analysis.get('llm_analysis', 'Análise não disponível')
                    st.markdown(f"```\n{llm_analysis}\n```")
                
                st.header("Dados Detalhados")
                tab1, tab2 = st.tabs(["Conclusões", "Reprovações"])
                with tab1:
                    st.dataframe(concl_df, hide_index=True, use_container_width=True)
                with tab2:
                    st.dataframe(reprov_df, hide_index=True, use_container_width=True)
            except Exception as e:
                st.error(f"Erro crítico: {str(e)}")
                st.exception(e)
        else:  # Período Diário na consulta específica
            try:
                with st.spinner("Obtendo dados do Jira (Consulta Específica, Diário)..."):
                    data = fetch_specific_daily(str(selected_board_id), str(selected_sprint_id))
                concluded_cards = data.get("concluded_cards", [])
                total_sp = data.get("total_story_points", 0)
                
                # Processa os cards concluídos para garantir a coluna 'responsavel'
                daily_df = process_dataframe(pd.DataFrame(concluded_cards), "Cards Concluídos")
                
                st.title("📊 Consulta Específica (Diário)")
                st.header("Tabela dos Cards Concluídos")
                st.dataframe(daily_df, hide_index=True, use_container_width=True)
                
                st.header("Gráfico de Cards Concluídos por Responsável")
                fig1 = plot_responsavel_performance(daily_df, "Cards Concluídos por Responsável")
                if fig1:
                    st.pyplot(fig1)
                else:
                    st.info("Sem dados para gráfico de desempenho.")
                
                st.header("Gráfico da Soma dos Story Points dos Cards Concluídos")
                fig2 = plot_sp_conclusions(daily_df, "Story Points dos Cards Concluídos")
                if fig2:
                    st.pyplot(fig2)
                else:
                    st.info("Sem dados para Story Points.")
                
                st.markdown(f"**Total Story Points:** {total_sp}")
            except Exception as e:
                st.error(f"Erro crítico: {str(e)}")
                st.exception(e)
    else:  # Modo "Todos Boards e Sprints"
        if periodo == "15 dias":
            try:
                with st.spinner("Obtendo dados do Jira (Todos Boards e Sprints, 15 dias)..."):
                    all_data = fetch_all_15days(num_sprints)
                analysis = all_data.get("analysis", {})
                charts_data = analysis.get("charts_data", {})
                metrics = charts_data.get("metrics", {})
                
                st.title("📊 Análise de Performance - Todos Boards e Sprints (15 dias)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(format_metric(metrics.get('total_concluidos', 0), "Concluídos"), unsafe_allow_html=True)
                with col2:
                    st.markdown(format_metric(metrics.get('total_reprovados', 0), "Reprovados"), unsafe_allow_html=True)
                with col3:
                    st.markdown(format_metric(metrics.get('total_reprovas', 0), "Reprovações"), unsafe_allow_html=True)
                
                concl_df = process_dataframe(pd.DataFrame(charts_data.get('conclusoes', [])), "Conclusões")
                reprov_df = process_dataframe(pd.DataFrame(charts_data.get('reprovacoes', [])), "Reprovações")
                
                st.header("Performance por Responsável")
                col1, col2, col3 = st.columns(3)
                with col1:
                    fig1 = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
                    if fig1:
                        st.pyplot(fig1)
                    else:
                        st.info("Sem dados de conclusões")
                with col2:
                    fig2 = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
                    if fig2:
                        st.pyplot(fig2)
                    else:
                        st.info("Sem dados de reprovações")
                with col3:
                    fig3 = plot_sp_conclusions(concl_df, "Story Points - Conclusões")
                    if fig3:
                        st.pyplot(fig3)
                    else:
                        st.info("Sem dados para Story Points")
                
                st.header("Insights Analíticos")
                with st.expander("Ver Análise Detalhada"):
                    llm_analysis = analysis.get("llm_analysis", "Análise não disponível")
                    st.markdown(f"```\n{llm_analysis}\n```")
                
                st.header("Dados Detalhados")
                tab1, tab2 = st.tabs(["Conclusões", "Reprovações"])
                with tab1:
                    st.dataframe(concl_df, hide_index=True, use_container_width=True)
                with tab2:
                    st.dataframe(reprov_df, hide_index=True, use_container_width=True)
            except Exception as e:
                st.error(f"Erro crítico: {str(e)}")
                st.exception(e)
        else:  # Período Diário na consulta agregada
            try:
                with st.spinner("Obtendo dados do Jira (Todos Boards e Sprints, Diário)..."):
                    data = fetch_all_daily(num_sprints)
                daily_cards = data.get("daily_concluded_cards", [])
                total_sp = data.get("total_story_points", 0)
                
                daily_df = process_dataframe(pd.DataFrame(daily_cards), "Cards Concluídos")
                
                st.title("📊 Análise Diária - Todos Boards e Sprints")
                st.header("Tabela dos Cards Concluídos")
                st.dataframe(daily_df, hide_index=True, use_container_width=True)
                
                st.header("Gráfico de Cards Concluídos por Responsável")
                fig1 = plot_responsavel_performance(daily_df, "Cards Concluídos por Responsável")
                if fig1:
                    st.pyplot(fig1)
                else:
                    st.info("Sem dados para gráfico de desempenho.")
                
                st.header("Gráfico da Soma dos Story Points dos Cards Concluídos")
                fig2 = plot_sp_conclusions(daily_df, "Story Points dos Cards Concluídos")
                if fig2:
                    st.pyplot(fig2)
                else:
                    st.info("Sem dados para Story Points.")
                
                st.markdown(f"**Total Story Points:** {total_sp}")
            except Exception as e:
                st.error(f"Erro crítico: {str(e)}")
                st.exception(e)
else:
    st.info("Clique em **Run** para buscar os dados do Jira.")
