import wx
import json
import os
import threading
from src.config.settings import CONFIG_FILE
from src.services.sqlite_service import buscar_sqlite, excluir_sqlite
from src.services.supabase_service import buscar_supabase, excluir_supabase
from src.services.playwright_service import gerar_baixa
from src.services.excel_service import salvar_codigos_em_xlsx


class TelaBaixa(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Baixa Interna Automática - Correios", size=(520, 820))
        panel = wx.Panel(self)

        title = wx.StaticText(panel, label="📦 Sistema de Baixa Interna")
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.txt_user = wx.TextCtrl(panel)
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        btn_salvar = wx.Button(panel, label="Salvar Credenciais")
        btn_salvar.Bind(wx.EVT_BUTTON, self.salvar_credenciais)

        # Campo de pesquisa
        self.txt_pesquisa = wx.TextCtrl(panel)
        btn_pesquisar = wx.Button(panel, label="Pesquisar")
        btn_pesquisar.Bind(wx.EVT_BUTTON, self.pesquisar_codigo)

        # Lista de códigos
        self.lst_codigos = wx.ListBox(panel, style=wx.LB_EXTENDED)

        # Botões principais
        btn_excluir = wx.Button(panel, label="Excluir Selecionado")
        btn_excluir.Bind(wx.EVT_BUTTON, self.excluir_selecionado)

        btn_atualizar = wx.Button(panel, label="Atualizar Lista")
        btn_atualizar.Bind(wx.EVT_BUTTON, self.atualizar_manual)

        btn_baixar = wx.Button(panel, label="Baixar Todos")
        btn_baixar.Bind(wx.EVT_BUTTON, self.baixar_todos)

        # Layout organizado
        s = wx.BoxSizer(wx.VERTICAL)

        s.Add(title, 0, wx.ALL | wx.CENTER, 15)
        s.Add(self.txt_user, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(self.txt_pass, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(btn_salvar, 0, wx.EXPAND | wx.ALL, 10)

        s.Add(wx.StaticText(panel, label="Pesquisar Código:"), 0, wx.LEFT | wx.TOP, 10)
        s.Add(self.txt_pesquisa, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(btn_pesquisar, 0, wx.EXPAND | wx.ALL, 10)

        s.Add(self.lst_codigos, 1, wx.EXPAND | wx.ALL, 10)

        s.Add(btn_excluir, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(btn_atualizar, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(btn_baixar, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(s)

        self.carregar_credenciais()
        self.atualizar_lista()
        self.Show()

    # ----------------------------
    # Credenciais
    # ----------------------------

    def salvar_credenciais(self, event):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "usuario": self.txt_user.GetValue(),
                "senha": self.txt_pass.GetValue()
            }, f)
        wx.MessageBox("Credenciais salvas!")

    def carregar_credenciais(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                d = json.load(f)
                self.txt_user.SetValue(d.get("usuario", ""))
                self.txt_pass.SetValue(d.get("senha", ""))

    # ----------------------------
    # Atualização de lista
    # ----------------------------

    def atualizar_lista(self):
        self.lst_codigos.Clear()
        supa = buscar_supabase()
        sqlite = buscar_sqlite()

        todos = set(
            [i["codigo_rastreio"] for i in supa] +
            [i[0] for i in sqlite]
        )

        for c in sorted(todos):
            self.lst_codigos.Append(c)

    def atualizar_manual(self, event):
        self.atualizar_lista()
        wx.MessageBox("Lista atualizada com sucesso!")

    # ----------------------------
    # Pesquisa
    # ----------------------------

    def pesquisar_codigo(self, event):
        termo = self.txt_pesquisa.GetValue().strip().lower()

        if not termo:
            self.atualizar_lista()
            return

        resultados = []

        for i in range(self.lst_codigos.GetCount()):
            codigo = self.lst_codigos.GetString(i)
            if termo in codigo.lower():
                resultados.append(codigo)

        self.lst_codigos.Clear()

        for c in resultados:
            self.lst_codigos.Append(c)

    # ----------------------------
    # Exclusão
    # ----------------------------

    def excluir_selecionado(self, event):
        selecao = self.lst_codigos.GetSelections()

        if not selecao:
            wx.MessageBox("Selecione um código para excluir.")
            return

        for i in reversed(selecao):
            codigo = self.lst_codigos.GetString(i)
            excluir_sqlite(codigo)
            excluir_supabase(codigo)

        self.atualizar_lista()
        wx.MessageBox("Código(s) excluído(s) com sucesso!")

    # ----------------------------
    # Automação principal
    # ----------------------------

    def baixar_todos(self, event):
        codigos = [
            self.lst_codigos.GetString(i)
            for i in range(self.lst_codigos.GetCount())
        ]

        if not codigos:
            wx.MessageBox("Não há códigos para processar.")
            return

        def t():
            gerar_baixa(codigos, self.txt_user.GetValue(), self.txt_pass.GetValue())
            salvar_codigos_em_xlsx(codigos)

            for c in codigos:
                excluir_sqlite(c)
                excluir_supabase(c)

            wx.CallAfter(self.atualizar_lista)
            wx.CallAfter(lambda: wx.MessageBox("Processo finalizado com sucesso!"))

        threading.Thread(target=t).start()