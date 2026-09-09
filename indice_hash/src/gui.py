"""Interface gráfica para construção e consulta do índice hash."""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from data_loader import carregar_palavras
from pagina import (paginar_registros, calcular_quantidade_paginas,
                     calcular_tamanho_pagina)
from indice_hash import IndiceHash
from hash_function import FUNCOES_HASH

_DIR_SRC = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PADRAO_DADOS = os.path.normpath(os.path.join(_DIR_SRC, "..", "data", "words.txt"))

COR_FUNDO = "#f4f6fb"
COR_PAINEL = "#ffffff"
COR_PRIMARIA = "#2b3a67"        # azul petróleo escuro (header, botões principais)
COR_PRIMARIA_HOVER = "#3d4f86"
COR_ACENTO = "#5c9ead"          # azul acinzentado (destaques secundários)
COR_SUCESSO = "#1f8a53"
COR_SUCESSO_BG = "#e5f6ed"
COR_ERRO = "#c1443c"
COR_ERRO_BG = "#fbeae9"
COR_TEXTO = "#22283b"
COR_TEXTO_SUAVE = "#5a6178"
COR_BORDA = "#e1e4ee"

FONTE_BASE = ("Segoe UI", 10)
FONTE_TITULO = ("Segoe UI", 17, "bold")
FONTE_SUBTITULO = ("Segoe UI", 10)
FONTE_SECAO = ("Segoe UI", 11, "bold")
FONTE_CARD_VALOR = ("Segoe UI", 19, "bold")
FONTE_CARD_LABEL = ("Segoe UI", 9)
FONTE_MONO = ("Consolas", 10)


