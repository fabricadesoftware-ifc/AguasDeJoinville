import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def filter_data(df, time_filter):
    return df[
        df["Carimbo de data/hora"] >= time_filter
    ]  # filtra o DataFrame para conter apenas dados a partir de uma data mínima


def plot_daily_aggregation(df):
    agg_df = df.groupby("DATA", as_index=False).agg(
        {"Nível do Rio (m)": ["mean", "min", "max"]}
    )  # agrupa os dados por DATA

    agg_df.columns = [
        "DATA",
        "media",
        "minimo",
        "maximo",
    ]  # calcula a média, mínimo e máximo do nível do rio

    agg_df["Carimbo de data/hora"] = pd.to_datetime(
        agg_df["DATA"], format="%d/%m/%Y"
    )  # converte a coluna DATA para datetime para ordenação correta

    agg_df = agg_df.sort_values("Carimbo de data/hora")

    fig = px.line(
        agg_df,
        x="Carimbo de data/hora",
        y="media",
        title="Variação do Nível do Rio - Agregado (média diária)",
        labels={"media": "Nível do Rio (m)", "Carimbo de data/hora": "Data"},
        hover_data={"media": ":.2f", "minimo": ":.2f", "maximo": ":.2f"},
    )  # cria um gráfico de linha
    return fig


def plot_line(df, title="Variação do Nível do Rio (valores zero ignorados)"):
    fig = px.line(
        df,
        x="Carimbo de data/hora",
        y="Nível do Rio (m)",
        title=title,
        labels={"Carimbo de data/hora": "Data/Hora"},
        hover_data={"Nível do Rio (m)": ":.2f", "NOME": True, "HORA": True},
    )  # exibe os dados do nível do rio em tempo real

    fig.update_layout(template="plotly_dark")
    return fig


def plot_combined(df):
    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )  # cria um gráfico com dois eixos y:

    fig.add_trace(
        go.Scatter(
            x=df["Carimbo de data/hora"],
            y=df["Nível do Rio (m)"],
            mode="lines",
            name="Nível do Rio (m)",
            hovertemplate="Data: %{x}<br>Nível: %{y:.2f} m",
        ),
        secondary_y=False,
    )  # eixo principal: Nível do rio
    fig.add_trace(
        go.Scatter(
            x=df["Carimbo de data/hora"],
            y=df["Chuva (mm)"],
            mode="lines",
            name="Chuva (mm)",
            hovertemplate="Data: %{x}<br>Chuva: %{y:.2f} mm",
        ),
        secondary_y=True,
    )  # eixo secundário: Chuva

    fig.update_layout(
        title="Variação do Nível do Rio e Chuva",
        template="plotly_dark",
        plot_bgcolor="rgba(17, 17, 17, 0.8)",
        paper_bgcolor="rgba(17, 17, 17, 0.8)",
        font=dict(size=12),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(17, 17, 17, 0.5)",
        ),
        hovermode="x unified",
        transition_duration=500,
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
        zeroline=True,
        zerolinecolor="rgba(128, 128, 128, 0.5)",
        zerolinewidth=1,
    )
    fig.update_yaxes(
        gridcolor="rgba(128, 128, 128, 0.2)",
        zeroline=True,
        zerolinecolor="rgba(128, 128, 128, 0.5)",
        zerolinewidth=1,
        title_text="Nível do Rio (m)",
        secondary_y=False,
    )
    fig.update_yaxes(
        gridcolor="rgba(128, 128, 128, 0.2)",
        zeroline=True,
        zerolinecolor="rgba(128, 128, 128, 0.5)",
        zerolinewidth=1,
        title_text="Chuva (mm)",
        secondary_y=True,
    )
    return fig


def analise_temporal_section(df, view_mode):
    st.header("📈 Análise Temporal")

    time_filter = df["Carimbo de data/hora"].min()  # define o filtro de tempo
    filtered_df_valid = filter_data(df, time_filter)  # filtra os dados

    if view_mode == "Agregado (média diária)":
        agg_df = filtered_df_valid.groupby("DATA", as_index=False).agg(
            {"Nível do Rio (m)": ["mean", "min", "max"]}
        )
        agg_df.columns = ["DATA", "media", "minimo", "maximo"]
        agg_df["Carimbo de data/hora"] = pd.to_datetime(
            agg_df["DATA"], format="%d/%m/%Y"
        )
        agg_df = agg_df.sort_values("Carimbo de data/hora")
        plot_data = agg_df.copy()

        fig = px.line(
            plot_data,
            x="Carimbo de data/hora",
            y="media",
            title="Variação do Nível do Rio - Agregado (média diária)",
            labels={"media": "Nível do Rio (m)", "Carimbo de data/hora": "Data"},
            hover_data={"media": ":.2f", "minimo": ":.2f", "maximo": ":.2f"},
        )  # agrupa os dados por DATA, calcula estatísticas e plota

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
                    hovertemplate="Data: %{x}<br>Nível: %{y:.2f} m",
                ),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=plot_data["Carimbo de data/hora"],
                    y=plot_data["Chuva (mm)"],
                    mode="lines",
                    name="Chuva (mm)",
                    hovertemplate="Data: %{x}<br>Chuva: %{y:.2f} mm",
                ),
                secondary_y=True,
            )

            fig.update_layout(
                title="Variação do Nível do Rio e Chuva",
                template="plotly_dark",
                plot_bgcolor="rgba(17, 17, 17, 0.8)",
                paper_bgcolor="rgba(17, 17, 17, 0.8)",
                font=dict(size=12),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    bgcolor="rgba(17, 17, 17, 0.5)",
                ),
                hovermode="x unified",
                transition_duration=500,
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                gridcolor="rgba(128, 128, 128, 0.2)",
                zeroline=True,
                zerolinecolor="rgba(128, 128, 128, 0.5)",
                zerolinewidth=1,
            )
            fig.update_yaxes(
                gridcolor="rgba(128, 128, 128, 0.2)",
                zeroline=True,
                zerolinecolor="rgba(128, 128, 128, 0.5)",
                zerolinewidth=1,
                title_text="Nível do Rio (m)",
                secondary_y=False,
            )
            fig.update_yaxes(
                gridcolor="rgba(128, 128, 128, 0.2)",
                zeroline=True,
                zerolinecolor="rgba(128, 128, 128, 0.5)",
                zerolinewidth=1,
                title_text="Chuva (mm)",
                secondary_y=True,
            )  # usa plot_combined() com dois eixos y

        else:
            fig = px.line(
                plot_data,
                x="Carimbo de data/hora",
                y="Nível do Rio (m)",
                title="Variação do Nível do Rio (valores zero ignorados)",
                labels={"Carimbo de data/hora": "Data/Hora"},
                hover_data={"Nível do Rio (m)": ":.2f", "NOME": True, "HORA": True},
            )
            fig.update_layout(template="plotly_dark")  # plota apenas o nível do rio

    st.plotly_chart(fig, use_container_width=True)
    return plot_data
