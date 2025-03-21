import streamlit as st
import pandas as pd
import time

def load_parquet(uploaded_file):
    """Carrega um arquivo Parquet e retorna um DataFrame com barra de progresso que desaparece ao finalizar."""
    df = pd.read_parquet(uploaded_file)
    st.success("✅ Leitura do Dataset Concluída!")

    return df
