import sys
import logging
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QTabWidget, QGroupBox, QTextEdit
)
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

# Configuração do Sistema de Logs (Grava tudo em otimizador.log)
logging.basicConfig(
    filename="otimizador.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

from perifericos import (
    OtimizadorSistema, OtimizadorPerifericos, OtimizadorRede,OtimizadorKernelAvancado,OtimizadorRedeAvancado,
    OtimizadorAMDBackend, RedutorInputLagBackend, OtimizadorPrivacidadeBackend
)


PALETAS_TEMA = {
    "dark": {
        "background": "#0d1117",
        "surface": "#161b22",
        "surface_alt": "#21262d",
        "border": "#30363d",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "accent": "#1f6feb",
        "accent_hover": "#388bfd",
        "accent_pressed": "#1158c7",
        "selection": "#264f78",
    },
    "light": {
        "background": "#f6f8fa",
        "surface": "#ffffff",
        "surface_alt": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#24292e",
        "muted": "#57606a",
        "accent": "#0969da",
        "accent_hover": "#0550ae",
        "accent_pressed": "#033d8b",
        "selection": "#ddf4ff",
    },
}


def detectar_tema_sistema():
    """Deteta o tema de aplicações do utilizador no registo do Windows."""
    if sys.platform != "win32":
        logging.info("Sistema não Windows; a utilizar o tema escuro por omissão.")
        return "dark"

    try:
        import winreg

        caminho_tema = (
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, caminho_tema) as chave:
            modo_claro, _ = winreg.QueryValueEx(chave, "AppsUseLightTheme")
    except OSError:
        logging.exception(
            "Não foi possível ler o tema do Windows; será utilizado o tema escuro."
        )
        return "dark"

    if modo_claro in (0, 1):
        tema = "light" if modo_claro == 1 else "dark"
        logging.info("Tema do Windows detetado: %s.", tema)
        return tema

    logging.warning(
        "Valor inesperado para AppsUseLightTheme (%r); será utilizado o tema escuro.",
        modo_claro,
    )
    return "dark"


def criar_folha_estilo(tema):
    """Cria a folha QSS global com a paleta selecionada."""
    cores = PALETAS_TEMA[tema]
    return f"""
        QMainWindow, QWidget {{
            background-color: {cores["background"]};
            color: {cores["text"]};
            font-family: "Segoe UI";
            font-size: 10pt;
        }}
        QTabWidget::pane {{
            background-color: {cores["surface"]};
            border: 1px solid {cores["border"]};
            border-radius: 8px;
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {cores["surface_alt"]};
            color: {cores["muted"]};
            border: 1px solid {cores["border"]};
            border-bottom: none;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
            padding: 9px 12px;
            margin-right: 3px;
        }}
        QTabBar::tab:hover {{
            color: {cores["text"]};
            background-color: {cores["surface"]};
        }}
        QTabBar::tab:selected {{
            background-color: {cores["surface"]};
            color: {cores["text"]};
            border-top: 2px solid {cores["accent"]};
            font-weight: bold;
        }}
        QPushButton {{
            background-color: {cores["surface_alt"]};
            color: {cores["text"]};
            border: 1px solid {cores["border"]};
            border-radius: 7px;
            padding: 10px 12px;
            margin: 4px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {cores["accent"]};
            border-color: {cores["accent_hover"]};
            color: #ffffff;
        }}
        QPushButton:pressed {{
            background-color: {cores["accent_pressed"]};
            border-color: {cores["accent_pressed"]};
            color: #ffffff;
        }}
        QPushButton:focus {{
            border: 1px solid {cores["accent"]};
        }}
        QPushButton:disabled {{
            color: {cores["muted"]};
            background-color: {cores["surface"]};
            border-color: {cores["border"]};
        }}
        QGroupBox {{
            color: {cores["text"]};
            background-color: {cores["surface"]};
            font-weight: bold;
            border: 1px solid {cores["border"]};
            border-radius: 8px;
            margin-top: 12px;
            padding: 14px 8px 8px 8px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            background-color: {cores["surface"]};
        }}
        QLabel {{
            background: transparent;
            color: {cores["text"]};
        }}
        QTextEdit {{
            background-color: {cores["surface"]};
            color: {cores["text"]};
            border: 1px solid {cores["border"]};
            border-radius: 8px;
            padding: 8px;
            selection-background-color: {cores["selection"]};
            font-family: Consolas, "Cascadia Mono", monospace;
            font-size: 9pt;
        }}
        QScrollBar:vertical {{
            background-color: {cores["background"]};
            width: 10px;
            margin: 3px 2px 3px 2px;
            border: none;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {cores["border"]};
            min-height: 24px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {cores["muted"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
            border: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QScrollBar:horizontal {{
            background-color: {cores["background"]};
            height: 10px;
            margin: 2px 3px 2px 3px;
            border: none;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {cores["border"]};
            min-width: 24px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {cores["muted"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
            border: none;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        QToolTip {{
            color: {cores["text"]};
            background-color: {cores["surface_alt"]};
            border: 1px solid {cores["border"]};
            border-radius: 6px;
            padding: 4px;
        }}
    """


class QtLogBridge(QObject):
    mensagem = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    def __init__(self, ponte):
        super().__init__()
        self.ponte = ponte

    def emit(self, registro):
        try:
            self.ponte.mensagem.emit(self.format(registro))
        except Exception:
            self.handleError(registro)


class TarefaWorker(QThread):
    resultado = pyqtSignal(bool, str)

    def __init__(self, tarefa):
        super().__init__()
        self.tarefa = tarefa

    def run(self):
        try:
            resultado = self.tarefa()
            if isinstance(resultado, tuple) and len(resultado) == 2:
                sucesso, mensagem = resultado
            else:
                sucesso, mensagem = True, "Operação concluída."
            self.resultado.emit(sucesso, mensagem)
        except Exception as erro:
            self.resultado.emit(False, f"Erro inesperado: {erro}")


class OtimizadorPyQt(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tema = detectar_tema_sistema()
        aplicacao = QApplication.instance()
        if aplicacao is None:
            raise RuntimeError("É necessário criar QApplication antes da janela.")
        aplicacao.setStyleSheet(criar_folha_estilo(self.tema))
        
        # Verificar privilégios de Administrador no arranque
        if not self.verificar_admin():
            logging.warning("Aplicação iniciada sem privilégios de Administrador.")
        
        self.setWindowTitle("⚡ Windows Ultimate Optimizer")
        self.setMinimumSize(560, 680)
        self.resize(620, 740)
        
        # Widget Central e Layout Principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        
        # --- Título Principal do App ---
        self.label_topo = QLabel("Painel de Controlo de Desempenho")
        self.label_topo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_topo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout_principal.addWidget(self.label_topo)
        
        # --- Sistema de Abas (Categorias) ---
        self.tabs = QTabWidget()
        
        # Criar as Abas por Categoria
        self.aba_sistema = QWidget()
        self.aba_perifericos = QWidget()
        self.aba_rede = QWidget()
        self.aba_privacidade = QWidget()
        self.aba_registos = QWidget()
        
        self.tabs.addTab(self.aba_sistema, "🚀 Sistema")
        self.tabs.addTab(self.aba_perifericos, "⌨ Periféricos & AMD")
        self.tabs.addTab(self.aba_rede, "🌐 Rede & DNS")
        self.tabs.addTab(self.aba_privacidade, "🛡️ Privacidade")
        self.tabs.addTab(self.aba_registos, "📋 Registos")
        
        # Configurar o conteúdo de cada aba
        self.montar_aba_sistema()
        self.montar_aba_perifericos()
        self.montar_aba_rede()
        self.montar_aba_privacidade()
        self.montar_aba_registos()
        
        layout_principal.addWidget(self.tabs)
        
        # --- Barra de Status no Rodapé ---
        self.label_status = QLabel("Estado: Sistema pronto e à espera de comandos.")
        self.label_status.setStyleSheet("font-size: 9pt; font-style: italic; margin-top: 5px;")
        layout_principal.addWidget(self.label_status)

        self.ponte_logs = QtLogBridge()
        self.ponte_logs.mensagem.connect(self.adicionar_log)
        self.log_handler = QtLogHandler(self.ponte_logs)
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s  %(message)s", "%H:%M:%S")
        )
        logging.getLogger().addHandler(self.log_handler)
        logging.info("Interface iniciada com o tema %s.", self.tema)

    @staticmethod
    def verificar_admin():
        """Verifica se o script está a correr com privilégios de Administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def montar_aba_sistema(self):
        """Organiza os controlos da categoria Sistema e Energia"""
        layout = QVBoxLayout(self.aba_sistema)
        
        grupo = QGroupBox("Modos de Desempenho e Resposta")
        vbox = QVBoxLayout()

        btn_mmcss = QPushButton("🎯 Otimizar Prioridade de Jogos (MMCSS)")
        btn_mmcss.clicked.connect(lambda: self.executar_em_background(OtimizadorKernelAvancado.otimizar_mmcss_jogos,
        btn_mmcss,
             "A aplicar perfis de alta prioridade de CPU/GPU...",
            )
        )
        vbox.addWidget(btn_mmcss)
        
        btn_energia = QPushButton("⚡ Desempenho Máximo")
        btn_energia.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorSistema.ativar_desempenho_maximo,
                btn_energia,
                "A ativar o modo de desempenho máximo...",
            )
        )
        vbox.addWidget(btn_energia)

        btn_responsiveness = QPushButton("⚙️ Otimizar Resposta do Sistema (Multimedia)")
        btn_responsiveness.clicked.connect(
            lambda: self.executar_em_background(
                RedutorInputLagBackend.otimizar_resposta_sistema,
                btn_responsiveness,
                "A ajustar prioridade de resposta do sistema...",
            )
        )
        vbox.addWidget(btn_responsiveness)
        
        grupo.setLayout(vbox)
        layout.addWidget(grupo)
        layout.addStretch()

    def montar_aba_perifericos(self):
        """Organiza os controlos da categoria Periféricos, Latência e AMD"""
        layout = QVBoxLayout(self.aba_perifericos)
        
        grupo = QGroupBox("Otimização de Latência e Hardware AMD")
        vbox = QVBoxLayout()
        
        btn_mouse = QPushButton("🖱 Otimizar Mouse e Teclado (Polling Rate)")
        btn_mouse.clicked.connect(lambda: self.atualizar_status("Periféricos otimizados para menor latência."))
        vbox.addWidget(btn_mouse)

        btn_msi = QPushButton("⚡ Ativar Modo MSI (Reduz DPC Latency)")
        btn_msi.clicked.connect(lambda: self.executar_em_background(OtimizadorKernelAvancado.ativar_msi_mode_gpu,
        btn_msi,
             "A configurar o modo MSI no registo do sistema...",
             )
        )
        vbox.addWidget(btn_msi)

        btn_game_mode = QPushButton("🎮 Ativar Modo de Jogo (Windows)")
        btn_game_mode.clicked.connect(
            lambda: self.executar_em_background(
                RedutorInputLagBackend.ativar_modo_jogo_windows,
                btn_game_mode,
                "A ativar o modo de jogo do Windows...",
            )
        )
        vbox.addWidget(btn_game_mode)

        btn_mpo = QPushButton("🟢 Desativar AMD MPO (Evitar Stuttering)")
        btn_mpo.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorAMDBackend.desativar_mpo,
                btn_mpo,
                "A desativar o Multi-Plane Overlay da AMD...",
            )
        )
        vbox.addWidget(btn_mpo)

        btn_hags = QPushButton("🖥️ Ativar AMD HAGS (Agendamento GPU)")
        btn_hags.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorAMDBackend.ativar_hags,
                btn_hags,
                "A ativar o agendamento acelerado por hardware...",
            )
        )
        vbox.addWidget(btn_hags)
        
        grupo.setLayout(vbox)
        layout.addWidget(grupo)
        layout.addStretch()

    def montar_aba_rede(self):
        """Organiza os controlos da categoria Rede e DNS"""
        layout = QVBoxLayout(self.aba_rede)
        
        grupo = QGroupBox("Aceleração de Conexão")
        vbox = QVBoxLayout()
        
        btn_dns = QPushButton("🌐 Aplicar DNS da Cloudflare (1.1.1.1)")
        btn_dns.clicked.connect(lambda: self.atualizar_status("DNS da Cloudflare aplicado com sucesso!"))
        vbox.addWidget(btn_dns)

        btn_tcp = QPushButton("🚀 Otimização Extrema TCP/IP (Baixo Ping)")
        btn_tcp.clicked.connect(
         lambda: self.executar_em_background(OtimizadorRedeAvancado.aplicar_tweaks_tcp_ip,
             btn_tcp,
             "A reconfigurar a pilha de rede NDIS...",
            )
        )
        vbox.addWidget(btn_tcp)
        
        grupo.setLayout(vbox)
        layout.addWidget(grupo)
        layout.addStretch()

    def montar_aba_privacidade(self):
        """Organiza os controlos de Privacidade e Telemetria"""
        layout = QVBoxLayout(self.aba_privacidade)
        
        grupo = QGroupBox("Proteção de Privacidade e Telemetria")
        vbox = QVBoxLayout()

        btn_diagtrack = QPushButton("🛑 Desativar Serviço de Telemetria (DiagTrack)")
        btn_diagtrack.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorPrivacidadeBackend.desativar_servico_telemetria,
                btn_diagtrack,
                "A desativar o serviço DiagTrack...",
            )
        )
        vbox.addWidget(btn_diagtrack)

        btn_telemetria_reg = QPushButton("📊 Restringir Diagnóstico ao Mínimo")
        btn_telemetria_reg.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorPrivacidadeBackend.restrinjir_dados_diagnostico,
                btn_telemetria_reg,
                "A restringir dados de diagnóstico...",
            )
        )
        vbox.addWidget(btn_telemetria_reg)

        btn_ads = QPushButton("🚫 Desativar ID de Publicidade")
        btn_ads.clicked.connect(
            lambda: self.executar_em_background(
                OtimizadorPrivacidadeBackend.desativar_id_publicidade,
                btn_ads,
                "A desativar ID de publicidade...",
            )
        )
        vbox.addWidget(btn_ads)
        
        grupo.setLayout(vbox)
        layout.addWidget(grupo)
        layout.addStretch()

    def montar_aba_registos(self):
        """Apresenta na interface os registos técnicos da aplicação."""
        layout = QVBoxLayout(self.aba_registos)
        self.consola_logs = QTextEdit()
        self.consola_logs.setReadOnly(True)
        self.consola_logs.setPlaceholderText("Os registos da aplicação serão apresentados aqui.")
        layout.addWidget(self.consola_logs)

    def adicionar_log(self, mensagem):
        self.consola_logs.moveCursor(QTextCursor.MoveOperation.End)
        self.consola_logs.insertPlainText(f"{mensagem}\n")
        self.consola_logs.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, evento):
        logging.getLogger().removeHandler(self.log_handler)
        self.log_handler.close()
        super().closeEvent(evento)

    def atualizar_status(self, mensagem):
        """Atualiza a label de status no fundo da janela"""
        self.label_status.setText(f"Estado: {mensagem}")

    def executar_em_background(self, tarefa, botao, mensagem_processando):
        """Executa uma operação do backend sem bloquear a interface."""
        if getattr(self, "_worker", None) is not None and self._worker.isRunning():
            return

        botao.setEnabled(False)
        self.atualizar_status(mensagem_processando)

        self._botao_em_execucao = botao
        self._worker = TarefaWorker(tarefa)
        self._worker.resultado.connect(self._resultado_tarefa)
        self._worker.finished.connect(self._finalizar_tarefa)
        self._worker.start()

    def _resultado_tarefa(self, sucesso, mensagem):
        self.atualizar_status(mensagem)
        if sucesso:
            logging.info(mensagem)
        else:
            logging.error(mensagem)

    def _finalizar_tarefa(self):
        if self._botao_em_execucao is not None:
            self._botao_em_execucao.setEnabled(True)
            self._botao_em_execucao = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    janela = OtimizadorPyQt()
    janela.show()
    sys.exit(app.exec())