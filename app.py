import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Tenta usar o estilo 'seaborn-v0_8-darkgrid', se não conseguir, usa 'ggplot'
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    print("Estilo 'seaborn-darkgrid' não encontrado, usando estilo padrão.")
    plt.style.use('ggplot')

def parse_js_date(js_date_str):
    """
    Converte a string do formato JavaScript "Date(YYYY, M, D, H, M, S)"
    para um objeto datetime do Python. Lembre que os meses no JS começam em 0.
    """
    try:
        inside = js_date_str[js_date_str.find("(")+1: js_date_str.find(")")]
        parts = inside.split(',')
        year = int(parts[0])
        month = int(parts[1]) + 1  # Ajusta para que janeiro seja 1
        day = int(parts[2])
        hour = int(parts[3]) if len(parts) > 3 else 0
        minute = int(parts[4]) if len(parts) > 4 else 0
        second = int(parts[5]) if len(parts) > 5 else 0
        return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        return None

# Carrega os dados do arquivo JSON
with open('dados.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

dates = []
niveis = []

# Itera sobre as linhas, extraindo as datas e o nível do rio,
# ignorando registros com dados ausentes ou inválidos.
for row in data["table"]["rows"]:
    cells = row["c"]
    if cells[0] is not None and cells[4] is not None:
        js_date = cells[0]["v"]
        # Converte a data do formato JavaScript para datetime
        if isinstance(js_date, str) and js_date.startswith("Date("):
            date_val = parse_js_date(js_date)
        else:
            date_val = pd.to_datetime(js_date)
        if date_val is None:
            continue  # Pula linhas com data inválida
        nivel = cells[4]["v"]
        # Verifica se o nível do rio é numérico; caso contrário, ignora a linha
        if not isinstance(nivel, (int, float)):
            continue
        dates.append(date_val)
        niveis.append(nivel)

# Cria o DataFrame, ordena e descarta eventuais valores nulos
df = pd.DataFrame({'Data': dates, 'Nível_Rio': niveis})
df.sort_values('Data', inplace=True)
df = df.dropna(subset=['Nível_Rio'])

# Filtra registros onde o nível do rio é 0, assumindo que sejam dados inválidos
df = df[df['Nível_Rio'] != 0]

# Configura o gráfico com um tamanho maior e formatação de datas no eixo x
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df['Data'], df['Nível_Rio'], marker='o', linestyle='-', color='royalblue', markersize=4)

# Formata o eixo X para exibir as datas de forma legível
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
plt.xticks(rotation=45)

ax.set_title('Variação do Nível do Rio ao Longo do Tempo', fontsize=16, fontweight='bold')
ax.set_xlabel('Data', fontsize=14)
ax.set_ylabel('Nível do Rio (m)', fontsize=14)
plt.tight_layout()

plt.show()
