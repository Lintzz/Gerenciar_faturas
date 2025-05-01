from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
import Tratamento_pdf
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
from io import BytesIO
from config import STORAGE_DIR
import config
import sqlite3
from BancoDados import importar_csv_para_sqlite, criar_tabela_gastos

csv_formatado_limpo = STORAGE_DIR / 'formatado_limpo.csv'
gasto_bd = STORAGE_DIR / 'gastos.db'

data_selecionada = ""

def enviar():
    global data_selecionada

    nomeget = nome.get()
    precoget = preco.get()
    categoriaget = categoria.get()

    if data_selecionada == "" or nomeget == "" or precoget == "" or categoriaget == "Categorias":
        messagebox.showinfo(title="ERRO", message="Digite todos os dados")
    else:
        try:
            # Converte o valor para float (substitui vírgula por ponto)
            valor_float = float(precoget.replace(",", "."))
        except ValueError:
            messagebox.showinfo(title="ERRO", message="Preço inválido")
            return

        # Conecta ao banco e insere os dados
        conn = sqlite3.connect(gasto_bd)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gastos (data, descricao, valor, categoria)
            VALUES (?, ?, ?, ?)
        ''', (data_selecionada, nomeget, valor_float, categoriaget))
        conn.commit()
        conn.close()

        # Limpa os campos
        nome.delete(0, END)
        preco.delete(0, END)
        categoria.set("Categorias")
        botao_data.configure(text="Escolher Data")

        # Atualiza a Treeview com os dados do banco
        tv.delete(*tv.get_children())
        carregar_dados_no_treeview() 

        # Atualiza gráficos
        grafico1()
        grafico2()

def arquivoPdf():
    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*")]
    )
    if caminho:
        Tratamento_pdf.processarpdfnubank(caminho)

    tv.delete(*tv.get_children())

    try:
        importar_csv_para_sqlite()
        carregar_dados_no_treeview()
    except Exception as e:
        messagebox.showerror(title="Erro", message=f"Ocorreu um erro: {e}")

    grafico1()
    grafico2()
    
def deletar():
    try:
        itemSelecionado = tv.selection()

        if not itemSelecionado:
            messagebox.showinfo(title="ERRO", message="Selecione ao menos um item para deletar")
            return

        conn = sqlite3.connect(gasto_bd)
        cursor = conn.cursor()

        for item_id in itemSelecionado:
            cursor.execute("DELETE FROM gastos WHERE id = ?", (item_id,))
            tv.delete(item_id)

        conn.commit()
        conn.close()

    except Exception as e:
        messagebox.showinfo(title="ERRO", message=f"Ocorreu um erro ao deletar: {e}")

    grafico1()
    grafico2()

def editar():
    global data_selecionada
    global botao_dataa
    try:
        itemSelecionado = tv.selection()

        if not itemSelecionado:
            messagebox.showinfo(title="ERRO", message="Selecione ao menos um item para editar")
            return

        item_id = itemSelecionado[0]
        valores = tv.item(item_id,'values')

        if not valores:
            messagebox.showinfo(title="ERRO", message="Não foi possível obter os dados do item selecionado")
            return
    
        data_atual, nome_atual, valor_atual, categoria_atual = valores

        edit_window = Toplevel()
        edit_window.title("Editar Item")
        edit_window.geometry("670x90")

        edit_window.geometry("670x90") 

        largura_tela = edit_window.winfo_screenwidth()
        altura_tela = edit_window.winfo_screenheight()

        largura_edit_window = 670
        altura_edit_window = 90

        x = (largura_tela // 2) - (largura_edit_window // 2)
        y = (altura_tela // 2) - (altura_edit_window // 2) - 395  # Subir 50 pixels

        edit_window.geometry(f"{largura_edit_window}x{altura_edit_window}+{x}+{y}")

        edit_window.configure(bg="#2e2e2e")

        botao_dataa = ctk.CTkButton(edit_window, width=100, text=f"Data: {data_atual}", command=lambda: abrir_calendario(botao_dataa))
        botao_dataa.place(x=80, y=10)

        nome = ctk.CTkEntry(edit_window, width=200, placeholder_text=nome_atual)
        nome.place(x=190, y=10)

        preco = ctk.CTkEntry(edit_window,width=90, placeholder_text=valor_atual)
        preco.place(x=400, y=10)

        categoria = ctk.CTkOptionMenu(edit_window,width=90, values=["Assinaturas","Compras","Transporte","Saúde","Alimentação","Celular","Casa","Outro"])
        categoria.place(x=500, y=10)
        categoria.set(categoria_atual)

        def salvar_edicao():
            novo_nome = nome.get()
            novo_valor = preco.get().replace(',', '.')
            novo_categoria = categoria.get()

            if not data_selecionada or not novo_nome or not novo_valor or not novo_categoria:
                messagebox.showinfo(title="ERRO", message="Todos os campos devem ser preenchidos")
                return

            conn = sqlite3.connect(gasto_bd)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE gastos
                SET data = ?, descricao = ?, valor = ?, categoria = ?
                WHERE id = ?
            """, (data_selecionada, novo_nome, novo_valor, novo_categoria, item_id))

            conn.commit()
            conn.close()

            novo_valor_tabela = f'R$ {novo_valor}'
            tv.item(item_id, values=(data_selecionada, novo_nome, novo_valor_tabela, novo_categoria))

            messagebox.showinfo(title="Sucesso", message="Item editado com sucesso")
            edit_window.destroy()

        salvar_btn = ctk.CTkButton(edit_window, text="Salvar", command=salvar_edicao)
        salvar_btn.place(x=190, y=50)

    except Exception as e:
        messagebox.showinfo(title="ERRO", message=f"Ocorreu um erro ao editar: {e}") 

def abrir_calendario(botao):
    global data_selecionada
    top = tk.Toplevel(janela)
    top.configure(bg="#2d2d2d")
    top.grab_set()
    top.title("Selecionar Data")
    x = botao.winfo_rootx()
    y = botao.winfo_rooty() + botao.winfo_height()
    top.geometry(f"+{x}+{y}")

    calendario = Calendar(
        top,
        selectmode='day',
        date_pattern='dd/mm/yyyy',
        locale='pt_BR',
        background='#2d2d2d',
        foreground='white',
        selectbackground='#ff8c00',
        selectforeground='white',
        headersbackground='#2d2d2d',
        headersforeground='white',
        weekendbackground='#2d2d2d',
        weekendforeground='white',
        disabledbackground='#444444',
        borderwidth=0
    )
    calendario.grid(row=0, column=0, padx=10, pady=10)

    def confirmar_data():
        global data_selecionada
        data_str = calendario.get_date()
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y")
        data_selecionada = data_formatada.strftime("%d %b").upper()

        # Substituir o mês em inglês para o mês em português
        meses_abreviados = {
            "JAN": "JAN", "FEB": "FEV", "MAR": "MAR", "APR": "ABR",
            "MAY": "MAI", "JUN": "JUN", "JUL": "JUL", "AUG": "AGO",
            "SEP": "SET", "OCT": "OUT", "NOV": "NOV", "DEC": "DEZ"
        }

        # Substitui o mês na data formatada
        for mes_ingles, mes_portugues in meses_abreviados.items():
            data_selecionada = data_selecionada.replace(mes_ingles, mes_portugues)

        botao.configure(text=f"Data: {data_selecionada}")

        top.destroy()

    ctk.CTkButton(top, text="Selecionar", command=confirmar_data).grid(row=1, column=0, pady=5)

canvas = None
mostrar1 = False
mostrar2 = False
def grafico1():
    global canvas
    conn = sqlite3.connect(gasto_bd)
    cursor = conn.cursor()
    dados = {}
    

    try:
        cursor.execute("SELECT categoria, valor FROM gastos")
        registros = cursor.fetchall()

        for categoria, valor in registros:
            if categoria in dados:
                dados[categoria] += valor
            else:
                dados[categoria] = valor

    except Exception as e:
        print(f"Erro ao consultar o banco: {e}")
    finally:
        conn.close()

    if dados:
        labels = dados.keys()
        sizes = dados.values()
    else:
        labels = ["Sem dados"]
        sizes = [1]

    # Ordenar os dados por valor (maior para menor)
    dados_ordenados = sorted(zip(labels, sizes), key=lambda item: item[1], reverse=True)
    labels_ordenados, valores_ordenados = zip(*dados_ordenados)

    # Criar frame do gráfico
    frame_grafico = ctk.CTkFrame(janela,fg_color="transparent")
    frame_grafico.place(x=20, y=470)

    # Criar gráfico de pizza
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100, facecolor='#2e2e2e')
    fig.subplots_adjust(left=0, right=0.65, top=1.0, bottom=0.05)

    # Rótulos formatados com os valores
    labels_com_valores = [f"{cat} - R$ {val:.2f}" for cat, val in zip(labels_ordenados, valores_ordenados)]

    # Gráfico de pizza sem rótulos diretos (eles vão só na legenda)
    ax.pie(valores_ordenados,
        labels=None,
        autopct=lambda p: f'R$ {p * sum(valores_ordenados) / 100:.2f}',
        startangle=90,
        textprops={'color': 'white', 'fontsize': 10, 'fontname': 'Arial', 'fontweight': 'bold'},
        pctdistance=0.55,
        wedgeprops={'edgecolor': 'black', 'linewidth': 0.5, 'linestyle': 'solid'})

    # Legenda com rótulos formatados
    legenda = plt.legend(labels_com_valores,
                         loc='center left',
                         bbox_to_anchor=(0.95, 0.5),
                         frameon=False,
                         handletextpad=1.5)
    
    total = sum(valores_ordenados)
    fig.text(0.8, 0.8, f"Total: R$ {total:.2f}", ha='center', fontsize=11, color='white', fontweight='bold')

    for text in legenda.get_texts():
        text.set_color('white')

    # Mostrar gráfico no frame
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def grafico2():
    global canvas
    meses = [
        'jan', 'fev', 'mar', 'abr', 'mai', 'jun',
        'jul', 'ago', 'set', 'out', 'nov', 'dez'
    ]
    y = [1432.64,0,0,0,0,0,0,0,0,0,0,0]

    # Criando o frame do gráfico
    frame_grafico = ctk.CTkFrame(janela,fg_color="transparent") 
    frame_grafico.place(x=20, y=495)

    # Criando o gráfico de linha
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100, facecolor='#2e2e2e')

    # Plotando a linha
    ax.plot(meses, y, marker='o', color='red', linestyle='-', linewidth=2, markersize=6)

    # Ajustando a aparência
    ax.set_facecolor('#2e2e2e') 
    ax.tick_params(axis='both', labelsize=10, colors='white') 
    fig.subplots_adjust(left=0.11, right=0.99, top=1, bottom=0.4)

    # Exibindo o gráfico
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def mostrar_grafico1():
    global mostrar1,mostrar2,canvas

    if mostrar2:
        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
        mostrar2 = False
        bnt_grafico2.configure(text=f"Exibir Gráfico Anual")

    if not mostrar1:
        janela.geometry("670x850")
        grafico1()
        mostrar1 = True
        bnt_grafico1.configure(text=f"Ocultar Gráfico Mensal")
    else:
        janela.geometry("670x480")
        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
        mostrar1 = False
        bnt_grafico1.configure(text=f"Exibir Gráfico Mensal")

def mostrar_grafico2():
    global mostrar1,mostrar2,canvas

    if mostrar1:
        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
        mostrar1 = False
        bnt_grafico1.configure(text=f"Exibir Gráfico Mensal")

    if not mostrar2:
        janela.geometry("670x850")
        grafico2()
        mostrar2 = True
        bnt_grafico2.configure(text=f"Ocultar Gráfico Anual")
    else:
        janela.geometry("670x480")
        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
        mostrar2 = False 
        bnt_grafico2.configure(text=f"Exibir Gráfico Anual")

def carregar_dados_no_treeview():
    conn = sqlite3.connect(gasto_bd)
    cursor = conn.cursor()

    for item in tv.get_children():
        tv.delete(item)

    cursor.execute("SELECT id, data, descricao, valor, categoria FROM gastos")
    for linha in cursor.fetchall():
        id_registro = linha[0]
        valor_formatado = f"R$ {float(linha[3]):.2f}".replace('.', ',')
        tv.insert("", "end", iid=id_registro, values=(linha[1], linha[2], valor_formatado, linha[4]))
    
    ordenar_coluna(tv, "data")

    conn.close()

def dados_db():
    conn = sqlite3.connect(gasto_bd)
    cursor = conn.cursor()

    cursor.execute("SELECT data, descricao, valor, categoria FROM gastos")
    dados = cursor.fetchall()
    
    conn.close()
    
    return [{"data": d[0], "nome": d[1], "preco": f"R$ {d[2]:.2f}".replace('.', ','), "categoria": d[3]} for d in dados]

def pesquisar():
    dadosdb = dados_db()
    texto_pesquisa = pesquisa.get().lower()
    categoria_filtro = Filtro_categoria.get()

    for item in tv.get_children():
        tv.delete(item)

    for item in dadosdb:
        nome_pesquisa = texto_pesquisa in item["nome"].lower()
        categoria_pesquisa = (categoria_filtro == "All" or item["categoria"] == categoria_filtro)

        if nome_pesquisa and categoria_pesquisa:
            tv.insert("", "end", values=(item["data"], item["nome"], item["preco"], item["categoria"]))

def fechar_tudo():
    print("Fechando com segurança...")
    try:
        plt.close('all')
        janela.quit()
        janela.destroy()
    except:
        pass

def ctkimage_from_b64(b64_string, size=(20,20)):
    data = base64.b64decode(b64_string)
    pil_img = Image.open(BytesIO(data))
    return ctk.CTkImage(pil_img, size=size)

ordem_colunas = {}
MESES_PT = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4,
    "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8,
    "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12
}

def ordenar_coluna(tv, col):
    global ordem_colunas
    reverso = ordem_colunas.get(col, False)

    def parse(valor):
        if col == "preco":
            return float(valor.replace("R$", "").replace(".", "").replace(",", "."))
        elif col == "data":
            try:
                dia, mes = valor.strip().split()
                return datetime(2025, MESES_PT[mes.upper()], int(dia))
            except:
                return datetime.min
        else:
            return valor.lower()

    dados = [(parse(tv.set(k, col)), k) for k in tv.get_children("")]
    dados.sort(reverse=reverso)

    for index, (_, k) in enumerate(dados):
        tv.move(k, "", index)

    ordem_colunas[col] = not reverso

    # Atualiza os headings com setinhas
    for nome_coluna in tv["columns"]:
        texto = {
            "data": " Data",
            "nome": " Nome",
            "preco": " Preço",
            "categoria": " Categoria"
        }.get(nome_coluna, nome_coluna.capitalize())

        setinha = ""
        if nome_coluna == col:
            setinha = " ↑" if not reverso else " ↓"

        tv.heading(nome_coluna, text=texto + setinha, command=lambda c=nome_coluna: ordenar_coluna(tv, c))

#imagens base 64 https://base64.guru/converter/encode/image
add_file_b64  = '''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'''
add_b64       = '''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'''
backspace_b64 = '''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'''
lupa_b64      = '''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'''

image_1 = ctkimage_from_b64(add_file_b64, size=(20,20))
image_2 = ctkimage_from_b64(add_b64, size=(20,20))
image_3 = ctkimage_from_b64(backspace_b64, size=(20,20))
image_4 = ctkimage_from_b64(lupa_b64, size=(20,20))

icon_path = config.obter_icone_path()

criar_tabela_gastos()

def abrir_janela_principal(janela):
    global botao_data,nome,preco,categoria,bnt,bnt2,bnt3,bnt4,tv,pesquisa,Filtro_categoria,bnt_grafico1,bnt_grafico2,bnt_pesquisa

    janela.deiconify()
    janela.resizable(width=False, height=False)
    janela.iconbitmap(icon_path)
    janela.protocol("WM_DELETE_WINDOW", fechar_tudo)

    #botao data
    botao_data = ctk.CTkButton(janela, width=100, text="Escolher Data", command=lambda: abrir_calendario(botao_data))
    botao_data.place(x=80, y=10)

    #input nome
    nome = ctk.CTkEntry(janela, width=200, placeholder_text='Nome')
    nome.place(x=190, y=10)

    #input preco
    preco = ctk.CTkEntry(janela,width=90, placeholder_text='preco')
    preco.place(x=400, y=10)

    #input categoria
    categoria = ctk.CTkOptionMenu(janela,width=90, values=["Assinaturas","Compras","Transporte","Saúde","Alimentação","Celular","Casa","Outro"])
    categoria.place(x=500, y=10)
    categoria.set('Categorias')

    #botao adicionar
    bnt = ctk.CTkButton(janela, image=image_2, text="Add Items  ", width=100, height=10, compound="right", anchor="e", font= ('Arial', 12), fg_color='#D2122E', hover_color="#7C0A02", command=enviar)
    bnt.place(x=170, y=50)

    #botao file
    bnt2 = ctk.CTkButton(janela, image=image_1, text="Add Folder  ", width=100, height=10, compound="right", anchor="e", font= ('Arial', 12), command=arquivoPdf)
    bnt2.place(x=280, y=50)

    #botao apagar
    bnt3 = ctk.CTkButton(janela, image=image_3, text="Apagar  ", width=100, height=10, compound="right", anchor="e", font= ('Arial', 12), fg_color='#D2122E', hover_color="#7C0A02", command=deletar)
    bnt3.place(x=395, y=50)

    #botao apagar
    bnt4 = ctk.CTkButton(janela, image=image_3, text="Editar  ", width=100, height=10, compound="right", anchor="e", font= ('Arial', 12), fg_color='#D2122E', hover_color="#7C0A02", command=editar)
    bnt4.place(x=505, y=50)

    #style tabela
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e", rowheight=25, borderwidth=0, relief="flat")        
    style.map("Treeview", background=[("selected", "#4a6984")], foreground=[("selected", "white")])
    style.configure("Treeview.Heading", background="#2e2e2e", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")       
    style.map("Treeview.Heading", background=[('active', style.lookup('Treeview.Heading', 'background'))], relief=[('active', 'flat')])
    style.configure("Vertical.TScrollbar", background="#444444", troughcolor="#2e2e2e", bordercolor="#2e2e2e", arrowcolor="white")         

    #frame tablea
    frame = tk.Frame(janela,width=520, height=300,bg="#2e2e2e")
    frame.place(x=75, y=90)

    # Tabela
    tv = ttk.Treeview(frame, columns=('data', 'nome', 'preco', 'categoria'), show='headings')
    tv.column('data', minwidth=0, width=50)
    tv.column('nome', minwidth=0, width=100)
    tv.column('preco', minwidth=0, width=80)
    tv.column('categoria', minwidth=0, width=50)

    tv.heading("data", text=" Data", anchor='w', command=lambda: ordenar_coluna(tv, "data"))
    tv.heading("nome", text=" Nome", anchor='w', command=lambda: ordenar_coluna(tv, "nome"))
    tv.heading("preco", text=" Preço", anchor='w', command=lambda: ordenar_coluna(tv, "preco"))
    tv.heading("categoria", text=" Categoria", anchor='w', command=lambda: ordenar_coluna(tv, "categoria"))

    tv.place(relx=0, rely=0, relwidth=1, relheight=1)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=tv.yview)
    scrollbar.place(relx=1.0, rely=0, relheight=1, anchor="ne", x=-2, y=10)
    tv.configure(yscrollcommand=scrollbar.set)

    carregar_dados_no_treeview()

    Filtro_categoria = ctk.CTkOptionMenu(janela,width=110, values=["All","Assinaturas","Compras","Transporte","Saúde","Alimentação","Celular","Casa","Outro"])
    Filtro_categoria.place(x=158, y=400)
    Filtro_categoria.set('All')

    pesquisa = ctk.CTkEntry(janela, width=200, placeholder_text='Pesquisa')
    pesquisa.place(x=278, y=400)

    bnt_pesquisa = ctk.CTkButton(janela, image=image_4, text="", width=25, height=25, compound="right", anchor="e", font= ('Arial', 12), command=pesquisar)
    bnt_pesquisa.place(x=488, y=400)

    bnt_grafico1 = ctk.CTkButton(janela, text="Exibir Gráfico Mensal", width =150, command=mostrar_grafico1)
    bnt_grafico1.place(x=188, y=440)

    bnt_grafico2 = ctk.CTkButton(janela, text="Exibir Gráfico Anual", width =150, command=mostrar_grafico2)
    bnt_grafico2.place(x=350, y=440)

def mostrar_splash(janela):
    splash = ctk.CTkToplevel(janela)
    splash.geometry("300x150")
    splash.title("Carregando...")
    splash.overrideredirect(True)

    label = ctk.CTkLabel(splash, text="Carregando...", font=("Arial", 18))
    label.pack(expand=True)

    # Centralizar splash
    splash.update_idletasks()
    x = (splash.winfo_screenwidth() // 2) - 150
    y = (splash.winfo_screenheight() // 2) - 75
    splash.geometry(f"+{x}+{y}")

    def finalizar():
        splash.withdraw()
        splash.destroy()
        abrir_janela_principal(janela)

    splash.after(2000, finalizar)

ctk.set_default_color_theme("green")
ctk.set_appearance_mode('dark')

janela = ctk.CTk()
janela.withdraw() 

janela.configure(fg_color="#2e2e2e")
janela.geometry("670x480")

largura_janela = 670
altura_janela = 480
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
x = (largura_tela // 2) - (largura_janela // 2)
y = (altura_tela // 2) - (altura_janela // 2) - 200
janela.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")

janela.title("Fatura")

mostrar_splash(janela)
janela.mainloop()