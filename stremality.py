import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from functions import mes_ano_extenso, nome_mes_ano
from datetime import datetime
import traceback
import requests
import io

st.set_page_config(
    page_title="Monitoramento Hidrológico",
    layout="wide",
    page_icon="🌊"
)

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
        .custom-text{
            top: 10px;
            color: rgb(136, 136, 136); 
            font-size: 1em !important; 
            position: absolute; 
            right: 0px; 
            bottom: -2em;
            z-index: 1;
        }
        .custom-text a{
            color: #00BFFF;
            text-decoration: none;
            font-size: 0.9em;
        }
        .version{
            position: absolute;
            bottom: 0;
            color: #FFFFFF;
            opacity: 0.4;
        }
    </style>
    <script>
            console.log("Desenvolvido por: Fabrica De Software");
    </script>
""", unsafe_allow_html=True)

st.markdown("""
            <p class="version"> Versão 1.0.0 </p>
            """ , unsafe_allow_html=True)

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
            # Converte usando dayfirst=True, pois as datas estão no formato DD/MM/YYYY
            df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True)
            df['DATA'] = df['Carimbo de data/hora'].dt.strftime('%d/%m/%Y')
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

        time_options = ["Período personalizado", "Últimas 24 horas", "Últimos 7 dias", "Últimos 30 dias", "Ultimo Ano"]
        selected_time_period = st.sidebar.radio("Selecione o Perído", time_options)

        min_date = df['Carimbo de data/hora'].min().date()
        max_date = df['Carimbo de data/hora'].max().date()
        current_date = datetime.now().date()

        if selected_time_period == "Últimas 24 horas":
            start_date = (datetime.now() - pd.Timedelta(days=1)).date()
            end_date = current_date
            date_range = [start_date, end_date]
        elif selected_time_period == "Últimos 7 dias":
            start_date = (datetime.now() - pd.Timedelta(days=7)).date()
            end_date = current_date
            date_range = [start_date, end_date]
        elif selected_time_period == "Últimos 30 dias":
            start_date = (datetime.now() - pd.Timedelta(days=30)).date()
            end_date = current_date
            date_range = [start_date, end_date]
        elif selected_time_period == "Ultimo Ano":
            start_date = (datetime.now() - pd.Timedelta(days=365)).date()
            end_date = current_date
            date_range = [start_date, end_date]
        else:
            date_range = st.sidebar.date_input(
                "Selecione as datas",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = min_date
            end_date = max_date
            date_range = [start_date, end_date]

        st.sidebar.write(f"Período: de {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
        
        view_mode = st.sidebar.selectbox(
            "Modo de Visualização do Gráfico Temporal", 
            ["Detalhado", "Agregado (média diária)"]
        )
        
        filtered_df = df[
            (df['Carimbo de data/hora'].dt.date >= date_range[0]) &
            (df['Carimbo de data/hora'].dt.date <= date_range[1])
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

        st.markdown("""
        <p class="custom-text">Desenvolvido por: <a href="https://fabricadesoftware.ifc.edu.br/" target="_blank">Fabrica De Software</a> <br/> Professor Responsável: <a href="https://github.com/ldmfabio" target="_blank">Fábio Longo De Moura</a> <br/> Alunos: <a href="https://github.com/jonatasperaza" target="_blank">Jonatas Peraza</a></p>
    """, unsafe_allow_html=True)

        st.header("📈 Análise Temporal")

        current_time = pd.Timestamp.now()
        time_filter = filtered_df_valid['Carimbo de data/hora'].min()
        filtered_df_valid = filtered_df_valid[filtered_df_valid['Carimbo de data/hora'] >= time_filter]

        if view_mode == "Agregado (média diária)":
            # Em vez de agrupar por ["DATA", "NOME"], faça apenas:
            agg_df = filtered_df_valid.groupby("DATA", as_index=False).agg({
                "Nível do Rio (m)": ["mean", "min", "max"]
            })
            agg_df.columns = ["DATA", "media", "minimo", "maximo"]

            # Converter a coluna DATA para datetime no formato DD/MM/YYYY
            agg_df["Carimbo de data/hora"] = pd.to_datetime(agg_df["DATA"], format='%d/%m/%Y')

            # Ordenar por data para não “pular” pontos
            agg_df = agg_df.sort_values("Carimbo de data/hora")

            plot_data= agg_df.copy()

            fig = px.line(
                agg_df,
                x='Carimbo de data/hora',
                y='media',
                title="Variação do Nível do Rio - Agregado (média diária)",
                labels={'media': 'Nível do Rio (m)', 'Carimbo de data/hora': 'Data'},
                hover_data={
                    'media': ':.2f',
                    'minimo': ':.2f',
                    'maximo': ':.2f'
                }
            )
        else:
            plot_data = filtered_df_valid.copy()
            if "Chuva (mm)" in plot_data.columns:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Scatter(
                        x=plot_data["Carimbo de data/hora"],
                        y=plot_data["Nível do Rio (m)"],
                        mode="lines",
                        name="Nível do Rio (m)",
                        hovertemplate="Data: %{x}<br>Nível: %{y:.2f} m"
                    ),
                    secondary_y=False
                )
                fig.add_trace(
                    go.Scatter(
                        x=plot_data["Carimbo de data/hora"],
                        y=plot_data["Chuva (mm)"],
                        mode="lines",
                        name="Chuva (mm)",
                        hovertemplate="Data: %{x}<br>Chuva: %{y:.2f} mm"
                    ),
                    secondary_y=True
                )
                fig.update_layout(
                    title="Variação do Nível do Rio e Chuva",
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
                    zerolinewidth=1
                )
                fig.update_yaxes(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    zeroline=True,
                    zerolinecolor='rgba(128, 128, 128, 0.5)',
                    zerolinewidth=1,
                    title_text="Nível do Rio (m)",
                    secondary_y=False
                )
                fig.update_yaxes(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    zeroline=True,
                    zerolinecolor='rgba(128, 128, 128, 0.5)',
                    zerolinewidth=1,
                    title_text="Chuva (mm)",
                    secondary_y=True
                )
            else:
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
                fig.update_layout(template="plotly_dark")
        
        st.plotly_chart(fig, use_container_width=True)

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
            elif 'Captação [Gradeamento]' in filtered_df.columns:
                fig_pie = px.pie(
                    filtered_df,
                    names='Captação [Gradeamento]',
                    title="Status de Captação"
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

        filtered_df = df.drop(columns=['Carimbo de data/hora'], errors='ignore', inplace=False)

        filtered_df['DATA_ORDENACAO'] = pd.to_datetime(filtered_df['DATA'], format='%d/%m/%Y')
        sorted_df = filtered_df.sort_values(by='DATA_ORDENACAO', ascending=False)
        sorted_df['DATA'] = sorted_df['DATA_ORDENACAO'].dt.strftime('%d/%m/%Y')
        sorted_df = sorted_df.drop(columns=['DATA_ORDENACAO'])
        if 'Carimbo de data/hora' in df.columns:
            sorted_df['MES_ANO'] = df.apply(lambda row: mes_ano_extenso(row['Carimbo de data/hora'].month, row['Carimbo de data/hora'].year), axis=1)
        sorted_df = sorted_df

        df_mm_mes = sorted_df.groupby(['MES_ANO'])['Chuva (mm)'].sum()

        fig = px.bar(
                df_mm_mes,
                x=df_mm_mes.index,
                y='Chuva (mm)',
                title="Chuva por Mês",
                labels={'x': 'Mês/Ano', 'y': 'Chuva (mm)'}
            )
        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(
                tickangle=-90,
                title='Meses'
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.header("📁 Dados Completos")
        st.dataframe(
            sorted_df,
            use_container_width=True,
            height=400
        )

    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.code(traceback.format_exc(), language='bash')

if __name__ == "__main__":
    main()
