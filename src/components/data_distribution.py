import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.utils import mes_ano_extenso


def data_distribution(filtered_df, df):
    st.header("📌 Distribuição de Dados")

    col5, col6 = st.columns(2)

    # renderiza o gráfico de pizza
    with col5:
        if (
            "Assoreamento [Nova]" in filtered_df.columns
        ):  # se filtered_df possui a coluna "Assoreamento [Nova]", exibe um gráfico de pizza com os valores dessa coluna
            fig_pie = px.pie(
                filtered_df,
                names="Assoreamento [Nova]",
                title="Status de Assoreamento",
            )
            fig_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

        elif (
            "Captação [Gradeamento]" in filtered_df.columns
        ):  # se não, mas existe "Captação [Gradeamento]", mostra a pizza com base nela.
            fig_pie = px.pie(
                filtered_df,
                names="Captação [Gradeamento]",
                title="Status de Captação",
            )
            fig_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

    with col6:
        # renderiza o gráfico de barras de chuvas por mês

        filtered_df = df.drop(
            columns=["Carimbo de data/hora"], errors="ignore", inplace=False
        )  # remove a coluna "Carimbo de data/hora" se ela existir (opcional)

        filtered_df["DATA_ORDENACAO"] = pd.to_datetime(
            filtered_df["DATA"], format="%d/%m/%Y"
        )
        sorted_df = filtered_df.sort_values(
            by="DATA_ORDENACAO", ascending=False
        )  # converte a coluna "DATA" para o tipo datetime e ordena em ordem decrescente

        sorted_df["DATA"] = sorted_df["DATA_ORDENACAO"].dt.strftime("%d/%m/%Y")
        sorted_df = sorted_df.drop(
            columns=["DATA_ORDENACAO"]
        )  # formata novamente a coluna "DATA" como string e remove a coluna temporária usada para ordenação

        if "Carimbo de data/hora" in df.columns:
            sorted_df["MES_ANO"] = df.apply(
                lambda row: mes_ano_extenso(
                    row["Carimbo de data/hora"].month, row["Carimbo de data/hora"].year
                ),
                axis=1,
            )  # se o df original tem a coluna "Carimbo de data/hora", cria a coluna MES_ANO com o mês e ano por extenso

        df_mm_mes = sorted_df.groupby(["MES_ANO"])[
            "Chuva (mm)"
        ].sum()  # agrupa os dados por MES_ANO e soma os valores de "Chuva (mm)"

        fig = px.bar(
            df_mm_mes,
            x=df_mm_mes.index,
            y="Chuva (mm)",
            title="Chuva por Mês",
            labels={"x": "Mês/Ano", "y": "Chuva (mm)"},
        )  # cria um gráfico de barras mostrando a precipitação total de cada mês.

        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(tickangle=-90, title="Meses"),
        )

        st.plotly_chart(fig)

    return sorted_df
