import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Configuração da página
st.set_page_config(page_title="Monitoramento do Rio", layout="wide")

# Função para carregar e processar os dados do JSON
def load_data(data_json):
    data = json.loads(data_json)
    rows = []
    for row in data['table']['rows']:
        processed_row = {}
        for i, col in enumerate(data['table']['cols']):
            value = row['c'][i]['v'] if row['c'][i] and 'v' in row['c'][i] else None
            if col['type'] == 'datetime' and value:
                # Exemplo: "Date(2025,0,3,16,15,11)"
                value = value.replace('Date(', '').replace(')', '')
                year, month, day, hour, minute, second = map(int, value.split(','))
                value = datetime(year, month + 1, day, hour, minute, second)
            elif col['type'] == 'date' and value:
                value = value.replace('Date(', '').replace(')', '')
                year, month, day = map(int, value.split(','))
                value = datetime(year, month + 1, day)
            processed_row[col['label']] = value
        rows.append(processed_row)
    return pd.DataFrame(rows)

# Título
st.title("📊 Dashboard de Monitoramento do Rio")

# Carrega os dados do arquivo JSON
with open('dados.json', 'r', encoding='utf-8') as file:
    json_data = file.read()
df = load_data(json_data)

# Converte a coluna "DATA" para datetime e extrai somente a data
if "DATA" in df.columns:
    df["DATA"] = pd.to_datetime(df["DATA"], errors='coerce').dt.date
else:
    st.error("Coluna 'DATA' não encontrada no conjunto de dados.")

# Calcula as datas válidas removendo os nulos para evitar comparações com float
valid_dates = df["DATA"].dropna()
if valid_dates.empty:
    st.error("Nenhuma data válida encontrada na coluna 'DATA'.")
    min_date = datetime.today().date()
    max_date = datetime.today().date()
else:
    min_date = valid_dates.min()
    max_date = valid_dates.max()

# Sidebar: Filtros
st.sidebar.header("Filtros")

date_range = st.sidebar.date_input(
    "Selecione o período",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

selected_names = st.sidebar.multiselect(
    "Selecione os operadores",
    options=df["NOME"].unique(),
    default=df["NOME"].unique()
)

# Filtra os dados com base no período e nos operadores
mask = (
    (df["DATA"].between(date_range[0], date_range[1])) &
    (df["NOME"].isin(selected_names))
)
filtered_df = df[mask]

# Conteúdo principal: gráficos e métricas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Nível do Rio ao Longo do Tempo")
    fig_level = px.line(
        filtered_df,
        x="Carimbo de data/hora",
        y="Nível do Rio (m)",
        markers=True
    )
    st.plotly_chart(fig_level, use_container_width=True)
    
    if "Chuva (mm)" in filtered_df.columns:
        st.subheader("Registro de Chuvas")
        fig_rain = px.bar(
            filtered_df,
            x="Carimbo de data/hora",
            y="Chuva (mm)"
        )
        st.plotly_chart(fig_rain, use_container_width=True)
        
with col2:
    st.subheader("Status de Assoreamento")
    fig_silting = px.pie(
        filtered_df,
        names="Assoreamento [Nova]",
        title="Distribuição do Status de Assoreamento"
    )
    st.plotly_chart(fig_silting, use_container_width=True)
    
    st.subheader("Atividade por Operador")
    operator_activity = filtered_df["NOME"].value_counts()
    fig_operators = px.bar(
        operator_activity,
        title="Número de Registros por Operador"
    )
    st.plotly_chart(fig_operators, use_container_width=True)

# Tabela de dados
st.subheader("Dados Detalhados")
st.dataframe(
    filtered_df.sort_values("Carimbo de data/hora", ascending=False),
    use_container_width=True
)

# Métricas principais
st.subheader("Métricas Principais")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Nível Médio do Rio", f"{filtered_df['Nível do Rio (m)'].mean():.2f}m")
with col2:
    st.metric("Último Nível Registrado", f"{filtered_df['Nível do Rio (m)'].iloc[-1]:.2f}m")
with col3:
    st.metric("Total de Registros", len(filtered_df))
with col4:
    st.metric("Número de Operadores", len(filtered_df["NOME"].unique()))
