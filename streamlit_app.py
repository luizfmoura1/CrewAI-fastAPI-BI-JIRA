import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional

# Configuração da página DEVE SER O PRIMEIRO COMANDO
st.set_page_config(
    page_title="JIRA Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS deve vir logo após
st.markdown("""
    <style>
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .st-emotion-cache-1v0mbdj {
        border-radius: 10px;
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
        if df.empty:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        counts = df['responsavel'].value_counts()
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(counts)))
        
        counts.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Quantidade', fontsize=10)
        ax.set_ylabel('Responsável', fontsize=10)
        plt.xticks(fontsize=9)
        plt.yticks(fontsize=9)
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None

@st.cache_data(ttl=3600, show_spinner="Carregando dados do Jira...")
def fetch_data(board_id: str, sprint_id: str) -> dict:
    from app import get_analitycs_with_changelogs
    return get_analitycs_with_changelogs(board_id, sprint_id)

def display_metrics(metrics: dict) -> None:
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

def main():
    # Sidebar com parâmetros
    with st.sidebar:
        st.title("Configurações")
        board_id = st.text_input("Board ID", value="123")
        sprint_id = st.text_input("Sprint ID", value="456")
        st.divider()
        st.header("Filtros")
        selected_developers = st.multiselect(
            "Selecione os desenvolvedores",
            options=[],
            placeholder="Escolha os responsáveis"
        )
    
    try:
        # Carregamento de dados com spinner
        with st.spinner("Obtendo dados do Jira..."):
            data = fetch_data(board_id, sprint_id)
            
        if 'error' in data:
            st.error(f"Erro na API: {data['error']}")
            return
            
        analysis = data.get('analysis', {})
        charts_data = analysis.get('charts_data', {})
        metrics = charts_data.get('metrics', {})
        
        # Processamento dos dados
        concl_df = pd.DataFrame(charts_data.get('conclusoes', []))
        reprov_df = pd.DataFrame(charts_data.get('reprovacoes', []))
        
        # Atualizar opções de desenvolvedores dinamicamente
        all_devs = list(set(
            concl_df['responsavel'].tolist() + 
            reprov_df['responsavel'].tolist()
        ))
        st.sidebar.multiselect.options = all_devs
        
        # Aplicar filtros
        if selected_developers:
            concl_df = concl_df[concl_df['responsavel'].isin(selected_developers)]
            reprov_df = reprov_df[reprov_df['responsavel'].isin(selected_developers)]
        
        # Layout principal
        st.title("📊 Análise de Performance de Sprint")
        
        # Seção de métricas
        display_metrics(metrics)
        
        # Seção de gráficos
        st.header("Performance por Responsável")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
            if fig:
                st.pyplot(fig)
            else:
                st.info("Nenhum dado disponível para conclusões")
        
        with col2:
            fig = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
            if fig:
                st.pyplot(fig)
            else:
                st.info("Nenhum dado disponível para reprovações")
        
        # Análise textual
        st.header("Insights Analíticos")
        with st.expander("Ver Análise Detalhada", expanded=False):
            llm_analysis = analysis.get('llm_analysis', 'Análise não disponível')
            st.markdown(f"```\n{llm_analysis}\n```")
            
        # Dados brutos
        st.header("Dados Detalhados")
        tab1, tab2 = st.tabs(["Conclusões", "Reprovações"])
        
        with tab1:
            st.dataframe(
                concl_df,
                column_config={
                    "card_key": "Card",
                    "responsavel": "Responsável",
                    "data_mudanca": "Data",
                    "sp": "Story Points"
                },
                hide_index=True,
                use_container_width=True
            )
        
        with tab2:
            st.dataframe(
                reprov_df,
                column_config={
                    "card_key": "Card",
                    "responsavel": "Responsável",
                    "data_mudanca": "Data"
                },
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Erro crítico: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()