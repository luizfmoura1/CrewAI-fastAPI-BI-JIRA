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
@st.cache_data(ttl=3600, show_spinner="Analisando fluxo de trabalho com IA...")
def fetch_progression_analysis(board_id: str):
    params = {"board_id": board_id}
    response = requests.get(f"{API_URL}/JIRA_card_progression", params=params)
    response.raise_for_status()
    return response.json()

# --- Interface do Usuário ---
with st.sidebar:
    st.title("Configurações da Análise")
    selected_board_id = "734" 
    st.info(f"Análise focada no Board ID: {selected_board_id}")
    st.success("A análise será feita automaticamente no board selecionado.")

    # --- BOTÃO PARA LIMPAR CACHE ---
    if st.button("Limpar Cache e Tentar Novamente"):
        st.cache_data.clear()
        st.success("Cache limpo! Clique para analisar novamente.")


run_query = st.button("Analisar Board")

if run_query:
    if selected_board_id:
        try:
            data = fetch_progression_analysis(str(selected_board_id))
            
            progression_list = data.get('progression_data', [])
            llm_analysis = data.get('llm_analysis', 'Análise de IA não disponível.')
            board_name = data.get('board_name', 'Board não identificado') # Usando board_name que a API retorna

            st.title(f"🤖 Análise de Fluxo do Board")

            st.header("Insights do Analista de IA")
            
            # --- LÓGICA DE EXIBIÇÃO MELHORADA ---
            # Verifica se a análise da IA contém uma mensagem de erro
            if "ERRO NO AGENTE DE IA:" in llm_analysis:
                st.error(llm_analysis) # Mostra o erro de forma destacada
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
            st.error("A conexão com a API falhou. Verifique se o servidor da API (Uvicorn) está rodando no outro terminal.")
        except Exception as e:
            st.error(f"Erro crítico ao gerar a análise: {str(e)}")
            st.exception(e)
else:
    st.info("Clique em **Analisar Board** para iniciar.")