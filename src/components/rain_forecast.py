import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go


def rain_forecast(df):
    try:
        df["data"] = pd.to_datetime(
            df["Carimbo de data/hora"]
        )  # cria uma nova coluna "data" convertida para o formato datetime

        df_mensal = (
            df.resample("ME", on="data")["Chuva (mm)"].sum().reset_index()
        )  # soma todas as chuvas do mês

        df_prophet = df_mensal.rename(
            columns={"data": "ds", "Chuva (mm)": "y"}
        )  # ds == datas; y == valores numéricos (chuva)

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
            title="Previsão de Chuva",
            xaxis_title="Data",
            yaxis_title="Chuva (mm)",
            hovermode="x unified",
        )  # define o estilo, títulos, e interação do gráfico

        st.header("📈 Previsão de Chuva")
        st.plotly_chart(fig, use_container_width=True)  # renderiza o gráfico

    except:
        st.error("Erro ao gerar previsão de chuva")
