import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime

# Import direto das rotas, sem usar importlib
from src.routes.jira_routes import (
    get_all_analytics,
    get_daily_all_analytics,
    get_analitycs_with_changelogs,
    get_analitycs_daily,
    list_boards,
    list_sprints,
)

st.set_page_config(
    page_title="JIRA Analytics",
    page_icon="📊",
    layout="wide"
)

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
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(counts)))
        counts.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Quantidade', fontsize=14)
        ax.set_ylabel('Responsável', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
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
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(sp_sum)))
        sp_sum.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Total Story Points', fontsize=14)
        ax.set_ylabel('Responsável', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        for i, value in enumerate(sp_sum):
            ax.text(value, i, f' {value}', va='center', ha='left', fontsize=10)
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Erro ao gerar gráfico de Story Points: {str(e)}")
        return None

def process_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    if df.empty:
        return df
    if "responsavel" not in df.columns:
        if "assignee" in df.columns:
            df["responsavel"] = df["assignee"].apply(lambda x: x.get("displayName") if isinstance(x, dict) else "Não definido")
        else:
            st.warning(f"Coluna 'responsavel' não encontrada em {df_name}. Definindo como 'Não definido'.")
            df["responsavel"] = "Não definido"
    if "desenvolvedor" not in df.columns:
        df["desenvolvedor"] = "Não definido"
    df["responsavel"] = df["responsavel"].fillna("Não definido").replace({'': "Não definido"})
    estagiario_variations = ["estagiario", "estagiarios", "estagiário", "estagiários", "não definido", "Não definido", "Não atribuído"]
    df["responsavel"] = df.apply(
        lambda row: row["desenvolvedor"] if row["responsavel"].strip().lower() in estagiario_variations else row["responsavel"],
        axis=1
    )
    return df


def format_data_mudanca(data_str: str) -> str:
    if not data_str:
        return data_str
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return data_str

def normalize_issue(issue: dict) -> dict:
    fields = issue.get("fields", {})
    assignee = fields.get("assignee", {})
    raw_data_mudanca = issue.get("data_mudanca") or fields.get("created", "")
    data_mudanca_fmt = format_data_mudanca(raw_data_mudanca)
    responsavel = issue.get("responsavel") or assignee.get("displayName", "Não definido")
    if responsavel.strip().lower() in ["estagiario", "estagiarios", "estagiário", "estagiários", "Não definido", "não definido", "Não atribuído", "Não atribuido"]:
        responsavel = fields.get("customfield_10172", "Não definido")
    return {
        "card_key": issue.get("card_key") or issue.get("key", ""),
        "responsavel": responsavel,
        "desenvolvedor": issue.get("desenvolvedor") or fields.get("customfield_10172", "Não definido"),
        "status_novo": issue.get("status_novo") or fields.get("status", {}).get("name", ""),
        "data_mudanca": data_mudanca_fmt,
        "sp": issue.get("sp") or fields.get("customfield_10106", 0)
    }

def normalize_issues_list(issues_list: list) -> pd.DataFrame:
    normalized = [normalize_issue(issue) for issue in issues_list]
    df = pd.DataFrame(normalized)
    
    desired_order = ["card_key", "responsavel", "desenvolvedor", "status_novo", "data_mudanca", "sp"]
    missing = set(desired_order) - set(df.columns)
    if not missing:
        df = df[desired_order]
    
    if not df.empty:
        df["responsavel"] = df["responsavel"].fillna("Não definido").replace({'': "Não definido"})
        estagiario_variations = ["estagiario", "estagiarios", "estagiário", "estagiários", "não definido"]
        df["responsavel"] = df.apply(
            lambda row: row["desenvolvedor"]
            if row["responsavel"].strip().lower() in estagiario_variations
            else row["responsavel"],
            axis=1
        )
    
    return df


@st.cache_data(ttl=3600, show_spinner="Carregando dados para consulta específica (15 dias)...")
def fetch_specific_15days(board_id: str, sprint_id: Optional[str]):
    return get_analitycs_with_changelogs(board_id, sprint_id)

@st.cache_data(ttl=3600, show_spinner="Carregando dados para consulta específica (diária)...")
def fetch_specific_daily(board_id: str, sprint_id: Optional[str]):
    return get_analitycs_daily(board_id, sprint_id)

@st.cache_data(ttl=3600, show_spinner="Carregando dados para todos os boards e sprints (15 dias)...")
def fetch_all_15days(num_sprints: int):
    try:
        return get_all_analytics(num_sprints=num_sprints)
    except Exception as e:
        st.error(f"Erro ao obter analytics: {str(e)}")
        return {}

@st.cache_data(ttl=3600, show_spinner="Carregando dados para todos os boards e sprints (diária)...")
def fetch_all_daily(num_sprints: int):
    return get_daily_all_analytics(num_sprints=num_sprints)

with st.sidebar:
    st.title("Configurações")
    modo_consulta = st.radio("Selecione o modo de consulta:", options=["Consulta Específica", "Todos Boards e Sprints"])
    periodo = st.radio("Selecione o período:", options=["Diário", "15 dias"])
    
    if modo_consulta == "Consulta Específica":
        selected_board_id = "734"
        st.info(f"Análise focada no Board ID: {selected_board_id}")
        
        sprints = []
        selected_sprint_id = None  # Inicializa como None
        
        try:
            sprints_data = list_sprints(selected_board_id)
            sprints = sprints_data.get("sprints", [])
        except Exception as e:
            # Captura o erro, mas só exibe se não for o esperado para boards Kanban
            if "O quadro não aceita sprints" not in str(e):
                st.error(f"Erro ao carregar sprints: {e}")
            sprints = [] # Garante que a lista de sprints está vazia em caso de erro
        
        # Se houver sprints, mostra a seleção
        if sprints:
            sprint_options = {str(s["id"]): s.get("name", f"Sprint {s['id']}") for s in sprints}
            selected_sprint_id = st.selectbox(
                "Selecione a Sprint",
                options=list(sprint_options.keys()),
                format_func=lambda x: sprint_options[x]
            )
        # Se não houver sprints, apenas informa o usuário
        else:
            st.info("Nenhuma sprint disponível. A análise será feita nos cards do board (modo Kanban).")

    else: # modo_consulta == "Todos Boards e Sprints"
        st.info("A consulta será realizada em TODOS os boards e sprints.")
        num_sprints = st.number_input("Número de últimas sprints para análise", min_value=1, value=2, step=1)

run_query = st.button("Run")

if run_query:
    if modo_consulta == "Consulta Específica":
        # A condição agora permite rodar a consulta mesmo sem uma sprint selecionada
        if selected_board_id:
            if periodo == "15 dias":
                try:
                    with st.spinner("Obtendo dados do Jira (Consulta Específica, 15 dias)..."):
                        data = fetch_specific_15days(str(selected_board_id), selected_sprint_id)
                    
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
                        st.markdown(format_metric(metrics.get('total_reprovacoes', 0), "Reprovações"), unsafe_allow_html=True)
                    
                    concl_df = process_dataframe(pd.DataFrame(charts_data.get('conclusoes', [])), "Conclusões")
                    reprov_df = process_dataframe(pd.DataFrame(charts_data.get('reprovacoes', [])), "Reprovações")

                    st.header("Gráficos de Desempenho")
                    col_g1, col_g2, col_g3 = st.columns(3)
                    with col_g1:
                        fig1 = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
                        if fig1: st.pyplot(fig1)
                        else: st.info("Sem dados de conclusões")
                    with col_g2:
                        fig2 = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
                        if fig2: st.pyplot(fig2)
                        else: st.info("Sem dados de reprovações")
                    with col_g3:
                        fig3 = plot_sp_conclusions(concl_df, "Story Points - Conclusões")
                        if fig3: st.pyplot(fig3)
                        else: st.info("Sem dados para Story Points")
                    
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

            else: # periodo == "Diário"
                try:
                    with st.spinner("Obtendo dados do Jira (Consulta Específica, Diário)..."):
                        data = fetch_specific_daily(str(selected_board_id), selected_sprint_id)

                    concluded_cards = data.get("concluded_cards", [])
                    total_sp = data.get("total_story_points", 0)
                    daily_df = normalize_issues_list(concluded_cards)

                    st.title("📊 Consulta Específica (Diário)")
                    st.header("Gráficos de Desempenho")
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        fig1 = plot_responsavel_performance(daily_df, "Cards Concluídos por Responsável")
                        if fig1: st.pyplot(fig1)
                        else: st.info("Sem dados para gráfico de desempenho.")
                    with col_g2:
                        fig2 = plot_sp_conclusions(daily_df, "Story Points dos Cards Concluídos")
                        if fig2: st.pyplot(fig2)
                        else: st.info("Sem dados para Story Points.")

                    st.markdown(f"**Total Story Points:** {total_sp}")
                    st.header("Tabela dos Cards Concluídos")
                    st.dataframe(daily_df, hide_index=True, use_container_width=True)

                except Exception as e:
                    st.error(f"Erro crítico: {str(e)}")
                    st.exception(e)
    
    else: # modo_consulta == "Todos Boards e Sprints"
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
                    st.markdown(format_metric(metrics.get('total_reprovacoes', 0), "Reprovações"), unsafe_allow_html=True)
                
                concl_df = process_dataframe(pd.DataFrame(charts_data.get('conclusoes', [])), "Conclusões")
                reprov_df = process_dataframe(pd.DataFrame(charts_data.get('reprovacoes', [])), "Reprovações")

                st.header("Gráficos de Desempenho")
                col_g1, col_g2, col_g3 = st.columns(3)
                with col_g1:
                    fig1 = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
                    if fig1: st.pyplot(fig1)
                    else: st.info("Sem dados de conclusões")
                with col_g2:
                    fig2 = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
                    if fig2: st.pyplot(fig2)
                    else: st.info("Sem dados de reprovações")
                with col_g3:
                    fig3 = plot_sp_conclusions(concl_df, "Story Points - Conclusões")
                    if fig3: st.pyplot(fig3)
                    else: st.info("Sem dados para Story Points")

                st.header("Insights Analíticos")
                with st.expander("Ver Análise Detalhada"):
                    llm_analysis = analysis.get('llm_analysis', "Análise não disponível")
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
        else: # periodo == "Diário"
            try:
                with st.spinner("Obtendo dados do Jira (Todos Boards e Sprints, Diário)..."):
                    data = fetch_all_daily(num_sprints)

                daily_cards = data.get("daily_concluded_cards", [])
                total_sp = data.get("total_story_points", 0)
                daily_df = normalize_issues_list(daily_cards)

                st.title("📊 Análise Diária - Todos Boards e Sprints")
                st.header("Gráficos de Desempenho")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig1 = plot_responsavel_performance(daily_df, "Cards Concluídos por Responsável")
                    if fig1: st.pyplot(fig1)
                    else: st.info("Sem dados para gráfico de desempenho.")
                with col_g2:
                    fig2 = plot_sp_conclusions(daily_df, "Story Points dos Cards Concluídos")
                    if fig2: st.pyplot(fig2)
                    else: st.info("Sem dados para Story Points.")

                st.markdown(f"**Total Story Points:** {total_sp}")
                st.header("Tabela dos Cards Concluídos")
                st.dataframe(daily_df, hide_index=True, use_container_width=True)

            except Exception as e:
                st.error(f"Erro crítico: {str(e)}")
                st.exception(e)
else:
    st.info("Clique em **Run** para buscar os dados do Jira.")