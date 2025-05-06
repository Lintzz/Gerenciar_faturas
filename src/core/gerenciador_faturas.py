from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from tkcalendar import Calendar
from src.utils import Tratamento_pdf
from PIL import ImageFilter, ImageGrab, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config.config import STORAGE_DIR , obter_icone_path
import sqlite3
from ..database.BancoDados import criar_db_e_tabela, importar_csv_para_sqlite
from ..utils.images import image_1, image_2, image_4, image_5, image_6
from datetime import datetime

ctk.set_default_color_theme("green")
ctk.set_appearance_mode('dark')

class GerenciadorFaturas:
    def __init__(self):
        self.data_selecionada = ""
        self.csv_formatado_limpo = STORAGE_DIR / 'formatado_limpo.csv'
        self.janela_principal = None
        self.interface = None
        self.dados = None
        self.graficos = None
        self.calendario = None
        self.tabela = None

    def iniciar_aplicacao(self):
        self.janela_principal = ctk.CTk()
        self.janela_principal.withdraw()
        
        self.janela_principal.configure(fg_color="#252524")
        self.janela_principal.geometry("670x480")
        self.janela_principal.resizable(width=False, height=False)
        
        largura_janela = 670
        altura_janela = 480
        largura_tela = self.janela_principal.winfo_screenwidth()
        altura_tela = self.janela_principal.winfo_screenheight()
        x = (largura_tela // 2) - (largura_janela // 2)
        y = (altura_tela // 2) - (altura_janela // 2)
        self.janela_principal.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")
        
        self.janela_principal.title("Gerenciador de Faturas")
        self.janela_principal.iconbitmap(obter_icone_path())
        self.janela_principal.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
        
        self.interface = InterfaceGrafica(self)
        self.dados = GerenciadorDados(self)
        self.graficos = GerenciadorGraficos(self)
        self.calendario = Calendario(self)
        self.tabela = TabelaManager(self)
        
        self.interface.configurar_interface()
        
        self.dados.inicializar_banco()
        self.dados.carregar_dados_no_treeview(self.interface.treeview)
        
        self.interface.mostrar_splash()
        
        self.janela_principal.mainloop()

    def fechar_aplicacao(self):
        try:
            if hasattr(self, 'graficos'):
                if self.graficos.canvas1:
                    self.graficos.canvas1.get_tk_widget().destroy()
                if self.graficos.canvas2:
                    self.graficos.canvas2.get_tk_widget().destroy()
                plt.close('all')
                
            if hasattr(self, 'dados') and self.dados.conexao:
                self.dados.conexao.close()
                
            if hasattr(self, 'interface'):
                if hasattr(self.interface, 'overlay_frame') and self.interface.overlay_frame:
                    self.interface.overlay_frame.destroy()
                if hasattr(self.interface, 'frame_borda_add') and self.interface.frame_borda_add:
                    self.interface.frame_borda_add.destroy()
                if hasattr(self.interface, 'frame_borda_editar') and self.interface.frame_borda_editar:
                    self.interface.frame_borda_editar.destroy()
                    
        except:
            pass
            
        self.janela_principal.quit()
        self.janela_principal.destroy()

class InterfaceGrafica:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.treeview = None
        self.config_ano = None
        self.config_mes = None
        self.filtro_categoria = None
        self.pesquisa_entry = None
        self.bnt_grafico1 = None
        self.bnt_grafico2 = None
        self.bnt_pesquisa = None
        self.mostrar1 = False
        self.mostrar2 = False
        
    def get_config_values(self):
        return self.config_ano.get(), self.config_mes.get()
        
    def mostrar_splash(self):
        splash = ctk.CTkToplevel(self.gerenciador.janela_principal)
        splash.geometry("300x150")
        splash.title("Carregando...")
        splash.overrideredirect(True)

        label = ctk.CTkLabel(splash, text="Carregando...", font=("Arial", 18))
        label.pack(expand=True)

        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - 150
        y = (splash.winfo_screenheight() // 2) - 75
        splash.geometry(f"+{x}+{y}")

        def finalizar():
            self.gerenciador.janela_principal.deiconify()
            self.gerenciador.janela_principal.focus_force()
            splash.destroy()

        splash.after(2000, finalizar)

        splash.grab_set()
        splash.focus_force()
        
    def carregar_dados_iniciais(self):
        self.gerenciador.dados.carregar_dados_no_treeview(self.treeview)

    def configurar_interface(self):
        self.config_ano = ctk.CTkOptionMenu(
            self.gerenciador.janela_principal,
            width=100,
            values=["2025","2026","2027","2028","2029","2030"],
            fg_color="#3A3A3A",
            text_color="white",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#2b2b2b",
            dropdown_text_color="white",
            command=self.gerenciador.tabela.filtrar_ano_mes
        )
        self.config_ano.set("2025")
        self.config_ano.place(x=230, y=10)

        self.config_mes = ctk.CTkOptionMenu(
            self.gerenciador.janela_principal,
            width=100,
            values=["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"],
            fg_color="#3A3A3A",
            text_color="white",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#2b2b2b",
            dropdown_text_color="white",
            command=self.gerenciador.tabela.filtrar_ano_mes
        )
        self.config_mes.set("JAN")
        self.config_mes.place(x=345, y=10)

        self.pesquisa_entry = ctk.CTkEntry(
            self.gerenciador.janela_principal,
            width=200,
            placeholder_text="Pesquisar...",
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=2,
            text_color="white"
        )
        self.pesquisa_entry.place(x=278, y=400)

        self.filtro_categoria = ctk.CTkOptionMenu(
            self.gerenciador.janela_principal,
            width=110,
            values=["Todos","Assinaturas","Compras","Transporte","Saúde","Alimentação","Celular","Casa","Outro"],
            fg_color="#3A3A3A",
            text_color="white",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#2b2b2b",
            dropdown_text_color="white"
        )
        self.filtro_categoria.set("Todos")
        self.filtro_categoria.place(x=158, y=400)

        self.bnt_add = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Add Items  ",
            width=100,
            height=10,
            compound="right",
            anchor="e",
            font=('Arial', 12),
            command=self.adicionar_frameAdd,
            image=image_2
        )
        self.bnt_add.place(x=120, y=50)

        self.bnt_folder = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Add Folder  ",
            width=100,
            height=10,
            compound="right",
            anchor="e",
            font=('Arial', 12),
            command=self.gerenciador.tabela.inserir_arquivo,
            image=image_1
        )
        self.bnt_folder.place(x=230, y=50)

        self.bnt_delete = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Apagar  ",
            width=100,
            height=10,
            compound="right",
            anchor="e",
            font=('Arial', 12),
            fg_color='#252524',
            hover_color="#3A3A3A",
            border_width=1,
            border_color="#3A3A3A",
            command=self.gerenciador.tabela.deletar_item,
            image=image_5
        )
        self.bnt_delete.place(x=345, y=50)

        self.bnt_edit = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Editar  ",
            width=100,
            height=10,
            compound="right",
            anchor="e",
            font=('Arial', 12),
            fg_color='#252524',
            hover_color="#3A3A3A",
            border_width=1,
            border_color="#3A3A3A",
            command=self.abrir_frame_editar,
            image=image_6
        )
        self.bnt_edit.place(x=455, y=50)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                       background="#252524",
                       foreground="white",
                       fieldbackground="#252524",
                       rowheight=25,
                       borderwidth=0,
                       relief="flat",
                       highlightthickness=0)
        style.map("Treeview",
                 background=[("selected", "#444444")],
                 foreground=[("selected", "white")])
        style.configure("Treeview.Heading",
                       background="#252524",
                       foreground="white",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0,
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[('active', style.lookup('Treeview.Heading', 'background'))],
                 relief=[('active', 'flat')])
        style.configure("Vertical.TScrollbar",
                       background="#444444",
                       troughcolor="#252524",
                       bordercolor="#252524",
                       arrowcolor="white")

        frame = tk.Frame(self.gerenciador.janela_principal, width=520, height=300, bg="#252524")
        frame.place(x=75, y=90)

        self.treeview = ttk.Treeview(frame, columns=('data', 'nome', 'preco', 'categoria'), show='headings')
        self.treeview.column('data', minwidth=0, width=50)
        self.treeview.column('nome', minwidth=0, width=100)
        self.treeview.column('preco', minwidth=0, width=80)
        self.treeview.column('categoria', minwidth=0, width=50)

        self.treeview.heading("data", text=" Data", anchor='w', command=lambda: Utilitarios.ordenar_coluna(self.treeview, "data"))
        self.treeview.heading("nome", text=" Nome", anchor='w', command=lambda: Utilitarios.ordenar_coluna(self.treeview, "nome"))
        self.treeview.heading("preco", text=" Preço", anchor='w', command=lambda: Utilitarios.ordenar_coluna(self.treeview, "preco"))
        self.treeview.heading("categoria", text=" Categoria", anchor='w', command=lambda: Utilitarios.ordenar_coluna(self.treeview, "categoria"))

        self.treeview.place(relx=0, rely=0, relwidth=1, relheight=1)

        scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=self.treeview.yview)
        scrollbar.place(relx=1.0, rely=0, relheight=1, anchor="ne", x=-2, y=0)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        self.bnt_pesquisa = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="",
            width=25,
            height=25,
            compound="right",
            anchor="e",
            font=('Arial', 12),
            command=lambda: self.gerenciador.tabela.pesquisar(self.pesquisa_entry.get(), self.filtro_categoria.get()),
            image=image_4
        )
        self.bnt_pesquisa.place(x=488, y=400)

        self.bnt_grafico1 = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Exibir Gráfico Mensal",
            width=150,
            command=self.gerenciador.graficos.mostrar_grafico1
        )
        self.bnt_grafico1.place(x=188, y=440)

        self.bnt_grafico2 = ctk.CTkButton(
            self.gerenciador.janela_principal,
            text="Exibir Gráfico Anual",
            width=150,
            command=self.gerenciador.graficos.mostrar_grafico2
        )
        self.bnt_grafico2.place(x=350, y=440)

    def adicionar_frameAdd(self):
        self.gerenciador.janela_principal.update_idletasks()
        
        if hasattr(self, 'overlay_frame') and self.overlay_frame:
            self.overlay_frame.destroy()
            
        if hasattr(self, 'frame_borda_add') and self.frame_borda_add:
            self.frame_borda_add.destroy()
            
        self.overlay_frame = tk.Frame(self.gerenciador.janela_principal)
        self.frame_borda_add = ctk.CTkFrame(self.gerenciador.janela_principal, fg_color="#3A3A3A", corner_radius=0)
        self.frame_add = ctk.CTkFrame(self.frame_borda_add, fg_color="#252524", corner_radius=0)
        
        ctk.CTkLabel(self.frame_add, text="Adicionar Item", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        self.criar_campos_formulario()
        
        img_blur = Utilitarios.aplicar_blur(self.gerenciador.janela_principal)
        
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.canvas_blur = tk.Canvas(self.overlay_frame, highlightthickness=0)
        self.canvas_blur.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas_blur.create_image(0, 0, anchor="nw", image=img_blur)
        self.canvas_blur.image = img_blur
        
        self.frame_borda_add.place(x=180, y=80)
        self.frame_add.pack(padx=2, pady=2)
        
        self.frame_borda_add.lift()
        self.frame_add.lift()
        
    def criar_campos_formulario(self):
        input_width = 200

        frame_data = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        frame_data.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_data.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_data, text="Data: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.botao_data = ctk.CTkButton(
            frame_data,
            text="Escolher Data",
            command=lambda: self.gerenciador.calendario.abrir_calendario(self.botao_data),
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            hover_color="#444444",
            width=input_width
        )
        self.botao_data.grid(row=0, column=1, sticky="e")
        
        frame_nome = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        frame_nome.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_nome.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_nome, text="Nome: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.nome_entry = ctk.CTkEntry(
            frame_nome,
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            width=input_width
        )
        self.nome_entry.grid(row=0, column=1, sticky="e")
        
        frame_preco = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        frame_preco.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_preco.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_preco, text="Preço: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.preco_entry = ctk.CTkEntry(
            frame_preco,
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            width=input_width
        )
        self.preco_entry.grid(row=0, column=1, sticky="e")
        
        frame_categoria = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        frame_categoria.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_categoria.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_categoria, text="Categoria: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.categoria_combobox = ctk.CTkOptionMenu(
            frame_categoria,
            values=["Assinaturas", "Compras", "Transporte", "Saúde", "Alimentação", "Celular", "Casa", "Outro"],
            fg_color="#3A3A3A",
            button_color="#3A3A3A",
            button_hover_color="#444444",
            width=input_width
        )
        self.categoria_combobox.grid(row=0, column=1, sticky="e")
        self.categoria_combobox.set("Categorias")
        
        frame_botoes = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=20)
        
        btn_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            fg_color="#3A3A3A",
            hover_color="#444444",
            command=self.fechar_frameAdd
        )
        btn_cancelar.grid(row=0, column=0, padx=10)
        
        btn_salvar = ctk.CTkButton(
            frame_botoes,
            text="Salvar",
            command=self.salvar_novo_item
        )
        btn_salvar.grid(row=0, column=1, padx=10)
        
    def fechar_frameAdd(self):
        if hasattr(self, 'frame_borda_add') and self.frame_borda_add:
            self.frame_borda_add.destroy()
            self.frame_borda_add = None
            self.frame_add = None
            
        if hasattr(self, 'overlay_frame') and self.overlay_frame:
            self.overlay_frame.destroy()
            self.overlay_frame = None
            
        if hasattr(self, 'canvas_blur'):
            self.canvas_blur = None
            
    def abrir_frame_editar(self):
        input_width = 200
        treeview = self.treeview
        itemSelecionado = treeview.selection()
        
        if not itemSelecionado:
            messagebox.showinfo("ERRO", "Selecione um item para editar")
            return
            
        item = itemSelecionado[0]
        valores = treeview.item(item)['values']
        
        if hasattr(self, 'overlay_frame') and self.overlay_frame:
            self.overlay_frame.destroy()
            
        if hasattr(self, 'frame_borda_editar') and self.frame_borda_editar:
            self.frame_borda_editar.destroy()
            
        self.overlay_frame = tk.Frame(self.gerenciador.janela_principal)
        self.frame_borda_editar = ctk.CTkFrame(self.gerenciador.janela_principal, fg_color="#3A3A3A", corner_radius=0)
        self.frame_editar = ctk.CTkFrame(self.frame_borda_editar, fg_color="#252524", corner_radius=0)
        
        ctk.CTkLabel(self.frame_editar, text="Editar Item", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        frame_data = ctk.CTkFrame(self.frame_editar, fg_color="transparent")
        frame_data.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_data.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_data, text="Data: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.botao_data = ctk.CTkButton(
            frame_data,
            text=valores[0],
            command=lambda: self.gerenciador.calendario.abrir_calendario(self.botao_data),
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            hover_color="#444444",
            width=input_width
        )
        self.botao_data.grid(row=0, column=1, sticky="e")
        
        frame_nome = ctk.CTkFrame(self.frame_editar, fg_color="transparent")
        frame_nome.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_nome.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_nome, text="Nome: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.nome_entry = ctk.CTkEntry(
            frame_nome,
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            width=input_width
        )
        self.nome_entry.insert(0, valores[1])
        self.nome_entry.grid(row=0, column=1, sticky="e")
        
        frame_preco = ctk.CTkFrame(self.frame_editar, fg_color="transparent")
        frame_preco.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_preco.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_preco, text="Preço: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.preco_entry = ctk.CTkEntry(
            frame_preco,
            fg_color="#252524",
            border_color="#3A3A3A",
            border_width=1,
            width=input_width
        )
        preco_limpo = valores[2].replace("R$", "").strip()
        self.preco_entry.insert(0, preco_limpo)
        self.preco_entry.grid(row=0, column=1, sticky="e")
        
        frame_categoria = ctk.CTkFrame(self.frame_editar, fg_color="transparent")
        frame_categoria.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        frame_categoria.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame_categoria, text="Categoria: ", font=("Arial", 15)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.categoria_combobox = ctk.CTkOptionMenu(
            frame_categoria,
            values=["Assinaturas", "Compras", "Transporte", "Saúde", "Alimentação", "Celular", "Casa", "Outro"],
            fg_color="#3A3A3A",
            button_color="#3A3A3A",
            button_hover_color="#444444",
            width=input_width
        )
        self.categoria_combobox.set(valores[3])
        self.categoria_combobox.grid(row=0, column=1, sticky="e")
        
        frame_botoes = ctk.CTkFrame(self.frame_editar, fg_color="transparent")
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=20)
        
        btn_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            fg_color="#3A3A3A",
            hover_color="#444444",
            command=self.fechar_frame_editar
        )
        btn_cancelar.grid(row=0, column=0, padx=10)
        
        btn_salvar = ctk.CTkButton(
            frame_botoes,
            text="Salvar",
            command=lambda: self.editar_item(item)
        )
        btn_salvar.grid(row=0, column=1, padx=10)
        
        img_blur = Utilitarios.aplicar_blur(self.gerenciador.janela_principal)
        
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.canvas_blur = tk.Canvas(self.overlay_frame, highlightthickness=0)
        self.canvas_blur.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas_blur.create_image(0, 0, anchor="nw", image=img_blur)
        self.canvas_blur.image = img_blur
        
        self.frame_borda_editar.place(x=180, y=80)
        self.frame_editar.pack(padx=2, pady=2)
        
        self.frame_borda_editar.lift()
        self.frame_editar.lift()
        
    def editar_item(self, item_id):
        self.gerenciador.tabela.editar_item(item_id)
        
    def fechar_frame_editar(self):
        if hasattr(self, 'frame_borda_editar') and self.frame_borda_editar:
            self.frame_borda_editar.destroy()
            self.frame_borda_editar = None
            self.frame_editar = None
            
        if hasattr(self, 'overlay_frame') and self.overlay_frame:
            self.overlay_frame.destroy()
            self.overlay_frame = None
            
        if hasattr(self, 'canvas_blur'):
            self.canvas_blur = None
            
    def salvar_novo_item(self):
        resultado = self.gerenciador.tabela.inserir_item(
            self.botao_data.cget("text"),
            self.nome_entry.get(),
            self.preco_entry.get(),
            self.categoria_combobox.get()
        )

