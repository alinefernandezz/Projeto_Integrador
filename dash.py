import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Consulta no banco de dados
query = "SELECT * FROM tb_registro"

# Carregar os dados do MySQL
df = conexao(query)

# Botão para atualização dos dados
if st.button("Atualizar dados"):
    df = conexao(query)

# Menu lateral
st.sidebar.header("Selecione a informação para gerar o gráfico")

# Seleção de colunas X e Y
colunaX = st.sidebar.selectbox(
    "Eixo X",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=0
)

colunaY = st.sidebar.selectbox(
    "Eixo Y",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=1
)

# Função para verificar se um atributo está nos eixos selecionados
def filtros(atributo):
    return atributo in [colunaX, colunaY]

# Filtro de range (slider) para atributos
st.sidebar.header("Selecione o filtro")

# Temperatura
if filtros("temperatura"):
    temperatura_range = st.sidebar.slider(
        "Temperatura (°C)",
        min_value=float(df["temperatura"].min()),
        max_value=float(df["temperatura"].max()),
        value=(float(df["temperatura"].min()), float(df["temperatura"].max())),
        step=0.1
    )

# Umidade
if filtros("umidade"):
    umidade_range = st.sidebar.slider(
        "Umidade",
        min_value=float(df["umidade"].min()),
        max_value=float(df["umidade"].max()),
        value=(float(df["umidade"].min()), float(df["umidade"].max())),
        step=0.1
    )

# Altitude
if filtros("altitude"):
    altitude_range = st.sidebar.slider(
        "Altitude",
        min_value=float(df["altitude"].min()),
        max_value=float(df["altitude"].max()),
        value=(float(df["altitude"].min()), float(df["altitude"].max())),
        step=0.1
    )

# Pressão
if filtros("pressao"):
    pressao_range = st.sidebar.slider(
        "Pressão",
        min_value=float(df["pressao"].min()),
        max_value=float(df["pressao"].max()),
        value=(float(df["pressao"].min()), float(df["pressao"].max())),
        step=0.1
    )

# CO2
if filtros("co2"):
    co2_range = st.sidebar.slider(
        "CO2",
        min_value=float(df["co2"].min()),
        max_value=float(df["co2"].max()),
        value=(float(df["co2"].min()), float(df["co2"].max())),
        step=0.1
    )

# Poeira
if filtros("poeira"):
    poeira_range = st.sidebar.slider(
        "Poeira",
        min_value=float(df["poeira"].min()),
        max_value=float(df["poeira"].max()),
        value=(float(df["poeira"].min()), float(df["poeira"].max())),
        step=0.1
    )

# Aplicação dos filtros
df_selecionado = df.copy()
if filtros("temperatura"):
    df_selecionado = df_selecionado[
        (df_selecionado["temperatura"] >= temperatura_range[0]) &
        (df_selecionado["temperatura"] <= temperatura_range[1])
    ]
if filtros("umidade"):
    df_selecionado = df_selecionado[
        (df_selecionado["umidade"] >= umidade_range[0]) &
        (df_selecionado["umidade"] <= umidade_range[1])
    ]
if filtros("altitude"):
    df_selecionado = df_selecionado[
        (df_selecionado["altitude"] >= altitude_range[0]) &
        (df_selecionado["altitude"] <= altitude_range[1])
    ]
if filtros("pressao"):
    df_selecionado = df_selecionado[
        (df_selecionado["pressao"] >= pressao_range[0]) &
        (df_selecionado["pressao"] <= pressao_range[1])
    ]
if filtros("co2"):
    df_selecionado = df_selecionado[
        (df_selecionado["co2"] >= co2_range[0]) &
        (df_selecionado["co2"] <= co2_range[1])
    ]
if filtros("poeira"):
    df_selecionado = df_selecionado[
        (df_selecionado["poeira"] >= poeira_range[0]) &
        (df_selecionado["poeira"] <= poeira_range[1])
    ]

