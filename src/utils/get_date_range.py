import streamlit as st
from datetime import datetime, timedelta


def get_date_range_from_sidebar(df):
    time_options = [
        "Período personalizado",
        "Últimas 24 horas",
        "Últimos 7 dias",
        "Últimos 30 dias",
        "Último ano",
    ]

    selected_time_period = st.sidebar.radio(
        "Selecione o Período", time_options
    )  # escolhe um período via rádio button na barra lateral.

    min_date = df["Carimbo de data/hora"].min().date()
    max_date = df["Carimbo de data/hora"].max().date()
    current_date = (
        datetime.now().date()
    )  # garante que o calendário fique dentro dos limites reais dos dados

    predefined_periods = {
        "Últimas 24 horas": 1,
        "Últimos 7 dias": 7,
        "Últimos 30 dias": 30,
        "Último ano": 365,
    }  # dicionário com rótulos e o número de dias correspondentes

    if selected_time_period in predefined_periods:
        delta = predefined_periods[selected_time_period]
        start_date = current_date - timedelta(days=delta)
        end_date = current_date
        # se o usuário escolher um dos períodos fixos, calcula automaticamente o intervalo de datas

    else:
        start_date, end_date = st.sidebar.date_input(
            "Selecione o intervalo de datas",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )
        # quando seleciona "Período personalizado", o usuário escolhe as datas manualmente

    return start_date, end_date
