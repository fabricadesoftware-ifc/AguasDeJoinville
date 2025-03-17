def mes_ano_extenso(mes, ano):
    meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    return f'{ano}-{meses[mes - 1]}'

def nome_mes_ano(mes_ano):
    ano = mes_ano[:4]
    mes = int(mes_ano[5:])
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    return f'{meses[mes - 1]} de {ano}'