# Função para calcular o Índice de Qualidade do Ar (AQI)
def calcular_aqi(df):
    # Definir faixas para as variáveis com base em níveis típicos de qualidade do ar
    def classificar_aqi(co2, temp, umid):
        # Se algum dos valores for None ou NaN, retorna 'Desconhecido'
        if pd.isna(co2) or pd.isna(temp) or pd.isna(umid):
            return "Desconhecido", "#808080"  # Cinza para indicar ausência de dados

        # Classificação de AQI com base nas faixas definidas
        if co2 < 400 and 15 <= temp <= 25 and 30 <= umid <= 60:
            return "Bom", "#00ff00"  # Verde
        elif co2 < 800 and (15 <= temp <= 30) and (20 <= umid <= 70):
            return "Moderado", "#ffff00"  # Amarelo
        elif co2 < 1200 or (temp < 15 or temp > 30) or (umid < 20 or umid > 70):
            return "Ruim", "#ffa500"  # Laranja
        else:
            return "Perigoso", "#ff0000"  # Vermelho

    # Aplicar a classificação em cada linha do DataFrame
    df['AQI'], df['AQI_cor'] = zip(*df.apply(lambda row: classificar_aqi(row['co2'], row['temperatura'], row['umidade']), axis=1))
    return df

# Atualizar o DataFrame com o AQI
df_selecionado = calcular_aqi(df_selecionado)

# Função para exibir o Índice de Qualidade do Ar (AQI)
def exibir_aqi():
    st.sidebar.header("Índice de Qualidade do Ar (AQI)")
    if not df_selecionado.empty:
        # Verificar se existem valores válidos antes de exibir
        if df_selecionado['AQI'].iloc[-1] != "Desconhecido":
            aqi_status, aqi_cor = df_selecionado.iloc[-1][['AQI', 'AQI_cor']]
            st.sidebar.markdown(f"<h2 style='color:{aqi_cor}'>AQI: {aqi_status}</h2>", unsafe_allow_html=True)
        else:
            st.sidebar.write("AQI não disponível devido a dados insuficientes.")
    else:
        st.sidebar.write("Nenhum dado disponível para calcular o AQI")

# Função para exibir informações
def Home():
    with st.expander("Tabela"):
        mostrarDados = st.multiselect(
            "Filtros:",
            df_selecionado.columns,
            default=[],
            key="showData_home"
        )
        if mostrarDados:
            st.write(df_selecionado[mostrarDados])

    if not df_selecionado.empty:
        media_umidade = df_selecionado['umidade'].mean()
        media_temperatura = df_selecionado['temperatura'].mean()
        media_co2 = df_selecionado['co2'].mean()

        media1, media2, media3 = st.columns(3, gap='large')
        with media1:
            st.info('Média de Registros de Umidade')
            st.metric(label='Média', value=f'{media_umidade:.2f}')
        with media2:
            st.info('Média de Registros de Temperatura')
            st.metric(label='Média', value=f'{media_temperatura:.2f}')
        with media3:
            st.info('Média de Registros de CO2')
            st.metric(label='Média', value=f'{media_co2:.2f}')
        st.markdown("""-------------------""")

    # Botão para exportar dados
    if not df_selecionado.empty:
        st.download_button(
            label="Baixar dados filtrados como CSV",
            data=df_selecionado.to_csv(index=False).encode('utf-8'),
            file_name='dados_filtrados.csv',
            mime='text/csv'
        )

