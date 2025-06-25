import streamlit as st
import traceback
from src.config.data import sheet_config
from src.utils.load_data import load_sheet_data
from src.views import Cubatao, Pirai

view_map = {
    "ETA Cubatão": Cubatao,
    "ETA Piraí": Pirai,
}  # dicionário que associa o nome da estação à view correspondente


def router(station, date_range, view_mode):
    config = sheet_config[station]
    view = view_map.get(station)  # obtém as configurações e a view correspondente

    try:
        with st.spinner("Carregando dados..."):
            df = load_sheet_data(config["SHEET_ID"], config["GID"])

        # garante que os dados não estejam vazios e que as colunas essenciais existam
        if df.empty:
            st.warning("Nenhum dado encontrado na planilha!")
            return

        required_cols = ["Carimbo de data/hora", "NOME", "Nível do Rio (m)"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colunas obrigatórias faltando: {', '.join(missing_cols)}")
            return

        # filtra os dados com base no intervalo selecionado no layout
        mask = df["Carimbo de data/hora"].dt.date.between(date_range[0], date_range[1])
        df_filtered = df.loc[mask]

        # Executa a view
        if view:
            view.main(df_filtered, date_range, view_mode)
        else:
            st.error(f"Página '{station}' não encontrada.")

    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.code(traceback.format_exc(), language="bash")
