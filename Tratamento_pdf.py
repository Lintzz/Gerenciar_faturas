import re
from PyPDF2 import PdfReader
import csv

from config import STORAGE_DIR

txt_pagina = STORAGE_DIR / 'pagina.txt'
csv_formatado = STORAGE_DIR / 'formatado.csv'
csv_formatado_limpo = STORAGE_DIR / 'formatado_limpo.csv'


substituicoes = {
    "Pagamento em 13 MAR −": "Pagamento",
    "Netflix.Com": "Netflix",
    "Cyber Cell Celulares": "Cyber Cell Celulares",
    "Picpay*Mario Campos": "PicPay - Mario Campos",
    "Cluberotas": "Clube Rotas",
    "99app *99app": "99 App",
    "Google Sim Dashboard": "Google Sim Dashboard",
    "Saldo restante da fatura anterior": "Saldo Fatura Anterior",
    "Mp *Hbomaxassin": "HBO Max",
    "Mp *Melimais": "Meli+",
    "Amanda Cristina Vieira - Parcela 1/4": "Dentista",
    "Amazonmktplc*Fabiosant - Parcela 1/10": "Amazon (1/10)",
    "Ebn *Crunchyroll": "Crunchyroll",
    "Pipocas Kennedy": "Pipocas Kennedy",
    "Dm*Spotify": "Spotify",
    "Amazonprimebr": "Amazon Prime",
    "Tim*12982375701": "Tim*12982375701",
    "Servicos Cla*129914457": "Cla*129914457",
    "Google Youtubepremium": "YouTube Premium"
}

categorias = {
    "Pagamento": "pagamento",
    "Netflix": "Assinaturas",
    "Cyber Cell Celulares": "Compras",
    "PicPay - Mario Campos": "Compras",
    "Clube Rotas": "Assinaturas",
    "99 App": "Transporte",
    "Google Sim Dashboard": "Compras",
    "Saldo Fatura Anterior": "pagamento",
    "HBO Max": "Assinaturas",
    "Meli+": "Assinaturas",
    "Dentista": "Saúde",
    "Amazon (1/10)": "Compras",
    "Crunchyroll": "Assinaturas",
    "Pipocas Kennedy": "Alimentação",
    "Amazon Prime": "Assinaturas",
    "Tim*12982375701": "Celular",
    "Cla*129914457": "Celular",
    "YouTube Premium": "Assinaturas",
    "Spotify": "Assinaturas",
    "iFood": "Alimentação",
    "Outro": "Outro"
}

def extrair_texto_pdf(pdf_path, txt_path=txt_pagina):
    text= ''
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)

        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]

            text += page.extract_text()
            
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

def organizar_fatura(txt_path=txt_pagina, csv_path=csv_formatado):
    with open(txt_path, 'r', encoding='utf-8') as f:
        texto = f.read()

    linhas = texto.strip().split("\n")
    resultado = []
    data_atual = None

    for linha in linhas:
        linha = linha.strip()
        if re.match(r"\d{2} [A-Z]{3}", linha):
            data_atual = linha
        elif linha and data_atual:
            match = re.match(r"(.*) ?[−-−]?R\$ ?([\d.,]+)", linha)
            if match:
                descricao = match.group(1).strip()
                valor = f"R$ {match.group(2)}"
                resultado.append(f"{data_atual},{descricao},{valor}")

    with open(csv_path, 'w', encoding='utf-8') as f:
            for linha in resultado:
                f.write(linha+ "\n")

def corrigir_descricao(descricao):
    if descricao.startswith("Ifd") or descricao.startswith("Ifood"):
        return "iFood"
    
    return substituicoes.get(descricao, descricao)

def atribuir_categoria(descricao_corrigida):
    return categorias.get(descricao_corrigida, "Diversos")

def SubNomes_pdf():
    with open(csv_formatado, 'r', encoding='utf-8') as arquivo_entrada:
        leitor = csv.reader(arquivo_entrada)
        linhas_corrigidas = []

        for linha in leitor:
            if len(linha) >= 3:
                data, descricao, valor = linha[0], linha[1].strip(), ','.join(linha[2:]).strip()

                descricao_corrigida = corrigir_descricao(descricao)

                categoria = atribuir_categoria(descricao_corrigida)

                linhas_corrigidas.append([data, descricao_corrigida, valor, categoria])

    with open(csv_formatado_limpo, 'w', encoding='utf-8', newline='') as arquivo_saida:
        escritor = csv.writer(arquivo_saida)
        escritor.writerows(linhas_corrigidas)

        
def TirarCategorias():
    with open(csv_formatado_limpo, 'r', encoding='utf-8') as arquivo_entrada:
        leitor = csv.reader(arquivo_entrada)
        linhas_filtradas = [linha for linha in leitor if len(linha) == 4 and linha[3].strip().lower() != 'pagamento']

    with open(csv_formatado_limpo, 'w', encoding='utf-8', newline='') as arquivo_saida:
        escritor = csv.writer(arquivo_saida)
        escritor.writerows(linhas_filtradas)

def processarpdfnubank(pdf_path):
    extrair_texto_pdf(pdf_path, txt_pagina)
    organizar_fatura(txt_pagina, csv_formatado)
    SubNomes_pdf()
    TirarCategorias()

