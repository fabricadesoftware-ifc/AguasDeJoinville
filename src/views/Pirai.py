from src.components.main_indicators import main_indicators
from src.components.temporal_analysis import analise_temporal_section
from src.components.period_statistics import period_statistics
from src.components.data_distribution import data_distribution
from src.components.rain_forecast import rain_forecast
from src.components.river_level_forecast import river_level_forecast
from src.components.complete_data import complete_data


def main(df, date_range, view_mode):
    main_indicators(df, date_range)
    filtered_df = df[
        (df["Carimbo de data/hora"].dt.date >= date_range[0])
        & (df["Carimbo de data/hora"].dt.date <= date_range[1])
    ]
    filtered_df = filtered_df.sort_values(
        "Carimbo de data/hora", ascending=False
    )  # filtra os dados conforme o período selecionado e ordena os dados da data mais recente para a mais antigas

    filtered_df_valid = filtered_df[
        filtered_df["Nível do Rio (m)"] != 0
    ].copy()  # garante que apenas leituras válidas do nível do rio sejam analisadas

    filtered_df_valid["DATA"] = filtered_df_valid["Carimbo de data/hora"].dt.strftime(
        "%d/%m/%Y"
    )  # necessária para agrupamento diário quando o modo for “Agregado”

    plot_data = analise_temporal_section(filtered_df_valid, view_mode)
    period_statistics(plot_data, view_mode)
    sorted_df = data_distribution(filtered_df, df)
    rain_forecast(df)
    river_level_forecast(df)
    sorted_df = sorted_df.drop(columns=["NOME"], errors="ignore")
    complete_data(sorted_df)
