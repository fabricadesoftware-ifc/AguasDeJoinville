import streamlit as st


def load_css(file_name):  # função para carregar o CSS
    with open(file_name) as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def mes_ano_extenso(mes, ano):  # função para retornar a data escrita por extenso
    meses = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    return f"{ano}-{meses[mes - 1]}"
