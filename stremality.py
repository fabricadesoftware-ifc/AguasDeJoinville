import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import traceback

# Configuração da página
st.set_page_config(
    page_title="Monitoramento Hidrológico",
    layout="wide",
    page_icon="🌊"
)

@st.cache_data
def load_and_process_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validação da estrutura do JSON
        if 'table' not in data or 'cols' not in data['table'] or 'rows' not in data['table']:
            raise ValueError("Estrutura JSON inválida - formato esperado não encontrado")

        # Mapeamento de tipos
        type_map = {
            'datetime': 'datetime',
            'date': 'date',
            'number': 'float64',
            'string': 'object'
        }

        # Processar metadados das colunas
        cols_meta = []
        for col in data['table']['cols']:
            cols_meta.append({
                'id': col['id'],
                'label': col['label'],
                'type': col['type'],
                'dtype': type_map.get(col['type'], 'object')
            })

        # Processar linhas
        processed_rows = []
        for row in data['table']['rows']:
            processed_row = {}
            for i, cell in enumerate(row['c']):
                col_info = cols_meta[i]
                value = cell['v'] if cell and 'v' in cell else None

                # Conversão de datas
                if value and isinstance(value, str) and 'Date(' in value:
                    try:
                        date_str = value.replace('Date(', '').replace(')', '')
                        parts = list(map(int, date_str.split(',')))
                        
                        # Ajustar meses zero-based (correção principal)
                        if len(parts) >= 2:
                            parts[1] += 1  # Janeiro=0 → 1
                        
                        if col_info['type'] == 'datetime':
                            dt_params = parts[:6] if len(parts) >= 6 else parts[:3] + [0]*3
                            value = datetime(*dt_params)
                        elif col_info['type'] == 'date':
                            value = datetime(*parts[:3])
                    except Exception as e:
                        st.error(f"Erro na conversão de data: {value}")
                        value = None
                
                processed_row[col_info['label']] = value
            
            processed_rows.append(processed_row)

        df = pd.DataFrame(processed_rows)

        # Converter tipos de dados
        for col in cols_meta:
            if col['dtype'] == 'datetime':
                df[col['label']] = pd.to_datetime(df[col['label']])
            elif col['dtype'] in ['float64', 'int64']:
                df[col['label']] = pd.to_numeric(df[col['label']], errors='coerce')

        # Pós-processamento
        if 'Carimbo de data/hora' in df.columns:
            df = df.sort_values('Carimbo de data/hora', ascending=False)
            df['Data'] = df['Carimbo de data/hora'].dt.date
            df['Hora'] = df['Carimbo de data/hora'].dt.strftime('%H:%M')
            df = df.dropna(subset=['Carimbo de data/hora'])

        return df

    except json.JSONDecodeError:
        st.error("Erro na leitura do arquivo JSON - verifique a formatação")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro crítico: {str(e)}")
        st.code(traceback.format_exc(), language='bash')
        return pd.DataFrame()

def main():
    st.title("🌊 Monitoramento Hidrológico em Tempo Real")
    
    try:
        df = load_and_process_data('dados.json')
        
        if df.empty:
            st.warning("Nenhum dado encontrado no arquivo!")
            return

        # Validação de colunas essenciais
        required_cols = ['Carimbo de data/hora', 'NOME', 'Nível do Rio (m)']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colunas obrigatórias faltando: {', '.join(missing_cols)}")
            return

        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        
        # Seletor de datas
        min_date = df['Carimbo de data/hora'].min().date()
        max_date = df['Carimbo de data/hora'].max().date()
        date_range = st.sidebar.date_input(
            "Período de análise:",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Seletor de operadores
        operadores = st.sidebar.multiselect(
            "Operadores responsáveis:",
            options=df['NOME'].unique(),
            default=df['NOME'].unique()
        )
        
        # Aplicar filtros
        filtered_df = df[
            (df['Carimbo de data/hora'].dt.date >= date_range[0]) &
            (df['Carimbo de data/hora'].dt.date <= date_range[1]) &
            (df['NOME'].isin(operadores))
        ]
        
        if filtered_df.empty:
            st.warning("Nenhum registro encontrado com os filtros atuais!")
            return

        # Métricas
        st.header("📊 Indicadores Principais")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nivel_medio = filtered_df['Nível do Rio (m)'].mean()
            st.metric("Nível Médio", f"{nivel_medio:.2f}m")
        with col2:
            ultimo_nivel = filtered_df.iloc[0]['Nível do Rio (m)']
            st.metric("Última Medição", f"{ultimo_nivel:.2f}m")
        with col3:
            st.metric("Total de Registros", len(filtered_df))
        with col4:
            st.metric("Operadores Ativos", len(filtered_df['NOME'].unique()))

        # Visualizações
        st.header("📈 Análise Temporal")
        fig = px.line(filtered_df, 
                     x='Carimbo de data/hora', 
                     y='Nível do Rio (m)',
                     title="Variação do Nível do Rio",
                     markers=True)
        fig.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(fig, use_container_width=True)

        st.header("📌 Distribuição de Dados")
        col5, col6 = st.columns(2)
        
        with col5:
            fig = px.pie(filtered_df, 
                        names='Assoreamento [Nova]',
                        title="Status de Assoreamento")
            st.plotly_chart(fig, use_container_width=True)
            
        with col6:
            fig = px.bar(filtered_df['NOME'].value_counts(), 
                        title="Atividades por Operador",
                        labels={'value': 'Registros', 'index': 'Operador'})
            st.plotly_chart(fig, use_container_width=True)

        # Dados brutos
        st.header("📁 Dados Completos")
        st.dataframe(
            filtered_df.sort_values('Carimbo de data/hora', ascending=False),
            use_container_width=True,
            height=400
        )

    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.code(traceback.format_exc(), language='bash')

if __name__ == "__main__":
    main()