# outliers.py

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

def detectar_outliers(df, grupo, coluna, classe_map=None):
    df_temp = df.copy()

    stats = df_temp.groupby(grupo)[coluna].agg(['mean', 'std', 'count'])
    df_temp = df_temp.merge(stats, on=grupo, how='left')
    df_temp['z_score'] = (df_temp[coluna] - df_temp['mean']) / df_temp['std'].replace(0, np.nan)
    df_temp[f'{coluna}_outlier'] = df_temp['z_score'].abs() > 3

    outlier_counts = df_temp.groupby(grupo)[f'{coluna}_outlier'].sum()
    outlier_counts = outlier_counts.to_frame(name='outliers').merge(stats, left_index=True, right_index=True)

    if classe_map:
        outlier_counts.index = outlier_counts.index.map(classe_map)

    return outlier_counts, df_temp


def exibir_analise_outliers(df):
    st.subheader("Análise de Outliers por Classe de Consumo")

    col_tusd = [col for col in df.columns if "ConsAtivoFatTusd" in col]
    if not col_tusd:
        st.warning("Nenhuma coluna com 'ConsAtivoFatTusd' encontrada no dataset.")
        return

    df['ConsumoAtivoFatTusd'] = df[col_tusd].sum(axis=1)

    classe_map = {
        1: "Residencial",
        2: "Industrial",
        3: "Comercial",
        4: "Rural",
        5: "Servico Publico",
        6: "Poder Publico",
        7: "Iluminacao Publica",
        8: "Consumo Proprio",
        9: "Nao se aplica"
    }

    outlier_df, df_completo = detectar_outliers(
        df,
        grupo='DescricaoClasse',
        coluna='ConsumoAtivoFatTusd',
        classe_map=classe_map
    )

    # Renomear colunas
    outlier_df.rename(columns={
        'mean': 'Média',
        'std': 'STD',
        'count': 'Total',
        'outliers': 'Outliers'
        
    }, inplace=True)

    # Calcular porcentagem de outliers
    outlier_df['% Outliers'] = (outlier_df['Outliers'] / outlier_df['Total'] * 100).round(2)

    # Reordenar colunas
    outlier_df = outlier_df[['Outliers', 'Total', '% Outliers', 'Média', 'STD']]

    # Aplicar formatação
    styled_df = outlier_df.style.format({
        'Outliers': '{:,.0f}'.format,
        'Total': '{:,.0f}'.format,
        '% Outliers': '{:,.2f}'.format,
        'Média': '{:,.2f}'.format,
        'STD': '{:,.2f}'.format,
    }, decimal=",", thousands="")

    st.dataframe(styled_df, use_container_width=False)

# Função para exibir histograma
def exibir_histograma(df, classe):
    st.subheader(f"Histograma para a Classe {classe}")
    
    # Filtrar dados pela classe selecionada
    dados_classe = df[df['DescricaoClasse'] == classe]
    
    # Gerar histograma
    plt.figure(figsize=(10, 6))
    plt.hist(dados_classe['ConsumoAtivoFatTusd'], bins=30, edgecolor='k')
    plt.title(f"Histograma de Consumo Ativo Fat Tusd - Classe {classe}")
    plt.xlabel("Consumo Ativo Fat Tusd")
    plt.ylabel("Frequência")
    
    # Exibir histograma no Streamlit
    st.pyplot(plt)