import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Assistente de Análise Usiminas")

# --- Funções de Controle ---
def next_step():
    """Avança para o próximo passo."""
    st.session_state.step += 1

def restart_analysis():
    """Reinicia a análise, limpando o estado da sessão."""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.step = 0


# --- Inicialização do Estado da Sessão ---
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- Título e Descrição ---
st.title("🤖 Assistente de Análise Guiada (v2)")
st.markdown("Uma ferramenta interativa para construir o prompt de análise perfeito.")

# Adiciona um botão de reinício no topo para fácil acesso
if st.session_state.step > 0:
    st.button("Iniciar Nova Análise", on_click=restart_analysis)

# --- PASSO 0: UPLOAD DO ARQUIVO ---
if st.session_state.step == 0:
    st.header("Passo 1: Carregue sua planilha de dados")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV ou Excel", type=['csv', 'xlsx'], key="uploader")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
            
            # Avança para o próximo passo automaticamente após o upload
            next_step()
            st.rerun()

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# --- PASSO 1: VISUALIZAÇÃO E SELEÇÃO DE COLUNAS ---
if st.session_state.step == 1:
    st.header("Passo 2: Confirme os dados e selecione as colunas para análise")
    st.dataframe(st.session_state.df)
    
    all_columns = st.session_state.df.columns.tolist()
    
    with st.form("column_selection_form"):
        st.session_state.selected_columns = st.multiselect(
            "Selecione as colunas relevantes para o seu problema:",
            options=all_columns,
            default=all_columns
        )
        submit_button = st.form_submit_button("Confirmar Colunas e Continuar")
        if submit_button:
            next_step()
            st.rerun()

# --- PASSO 2: PERGUNTA PRINCIPAL (OBJETIVO) ---
if st.session_state.step == 2:
    st.header("Passo 3: Qual é o seu objetivo principal com estes dados?")
    
    with st.form("objective_form"):
        st.session_state.objetivo = st.selectbox("Selecione uma opção:", [
            "", "Analisar a Causa Raiz de um Problema", "Otimizar um Processo ou KPI", "Criar um Relatório Gerencial"
        ], key="objetivo_selector")
        submit_button = st.form_submit_button("Avançar")
        if submit_button and st.session_state.objetivo:
            next_step()
            st.rerun()
        elif submit_button and not st.session_state.objetivo:
            st.warning("Por favor, selecione um objetivo para continuar.")

# --- PASSO 3: PERGUNTAS SUCESSIVAS (DETALHES DA ANÁLISE) ---
if st.session_state.step == 3:
    st.header("Passo 4: Forneça os detalhes para a análise")
    objetivo = st.session_state.objetivo
    st.info(f"Objetivo selecionado: **{objetivo}**")

    with st.form("details_form"):
        if objetivo == "Analisar a Causa Raiz de um Problema":
            col_evento = st.selectbox("Em qual coluna está o evento/falha?", st.session_state.selected_columns)
            valor_evento = st.text_input(f"Qual valor na coluna '{col_evento}' representa o problema?")
            st.session_state.detalhes = f"O problema a ser investigado é quando a coluna `{col_evento}` apresenta o valor `{valor_evento}`."

        elif objetivo == "Otimizar um Processo ou KPI":
            col_kpi = st.selectbox("Qual coluna representa o KPI a ser otimizado?", st.session_state.selected_columns)
            acao_kpi = st.radio("Qual ação você deseja?", ("Maximizar este KPI", "Minimizar este KPI"))
            acao_texto = "maximizar" if "Maximizar" in acao_kpi else "minimizar"
            st.session_state.detalhes = f"O objetivo é encontrar as condições ideais para **{acao_texto}** o indicador da coluna `{col_kpi}`."

        elif objetivo == "Criar um Relatório Gerencial":
            col_agrupamento = st.selectbox("Por qual coluna você gostaria de agrupar os dados?", st.session_state.selected_columns)
            cols_metricas = st.multiselect("Quais métricas numéricas devem ser sumarizadas?", st.session_state.selected_columns)
            st.session_state.detalhes = f"A tarefa é criar um resumo dos dados, agrupando-os por `{col_agrupamento}` e calculando métricas (soma, média) para as colunas: {', '.join(cols_metricas)}."

        submit_button = st.form_submit_button("Finalizar e Gerar Prompt")
        if submit_button:
            next_step()
            st.rerun()

# --- PASSO 4: GERAÇÃO DO PROMPT FINAL ---
if st.session_state.step == 4:
    st.header("✅ Prompt Final Gerado com Sucesso!")
    
    prompt_final = f"""**Persona:**
Você é um engenheiro de dados sênior, especialista em análise de processos industriais.

**Contexto:**
Estou analisando uma tabela de dados com as seguintes colunas relevantes: {', '.join(st.session_state.selected_columns)}.

**Tarefa Principal:**
Meu objetivo é: **{st.session_state.objetivo}**.

**Detalhes da Análise:**
{st.session_state.detalhes}

**Instruções para a IA:**
1.  Concentre sua análise exclusivamente nas colunas selecionadas.
2.  Apresente os resultados de forma clara, usando tabelas e listas (bullet points).
3.  Forneça um breve resumo textual com os principais insights encontrados.
4.  Se aplicável, sugira um código em Python com `pandas` e `plotly` para criar uma visualização gráfica dos resultados.
"""
    st.code(prompt_final, language="markdown")