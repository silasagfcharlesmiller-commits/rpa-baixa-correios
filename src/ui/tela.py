import wx
import json
import os
import threading
import logging  # Adicionado para Logs Profissionais
from src.config.settings import CONFIG_FILE
from src.services.sqlite_service import buscar_sqlite, excluir_sqlite
from src.services.supabase_service import buscar_supabase, excluir_supabase
from src.services.playwright_service import gerar_baixa
from src.services.excel_service import salvar_codigos_em_xlsx

# Configuração do Logger para persistência e auditoria do RPA
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("rpa_execucao.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"usuario": self.txt_user.GetValue(), "senha": self.txt_pass.GetValue()}, f)
            logger.info("Credenciais de acesso salvas com sucesso localmente.")
            wx.MessageBox("Credenciais salvas!")
        except IOError as e:
            logger.error(f"Falha ao salvar arquivo de configuração: {e}")
            wx.MessageBox(f"Erro ao salvar credenciais: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def carregar_credenciais(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    d = json.load(f)
                    self.txt_user.SetValue(d.get("usuario", ""))
                    self.txt_pass.SetValue(d.get("senha", ""))
                logger.info("Credenciais carregadas com sucesso.")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Erro ao ler o arquivo de credenciais: {e}")

    # ----------------------------
    # Atualização de lista
    # ----------------------------
    def atualizar_lista(self):
        self.lst_codigos.Clear()
        try:
            supa = buscar_supabase()
            sqlite = buscar_sqlite()
            todos = set([i["codigo_rastreio"] for i in supa] + [i[0] for i in sqlite])
            
            for c in sorted(todos):
                self.lst_codigos.Append(c)
            logger.info(f"Lista sincronizada com sucesso. Total de {len(todos)} códigos únicos encontrados.")
        except Exception as e:
            logger.error(f"Erro na sincronização de dados (Supabase/SQLite): {e}")
            wx.MessageBox("Falha ao atualizar dados dos bancos de dados.", "Erro", wx.OK | wx.ICON_ERROR)

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
            try:
                excluir_sqlite(codigo)
                excluir_supabase(codigo)
                logger.info(f"Código {codigo} excluído manualmente pelo operador.")
            except Exception as e:
                logger.error(f"Falha ao excluir o código {codigo}: {e}")
                
        self.atualizar_lista()
        wx.MessageBox("Código(s) excluído(s) com sucesso!")

    # ----------------------------
    # Automação principal
    # ----------------------------
    def baixar_todos(self, event):
        codigos = [self.lst_codigos.GetString(i) for i in range(self.lst_codigos.GetCount())]
        if not codigos:
            wx.MessageBox("Não há códigos para processar.")
            return

        usuario = self.txt_user.GetValue()
        senha = self.txt_pass.GetValue()

        def thread_automacao():
            logger.info(f"Iniciando lote de automação para {len(codigos)} códigos.")
            try:
                # Executa a automação via Playwright
                gerar_baixa(codigos, usuario, senha)
                
                # Salva o relatório de auditoria
                salvar_codigos_em_xlsx(codigos)
                logger.info("Relatório Excel (.xlsx) gerado com sucesso.")
                
                # Se a automação ocorreu sem crashes, limpa as filas
                for c in codigos:
                    try:
                        excluir_sqlite(c)
                        excluir_supabase(c)
                    except Exception as db_err:
                        logger.error(f"Erro ao limpar código {c} da base: {db_err}")
                
                # Atualiza a UI de forma segura a partir da Thread
                wx.CallAfter(self.atualizar_lista)
                wx.CallAfter(lambda: wx.MessageBox("Processo finalizado com sucesso!", "RPA Concluído", wx.OK | wx.ICON_INFORMATION))
                
            except Exception as err:
                logger.critical(f"Falha crítica na execução do robô: {err}")
                wx.CallAfter(lambda: wx.MessageBox(f"Ocorreu um erro crítico na automação:\n{err}", "Erro no RPA", wx.OK | wx.ICON_ERROR))

        # Dispara a thread sem travar a interface gráfica (wxPython)
        threading.Thread(target=thread_automacao, daemon=True).start()
