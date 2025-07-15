# streamlit_app.py

import streamlit as st
import pandas as pd
import requests 

API_URL = "http://127.0.0.1:8000" 

st.set_page_config(
    page_title="JIRA Workflow Analysis",
    page_icon="🤖",
    layout="wide"
)

# --- Funções para chamar a API ---
@st.cache_data(ttl=3600, show_spinner="Buscando boards disponíveis...")
def fetch_boards():
    """Busca a lista de boards da sua API."""
    try:
        response = requests.get(f"{API_URL}/boards")
        response.raise_for_status()
        boards = response.json().get("boards", [])
        # Retorna um dicionário mapeando Nome do Board -> ID do Board
        return {board['name']: board['id'] for board in boards}
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar os boards do Jira. A API está rodando? Detalhe: {e}")
        return {}

@st.cache_data(ttl=3600, show_spinner="Analisando fluxo de trabalho com IA...")
def fetch_progression_analysis(board_id: str):
    """Busca a análise de progressão para um board específico."""
    params = {"board_id": board_id}
    response = requests.get(f"{API_URL}/JIRA_card_progression", params=params)
    response.raise_for_status()
    return response.json()

# --- Interface do Usuário (Sidebar) ---
with st.sidebar:
    st.title("Configurações da Análise")

    # --- SELEÇÃO DINÂMICA DE BOARD ---
    available_boards = fetch_boards()
    selected_board_name = None
    selected_board_id = None

    if available_boards:
        selected_board_name = st.selectbox(
            "Selecione o Board do Jira para Análise:",
            options=list(available_boards.keys())
        )
        if selected_board_name:
            selected_board_id = available_boards[selected_board_name]
            st.info(f"Board selecionado: **{selected_board_name}** (ID: {selected_board_id})")
    else:
        st.warning("Nenhum board encontrado ou falha ao carregar. Verifique a API.")

    # --- BOTÃO PARA LIMPAR CACHE ---
    if st.button("Limpar Cache e Recarregar Boards"):
        st.cache_data.clear()
        st.success("Cache limpo! A lista de boards e as análises serão recarregadas.")
        st.rerun()

# --- Conteúdo Principal ---
st.title("🤖 Análise de Fluxo do Board")

if not selected_board_id:
    st.info("⬅️ Por favor, selecione um board na barra lateral para começar.")
else:
    run_query = st.button(f"Analisar Board '{selected_board_name}'")

    if run_query:
        try:
            data = fetch_progression_analysis(str(selected_board_id))
            
            progression_list = data.get('progression_data', [])
            llm_analysis = data.get('llm_analysis', 'Análise de IA não disponível.')
            board_name = data.get('board_name', selected_board_name) 

            st.header(f"Insights Analíticos")
            
            # --- LÓGICA DE EXIBIÇÃO MELHORADA ---
            if "ERRO: " in llm_analysis:
                st.error(llm_analysis)
            else:
                with st.expander("Clique para ver o relatório completo", expanded=True):
                    st.markdown(llm_analysis)

            # A tabela de dados agora será exibida mesmo se a IA falhar
            if not progression_list:
                st.warning("Nenhum histórico de progressão encontrado para este board.")
            else:
                df = pd.DataFrame(progression_list)
                df['data_mudanca'] = pd.to_datetime(df['data_mudanca']).dt.strftime('%Y-%m-%d %H:%M:%S')
                df = df[[
                    'card_key', 'data_mudanca', 'status_antigo', 'status_novo', 
                    'autor_mudanca', 'responsavel_card', 'sp', 'desenvolvedor'
                ]]
                df = df.sort_values(by=['card_key', 'data_mudanca'], ascending=[True, True])

                st.header("Dados Detalhados da Progressão")
                st.dataframe(df, hide_index=True, use_container_width=True)

        except requests.exceptions.ConnectionError:
            st.error("A conexão com a API falhou. Verifique se o servidor da API (Uvicorn) está rodando.")
        except Exception as e:
            st.error(f"Erro crítico ao gerar a análise: {str(e)}")
            st.exception(e)