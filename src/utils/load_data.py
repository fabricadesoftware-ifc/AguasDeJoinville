import streamlit as st
import pandas as pd
import traceback
import requests
import io


@st.cache_data(ttl=3600)  # a função é armazenada em cache por 1 hora
def load_sheet_data(sheet_id, gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(
            io.BytesIO(response.content), encoding="utf-8"
        )  # faz download direto da planilha como CSV e lê

        if "Carimbo de data/hora" in df.columns:
            df["Carimbo de data/hora"] = pd.to_datetime(
                df["Carimbo de data/hora"], dayfirst=True
            )
            df["DATA"] = df["Carimbo de data/hora"].dt.strftime("%d/%m/%Y")
            df["HORA"] = df["Carimbo de data/hora"].dt.strftime("%H:%M")
            df = df.sort_values(by="Carimbo de data/hora", ascending=True)
            # converte a coluna de carimbo de data/hora, extrai as colunas auxiliares DATA e HORA e ordena os dados pela data

        if "Nível do Rio (m)" in df.columns:
            df["Nível do Rio (m)"] = df["Nível do Rio (m)"].str.replace(
                "m", ""
            )  # Remover "m"
            df["Nível do Rio (m)"] = pd.to_numeric(
                df["Nível do Rio (m)"].str.replace(",", "."), errors="coerce"
            )  # Convertendo para numérico

        if "Chuva (mm)" in df.columns:
            df["Chuva (mm)"] = df["Chuva (mm)"].str.replace("mm", "")  # Remover "mm"
            df["Chuva (mm)"] = pd.to_numeric(
                df["Chuva (mm)"].astype(str).str.replace(",", "."), errors="coerce"
            )

        return df

    except requests.RequestException as e:
        st.error(f"Erro ao acessar a planilha: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
        st.code(traceback.format_exc(), language="bash")

    return pd.DataFrame()