class AplicacaoIndiceHash(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Índice Hash Estático — Trabalho de Banco de Dados")
        self.geometry("1150x760")
        self.minsize(860, 560)
        self.configure(bg=COR_FUNDO)

        self.indice: IndiceHash | None = None
        self.paginas = []
        self.ultima_busca_ok = False

        self._configurar_estilo()
        self._construir_layout()
        self._maximizar_janela()

    def _maximizar_janela(self):
        """Maximiza a janela e aplica um tamanho manual se necessário."""
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()

        self.update_idletasks()
        largura_antes = self.winfo_width()
        altura_antes = self.winfo_height()

        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)  # Linux/alguns window managers
            except tk.TclError:
                pass

        self.update_idletasks()
        largura_depois = self.winfo_width()
        altura_depois = self.winfo_height()

        nao_mudou = (largura_depois, altura_depois) == (largura_antes, altura_antes)
        maior_que_tela = largura_depois > largura_tela or altura_depois > altura_tela

        if nao_mudou and maior_que_tela:
            self.geometry(f"{largura_tela}x{altura_tela}+0+0")

    def _configurar_estilo(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_BASE)
        style.configure("TFrame", background=COR_FUNDO)
        style.configure("Card.TFrame", background=COR_PAINEL, relief="flat")
        style.configure("Header.TFrame", background=COR_PRIMARIA)

        style.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_BASE)
        style.configure("Card.TLabel", background=COR_PAINEL, foreground=COR_TEXTO, font=FONTE_BASE)
        style.configure("Header.TLabel", background=COR_PRIMARIA, foreground="#ffffff")
        style.configure("Titulo.Header.TLabel", background=COR_PRIMARIA, foreground="#ffffff", font=FONTE_TITULO)
        style.configure("Subtitulo.Header.TLabel", background=COR_PRIMARIA, foreground="#c9d3ef", font=FONTE_SUBTITULO)
        style.configure("Secao.TLabel", background=COR_FUNDO, foreground=COR_PRIMARIA, font=FONTE_SECAO)
        style.configure("SecaoCard.TLabel", background=COR_PAINEL, foreground=COR_PRIMARIA, font=FONTE_SECAO)
        style.configure("Suave.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SUAVE, font=("Segoe UI", 9))
        style.configure("SuaveCard.TLabel", background=COR_PAINEL, foreground=COR_TEXTO_SUAVE, font=("Segoe UI", 9))

        style.configure("TLabelframe", background=COR_PAINEL, bordercolor=COR_BORDA, relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=COR_PAINEL, foreground=COR_PRIMARIA, font=FONTE_SECAO)

        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure("TNotebook.Tab", background="#e4e8f4", foreground=COR_TEXTO_SUAVE,
                         padding=(16, 9), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", COR_PAINEL)],
                  foreground=[("selected", COR_PRIMARIA)])

        style.configure("TButton", background=COR_PRIMARIA, foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"), padding=(14, 8), borderwidth=0)
        style.map("TButton",
                  background=[("active", COR_PRIMARIA_HOVER), ("disabled", "#aab1c8")],
                  foreground=[("disabled", "#e7e9f2")])

        style.configure("Secundario.TButton", background=COR_ACENTO, foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"), padding=(14, 8), borderwidth=0)
        style.map("Secundario.TButton",
                  background=[("active", "#4a8b99"), ("disabled", "#aab1c8")])

        style.configure("TEntry", fieldbackground="#ffffff", padding=6, bordercolor=COR_BORDA)
        style.configure("TCombobox", fieldbackground="#ffffff", padding=5)
        style.configure("TRadiobutton", background=COR_PAINEL, font=FONTE_BASE)
        style.configure("TProgressbar", background=COR_ACENTO, troughcolor="#e4e8f4",
                         bordercolor=COR_FUNDO, lightcolor=COR_ACENTO, darkcolor=COR_ACENTO)

    def _construir_layout(self):
        self._construir_header()

        self.status_var = tk.StringVar(value="Pronto. Configure os parâmetros e construa o índice.")
        status_bar = tk.Label(self, textvariable=self.status_var, bg=COR_PRIMARIA, fg="#ffffff",
                               anchor="w", padx=14, pady=5, font=("Segoe UI", 9))
        status_bar.pack(fill="x", side="bottom")

        self.corpo = self._construir_area_rolavel()

        self._construir_frame_configuracao()

        self.notebook = ttk.Notebook(self.corpo)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.tab_paginas = ttk.Frame(self.notebook, style="TFrame")
        self.tab_estatisticas = ttk.Frame(self.notebook, style="TFrame")
        self.tab_busca = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_paginas, text="  📄  Páginas carregadas  ")
        self.notebook.add(self.tab_estatisticas, text="  📊  Estatísticas  ")
        self.notebook.add(self.tab_busca, text="  🔍  Busca e Table Scan  ")

        self._construir_tab_paginas()
        self._construir_tab_estatisticas()
        self._construir_tab_busca()

    def _construir_area_rolavel(self) -> tk.Widget:
        """Cria a área central com rolagem vertical e horizontal."""
        container = tk.Frame(self, bg=COR_FUNDO)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(container, bg=COR_FUNDO, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hscroll = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")

        frame_interno = ttk.Frame(canvas, style="TFrame")
        janela_id = canvas.create_window((0, 0), window=frame_interno, anchor="nw")

        def _atualizar_regiao_rolagem(_evento=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _ajustar_largura_interna(evento):
            largura_necessaria = frame_interno.winfo_reqwidth()
            nova_largura = max(evento.width, largura_necessaria)
            canvas.itemconfig(janela_id, width=nova_largura)

        frame_interno.bind("<Configure>", _atualizar_regiao_rolagem)
        canvas.bind("<Configure>", _ajustar_largura_interna)

        def _rolar_vertical(evento):
            if evento.num == 4:
                canvas.yview_scroll(-1, "units")
            elif evento.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

        def _rolar_horizontal(evento):
            if evento.delta:
                canvas.xview_scroll(int(-1 * (evento.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _rolar_vertical)
        canvas.bind_all("<Shift-MouseWheel>", _rolar_horizontal)
        canvas.bind_all("<Button-4>", _rolar_vertical)
        canvas.bind_all("<Button-5>", _rolar_vertical)

        return frame_interno

    def _construir_header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")
        interno = ttk.Frame(header, style="Header.TFrame")
        interno.pack(fill="x", padx=20, pady=14)

        ttk.Label(interno, text="Índice Hash Estático", style="Titulo.Header.TLabel").pack(anchor="w")
        ttk.Label(interno, text="Construção, busca indexada e table scan sobre uma tabela paginada",
                  style="Subtitulo.Header.TLabel").pack(anchor="w", pady=(2, 0))

    def _construir_frame_configuracao(self):
        wrapper = ttk.Frame(self.corpo, style="TFrame")
        wrapper.pack(fill="x", padx=16, pady=14)

        frame = ttk.Frame(wrapper, style="Card.TFrame", padding=18)
        frame.pack(fill="x")

        ttk.Label(frame, text="⚙  Configuração e Carga do Índice", style="SecaoCard.TLabel").grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 12))

        ttk.Label(frame, text="Arquivo de dados:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.var_arquivo = tk.StringVar(value=CAMINHO_PADRAO_DADOS)
        ttk.Entry(frame, textvariable=self.var_arquivo, width=55).grid(row=1, column=1, columnspan=3, sticky="we", padx=5)
        ttk.Button(frame, text="Procurar...", style="Secundario.TButton",
                   command=self._selecionar_arquivo).grid(row=1, column=4, padx=5)

        ttk.Label(frame, text="Limitar nº de palavras (vazio = usar todas):", style="Card.TLabel").grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.var_limite = tk.StringVar(value="")
        ttk.Entry(frame, textvariable=self.var_limite, width=15).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(frame, text="Definir paginação por:", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.var_modo_paginacao = tk.StringVar(value="tamanho")
        ttk.Radiobutton(frame, text="Tamanho da página (registros/página)",
                         variable=self.var_modo_paginacao, value="tamanho",
                         command=self._atualizar_estado_campos_paginacao).grid(row=3, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(frame, text="Quantidade de páginas",
                         variable=self.var_modo_paginacao, value="quantidade",
                         command=self._atualizar_estado_campos_paginacao).grid(row=3, column=3, sticky="w")

        self.var_tamanho_pagina = tk.StringVar(value="500")
        self.entry_tamanho_pagina = ttk.Entry(frame, textvariable=self.var_tamanho_pagina, width=12)
        self.entry_tamanho_pagina.grid(row=4, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="registros/página", style="SuaveCard.TLabel").grid(row=4, column=2, sticky="w")

        self.var_qtd_paginas = tk.StringVar(value="")
        self.entry_qtd_paginas = ttk.Entry(frame, textvariable=self.var_qtd_paginas, width=12, state="disabled")
        self.entry_qtd_paginas.grid(row=4, column=3, sticky="w", padx=5)
        ttk.Label(frame, text="páginas", style="SuaveCard.TLabel").grid(row=4, column=4, sticky="w")

        ttk.Label(frame, text="FR (tuplas por bucket):", style="Card.TLabel").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.var_fr = tk.StringVar(value="8")
        ttk.Entry(frame, textvariable=self.var_fr, width=12).grid(row=5, column=1, sticky="w", padx=5)

        ttk.Label(frame, text="Função hash:", style="Card.TLabel").grid(row=5, column=2, sticky="e", padx=5)
        self.var_funcao_hash = tk.StringVar(value=list(FUNCOES_HASH.keys())[0])
        ttk.Combobox(frame, textvariable=self.var_funcao_hash, values=list(FUNCOES_HASH.keys()),
                     state="readonly", width=28).grid(row=5, column=3, columnspan=2, sticky="w", padx=5)

        ttk.Label(frame, text="Fator de carga (folga do bucket):", style="Card.TLabel").grid(
            row=6, column=0, sticky="w", padx=5, pady=5)
        self.var_fator_carga = tk.StringVar(value="0.8")
        ttk.Entry(frame, textvariable=self.var_fator_carga, width=12).grid(row=6, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="0 a 1 — menor valor = mais buckets, menos overflow (recomendado: 0.7–0.9)",
                  style="SuaveCard.TLabel").grid(row=6, column=2, columnspan=3, sticky="w", padx=5)

        acao_frame = ttk.Frame(frame, style="Card.TFrame")
        acao_frame.grid(row=7, column=0, columnspan=5, sticky="we", pady=(14, 0))
        self.btn_construir = ttk.Button(acao_frame, text="▶  Carregar dados e Construir Índice",
                                         command=self._iniciar_construcao)
        self.btn_construir.pack(side="left")

        self.progress = ttk.Progressbar(acao_frame, mode="determinate", length=340)
        self.progress.pack(side="left", padx=15, fill="x", expand=True)

        frame.columnconfigure(1, weight=1)

    def _atualizar_estado_campos_paginacao(self):
        if self.var_modo_paginacao.get() == "tamanho":
            self.entry_tamanho_pagina.config(state="normal")
            self.entry_qtd_paginas.config(state="disabled")
        else:
            self.entry_tamanho_pagina.config(state="disabled")
            self.entry_qtd_paginas.config(state="normal")

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(title="Selecione o arquivo de dados (.txt)",
                                              filetypes=[("Arquivos de texto", "*.txt"), ("Todos", "*.*")])
        if caminho:
            self.var_arquivo.set(caminho)

    def _construir_tab_paginas(self):
        outer = ttk.Frame(self.tab_paginas, style="TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Primeira e última página carregadas na memória, após a divisão física da tabela:",
                  style="Suave.TLabel").pack(anchor="w", pady=(0, 10))

        container = ttk.Frame(outer, style="TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        card_esq = ttk.Frame(container, style="Card.TFrame", padding=12)
        card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        card_dir = ttk.Frame(container, style="Card.TFrame", padding=12)
        card_dir.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        container.rowconfigure(0, weight=1)

        ttk.Label(card_esq, text="⏮  Primeira página", style="SecaoCard.TLabel").pack(anchor="w", pady=(0, 8))
        self.lista_primeira_pagina = tk.Listbox(card_esq, font=FONTE_MONO, bg="#fbfbfd", fg=COR_TEXTO,
                                                 relief="flat", highlightthickness=1,
                                                 highlightbackground=COR_BORDA, selectbackground=COR_ACENTO)
        self.lista_primeira_pagina.pack(fill="both", expand=True)

        ttk.Label(card_dir, text="⏭  Última página", style="SecaoCard.TLabel").pack(anchor="w", pady=(0, 8))
        self.lista_ultima_pagina = tk.Listbox(card_dir, font=FONTE_MONO, bg="#fbfbfd", fg=COR_TEXTO,
                                               relief="flat", highlightthickness=1,
                                               highlightbackground=COR_BORDA, selectbackground=COR_ACENTO)
        self.lista_ultima_pagina.pack(fill="both", expand=True)

        self.label_resumo_paginas = ttk.Label(outer, text="", style="Suave.TLabel", wraplength=1100, justify="left")
        self.label_resumo_paginas.pack(anchor="w", pady=(10, 0))

    def _construir_tab_estatisticas(self):
        outer = ttk.Frame(self.tab_estatisticas, style="TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        self.frame_cards = ttk.Frame(outer, style="TFrame")
        self.frame_cards.pack(fill="x", pady=(0, 10))

        specs = [
            ("NR (nº de tuplas)", COR_PRIMARIA),
            ("NB (nº de buckets)", COR_PRIMARIA),
            ("FR (tuplas/bucket)", COR_PRIMARIA),
            ("Nº de páginas", COR_PRIMARIA),
            ("Fator de carga alvo", COR_ACENTO),
            ("Carga média real (NR/NB)", COR_ACENTO),
            ("Total de inserções", COR_ACENTO),
            ("Colisões", "#c98a2c"),
            ("Taxa de colisões (%)", "#c98a2c"),
            ("Overflows", COR_ERRO),
            ("Taxa de overflows (%)", COR_ERRO),
        ]

        self.labels_stats = {}
        for i, (chave, cor) in enumerate(specs):
            r, c = divmod(i, 3)
            card = tk.Frame(self.frame_cards, bg=COR_PAINEL, highlightthickness=1,
                             highlightbackground=COR_BORDA)
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8, ipadx=10, ipady=12)
            self.frame_cards.columnconfigure(c, weight=1)

            faixa = tk.Frame(card, bg=cor, height=4)
            faixa.pack(fill="x", side="top")

            valor_var = tk.StringVar(value="—")
            tk.Label(card, textvariable=valor_var, bg=COR_PAINEL, fg=cor, font=FONTE_CARD_VALOR).pack(
                anchor="w", padx=14, pady=(10, 0))
            tk.Label(card, text=chave, bg=COR_PAINEL, fg=COR_TEXTO_SUAVE, font=FONTE_CARD_LABEL,
                     wraplength=220, justify="left").pack(anchor="w", padx=14, pady=(0, 8))
            self.labels_stats[chave] = valor_var

        nota = ttk.Label(outer, text=("Colisão = duas chaves diferentes mapeadas para o mesmo bucket (normal e "
                                       "esperado quando FR > 1). Overflow = o bucket já estava com FR entradas e "
                                       "precisou de um bucket de transbordamento encadeado (esse é o que gera "
                                       "custo extra de acesso a disco). O fator de carga controla o overflow: "
                                       "valores menores que 1 criam mais buckets de propósito, dando folga e "
                                       "reduzindo a chance de estouro — sem violar a regra do enunciado (NB > NR/FR "
                                       "continua sempre garantido como piso mínimo)."),
                          style="Suave.TLabel", wraplength=1100, justify="left")
        nota.pack(anchor="w", pady=(6, 0))

    def _atualizar_estatisticas(self):
        resumo = self.indice.resumo()
        for chave, valor in resumo.items():
            if chave in self.labels_stats:
                self.labels_stats[chave].set(str(valor))

    def _construir_tab_busca(self):
        outer = ttk.Frame(self.tab_busca, style="TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        frame_busca = ttk.Labelframe(outer, text="  Busca por chave (usando o índice)  ", padding=14)
        frame_busca.pack(fill="x", pady=(0, 12))

        linha = ttk.Frame(frame_busca, style="Card.TFrame")
        linha.pack(fill="x")
        ttk.Label(linha, text="Chave de busca:", style="Card.TLabel").pack(side="left", padx=(0, 8))
        self.var_chave_busca = tk.StringVar()
        entry_busca = ttk.Entry(linha, textvariable=self.var_chave_busca, width=32)
        entry_busca.pack(side="left", padx=(0, 8))
        entry_busca.bind("<Return>", lambda e: self._executar_busca())
        self.btn_buscar = ttk.Button(linha, text="Buscar", command=self._executar_busca, state="disabled")
        self.btn_buscar.pack(side="left")

        self.resultado_busca_frame = tk.Frame(frame_busca, bg=COR_PAINEL)
        self.resultado_busca_frame.pack(fill="x", pady=(12, 0))
        self.label_resultado_busca = tk.Label(self.resultado_busca_frame, text="Aguardando busca...",
                                               bg=COR_PAINEL, fg=COR_TEXTO_SUAVE, justify="left",
                                               anchor="w", font=FONTE_BASE, wraplength=1080, padx=10, pady=8)
        self.label_resultado_busca.pack(fill="x")

        frame_scan = ttk.Labelframe(outer, text="  Table Scan (sem usar índice)  ", padding=14)
        frame_scan.pack(fill="both", expand=True)

        self.btn_table_scan = ttk.Button(frame_scan, text="▶  Executar Table Scan",
                                          style="Secundario.TButton",
                                          command=self._executar_table_scan, state="disabled")
        self.btn_table_scan.pack(anchor="w", pady=(0, 8))

        ttk.Label(frame_scan, text="Páginas percorridas até a busca terminar:", style="SuaveCard.TLabel").pack(anchor="w")
        self.texto_scan = tk.Text(frame_scan, height=11, state="disabled", wrap="none", font=FONTE_MONO,
                                   bg="#fbfbfd", fg=COR_TEXTO, relief="flat", highlightthickness=1,
                                   highlightbackground=COR_BORDA, padx=8, pady=6)
        self.texto_scan.pack(fill="both", expand=True, pady=(4, 8))

        self.resultado_scan_frame = tk.Frame(frame_scan, bg=COR_PAINEL)
        self.resultado_scan_frame.pack(fill="x")
        self.label_resultado_scan = tk.Label(self.resultado_scan_frame, text="", bg=COR_PAINEL,
                                              fg=COR_TEXTO_SUAVE, justify="left", anchor="w",
                                              font=FONTE_BASE, wraplength=1080, padx=10, pady=8)
        self.label_resultado_scan.pack(fill="x")

        self.label_comparacao = tk.Label(outer, text="", bg=COR_FUNDO, fg=COR_PRIMARIA,
                                          font=("Segoe UI", 10, "bold"), justify="left",
                                          anchor="w", wraplength=1100)
        self.label_comparacao.pack(fill="x", pady=(10, 0))

    def _pintar_resultado(self, frame, label, texto, sucesso: bool):
        cor_fundo = COR_SUCESSO_BG if sucesso else COR_ERRO_BG
        cor_texto = COR_SUCESSO if sucesso else COR_ERRO
        frame.configure(bg=cor_fundo)
        label.configure(bg=cor_fundo, fg=cor_texto, text=texto)

    def _iniciar_construcao(self):
        try:
            fr = int(self.var_fr.get())
            if fr <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "FR deve ser um número inteiro maior que zero.")
            return

        try:
            fator_carga = float(self.var_fator_carga.get().replace(",", "."))
            if not (0 < fator_carga <= 1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "O fator de carga deve ser um número entre 0 (exclusivo) e 1 (inclusivo), ex.: 0.8.")
            return

        limite_txt = self.var_limite.get().strip()
        limite = None
        if limite_txt:
            try:
                limite = int(limite_txt)
                if limite <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "O limite de palavras deve ser um inteiro positivo.")
                return

        modo = self.var_modo_paginacao.get()
        tamanho_pagina_input = None
        qtd_paginas_input = None
        try:
            if modo == "tamanho":
                tamanho_pagina_input = int(self.var_tamanho_pagina.get())
                if tamanho_pagina_input <= 0:
                    raise ValueError
            else:
                qtd_paginas_input = int(self.var_qtd_paginas.get())
                if qtd_paginas_input <= 0:
                    raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe um valor inteiro positivo para a paginação.")
            return

        funcao_hash = FUNCOES_HASH[self.var_funcao_hash.get()]
        arquivo = self.var_arquivo.get()

        self.btn_construir.config(state="disabled")
        self.progress.config(mode="indeterminate")
        self.progress.start(10)
        self.status_var.set("Carregando arquivo de dados...")

        thread = threading.Thread(
            target=self._construir_em_background,
            args=(arquivo, limite, modo, tamanho_pagina_input, qtd_paginas_input, fr, funcao_hash, fator_carga),
            daemon=True,
        )
        thread.start()

    def _construir_em_background(self, arquivo, limite, modo, tamanho_pagina_input,
                                  qtd_paginas_input, fr, funcao_hash, fator_carga):
        try:
            palavras = carregar_palavras(arquivo, limite=limite)
            total = len(palavras)

            if modo == "tamanho":
                tamanho_pagina = tamanho_pagina_input
            else:
                tamanho_pagina = calcular_tamanho_pagina(total, qtd_paginas_input)

            paginas = paginar_registros(palavras, tamanho_pagina)

            indice = IndiceHash(paginas, fr, funcao_hash, fator_carga=fator_carga)
            indice.construir()

            self.after(0, self._finalizar_construcao, indice, paginas, total, tamanho_pagina)
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._erro_construcao, str(exc))

    def _erro_construcao(self, mensagem):
        self.progress.stop()
        self.progress.config(mode="determinate", value=0)
        self.btn_construir.config(state="normal")
        self.status_var.set("Erro na construção do índice.")
        messagebox.showerror("Erro ao construir índice", mensagem)

    def _finalizar_construcao(self, indice, paginas, total_registros, tamanho_pagina):
        self.indice = indice
        self.paginas = paginas

        self.progress.stop()
        self.progress.config(mode="determinate", value=100)
        self.btn_construir.config(state="normal")
        self.btn_buscar.config(state="normal")
        self.btn_table_scan.config(state="disabled")
        self.ultima_busca_ok = False

        self.lista_primeira_pagina.delete(0, tk.END)
        self.lista_ultima_pagina.delete(0, tk.END)
        primeira, ultima = paginas[0], paginas[-1]
        for chave in primeira.registros:
            self.lista_primeira_pagina.insert(tk.END, chave)
        for chave in ultima.registros:
            self.lista_ultima_pagina.insert(tk.END, chave)

        self.label_resumo_paginas.config(
            text=(f"Total de registros: {total_registros}   |   Tamanho da página: {tamanho_pagina}   "
                  f"|   Nº de páginas: {len(paginas)}   |   "
                  f"Primeira página: nº {primeira.numero} ({len(primeira)} registros)   |   "
                  f"Última página: nº {ultima.numero} ({len(ultima)} registros)")
        )

        self._atualizar_estatisticas()

        self.label_resultado_busca.config(text="Aguardando busca...", bg=COR_PAINEL, fg=COR_TEXTO_SUAVE)
        self.resultado_busca_frame.configure(bg=COR_PAINEL)
        self.label_resultado_scan.config(text="", bg=COR_PAINEL)
        self.resultado_scan_frame.configure(bg=COR_PAINEL)
        self.label_comparacao.config(text="")
        self.texto_scan.config(state="normal")
        self.texto_scan.delete("1.0", tk.END)
        self.texto_scan.config(state="disabled")

        self.status_var.set(f"Índice construído com sucesso — NR={indice.nr}, NB={indice.nb}, "
                             f"páginas={len(paginas)}.")
        self.notebook.select(self.tab_estatisticas)

    def _executar_busca(self):
        if self.indice is None:
            return
        chave = self.var_chave_busca.get().strip()
        if not chave:
            messagebox.showwarning("Atenção", "Digite uma chave de busca.")
            return

        resultado = self.indice.buscar(chave)
        self._ultimo_resultado_busca = resultado

        if resultado.encontrado:
            texto = (f"✅  Chave '{chave}' ENCONTRADA na página {resultado.pagina}\n"
                     f"Endereço do bucket: {resultado.endereco_bucket}   |   "
                     f"Custo de acessos (buckets + página): {resultado.custo_acessos}   |   "
                     f"Tempo: {resultado.tempo_segundos * 1000:.4f} ms")
        else:
            texto = (f"❌  Chave '{chave}' NÃO encontrada no índice\n"
                     f"Endereço do bucket verificado: {resultado.endereco_bucket}   |   "
                     f"Custo de acessos: {resultado.custo_acessos}   |   "
                     f"Tempo: {resultado.tempo_segundos * 1000:.4f} ms")

        self._pintar_resultado(self.resultado_busca_frame, self.label_resultado_busca, texto, resultado.encontrado)
        self.btn_table_scan.config(state="normal")
        self.ultima_busca_ok = True
        self.label_resultado_scan.config(text="", bg=COR_PAINEL)
        self.resultado_scan_frame.configure(bg=COR_PAINEL)
        self.label_comparacao.config(text="")
        self.texto_scan.config(state="normal")
        self.texto_scan.delete("1.0", tk.END)
        self.texto_scan.config(state="disabled")

    def _executar_table_scan(self):
        if self.indice is None or not self.ultima_busca_ok:
            return
        chave = self.var_chave_busca.get().strip()

        resultado = self.indice.table_scan(chave)

        self.texto_scan.config(state="normal")
        self.texto_scan.delete("1.0", tk.END)
        linhas_por_bloco = 20
        paginas_str = [str(p) for p in resultado.log_paginas]
        for i in range(0, len(paginas_str), linhas_por_bloco):
            bloco = ", ".join(paginas_str[i:i + linhas_por_bloco])
            self.texto_scan.insert(tk.END, bloco + "\n")
        self.texto_scan.config(state="disabled")

        if resultado.encontrado:
            texto = (f"✅  Table scan encontrou '{chave}' na página {resultado.pagina_encontrada}\n"
                     f"Custo (páginas lidas): {resultado.paginas_lidas}   |   "
                     f"Tempo: {resultado.tempo_segundos * 1000:.4f} ms")
        else:
            texto = (f"❌  Table scan percorreu todas as {resultado.paginas_lidas} páginas e não encontrou '{chave}'\n"
                     f"Tempo: {resultado.tempo_segundos * 1000:.4f} ms")
        self._pintar_resultado(self.resultado_scan_frame, self.label_resultado_scan, texto, resultado.encontrado)

        r_idx = getattr(self, "_ultimo_resultado_busca", None)
        if r_idx is not None:
            t_idx = r_idx.tempo_segundos * 1000
            t_scan = resultado.tempo_segundos * 1000
            diferenca = t_scan - t_idx
            razao = (t_scan / t_idx) if t_idx > 0 else float("inf")
            self.label_comparacao.config(
                text=(f"⏱  Comparação — Índice: {r_idx.custo_acessos} acesso(s), {t_idx:.4f} ms   |   "
                      f"Table scan: {resultado.paginas_lidas} página(s), {t_scan:.4f} ms   |   "
                      f"Diferença: {diferenca:.4f} ms  (scan ~{razao:.1f}x mais lento)")
            )


def main():
    app = AplicacaoIndiceHash()
    app.mainloop()


if __name__ == "__main__":
    main()
