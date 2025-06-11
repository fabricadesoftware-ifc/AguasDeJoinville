import streamlit as st


def complete_data(sorted_df):
    st.header("📁 Dados Completos")
    st.dataframe(
        sorted_df, use_container_width=True, height=400
    )  # renderiza um DataFrame já ordenado por data e pré-processado, vindo de ./data_destribuition.py
