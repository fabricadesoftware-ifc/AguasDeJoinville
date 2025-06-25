import streamlit as st

from src.utils.utils import load_css
from src.layouts.default import layout
from src.router.index import router

st.set_page_config(
    page_title="Monitoramento Hidrológico", layout="wide", page_icon="🌊"
)

load_css("src/assets/main.css")  # carrega css

layout(router)  # carrega layout
