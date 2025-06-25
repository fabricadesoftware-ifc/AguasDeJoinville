import streamlit as st


def main_indicators(df, date_range):
    st.header("📊 Indicadores Principais")

    filtered_df = df[
        (df["Carimbo de data/hora"].dt.date >= date_range[0])
        & (df["Carimbo de data/hora"].dt.date <= date_range[1])
    ]  # filtra os dados de acordo com o intervalo date_range, usando a coluna "Carimbo de data/hora" (convertida para date),garantindo que os indicadores se refiram apenas ao período selecionado

    if filtered_df.empty:
        st.warning("Nenhum registro encontrado com os filtros atuais!")
        return  # se o DataFrame estiver vazio após o filtro, uma mensagem de aviso é exibida, e a função termina

    filtered_df = filtered_df.sort_values("Carimbo de data/hora", ascending=False)
    filtered_df_valid = filtered_df[
        filtered_df["Nível do Rio (m)"] != 0
    ].copy()  # os dados são ordenados da mais recente para a mais antiga e remove medições onde o nível do rio está zerado (possivelmente inconsistentes)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        nivel_medio = filtered_df_valid["Nível do Rio (m)"].mean()
        st.metric(
            "Nível Médio", f"{nivel_medio:.2f} m"
        )  # calcula a média do nível do rio (ignorando valores nulos ou zero)

    with col2:
        if not filtered_df_valid.empty:
            ultimo_nivel = filtered_df_valid.iloc[0]["Nível do Rio (m)"]
            st.metric(
                "Última Medição", f"{ultimo_nivel:.2f} m"
            )  # exibe o último valor válido do nível do rio
        else:
            st.metric(
                "Última Medição", "Dados inconsistentes"
            )  # se não houver valores válidos, exibe mensagem de inconsistência

    with col3:
        st.metric(
            "Total de Registros", len(filtered_df)
        )  # exibe a quantidade total de linhas do DataFrame filtrado, inclusive com níveis zero

    with col4:
        st.metric(
            "Operadores Ativos", len(filtered_df["NOME"].unique())
        )  # conta e exibe quantos operadores participaram no período selecionado

    st.markdown(
        """<p class="custom-text">
            Desenvolvido por: <a href="https://fabricadesoftware.ifc.edu.br/" target="_blank">Fabrica De Software</a> <br/> Professor Responsável: <a href="https://github.com/ldmfabio" target="_blank">Fábio Longo De Moura</a> <br/>
            Alunos: <a href="https://github.com/jonatasperaza" target="_blank">Jonatas Peraza</a>, <a href="https://github.com/nicolefemello" target="_blank">Nicole Ferreira Mello</a></p>""",
        unsafe_allow_html=True,
    )
