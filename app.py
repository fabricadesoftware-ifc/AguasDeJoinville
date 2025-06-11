import streamlit as st

from src.layouts.default import layout
from src.router.index import router

st.set_page_config(
    page_title="Monitoramento Hidrológico", layout="wide", page_icon="🌊"
)


layout(router)  # carrega layout
