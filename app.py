import streamlit as st
from data_loader import load_parquet
from analise import run_analysis
from outliers import exibir_analise_outliers, exibir_histograma

import time

# Configuração da página
st.set_page_config(page_title="Dashboard Parquet", page_icon="📊", layout="wide")

# Sidebar para seleção do arquivo Parquet
st.sidebar.title("Selecione um Arquivo")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo Parquet", type=["parquet"])

# Página Principal
st.markdown("### Qualidade dos Dados Cadastro Nacional de Distribuição")

if uploaded_file:
    df = load_parquet(uploaded_file)

    if df is not None:
        if st.sidebar.button("Executar Análises"):
            with st.spinner("Executando análise geral..."):
                run_analysis(df, uploaded_file.name)

            # Análise de outliers direto da função
            exibir_analise_outliers(df)
            
            
            