class GerenciadorDados:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.conexao = None
        
    def inicializar_banco(self):
        try:
            ano, mes = self.gerenciador.interface.get_config_values()
            if not ano or not mes:
                raise ValueError("Ano ou mês não configurados")
                
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            mes = f"{mes}_MES"
            criar_db_e_tabela(ano, mes)
            self.conexao = sqlite3.connect(banco_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar banco de dados: {str(e)}")
        
    def get_config_values(self):
        return self.gerenciador.interface.get_config_values()
        
    def carregar_dados_no_treeview(self, treeview):
        try:
            if not self.conexao:
                self.inicializar_banco()
                
            ano, mes = self.get_config_values()
            mes = f"{mes}_MES"
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, data, descricao, valor, categoria FROM {mes}")
            rows = cursor.fetchall()
            
            treeview.delete(*treeview.get_children())
            
            for row in rows:
                id_, data, descricao, valor, categoria = row
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                treeview.insert("", "end", iid=id_, values=(data, descricao, valor_formatado, categoria))
                
            conn.close()
            
            self.gerenciador.graficos.grafico1()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

class GerenciadorGraficos:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.canvas1 = None
        self.canvas2 = None
        
    def grafico1(self):
        ano, mes = self.gerenciador.interface.get_config_values()
        mes = f"{mes}_MES"
        banco_path = STORAGE_DIR / f"fatura_{ano}.db"

        conn = sqlite3.connect(banco_path)
        cursor = conn.cursor()
        dados = {}

        try:
            cursor.execute(f"SELECT categoria, valor FROM {mes}")
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

        dados_ordenados = sorted(zip(labels, sizes), key=lambda item: item[1], reverse=True)
        labels_ordenados, valores_ordenados = zip(*dados_ordenados)

        frame_grafico = ctk.CTkFrame(self.gerenciador.janela_principal, fg_color="transparent")
        frame_grafico.place(x=20, y=470)

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100, facecolor='#252524')
        fig.subplots_adjust(left=0, right=0.65, top=1.0, bottom=0.05)

        labels_com_valores = [f"{cat} - R$ {val:.2f}" for cat, val in zip(labels_ordenados, valores_ordenados)]

        ax.pie(valores_ordenados,
            labels=None,
            autopct=lambda p: f'R$ {p * sum(valores_ordenados) / 100:.2f}',
            startangle=90,
            textprops={'color': 'white', 'fontsize': 10, 'fontname': 'Arial', 'fontweight': 'bold'},
            pctdistance=0.55,
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.5, 'linestyle': 'solid'})

        legenda = plt.legend(labels_com_valores,
                            loc='center left',
                            bbox_to_anchor=(0.95, 0.5),
                            frameon=False,
                            handletextpad=1.5)
        
        total = sum(valores_ordenados)
        fig.text(0.8, 0.8, f"Total: R$ {total:.2f}", ha='center', fontsize=11, color='white', fontweight='bold')

        for text in legenda.get_texts():
            text.set_color('white')

        if self.canvas1:
            self.canvas1.get_tk_widget().destroy()
        self.canvas1 = FigureCanvasTkAgg(fig, master=frame_grafico)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

    def grafico2(self):
        ano, _ = self.gerenciador.interface.get_config_values()
        banco_path = STORAGE_DIR / f"fatura_{ano}.db"

        meses = ['JAN_MES', 'FEV_MES', 'MAR_MES', 'ABR_MES', 'MAI_MES', 'JUN_MES',
                'JUL_MES', 'AGO_MES', 'SET_MES', 'OUT_MES', 'NOV_MES', 'DEZ_MES']

        nomes_meses = []
        totais_por_mes = []

        conn = sqlite3.connect(banco_path)
        cursor = conn.cursor()

        for mes in meses:
            try:
                cursor.execute(f"SELECT SUM(valor) FROM {mes}")
                resultado = cursor.fetchone()[0]
                total = resultado if resultado else 0

                if total > 0:
                    nomes_meses.append(mes.split('_')[0].capitalize())
                    totais_por_mes.append(total)
            except sqlite3.OperationalError:
                continue

        conn.close()

        frame_grafico = ctk.CTkFrame(self.gerenciador.janela_principal, fg_color="transparent")
        frame_grafico.place(x=20, y=495)

        if not totais_por_mes:
            fig, ax = plt.subplots(figsize=(6, 5), dpi=100, facecolor='#252524')
            ax.set_facecolor('#2e2e2e')
            ax.tick_params(axis='both', labelsize=10, colors='white')
            fig.subplots_adjust(left=0.11, right=0.99, top=1, bottom=0.4)
            
            if self.canvas2:
                self.canvas2.get_tk_widget().destroy()
            self.canvas2 = FigureCanvasTkAgg(fig, master=frame_grafico)
            self.canvas2.draw()
            self.canvas2.get_tk_widget().pack(fill="both", expand=True)
            return

        fig, ax = plt.subplots(figsize=(6, 5), dpi=100, facecolor='#252524')

        ax.plot(nomes_meses, totais_por_mes, marker='o', color='red', linestyle='-', linewidth=2, markersize=6)

        ax.set_facecolor('#252524')
        ax.set_ylim(top=max(totais_por_mes) * 1.1)
        ax.tick_params(axis='both', labelsize=10, colors='white')
        fig.subplots_adjust(left=0.11, right=0.99, top=1, bottom=0.4)

        for i, valor in enumerate(totais_por_mes):
            ax.text(nomes_meses[i], valor + 100, f'{int(valor)}', ha='center', va='bottom', color='white', fontsize=10)

        if self.canvas2:
            self.canvas2.get_tk_widget().destroy()
        self.canvas2 = FigureCanvasTkAgg(fig, master=frame_grafico)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_grafico1(self):
        if self.gerenciador.interface.mostrar2:
            if self.canvas2:
                self.canvas2.get_tk_widget().destroy()
            self.gerenciador.interface.mostrar2 = False
            self.gerenciador.interface.bnt_grafico2.configure(text="Exibir Gráfico Anual")

        if not self.gerenciador.interface.mostrar1:
            self.gerenciador.janela_principal.geometry("670x850")
            self.grafico1()
            self.gerenciador.interface.mostrar1 = True
            self.gerenciador.interface.bnt_grafico1.configure(text="Ocultar Gráfico Mensal")
        else:
            self.gerenciador.janela_principal.geometry("670x480")
            if self.canvas1:
                self.canvas1.get_tk_widget().destroy()
            self.gerenciador.interface.mostrar1 = False
            self.gerenciador.interface.bnt_grafico1.configure(text="Exibir Gráfico Mensal")
            
    def mostrar_grafico2(self):
        if self.gerenciador.interface.mostrar1:
            if self.canvas1:
                self.canvas1.get_tk_widget().destroy()
            self.gerenciador.interface.mostrar1 = False
            self.gerenciador.interface.bnt_grafico1.configure(text="Exibir Gráfico Mensal")

        if not self.gerenciador.interface.mostrar2:
            self.gerenciador.janela_principal.geometry("670x850")
            self.grafico2()
            self.gerenciador.interface.mostrar2 = True
            self.gerenciador.interface.bnt_grafico2.configure(text="Ocultar Gráfico Anual")
        else:
            self.gerenciador.janela_principal.geometry("670x480")
            if self.canvas2:
                self.canvas2.get_tk_widget().destroy()
            self.gerenciador.interface.mostrar2 = False
            self.gerenciador.interface.bnt_grafico2.configure(text="Exibir Gráfico Anual")