# Função para exibir gráficos
def graficos():
    st.title('Dashboard de Monitoramento')
    
    aba1, aba2 = st.tabs(['Gráfico de Barras', 'Gráfico de Dispersão'])

    # Gráfico de Barras
    with aba1:
        if df_selecionado.empty:
            st.write('Nenhum dado está disponível para gerar o gráfico')
        else:
            try:
                grupo_dados = df_selecionado.groupby(by=[colunaX]).size().reset_index(name="contagem")

                fig_barras = px.bar(
                    grupo_dados,
                    x=colunaX,
                    y="contagem",
                    title=f"Contagem de Registros por {colunaX.capitalize()}",
                    color_discrete_sequence=["#0083b8"],
                    template="plotly_white"
                )
                st.plotly_chart(fig_barras, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao criar o gráfico de barras: {e}")

    # Gráfico de Dispersão
    with aba2:
        if df_selecionado.empty:
            st.write('Nenhum dado está disponível para gerar o gráfico de dispersão')
        elif colunaX == colunaY:
            st.warning('Selecione uma opção diferente para os eixos X e Y')
        else:
            try:
                fig_disp = px.scatter(
                    df_selecionado,
                    x=colunaX,
                    y=colunaY,
                    title=f"Gráfico de Dispersão: {colunaX.capitalize()} vs {colunaY.capitalize()}",
                    color_discrete_sequence=["#ff6600"],  # Cor do gráfico
                    template="plotly_white"
                )
                st.plotly_chart(fig_disp, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao criar o gráfico de dispersão: {e}")

# Função para feedback e denúncias
def feedback():
    st.title("Feedback e Denúncias")
    st.write("Por favor, preencha o formulário abaixo para enviar seu feedback ou denúncia:")
    
    nome = st.text_input("Seu nome:")
    email = st.text_input("Seu email:")
    mensagem = st.text_area("Sua mensagem:")
    
    if st.button("Enviar"):
        # implementar dados aqui para salvar ou enviar
        st.success("Obrigado pelo seu feedback! Sua mensagem foi enviada com sucesso.")

# Função principal
def main():
    st.title('Monitoramento da Qualidade do Ar')
    
    # Abas do dashboard
    aba_home, aba_graficos, aba_feedback = st.tabs(['Home', 'Gráficos', 'Feedback e Denúncias'])
    
    with aba_home:
        Home()
    
    with aba_graficos:
        exibir_aqi()
        graficos()
    
    with aba_feedback:
        feedback()


# Função para exibir alertas e avisos
def exibir_alertas():
    st.subheader("Alertas e Avisos")
    st.write("### Alertas em Tempo Real")
    # criar logica para exibir alerta em tempo real
    # mensagem de alertas ficticias
    alertas = [
        "Níveis de poluição elevados detectados na região central de São Paulo.",
        "Condições climáticas adversas previstas para os próximos dias: chuvas e vento forte.",
        "Monitoramento especial necessário em áreas com alta concentração de CO2."
    ]
    
    for alerta in alertas:
        st.warning(alerta)  # Exibe cada alerta como uma mensagem de aviso

# Atualizar a função Home para incluir alertas
def Home():
    with st.expander("Tabela"):
        mostrarDados = st.multiselect(
            "Filtros:",
            df_selecionado.columns,
            default=[],
            key="showData_home"
        )
        if mostrarDados:
            st.write(df_selecionado[mostrarDados])

    if not df_selecionado.empty:
        media_umidade = df_selecionado['umidade'].mean()
        media_temperatura = df_selecionado['temperatura'].mean()
        media_co2 = df_selecionado['co2'].mean()

        media1, media2, media3 = st.columns(3, gap='large')
        with media1:
            st.info('Média de Registros de Umidade')
            st.metric(label='Média', value=f'{media_umidade:.2f}')
        with media2:
            st.info('Média de Registros de Temperatura')
            st.metric(label='Média', value=f'{media_temperatura:.2f}')
        with media3:
            st.info('Média de Registros de CO2')
            st.metric(label='Média', value=f'{media_co2:.2f}')
        st.markdown("""-------------------""")

    # Exibir alertas e avisos na tela inicial
    exibir_alertas()

    # Botão para exportar dados
    if not df_selecionado.empty:
        st.download_button(
            label="Baixar dados filtrados como CSV",
            data=df_selecionado.to_csv(index=False).encode('utf-8'),
            file_name='dados_filtrados.csv',
            mime='text/csv'
        )



# Executar a função principal
if __name__ == "__main__":
    main()
