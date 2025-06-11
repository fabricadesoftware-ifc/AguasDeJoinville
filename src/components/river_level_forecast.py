import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet


def river_level_forecast(df):
    try:
        df["data"] = pd.to_datetime(
            df["Carimbo de data/hora"]
        )  # transforma os dados de data/hora para o formato datetime

        df_mensal = (
            df.resample("ME", on="data")["Nível do Rio (m)"].mean().reset_index()
        )  # agrupa os dados por mês e calcula a média mensal do nível do rio.

        df_prophet = df_mensal.rename(
            columns={"data": "ds", "Nível do Rio (m)": "y"}
        )  # ds == coluna de datas; y == níveis do rio que serão previstos

        model = Prophet()
        model.fit(df_prophet)  # cria e treina o modelo de previsão

        future = model.make_future_dataframe(
            periods=12, freq="ME"
        )  # gera um DataFrame com 12 meses à frente

        forecast = model.predict(future)
        forecast["yhat"] = forecast["yhat"].clip(lower=0).round(2)

        fig = go.Figure()  # cria gráfico
        fig.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=df_prophet["y"],
                mode="lines+markers",
                name="Dados Históricos",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast["ds"], y=forecast["yhat"], mode="lines", name="Previsão"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast["ds"],
                y=forecast["yhat_upper"],
                mode="lines",
                name="Limite Superior",
                line=dict(dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast["ds"],
                y=forecast["yhat_lower"],
                mode="lines",
                name="Limite Inferior",
                line=dict(dash="dash"),
            )
        )

        fig.update_layout(
            template="plotly_dark",
            title="Previsão de Nível do Rio",
            xaxis_title="Data",
            yaxis_title="Nível do Rio (m)",
            hovermode="x unified",
        )  # define o estilo, títulos, e interação do gráfico

        st.header("📈 Previsão de Nível do Rio")
        st.plotly_chart(fig)  # renderiza o gráfico

    except Exception as e:
        st.error(f"Erro ao gerar previsão de nível do rio: {str(e)}")
