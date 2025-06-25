import streamlit as st


def layout(content):
    st.markdown(
        '<p class="version"> Versão 1.0.0 </p>',
        unsafe_allow_html=True,
    )
    st.title("🌊 Monitoramento Hidrológico em Tempo Real")

    with st.sidebar:
        from src.config.data import sheet_config

        station = st.radio(
            "Selecione a Estação", list(sheet_config.keys())
        )  # cria um botão de seleção de estação

        config = sheet_config[
            station
        ]  # obtém as configurações correspondentes à estação escolhida

        from src.utils.load_data import load_sheet_data
        from src.utils.get_date_range import get_date_range_from_sidebar

        df = load_sheet_data(
            config["SHEET_ID"], config["GID"]
        )  # arrega os dados da planilha selecionada

        start, end = get_date_range_from_sidebar(
            df
        )  # obtém o intervalo de datas baseado nos dados carregados

        st.write(
            f"Período: de {start.strftime('%d/%m/%Y')} até {end.strftime('%d/%m/%Y')}"
        )

        date_range = [start, end]

        view_mode = st.sidebar.selectbox(
            "Modo de Visualização do Gráfico Temporal",
            ["Detalhado", "Agregado (média diária)"],
        )  # permite escolher entre um gráfico detalhado ou agregado

    with st.container():
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()  # limpa o cache dos dados e recarrega a página

    content(station, date_range, view_mode)
