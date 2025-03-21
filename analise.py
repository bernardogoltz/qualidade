import pandas as pd
import numpy as np
import re
from datetime import datetime
import streamlit as st
import time 

def extract_file_info(file_name):
    match = re.search(r'(\d{4})(\d{2})_(\w+).parquet', file_name)
    if match:
        ano, mes, distribuidora = match.groups()
        mes_nome = datetime.strptime(mes, "%m").strftime("%m").capitalize()  # Converte mês para nome (ex: 03 -> Março)
        return f"{mes_nome}/{ano}", distribuidora.upper()
    return "Desconhecido", "Desconhecido"

def show_result(label, classification):
    emoji = "✔️" if classification == "Bons" else "❌"
    color = "green" if classification == "Bons" else "red"
    st.markdown(f"{emoji} {label}: <span style='color:{color}; font-weight:bold;'>{classification}</span>", unsafe_allow_html=True)

def run_analysis(df , file_name):
    start_time = time.time()
    periodo, distribuidora = extract_file_info(file_name)
    with st.status("Executando Análise dos Dados...", expanded=True) as status:
        st.subheader(f"{distribuidora} - {periodo}")
        st.subheader("Resultados da Análise")

        """
        Precisão
        """
        precisao_faturamento = df['TipoFaturamento'].isin([1, 2, 3, 4]).sum()
        precisao_classe = df['DescricaoClasse'].isin([1, 2, 3, 4, 5, 6, 7, 8, 9]).sum()
        subclasse_permitidas = [str(i) for i in range(1, 34)]
        precisao_subclasse = df['DescricaoSubclasse'].astype(str).isin(subclasse_permitidas).sum()
        classificacao_precisao = "Bons" if precisao_faturamento > 90 and precisao_classe > 90 else "Ruins"
        show_result("Precisão", classificacao_precisao)

        """
        Completude
        """
        completude = df[['NomeCliente', 'CodUsuario', 'DataEmissaoFatura', 'CodigoIbge', 'NumCep']].isnull().sum() / len(df) * 100
        classificacao_completude = "Bons" if completude.max() < 5 else "Ruins"
        show_result("Completude", classificacao_completude)

        """
        Consistência
        """
        valid_cod_ibge = df['CodigoIbge'].apply(lambda x: len(str(x)) == 7).sum()
        valid_date_order = df[pd.to_datetime(df['DataVencimento']) < pd.to_datetime(df['DataEmissaoFatura'])].shape[0]
        classificacao_consistencia = "Bons" if valid_cod_ibge > 95 and valid_date_order == 0 else "Ruins"
        show_result("Consistência", classificacao_consistencia)

        """
        Unicidade
        """
        duplicatas_num_uc = df['CodUsuario'].duplicated().sum()
        duplicatas_cod_medidor = df['CodMedidor'].duplicated().sum()
        classificacao_unicidade = "Bons" if duplicatas_cod_medidor == duplicatas_num_uc else "Ruins"
        show_result("Unicidade", classificacao_unicidade)

        """
        Pontualidade
        """
        df['DataRevisaoCadastral'] = pd.to_datetime(df['DataRevisaoCadastral'])
        ultima_revisao = df['DataRevisaoCadastral'].max()
        diferenca_dias = (datetime.now() - ultima_revisao).days
        classificacao_pontualidade = "Bons" if diferenca_dias <= 365 else "Ruins"
        show_result("Pontualidade", classificacao_pontualidade)

        """
        Validade (CPF/CNPJ)
        """
        cpf_cnpj_valido = df['NumCpfCnpj'].apply(lambda x: validar_cpf(str(x)) if len(str(x)) <= 11 else validar_cnpj(str(x)))
        percentual_valido = cpf_cnpj_valido.mean() * 100
        classificacao_validade = "Bons" if percentual_valido > 95 else "Ruins"
        show_result("Validade", classificacao_validade)

        # Finaliza o status de carregamento
        execution_time = time.time() - start_time
        st.markdown(f"**Tempo de execução:** {execution_time:.2f} segundos")


        status.update(label="Análise Concluída!", state="complete", expanded=True)
        

# Função para validar CPF
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    return digito1 == int(cpf[9]) and digito2 == int(cpf[10])

# Função para validar CNPJ
def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    pesos2 = [6] + pesos1
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    return digito1 == int(cnpj[12]) and digito2 == int(cnpj[13])