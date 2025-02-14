import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from app import get_analitycs_with_changelogs  # Mantido conforme seu código original

def format_metric(value: int, title: str) -> str:
    return f"""
    <div style="text-align: center; padding: 10px; margin: 10px; 
                background: #f8f9fa; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
        <h3 style="color: #2c3e50; margin-bottom: 5px;">{title}</h3>
        <p style="font-size: 24px; color: #3498db; margin: 0;">{value}</p>
    </div>
    """

def plot_responsavel_performance(df: pd.DataFrame, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not df.empty:
        counts = df['responsavel'].value_counts()
        colors = plt.cm.viridis_r(np.linspace(0.2, 0.8, len(counts)))
        counts.plot(kind='barh', ax=ax, color=colors, title=title)
        ax.set_xlabel('Quantidade')
        ax.set_ylabel('Responsável')
        plt.tight_layout()
    else:
        ax.text(0.5, 0.5, 'Sem dados disponíveis', 
               ha='center', va='center', color='gray')
    
    return fig

def main():
    st.set_page_config(page_title="JIRA Analytics", layout="wide")
    
    # Widgets de entrada na sidebar
    with st.sidebar:
        st.header("Parâmetros de Análise")
        board_id = st.text_input("Board ID", value="123")
        sprint_id = st.text_input("Sprint ID", value="456")
        st.header("Filtros")
        selected_developers = st.multiselect(
            "Selecione os desenvolvedores",
            options=[],
            placeholder="Escolha os responsáveis"
        )
    
    try:
        # Busca dados
        data = get_analitycs_with_changelogs(board_id, sprint_id)
        metrics = data['analysis']['charts_data']['metrics']
        
        # Converte e filtra dados
        concl_df = pd.DataFrame(data['analysis']['charts_data']['conclusoes'])
        reprov_df = pd.DataFrame(data['analysis']['charts_data']['reprovacoes'])
        
        # Atualiza opções de desenvolvedores
        all_devs = list(set(concl_df['responsavel'].tolist() + reprov_df['responsavel'].tolist()))
        st.sidebar.multiselect.options = all_devs
        
        # Aplica filtros
        if selected_developers:
            concl_df = concl_df[concl_df['responsavel'].isin(selected_developers)]
            reprov_df = reprov_df[reprov_df['responsavel'].isin(selected_developers)]
        
        # Layout principal
        st.title("📊 Análise de Performance de Sprint")
        
        # Métricas
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
        
        # Gráficos
        st.header("Performance por Responsável")
        col1, col2 = st.columns(2)
        with col1:
            fig = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
            st.pyplot(fig)
        with col2:
            fig = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
            st.pyplot(fig)
        
        # Insights
        st.header("Análise Detalhada")
        with st.expander("Insights Analíticos"):
            st.write(data['analysis']['llm_analysis'])
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

if __name__ == "__main__":
    main()