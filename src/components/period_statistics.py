import streamlit as st


def period_statistics(plot_data, view_mode):
    st.subheader("📊 Estatísticas do Período")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Média do Período",
            f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'media'].mean():.2f} m",
        )  # se o modo de visualização não for "Agregado", usa a coluna "Nível do Rio (m)", mas se for "Agregado", usa a coluna "media"
    with col2:
        st.metric(
            "Valor Máximo",
            f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'maximo'].max():.2f} m",
        )  # se o modo de visualização for "Agregado", usa a coluna "maximo"
    with col3:
        st.metric(
            "Valor Mínimo",
            f"{plot_data['Nível do Rio (m)' if view_mode != 'Agregado (média diária)' else 'minimo'].min():.2f} m",
        )  # se o modo de visualização for "Agregado", usa a coluna "minimo"