class Calendario:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.calendario = None
        self.top_calendario = None
        self.meses = {
            "JAN": "JAN", "FEB": "FEV", "MAR": "MAR", "APR": "ABR",
            "MAY": "MAI", "JUN": "JUN", "JUL": "JUL", "AUG": "AGO",
            "SEP": "SET", "OCT": "OUT", "NOV": "NOV", "DEC": "DEZ"
        }
        
    def abrir_calendario(self, botao):
        if self.top_calendario:
            self.top_calendario.destroy()
            
        self.top_calendario = tk.Toplevel(self.gerenciador.janela_principal)
        self.top_calendario.configure(bg="#2d2d2d")
        self.top_calendario.grab_set()
        self.top_calendario.overrideredirect(True)
        self.top_calendario.title("Selecionar Data")
        
        x = botao.winfo_rootx()
        y = botao.winfo_rooty() + botao.winfo_height()
        self.top_calendario.geometry(f"+{x}+{y}")
        
        self.calendario = Calendar(
            self.top_calendario,
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
        self.calendario.grid(row=0, column=0, padx=10, pady=10)
        
        ctk.CTkButton(
            self.top_calendario,
            text="Selecionar",
            command=lambda: self.confirmar_data(botao)
        ).grid(row=1, column=0, pady=5)
        
    def confirmar_data(self, botao):
        data_str = self.calendario.get_date()
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y")
        data_selecionada = data_formatada.strftime("%d %b").upper()
        
        for mes_ingles, mes_portugues in self.meses.items():
            data_selecionada = data_selecionada.replace(mes_ingles, mes_portugues)
            
        botao.configure(text=f"{data_selecionada}")
        self.top_calendario.destroy()
        self.top_calendario = None

class Utilitarios:
    @staticmethod
    def aplicar_blur(janela):
        x = janela.winfo_rootx()
        y = janela.winfo_rooty()
        width = janela.winfo_width()
        height = janela.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
        blurred = screenshot.filter(ImageFilter.GaussianBlur(5))
        photo = ImageTk.PhotoImage(blurred)
        return photo
        
    @staticmethod
    def ordenar_coluna(tv, col):
        items = [(tv.set(item, col), item) for item in tv.get_children("")]
        
        reverse = False
        if hasattr(tv, "_last_sort"):
            if tv._last_sort == (col, False):
                reverse = True
                
        if col == "preco":
            def converter_preco(valor):
                try:
                    valor_limpo = valor.replace("R$", "").strip()
                    valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
                    return float(valor_limpo)
                except (ValueError, AttributeError):
                    return 0.0
                    
            items.sort(key=lambda x: converter_preco(x[0]), reverse=reverse)
        elif col == "data":
            meses = {
                "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4,
                "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8,
                "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12
            }
            
            def converter_data(data):
                try:
                    dia, mes = data.split()
                    return meses[mes], int(dia)
                except (ValueError, KeyError, AttributeError):
                    return (0, 0)
                    
            items.sort(key=lambda x: converter_data(x[0]), reverse=reverse)
        else:
            items.sort(reverse=reverse)
            
        for index, (val, item) in enumerate(items):
            tv.move(item, "", index)
            
        tv._last_sort = (col, reverse)

class TabelaManager:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        
    def filtrar_ano_mes(self, value=None):
        ano, mes = self.gerenciador.interface.get_config_values()
        mes = f"{mes}_MES"
        criar_db_e_tabela(ano, mes)
        self.gerenciador.dados.inicializar_banco()
        self.gerenciador.dados.carregar_dados_no_treeview(self.gerenciador.interface.treeview)
        
    def inserir_item(self, data, nome, preco, categoria):
        try:
            if not data or data == "Escolher Data":
                messagebox.showinfo("ERRO", "Selecione uma data")
                return False
                
            if not nome:
                messagebox.showinfo("ERRO", "Digite um nome")
                return False
                
            if not preco:
                messagebox.showinfo("ERRO", "Digite um preço")
                return False
                
            if categoria == "Categorias":
                messagebox.showinfo("ERRO", "Selecione uma categoria")
                return False
                
            try:
                preco_float = float(preco.replace(",", "."))
            except ValueError:
                messagebox.showinfo("ERRO", "Digite um preço válido")
                return False
                
            if not self.gerenciador.dados.conexao:
                self.gerenciador.dados.inicializar_banco()
                
            ano, mes = self.gerenciador.interface.get_config_values()
            mes = f"{mes}_MES"
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {mes} (data, descricao, valor, categoria)
                VALUES (?, ?, ?, ?)
            ''', (data, nome, preco_float, categoria))
            conn.commit()
            conn.close()
            
            self.gerenciador.dados.carregar_dados_no_treeview(self.gerenciador.interface.treeview)
            
            self.gerenciador.graficos.grafico1()
            
            self.gerenciador.interface.fechar_frameAdd()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar fatura: {str(e)}")
            return False
            
    def inserir_arquivo(self):
        ano, mes = self.gerenciador.interface.get_config_values()
        mes = f"{mes}_MES"
        
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            Tratamento_pdf.processarpdfnubank(caminho)
            
            try:
                importar_csv_para_sqlite(ano, mes)
                self.gerenciador.dados.carregar_dados_no_treeview(self.gerenciador.interface.treeview)
                self.gerenciador.graficos.grafico1()
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
                
    def deletar_item(self):
        try:
            if not self.gerenciador.dados.conexao:
                self.gerenciador.dados.inicializar_banco()
                
            treeview = self.gerenciador.interface.treeview
            itemSelecionado = treeview.selection()
            
            if not itemSelecionado:
                messagebox.showinfo("ERRO", "Selecione ao menos um item para deletar")
                return
                
            ano, mes = self.gerenciador.interface.get_config_values()
            mes = f"{mes}_MES"
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            
            for item_id in itemSelecionado:
                cursor.execute(f"DELETE FROM {mes} WHERE id = ?", (item_id,))
                treeview.delete(item_id)
                
            conn.commit()
            conn.close()
            
            self.gerenciador.graficos.grafico1()
            
        except Exception as e:
            messagebox.showerror("ERRO", f"Ocorreu um erro ao deletar: {str(e)}")
            
    def editar_item(self, item_id):
        try:
            data = self.gerenciador.interface.botao_data.cget("text")
            nome = self.gerenciador.interface.nome_entry.get()
            preco = self.gerenciador.interface.preco_entry.get()
            categoria = self.gerenciador.interface.categoria_combobox.get()
            
            if not data or data == "Escolher Data":
                messagebox.showinfo("ERRO", "Selecione uma data")
                return
                
            if not nome:
                messagebox.showinfo("ERRO", "Digite um nome")
                return
                
            if not preco:
                messagebox.showinfo("ERRO", "Digite um preço")
                return
                
            if categoria == "Categorias":
                messagebox.showinfo("ERRO", "Selecione uma categoria")
                return
                
            try:
                preco_limpo = preco.replace("R$", "").strip()
                preco_limpo = preco_limpo.replace(".", "").replace(",", ".")
                preco_float = float(preco_limpo)
            except ValueError:
                messagebox.showinfo("ERRO", "Digite um preço válido")
                return
                
            if not self.gerenciador.dados.conexao:
                self.gerenciador.dados.inicializar_banco()
                
            ano, mes = self.gerenciador.interface.get_config_values()
            mes = f"{mes}_MES"
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                UPDATE {mes}
                SET data = ?, descricao = ?, valor = ?, categoria = ?
                WHERE id = ?
            ''', (data, nome, preco_float, categoria, item_id))
            
            conn.commit()
            conn.close()
            
            self.gerenciador.dados.carregar_dados_no_treeview(self.gerenciador.interface.treeview)
            
            self.gerenciador.interface.fechar_frame_editar()
            
            self.gerenciador.graficos.grafico1()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar edição: {str(e)}")
            
    def pesquisar(self, termo_pesquisa, categoria_filtro=None):
        try:
            if not self.gerenciador.dados.conexao:
                self.gerenciador.dados.inicializar_banco()
                
            ano, mes = self.gerenciador.interface.get_config_values()
            mes = f"{mes}_MES"
            banco_path = STORAGE_DIR / f"fatura_{ano}.db"
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            
            if not termo_pesquisa and (not categoria_filtro or categoria_filtro == "Todos"):
                cursor.execute(f"SELECT id, data, descricao, valor, categoria FROM {mes}")
            elif categoria_filtro and categoria_filtro != "Todos":
                if termo_pesquisa:
                    cursor.execute(f"""
                        SELECT id, data, descricao, valor, categoria 
                        FROM {mes}
                        WHERE (descricao LIKE ? OR valor LIKE ?) AND categoria = ?
                    """, (f"%{termo_pesquisa}%", f"%{termo_pesquisa}%", categoria_filtro))
                else:
                    cursor.execute(f"""
                        SELECT id, data, descricao, valor, categoria 
                        FROM {mes}
                        WHERE categoria = ?
                    """, (categoria_filtro,))
            else:
                cursor.execute(f"""
                    SELECT id, data, descricao, valor, categoria 
                    FROM {mes}
                    WHERE descricao LIKE ? OR valor LIKE ?
                """, (f"%{termo_pesquisa}%", f"%{termo_pesquisa}%"))
                
            rows = cursor.fetchall()
            
            treeview = self.gerenciador.interface.treeview
            treeview.delete(*treeview.get_children())
            
            for row in rows:
                id_, data, descricao, valor, categoria = row
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                treeview.insert("", "end", iid=id_, values=(data, descricao, valor_formatado, categoria))
                
            conn.close()
            
            self.gerenciador.graficos.grafico1()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao pesquisar: {str(e)}")

def main():
    gerenciador = GerenciadorFaturas()
    gerenciador.iniciar_aplicacao()

if __name__ == "__main__":
    main() 