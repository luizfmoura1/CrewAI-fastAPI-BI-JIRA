import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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

def process_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """Processa um DataFrame garantindo a coluna 'responsavel'"""
    if not df.empty:
        possible_columns = ['responsavel', 'Responsável', 'assignee', 'desenvolvedor']
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
    else:
        # Mesmo se o DataFrame estiver vazio, adiciona a coluna 'responsavel'
        df['responsavel'] = pd.Series(dtype=str)
    return df

def main():
    with st.sidebar:
        st.title("Configurações")
        board_id = st.text_input("Board ID", value="123")
        sprint_id = st.text_input("Sprint ID", value="456")

    try:
        with st.spinner("Obtendo dados do Jira..."):
            data = fetch_data(board_id, sprint_id)

        if 'error' in data:
            st.error(f"Erro na API: {data['error']}")
            return

        analysis = data.get('analysis', {})
        charts_data = analysis.get('charts_data', {})

        concl_df = process_dataframe(
            pd.DataFrame(charts_data.get('conclusoes', [])),
            "Conclusões"
        )
        reprov_df = process_dataframe(
            pd.DataFrame(charts_data.get('reprovacoes', [])),
            "Reprovações"
        )

        # Calcula as opções dos desenvolvedores após processar os DataFrames
        all_devs = list(set(
            concl_df['responsavel'].astype(str).unique().tolist() +
            reprov_df['responsavel'].astype(str).unique().tolist()
        ))
        invalid_entries = ['', 'None', 'nan', 'Não definido']
        all_devs = [d for d in all_devs if str(d).strip() not in invalid_entries]

        # Cria o widget de multiselect usando as opções calculadas
        selected_developers = st.sidebar.multiselect(
            "Selecione os desenvolvedores",
            options=sorted(all_devs, key=lambda x: x.lower()),
            placeholder="Escolha os responsáveis"
        )

        if selected_developers:
            concl_df = concl_df[concl_df['responsavel'].isin(selected_developers)]
            reprov_df = reprov_df[reprov_df['responsavel'].isin(selected_developers)]

        # Extrai as métricas dos dados
        metrics = charts_data.get('metrics', {})

        st.title("📊 Análise de Performance de Sprint")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                format_metric(metrics.get('total_concluidos', 0), "Concluídos"),
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                format_metric(metrics.get('total_reprovados', 0), "Reprovados"),
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                format_metric(metrics.get('total_reprovas', 0), "Reprovações"),
                unsafe_allow_html=True
            )

        st.header("Performance por Responsável")
        col1, col2 = st.columns(2)
        with col1:
            fig = plot_responsavel_performance(concl_df, "Conclusões Bem-sucedidas")
            st.pyplot(fig) if fig else st.info("Sem dados de conclusões")
        with col2:
            fig = plot_responsavel_performance(reprov_df, "Reprovações por Responsável")
            st.pyplot(fig) if fig else st.info("Sem dados de reprovações")

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

if __name__ == "__main__":
    main()
