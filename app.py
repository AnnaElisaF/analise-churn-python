import streamlit as st
import pandas as pd
import pickle

# Configuração da página
st.set_page_config(
    page_title='Análise de Churn',
    page_icon='📊',
    layout='wide'
)

# Carregando artefatos salvos
# IMPORTANTE: Este é o caminho completo para a sua pasta de projeto
caminho_base = r'D:\Projeto_Churn' 

try:
    # Usamos f-strings para construir o caminho absoluto para cada arquivo
    # A barra '/' funciona em todos os sistemas (Windows, Mac, Linux) e é uma boa prática
    with open(f'{caminho_base}/modelo_campeao.pkl', 'rb') as f:
        modelo = pickle.load(f)
    with open(f'{caminho_base}/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)

    features_df = pd.read_csv(f'{caminho_base}/features.csv')
    feature_names = features_df.columns.tolist()

except FileNotFoundError:
    st.error(f"Erro: Arquivo não encontrado! O Streamlit tentou procurar os arquivos na pasta '{caminho_base}'. Por favor, verifique se este caminho está correto e se os arquivos existem lá.")
    st.stop()


# Layout do app com abas
st.title('Análise de Churn de clientes da Telecom')

tab1, tab2 = st.tabs(['Resumo do projeto', 'Simulador de Churn'])

# Aba 1: Resumo do projeto
with tab1:
    st.header('O problema do negócio')
    st.markdown("""
    A perda de clientes, ou *Churn*, é um dos desafios mais críticos para empresas de serviço. Um cliente que cancela não só representa uma perda de receita imediata, mas também custos associados à aquisição de novos clientes para substituí-lo.
    
    Nossa análise inicial revelou uma **taxa de churn de 26.5%**, um número que justifica uma investigação aprofundada para identificar os fatores que levam a esse cancelamento e criar uma solução proativa.
    """
    )

    st.header('Investigação e pistas')
    st.markdown("""
    Através da análise exploratória, descobrimos que o churn não é aleatório. Existe um perfil de cliente com maior risco, caracterizado principalmente por:
    - **Tipo de Contrato:** Clientes com contrato **mês a mês** são muito mais propensos a cancelar.
    - **Serviços:** Clientes com **internet de Fibra Ótica** mas **sem serviços de proteção** (como Suporte Técnico, Segurança e Backup Online) apresentam maior churn.
    - **Faturamento:** Faturas mensais **mais altas** e um **baixo tempo de contrato (tenure)** são fortes indicadores de risco.
                """)
    st.header('Solução baseada em dados')
    st.markdown("""
    Para combater o problema, desenvolvemos e comparamos múltiplos modelos de Machine Learning. O objetivo era criar uma ferramenta capaz de prever o churn com base nas características dos clientes.
    
    O modelo campeão foi a **Regressão Logística**, que apresentou o melhor equilíbrio entre performance e simplicidade, com um **F1-Score de 0.56** e um **Recall de 0.52** para a classe de churn.
    """)

    st.header('Impacto e recomendação')
    st.markdown("""
    **O que isso significa?** Nosso modelo consegue identificar corretamente **52% de todos os clientes que iriam cancelar**. Isso permite que a empresa mude de uma postura reativa para uma **estratégia proativa de retenção**.
    
    **Recomendação:** Implementar o modelo para gerar uma lista semanal de clientes em risco, permitindo que a equipe de retenção atue de forma direcionada com ofertas e suporte, otimizando recursos e maximizando a retenção.
    """)

# Simulador de Churn
with tab2:
    st.header('Simulador de risco de Churn')
    st.markdown('Preencha as características abaixo para obter uma previsão de churn para um cliente hipotético.')

    col1, col2, col3 = st.columns(3)

    with col1: 
        tenure = st.slider('Tempo de contrato (meses)', 0, 72, 12)
        contract = st.selectbox('Tipo de Contrato', ['Month-to-month', 'One-year', 'Two-year'])
        internet_service = st.selectbox('Serviço de Internet', ['DSL', 'Fiber optic', 'No'])
        online_security = st.selectbox('Seguranca Online', ['Yes', 'No', 'No internet service'])

    with col2:
        monthly_charges = st.slider('Fatura Mensal (R$)', 18.0, 120.0, 70.0)
        tech_support = st.selectbox('Suporte Técnico', ['Yes', 'No', 'No internet service'])
        dependents = st.selectbox('Possui Dependentes?', ['Yes', 'No'])
        payment_method = st.selectbox('Método de Pagamento', ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'])

    with col3:
        total_charges = st.number_input('Fatura Total (R$)', min_value=0.0, value=1000.0, step=100.0)
        paperless_billing = st.selectbox('Faturamento Eletrônico (Paperless)?', ['Yes', 'No'])
        partner = st.selectbox('Possui Parceiro(a)?', ['Yes', 'No'])
        senior_citizen = st.selectbox('É Idoso(a)?', [0, 1])

    if st.button('Calcular risco de Churn', key='predict_button'):
        # Preparando os dados do formulário para o modelo
        # 1. Criar um dicionário com os inputs do usuário

        user_input = {
            'SeniorCitizen': senior_citizen, 'Partner': partner, 'Dependents': dependents, 'tenure': tenure,
            'PhoneService': 'Yes', 'MultipleLines': 'No', 'InternetService': internet_service, 'OnlineSecurity': online_security,
            'OnlineBackup': 'No', 'DeviceProtection': 'No', 'TechSupport': tech_support, 'StreamingTV': 'No',
            'StreamingMovies': 'No', 'Contract': contract, 'PaperlessBilling': paperless_billing, 'PaymentMethod': payment_method,
            'MonthlyCharges': monthly_charges, 'TotalCharges': total_charges
        }

        # 2. Converter para DataFrame do Pandas
        input_df = pd.DataFrame([user_input])

        # 3. Aplicar One-hot encoding
        # Usamos o reindex para garantir que o input_df tenha exatamente as mesmas colunas que o modelo espera
        input_processed = pd.get_dummies(input_df).reindex(columns=feature_names, fill_value=0)

        # 4. Escalonar os dados
        input_scaled = scaler.transform(input_processed)

        # 5. Fazer a previsão 
        prediction = modelo.predict(input_scaled)
        prediction_proba = modelo.predict_proba(input_scaled)

        # 6. Exibir resultados
        churn_prob = prediction_proba[0][1]
        st.subheader('Resultado da previsão')
        if prediction[0] == 1:
            st.error(f"ALTO RISCO DE CHURN (Probabilidade: {churn_prob:.2%})")
            st.write("Recomendação: Incluir este cliente em uma campanha de retenção proativa.")
        else:
            st.success(f"Baixo Risco de Churn (Probabilidade de Churn: {churn_prob:.2%})")
            st.write("Recomendação: Manter o monitoramento padrão.")