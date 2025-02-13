import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import traceback
import requests
import io

st.set_page_config(
    page_title="Monitoramento Hidrológico",
    layout="wide",
    page_icon="🌊"
)

# Configurando o tema escuro globalmente
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stMetric {
            background-color: #262730;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

st.write("Versão do Streamlit:", st.__version__)

sheet_config = {
    "ETA Pirai": {
        "SHEET_ID": "13mElwgzhSr8ljUrIu_klMsO3rBLtzDF8fYt6aEOOnDg",
        "GID": "1698452995"
    },
    "ETA Cubatão": {
        "SHEET_ID": "1AUdMkuChcjdMmvQw_j_0z2MAgLhvfVeZZLZxnG9YETg",
        "GID": "487419985"
    }
}

@st.cache_data(ttl=6000)
def load_sheet_data(sheet_id, gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
        response = requests.get(url)
        response.raise_for_status() 
        df = pd.read_csv(io.StringIO(response.text))
        
        if 'Carimbo de data/hora' in df.columns:
            df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True)
            df['DATA'] = df['Carimbo de data/hora'].dt.date
            df['HORA'] = df['Carimbo de data/hora'].dt.strftime('%H:%M')
            df = df.sort_values(by='Carimbo de data/hora', ascending=True)

        if 'Nível do Rio (m)' in df.columns:
            df['Nível do Rio (m)'] = pd.to_numeric(df['Nível do Rio (m)'].astype(str).str.replace(',', '.'), errors='coerce')

        if 'Chuva (mm)' in df.columns:
            df['Chuva (mm)'] = pd.to_numeric(df['Chuva (mm)'].astype(str).str.replace(',', '.'), errors='coerce')

        return df

    except requests.RequestException as e:
        st.error(f"Erro ao acessar a planilha: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        st.code(traceback.format_exc(), language='bash')
        return pd.DataFrame()

def main():
    st.title("🌊 Monitoramento Hidrológico em Tempo Real")
    
    selected_station = st.sidebar.radio("Selecione a Estação", list(sheet_config.keys()))
    st.sidebar.write(f"Estação selecionada: **{selected_station}**")
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    config = sheet_config[selected_station]
    
    try:
        with st.spinner("Carregando dados..."):
            df = load_sheet_data(config["SHEET_ID"], config["GID"])
        
        if df.empty:
            st.warning("Nenhum dado encontrado na planilha!")
            return

        required_cols = ['Carimbo de data/hora', 'NOME', 'Nível do Rio (m)']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colunas obrigatórias faltando: {', '.join(missing_cols)}")
            return

        st.sidebar.header("🔍 Filtros")
        
        min_date = df['Carimbo de data/hora'].min().date()
        max_date = df['Carimbo de data/hora'].max().date()
        date_range = st.sidebar.date_input(
            "Período de análise:",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        operadores = st.sidebar.multiselect(
            "Operadores responsáveis:",
            options=sorted(df['NOME'].unique()),
            default=df['NOME'].unique()
        )
        
        view_mode = st.sidebar.selectbox(
            "Modo de Visualização do Gráfico Temporal", 
            ["Detalhado", "Agregado (média diária)"]
        )
        
        filtered_df = df[
            (df['Carimbo de data/hora'].dt.date >= date_range[0]) &
            (df['Carimbo de data/hora'].dt.date <= date_range[1]) &
            (df['NOME'].isin(operadores))
        ]
        
        if filtered_df.empty:
            st.warning("Nenhum registro encontrado com os filtros atuais!")
            return

        filtered_df = filtered_df.sort_values('Carimbo de data/hora', ascending=False)
        filtered_df_valid = filtered_df[filtered_df['Nível do Rio (m)'] != 0].copy()

        st.header("📊 Indicadores Principais")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nivel_medio = filtered_df_valid['Nível do Rio (m)'].mean()
            st.metric("Nível Médio", f"{nivel_medio:.2f} m")
        with col2:
            if not filtered_df_valid.empty:
                ultimo_nivel = filtered_df_valid.iloc[0]['Nível do Rio (m)']
                st.metric("Última Medição", f"{ultimo_nivel:.2f} m")
            else:
                st.metric("Última Medição", "Dados inconsistentes")
        with col3:
            st.metric("Total de Registros", len(filtered_df))
        with col4:
            st.metric("Operadores Ativos", len(filtered_df['NOME'].unique()))

        st.header("📈 Análise Temporal")

        # Time range selector
        time_range = st.radio(
            "Selecione o período de análise:",
            ["24 horas", "7 dias", "30 dias", "Personalizado"],
            horizontal=True
        )

        # Filter data based on time range
        current_time = pd.Timestamp.now()
        if time_range == "24 horas":
            time_filter = current_time - pd.Timedelta(days=1)
        elif time_range == "7 dias":
            time_filter = current_time - pd.Timedelta(days=7)
        elif time_range == "30 dias":
            time_filter = current_time - pd.Timedelta(days=30)
        else:
            time_filter = filtered_df_valid['Carimbo de data/hora'].min()

        filtered_df_valid = filtered_df_valid[filtered_df_valid['Carimbo de data/hora'] >= time_filter]

        if view_mode == "Agregado (média diária)":
            agg_df = filtered_df_valid.groupby(["DATA", "NOME"], as_index=False).agg({
                "Nível do Rio (m)": ["mean", "min", "max"]
            })
            agg_df.columns = ["DATA", "NOME", "media", "minimo", "maximo"]
            agg_df["Carimbo de data/hora"] = pd.to_datetime(agg_df["DATA"])
            plot_data = agg_df
            
            fig = px.line(
                plot_data,
                x='Carimbo de data/hora',
                y='media',
                title="Variação do Nível do Rio - Agregado (média diária)",
                labels={'media': 'Nível do Rio (m)', 'Carimbo de data/hora': 'Data'},
                hover_data={
                    'media': ':.2f',
                    'minimo': ':.2f',
                    'maximo': ':.2f',
                    'NOME': True
                }
            )
        else:
            plot_data = filtered_df_valid.copy()
            fig = px.line(
                plot_data,
                x='Carimbo de data/hora',
                y='Nível do Rio (m)',
                title="Variação do Nível do Rio (valores zero ignorados)",
                labels={'Carimbo de data/hora': 'Data/Hora'},
                hover_data={
                    'Nível do Rio (m)': ':.2f',
                    'NOME': True,
                    'HORA': True
                }
            )

        # Layout customization for dark theme
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(17, 17, 17, 0.8)',
            paper_bgcolor='rgba(17, 17, 17, 0.8)',
            font=dict(size=12),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(17, 17, 17, 0.5)'
            ),
            hovermode="x unified",
            transition_duration=500
        )

        fig.update_xaxes(
            rangeslider_visible=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            zeroline=True,
            zerolinecolor='rgba(128, 128, 128, 0.5)',
            zerolinewidth=1,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1a", step="year", stepmode="backward"),
                    dict(step="all", label="Tudo")
                ])
            )
        )

        fig.update_yaxes(
            gridcolor='rgba(128, 128, 128, 0.2)',
            zeroline=True,
            zerolinecolor='rgba(128, 128, 128, 0.5)',
            zerolinewidth=1
        )

        st.plotly_chart(fig, use_container_width=True)

        # Statistical summary
        st.subheader("📊 Estatísticas do Período")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Média do Período",
                f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'media'].mean():.2f} m"
            )
            
        with col2:
            st.metric(
                "Valor Máximo",
                f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'maximo'].max():.2f} m"
            )
            
        with col3:
            st.metric(
                "Valor Mínimo",
                f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'minimo'].min():.2f} m"
            )

        st.header("📌 Distribuição de Dados")
        col5, col6 = st.columns(2)
        
        with col5:
            if 'Assoreamento [Nova]' in filtered_df.columns:
                fig_pie = px.pie(
                    filtered_df,
                    names='Assoreamento [Nova]',
                    title="Status de Assoreamento"
                )
                fig_pie.update_layout(template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with col6:
            df_counts = filtered_df['NOME'].value_counts().reset_index()
            df_counts.columns = ['Operador', 'Registros']
            fig_bar = px.bar(
                df_counts,
                x='Operador',
                y='Registros',
                title="Atividades por Operador",
                labels={'Operador': 'Operador', 'Registros': 'Registros'}
            )
            fig_bar.update_layout(template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)

        st.header("📁 Dados Completos")
        st.dataframe(
            filtered_df.sort_values('Carimbo de data/hora', ascending=False),
            use_container_width=True,
            height=400
        )

    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.code(traceback.format_exc(), language='bash')

if __name__ == "__main__":
    main()