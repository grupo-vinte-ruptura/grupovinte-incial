import streamlit as st
import pandas as pd

# --- CSS CUSTOMIZADO PARA A ESTÉTICA VERDE E BRANCO ---
def load_custom_css():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: linear-gradient(180deg, #FFFFFF, #E8F5E9);
    }
    .stButton>button {
        border: 2px solid #00693C; border-radius: 10px; color: #00693C; background-color: #FFFFFF;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #004D2B; color: #FFFFFF; background-color: #00693C;
    }
    h1, h2, h3 { color: #004D2B; }
    [data-testid="stFileUploader"], [data-testid="stForm"], .stMultiSelect, .stSelectbox, .stRadio {
        border-radius: 10px; padding: 15px; background-color: rgba(255, 255, 255, 0.7);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- INÍCIO DA APLICAÇÃO ---
st.set_page_config(layout="wide", page_title="Assistente Preditivo Usiminas")
load_custom_css()

# --- Gerenciamento de Estado ---
if 'step' not in st.session_state:
    st.session_state.step = 0

def next_step(): st.session_state.step += 1
def restart_analysis():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 0

# --- Título e Descrição ---
st.title("IA para Análise Preditiva")
st.markdown("Construa um prompt de análise preditiva completo, passo a passo, apenas com cliques.")
if st.session_state.step > 0:
    st.button("⬅️ Iniciar Nova Análise", on_click=restart_analysis)
st.divider()

# --- ÁRVORE DE DECISÃO (Passos 0 a 4 permanecem idênticos) ---

# PASSO 0: Upload dos dados
if st.session_state.step == 0:
    st.header("Ponto de Partida: Seus Dados Históricos")
    st.info("Para prever o futuro, precisamos entender o passado. Por favor, carregue sua base de dados histórica.")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV ou Excel", type=['csv', 'xlsx'], key="uploader")
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        next_step()
        st.rerun()

# PASSO 1: Escolha do Problema Preditivo
if st.session_state.step == 1:
    st.header("Passo 1: Qual problema você quer prever?")
    with st.form("problem_form"):
        st.radio("Selecione o alvo da sua análise preditiva:",
            ('Falha em um componente do laminador', 'Variação da dureza do aço',
             'Surgimento de trincas na laminação a quente', 'Tempo ótimo de vida de um refratário no alto-forno'),
            key="problema_preditivo")
        if st.form_submit_button("Continuar ➡️"):
            next_step()
            st.rerun()

# PASSO 2: Preparação dos Dados
if st.session_state.step == 2:
    st.header("Passo 2: Descreva a preparação dos seus dados")
    with st.form("data_prep_form"):
        st.subheader("Fontes e Integração")
        st.multiselect("De quais fontes estes dados foram extraídos?",
            ['Sensores de Processo (SCADA)', 'Dados de Laboratório (LIMS)', 'Logs de Manutenção (SAP-PM)', 'Dados de Produção (ERP)'],
            key="fontes_dados")
        st.subheader("Padronização de Escalas")
        st.multiselect("Quais padronizações são necessárias?",
            ['Unificar unidades de medida', 'Normalizar dados (escala 0 a 1)'],
            key="padronizacao")
        st.subheader("Limpeza e Transformação")
        st.multiselect("Quais tarefas de limpeza e engenharia de features devem ser consideradas?",
            ['Tratar valores ausentes ou nulos (NaNs)', 'Remover outliers',
             'Criar variáveis derivadas', 'Consolidar dados em uma única tabela'],
            key="limpeza")
        if st.form_submit_button("Continuar ➡️"):
            next_step()
            st.rerun()

# PASSO 3: Foco da Análise e Variáveis
if st.session_state.step == 3:
    st.header("Passo 3: Defina o foco da análise e as variáveis")
    with st.form("analysis_focus_form"):
        st.subheader("Padrões Históricos a Investigar")
        st.multiselect("Que tipos de padrões a IA deve procurar nos dados históricos?",
            ['Correlação entre variáveis e o evento alvo', 'Sazonalidade ou ciclicidade nas falhas', 'Mudanças de comportamento que antecedem o evento'],
            key="padroes")
        st.subheader("Seleção de Variáveis Relevantes (Feature Selection)")
        st.info("Selecione as colunas da sua tabela que você acredita serem as mais importantes para prever o problema.")
        colunas_disponiveis = st.session_state.df.columns.tolist()
        st.multiselect("Selecione as variáveis (features):", colunas_disponiveis, default=colunas_disponiveis, key="variaveis")
        if st.form_submit_button("Continuar ➡️"):
            next_step()
            st.rerun()

# PASSO 4: Escolha da Técnica de Machine Learning
if st.session_state.step == 4:
    st.header("Passo 4: Escolha a abordagem de Machine Learning")
    problema = st.session_state.get("problema_preditivo", "")
    if "tempo ótimo de vida" in problema or "variação da dureza" in problema:
        sugestao_index = 0
    elif "falha em um componente" in problema or "surgimento de trincas" in problema:
        sugestao_index = 1
    else:
        sugestao_index = 2
    with st.form("ml_technique_form"):
        st.info("Com base no problema escolhido, sugerimos uma técnica. Você pode alterá-la se desejar.")
        st.selectbox("Selecione a técnica de modelagem preditiva:",
            ('Regressão (prever um valor numérico contínuo, ex: dureza, tempo de vida)',
             'Classificação (prever uma categoria, ex: "vai falhar" ou "não vai falhar")',
             'Análise de Séries Temporais (prever valores futuros com base em uma sequência de tempo)'),
            index=sugestao_index, key="tecnica_ml")
        if st.form_submit_button("Finalizar e Gerar Prompt ✨"):
            next_step()
            st.rerun()

# --- PASSO FINAL: GERAÇÃO DO PROMPT (COM A LÓGICA DO GRÁFICO APRIMORADA) ---
if st.session_state.step == 5:
    st.header("✅ Prompt Preditivo Gerado com Sucesso!")
    
    data_string = st.session_state.df.to_csv(index=False)
    
    # Montando o prompt final com as novas instruções
    prompt_final = f"""**Persona:**
Você é um cientista de dados sênior, especialista em modelagem preditiva para a indústria pesada. Sua tarefa é analisar os dados fornecidos e apresentar os resultados de forma clara e visual.

**1. Objetivo Principal da Análise Preditiva:**
O objetivo é criar um modelo capaz de prever: **{st.session_state.get("problema_preditivo", "Não definido")}**.

**2. Contexto e Preparação dos Dados (Instruções para você):**
- **Fontes de Dados:** Considere que os dados vieram de: {', '.join(st.session_state.get("fontes_dados", []))}.
- **Padronização e Normalização:** Ao analisar, realize as seguintes padronizações: {', '.join(st.session_state.get("padronizacao", []))}.
- **Limpeza e Engenharia de Features:** Execute as seguintes etapas de pré-processamento: {', '.join(st.session_state.get("limpeza", []))}.

**3. Abordagem Analítica e de Modelagem (Instruções para você):**
- **Análise de Padrões Históricos:** Investigue os seguintes padrões: {', '.join(st.session_state.get("padroes", []))}.
- **Variáveis Relevantes (Features):** Construa o modelo utilizando prioritariamente as seguintes variáveis: {', '.join(st.session_state.get("variaveis", []))}.
- **Técnica de Machine Learning:** Utilize a abordagem de: **{st.session_state.get("tecnica_ml", "Não definido").split(' (')[0]}**.

**4. Formato da Saída Esperada (O que você deve gerar):**
- **Análise Exploratória (EDA):** Apresente um resumo em bullet points com os principais insights encontrados nos dados.
- **Resultados do Modelo:** Apresente as principais métricas de performance do modelo (ex: R², MAE para regressão; Acurácia, F1-Score para classificação).
- **Visualização Gráfica (Resultado Principal):** Esta é a parte mais importante. Sua tarefa é gerar uma visualização da importância de cada variável (feature importance). Entregue o resultado usando a seguinte ORDEM DE PREFERÊNCIA:
    - **1º (Preferencial): Código SVG.** Gere diretamente o código para um gráfico de barras em formato SVG. Envolva o código SVG completo dentro de um bloco de código.
    - **2º (Alternativa): Código Python.** Se não for possível gerar SVG, forneça o código Python completo usando `matplotlib` ou `plotly` para gerar o gráfico de barras.
    - **3º (Último Recurso): Tabela Markdown.** Se nenhuma das opções acima for possível, apresente os dados da importância das variáveis em uma tabela formatada em Markdown com as colunas "Variável" e "Índice de Importância (0 a 1)".
- **Conclusão e Recomendações:** Forneça um resumo em 2-3 frases com os principais insights (ex: "A variável X foi a mais influente...") e recomende ações práticas com base na análise.

--- DADOS PARA ANÁLISE ---
{data_string}
"""
    st.code(prompt_final, language="markdown")
    st.info("✅ Copie todo o texto acima e cole na sua IA de preferência. Os dados já estão incluídos!")