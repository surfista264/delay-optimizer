import logging
import math
import os
import shutil
import sys
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import NOME_APLICACAO, VERSAO
from logger import obter_logger
from modules import (
    OtimizadorAMD,
    OtimizadorAudio,
    OtimizadorMouseTeclado,
    OtimizadorPrivacidade,
    OtimizadorRede,
    OtimizadorSistema,
)


logger = obter_logger(__name__)

CORES = {
    "background": "#0d111750",
    "sidebar": "#010409",
    "surface": "#161b22",
    "surface_alt": "#21262d",
    "border": "#30363d",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "accent": "#2f81f7",
    "accent_hover": "#388bfd",
    "green": "#238636",
    "green_hover": "#2ea043",
    "red": "#da3633",
}


def criar_folha_estilo():
    return f"""
        QWidget {{
            background-color: {CORES["background"]};
            color: {CORES["text"]};
            font-family: "Segoe UI";
            font-size: 10pt;
        }}

        QFrame#sidebar {{
            background-color: {CORES["sidebar"]};
            border-right: 1px solid {CORES["border"]};
        }}
        QFrame#card {{
            background-color: {CORES["surface"]};
            border: 1px solid {CORES["border"]};
            border-radius: 10px;
        }}
        QLabel#muted {{
            color: {CORES["muted"]};
        }}
        QLabel#pageTitle {{
            font-size: 20pt;
            font-weight: 700;
        }}
        QLabel#metricValue {{
            font-size: 25pt;
            font-weight: 700;
        }}
        QPushButton {{
            background-color: {CORES["surface_alt"]};
            border: 1px solid {CORES["border"]};
            border-radius: 7px;
            padding: 9px 12px;
            text-align: left;
        }}
        QPushButton:hover {{
            border-color: {CORES["accent"]};
            background-color: #1c2633;
        }}
        QPushButton:disabled {{
            color: {CORES["muted"]};
        }}
        QPushButton#navButton {{
            background-color: transparent;
            border: 1px solid transparent;
            color: {CORES["muted"]};
            padding: 11px 12px;
        }}
        QPushButton#navButton:hover {{
            background-color: {CORES["surface"]};
            color: {CORES["text"]};
        }}
        QPushButton#navButton[active="true"] {{
            background-color: #17263b;
            border-color: #1f3b60;
            color: {CORES["text"]};
            font-weight: 600;
        }}
        QPushButton#primaryButton {{
            background-color: {CORES["accent"]};
            border-color: {CORES["accent"]};
            color: white;
            font-weight: 600;
        }}
        QPushButton#primaryButton:hover {{
            background-color: {CORES["accent_hover"]};
        }}
        QPushButton#toggleButton {{
            min-width: 132px;
            min-height: 34px;
            border-radius: 17px;
            padding: 6px 14px;
            text-align: center;
        }}
        QPushButton#toggleButton[state="active"] {{
            background-color: {CORES["green"]};
            border-color: {CORES["green"]};
            color: white;
            font-weight: 600;
        }}
        QPushButton#toggleButton[state="active"]:hover {{
            background-color: {CORES["green_hover"]};
        }}
        QPushButton#toggleButton[state="inactive"] {{
            background-color: {CORES["surface_alt"]};
            border-color: {CORES["border"]};
            color: {CORES["muted"]};
        }}
        QPushButton#toggleButton[state="unknown"] {{
            background-color: {CORES["surface_alt"]};
            border-color: {CORES["border"]};
            color: {CORES["muted"]};
        }}
        QLineEdit {{
            background-color: {CORES["surface_alt"]};
            border: 1px solid {CORES["border"]};
            border-radius: 6px;
            padding: 9px;
            selection-background-color: {CORES["accent"]};
        }}
        QPlainTextEdit {{
            background-color: {CORES["surface"]};
            border: 1px solid {CORES["border"]};
            border-radius: 8px;
            padding: 8px;
            font-family: Consolas, "Cascadia Mono", monospace;
            font-size: 9pt;
        }}
        QProgressBar {{
            background-color: {CORES["surface_alt"]};
            border: none;
            border-radius: 4px;
            min-height: 19px;
            max-height: 8px;
        }}
        QProgressBar::chunk {{
            background-color: {CORES["accent"]};
            border-radius: 4px;
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 9px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {CORES["border"]};
            min-height: 26px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QToolTip {{
            background-color: {CORES["surface_alt"]};
            color: {CORES["text"]};
            border: 1px solid {CORES["border"]};
            padding: 5px;
        }}
    """


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
                self.resultado.emit(bool(sucesso), str(mensagem))
            elif isinstance(resultado, str):
                mensagem = resultado
                indicios_erro = ("Erro", "⚠️", "Falha", "Não foi possível")
                self.resultado.emit(
                    not mensagem.lstrip().startswith(indicios_erro),
                    mensagem,
                )
            elif isinstance(resultado, bool):
                self.resultado.emit(
                    resultado,
                    "Operação concluída." if resultado else "A operação falhou.",
                )
            else:
                self.resultado.emit(
                    False,
                    "A operação não devolveu um resultado reconhecido.",
                )
        except Exception as erro:
            self.resultado.emit(False, f"Erro inesperado: {erro}")


class CopiaPastasWorker(QThread):
    progresso = pyqtSignal(int, str)
    resultado = pyqtSignal(bool, str)

    def __init__(self, origem, destino):
        super().__init__()
        self.origem = Path(origem)
        self.destino = Path(destino)

    @staticmethod
    def _esta_dentro(caminho, raiz):
        try:
            caminho.relative_to(raiz)
            return True
        except ValueError:
            return False

    def run(self):
        pasta_criada = None
        try:
            origem = self.origem.resolve(strict=True)
            destino = self.destino.resolve(strict=True)
            if not origem.is_dir() or not destino.is_dir():
                raise ValueError("A origem e o destino têm de ser pastas existentes.")
            if origem == destino or self._esta_dentro(destino, origem):
                raise ValueError("O destino não pode ser a origem nem estar dentro dela.")

            pasta_criada = destino / origem.name
            if pasta_criada.exists():
                raise FileExistsError(
                    f"A pasta de destino já existe e não será sobrescrita: {pasta_criada}"
                )

            self.progresso.emit(0, "A analisar ficheiros...")
            ficheiros = []
            diretorios = []
            total_bytes = 0
            pastas_ignoradas = 0
            links_ignoradas = 0

            def erro_caminhada(erro):
                raise erro

            for raiz_atual, pastas, nomes in os.walk(
                origem, topdown=True, followlinks=False, onerror=erro_caminhada
            ):
                caminho_atual = Path(raiz_atual)
                pastas_validas = []
                for nome_pasta in pastas:
                    caminho_pasta = caminho_atual / nome_pasta
                    if caminho_pasta.is_symlink():
                        pastas_ignoradas += 1
                    else:
                        pastas_validas.append(nome_pasta)
                pastas[:] = pastas_validas
                diretorios.extend(
                    caminho_atual / nome_pasta for nome_pasta in pastas_validas
                )

                for nome in nomes:
                    ficheiro = caminho_atual / nome
                    if ficheiro.is_symlink():
                        links_ignoradas += 1
                        continue
                    tamanho = ficheiro.stat().st_size
                    ficheiros.append((ficheiro, tamanho))
                    total_bytes += tamanho

            pasta_criada.mkdir()
            for diretorio in diretorios:
                (pasta_criada / diretorio.relative_to(origem)).mkdir(
                    parents=True, exist_ok=True
                )
            bytes_copiados = 0
            ficheiros_copiados = 0
            total_ficheiros = len(ficheiros)

            for ficheiro, tamanho in ficheiros:
                caminho_relativo = ficheiro.relative_to(origem)
                destino_ficheiro = pasta_criada / caminho_relativo
                destino_ficheiro.parent.mkdir(parents=True, exist_ok=True)

                with ficheiro.open("rb") as entrada:
                    with destino_ficheiro.open("xb") as saida:
                        while True:
                            bloco = entrada.read(1024 * 1024)
                            if not bloco:
                                break
                            saida.write(bloco)
                            bytes_copiados += len(bloco)
                            if total_bytes:
                                percentagem = int(bytes_copiados * 100 / total_bytes)
                            elif total_ficheiros:
                                percentagem = int(
                                    (ficheiros_copiados + 1) * 100 / total_ficheiros
                                )
                            else:
                                percentagem = 100
                            self.progresso.emit(
                                min(percentagem, 100),
                                f"A copiar {caminho_relativo}",
                            )

                shutil.copystat(ficheiro, destino_ficheiro)
                ficheiros_copiados += 1
                if tamanho == 0 and total_ficheiros:
                    if total_bytes:
                        percentagem = int(bytes_copiados * 100 / total_bytes)
                    else:
                        percentagem = int(
                            ficheiros_copiados * 100 / total_ficheiros
                        )
                    self.progresso.emit(
                        percentagem,
                        f"A copiar {caminho_relativo}",
                    )

            self.progresso.emit(100, "Cópia concluída.")
            mensagem = (
                f"Cópia concluída: {ficheiros_copiados} ficheiro(s) em "
                f"{pasta_criada}. A origem foi mantida."
            )
            total_links_ignorados = pastas_ignoradas + links_ignoradas
            if total_links_ignorados:
                mensagem += (
                    f" {total_links_ignorados} ligação(ões) simbólica(s) ignorada(s)."
                )
            self.resultado.emit(True, mensagem)
        except Exception as erro:
            self.resultado.emit(
                False,
                f"Erro durante a cópia: {erro}. "
                "Se a operação já tinha começado, os ficheiros copiados parcialmente "
                "foram deixados na pasta de destino para inspeção.",
            )


class CartaoOtimizar(QFrame):
    def __init__(self, titulo, descricao, reversivel=True, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.estado = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 13, 16, 13)
        layout.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("font-size: 11pt; font-weight: 600;")
        descricao_label = QLabel(descricao)
        descricao_label.setObjectName("muted")
        descricao_label.setWordWrap(True)
        descricao_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        textos.addWidget(titulo_label)
        textos.addWidget(descricao_label)
        layout.addLayout(textos, 1)

        self.botao = QPushButton()
        self.botao.setMinimumWidth(132)
        if reversivel:
            self.botao.setObjectName("toggleButton")
            self.botao.setCheckable(True)
            self.botao.setText("Estado desconhecido")
            self.botao.setToolTip(
                "O estado do Windows não é consultado ao iniciar. "
                "Este indicador regista as alterações feitas nesta sessão."
            )
            self._atualizar_estilo("unknown")
        else:
            self.botao.setObjectName("primaryButton")
            self.botao.setText("Executar")
        layout.addWidget(self.botao)

    def definir_estado(self, estado):
        self.estado = estado
        if estado is None:
            texto, propriedade = "Estado desconhecido", "unknown"
            marcado = False
        elif estado:
            texto, propriedade = "Ativado", "active"
            marcado = True
        else:
            texto, propriedade = "Desativado", "inactive"
            marcado = False
        self.botao.blockSignals(True)
        self.botao.setChecked(marcado)
        self.botao.setText(texto)
        self.botao.blockSignals(False)
        self._atualizar_estilo(propriedade)

    def _atualizar_estilo(self, estado):
        self.botao.setProperty("state", estado)
        self.botao.style().unpolish(self.botao)
        self.botao.style().polish(self.botao)
        self.botao.update()


class OtimizadorPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self._worker = None
        self._botao_em_execucao = None
        self._cartao_em_execucao = None
        self._estado_anterior_toggle = None
        self._toggle_pretendido = None
        self.otimizador_sistema = OtimizadorSistema()
        self.otimizador_rede = OtimizadorRede()
        self.otimizador_privacidade = OtimizadorPrivacidade()
        self.otimizador_amd = OtimizadorAMD()
        self.otimizador_mouse_teclado = OtimizadorMouseTeclado()
        self.otimizador_audio = OtimizadorAudio()

        aplicacao = QApplication.instance()
        if aplicacao is None:
            raise RuntimeError("É necessário criar QApplication antes da janela.")
        aplicacao.setStyleSheet(criar_folha_estilo())

        self.setWindowTitle(f"{NOME_APLICACAO} — Centro de Controlo")
        self.setMinimumSize(760, 560)
        self.resize(1180, 780)

        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.setCentralWidget(central)

        self.sidebar = self._criar_sidebar()
        central_layout.addWidget(self.sidebar)

        area_principal = QWidget()
        area_layout = QVBoxLayout(area_principal)
        area_layout.setContentsMargins(28, 22, 28, 14)
        area_layout.setSpacing(14)
        central_layout.addWidget(area_principal, 1)

        self.titulo_pagina = QLabel()
        self.titulo_pagina.setObjectName("pageTitle")
        self.titulo_pagina.setWordWrap(True)
        self.subtitulo_pagina = QLabel()
        self.subtitulo_pagina.setObjectName("muted")
        self.subtitulo_pagina.setWordWrap(True)
        area_layout.addWidget(self.titulo_pagina)
        area_layout.addWidget(self.subtitulo_pagina)

        self.paginas = QStackedWidget()
        self.paginas.addWidget(self._criar_pagina_dashboard())
        self.paginas.addWidget(self._criar_pagina_otimizacao())
        self.paginas.addWidget(self._criar_pagina_ficheiros())
        self.paginas.addWidget(self._criar_pagina_logs())
        area_layout.addWidget(self.paginas, 1)

        self.label_status = QLabel("Pronto.")
        self.label_status.setObjectName("muted")
        self.label_status.setWordWrap(True)
        area_layout.addWidget(self.label_status)

        self.ponte_logs = QtLogBridge()
        self.ponte_logs.mensagem.connect(self.adicionar_log)
        self.log_handler = QtLogHandler(self.ponte_logs)
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s  %(message)s", "%H:%M:%S")
        )
        logger.addHandler(self.log_handler)
        logger.info("Interface de dashboard iniciada.")

        self.metrics_timer = QTimer(self)
        self.metrics_timer.setInterval(2000)
        self.metrics_timer.timeout.connect(self.atualizar_metricas)
        self.atualizar_metricas()
        self.metrics_timer.start()
        self._mudar_pagina(0)

    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 22, 16, 16)
        layout.setSpacing(8)

        marca = QLabel("⚡  WINDOWS\n     OPTIMIZER")
        marca.setStyleSheet("font-size: 13pt; font-weight: 700;")
        marca.setWordWrap(True)
        layout.addWidget(marca)

        versao = QLabel(f"Versão {VERSAO}")
        versao.setObjectName("muted")
        layout.addWidget(versao)
        layout.addSpacing(22)

        self.botoes_navegacao = []
        for indice, texto in enumerate(
            ("▦  Dashboard", "⚙  Otimização", "▤  Gestor de ficheiros", "≡  Logs")
        ):
            botao = QPushButton(texto)
            botao.setObjectName("navButton")
            botao.setCheckable(True)
            botao.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            botao.clicked.connect(
                lambda *_, pagina=indice: self._mudar_pagina(pagina)
            )
            layout.addWidget(botao)
            self.botoes_navegacao.append(botao)

        layout.addStretch()
        rodape = QLabel("Monitorização local\nAtualização a cada 2 segundos")
        rodape.setObjectName("muted")
        rodape.setWordWrap(True)
        layout.addWidget(rodape)
        return sidebar

    def _mudar_pagina(self, indice):
        self.paginas.setCurrentIndex(indice)
        for posicao, botao in enumerate(self.botoes_navegacao):
            ativo = posicao == indice
            botao.blockSignals(True)
            botao.setChecked(ativo)
            botao.setProperty("active", "true" if ativo else "false")
            botao.style().unpolish(botao)
            botao.style().polish(botao)
            botao.blockSignals(False)
        titulos = (
            ("Dashboard", "Visão geral do desempenho e armazenamento do computador."),
            ("Otimização", "Ações do sistema. As reversões disponíveis são indicadas por toggle."),
            ("Gestor de ficheiros", "Cópia segura de pastas: a origem permanece intacta."),
            ("Logs", "Atividade e mensagens dos módulos da aplicação."),
        )
        self.titulo_pagina.setText(titulos[indice][0])
        self.subtitulo_pagina.setText(titulos[indice][1])

    def _criar_pagina_dashboard(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(14)

        introducao = self._criar_cartao()
        intro_layout = QVBoxLayout(introducao)
        intro_layout.setContentsMargins(18, 16, 18, 16)
        saudacao = QLabel("Estado do sistema")
        saudacao.setStyleSheet("font-size: 13pt; font-weight: 600;")
        self.label_atualizacao = QLabel("A recolher métricas...")
        self.label_atualizacao.setObjectName("muted")
        self.label_atualizacao.setWordWrap(True)
        intro_layout.addWidget(saudacao)
        intro_layout.addWidget(self.label_atualizacao)
        layout.addWidget(introducao)

        grelha = QHBoxLayout()
        grelha.setSpacing(14)
        self.metricas = {}
        for chave, titulo in (
            ("cpu", "Utilização da CPU"),
            ("temperature", "Temperatura"),
            ("c", "Disco SSD (C:)"),
            ("d", "Disco HD (D:)"),
        ):
            cartao = self._criar_cartao()
            cartao_layout = QVBoxLayout(cartao)
            cartao_layout.setContentsMargins(16, 15, 16, 15)
            cartao_layout.setSpacing(9)
            label_titulo = QLabel(titulo)
            label_titulo.setWordWrap(True)
            label_valor = QLabel("—")
            label_valor.setObjectName("metricValue")
            label_valor.setWordWrap(True)
            label_detalhe = QLabel("A aguardar dados")
            label_detalhe.setObjectName("muted")
            label_detalhe.setWordWrap(True)
            barra = QProgressBar()
            barra.setTextVisible(False)
            barra.setRange(0, 100)
            barra.setValue(0)
            barra.setVisible(chave != "temperature")
            cartao_layout.addWidget(label_titulo)
            cartao_layout.addWidget(label_valor)
            cartao_layout.addWidget(label_detalhe)
            cartao_layout.addStretch()
            cartao_layout.addWidget(barra)
            self.metricas[chave] = {
                "valor": label_valor,
                "detalhe": label_detalhe,
                "barra": barra,
            }
            grelha.addWidget(cartao, 1)
        layout.addLayout(grelha)

        nota = QLabel(
            "A temperatura depende dos sensores expostos pelo hardware e pelo Windows; "
            "quando não está disponível, é apresentada como tal."
        )
        nota.setObjectName("muted")
        nota.setWordWrap(True)
        layout.addWidget(nota)
        layout.addStretch()
        return pagina

    def _criar_pagina_otimizacao(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        nota = QLabel(
            "Os toggles começam como desconhecidos: a aplicação não consulta "
            "automaticamente as definições atuais do Windows. Só mudam após uma "
            "operação bem-sucedida. Ações sem reversão são apresentadas como execução única."
        )
        nota.setObjectName("muted")
        nota.setWordWrap(True)
        layout.addWidget(nota)

        area = QScrollArea()
        area.setWidgetResizable(True)
        conteudo = QWidget()
        lista = QVBoxLayout(conteudo)
        lista.setContentsMargins(2, 4, 8, 4)
        lista.setSpacing(10)

        def adicionar_toggle(titulo, descricao, ativar, desativar):
            cartao = CartaoOtimizar(titulo, descricao, reversivel=True)
            cartao.botao.toggled.connect(
                lambda ativado, c=cartao, ligar=ativar, desligar=desativar:
                self._alternar_otimizacao(c, ativado, ligar, desligar)
            )
            lista.addWidget(cartao)
            return cartao

        def adicionar_acao(titulo, descricao, tarefa, em_progresso):
            cartao = CartaoOtimizar(titulo, descricao, reversivel=False)
            cartao.botao.clicked.connect(
                lambda *_, c=cartao, fn=tarefa, texto=em_progresso:
                self._executar_acao(c, fn, texto)
            )
            lista.addWidget(cartao)

        adicionar_toggle(
            "Plano de energia — Desempenho Máximo",
            "Guarda o plano atual antes de ativar. O toggle de desativação restaura esse plano.",
            self.otimizador_sistema.ativar_desempenho_maximo,
            self.otimizador_sistema.reverter_plano_energia,
        )
        adicionar_toggle(
            "Serviço de telemetria (DiagTrack)",
            "Guarda o estado do serviço e permite restaurá-lo através do backup criado.",
            self.otimizador_privacidade.desativar_servico_telemetria,
            self.otimizador_privacidade.restaurar_servico_telemetria,
        )
        adicionar_toggle(
            "Ajustes de rede TCP/IP",
            "Guarda a configuração TCP/IP atual antes de aplicar; desativar restaura o backup.",
            self.otimizador_rede.aplicar_tweaks_tcp_ip,
            self.otimizador_rede.restaurar_tweaks_tcp_ip,
        )
        adicionar_toggle(
            "AMD MPO",
            "Desativa o Multi-Plane Overlay; pode ser reativado pela ação de reversão.",
            self.otimizador_amd.desativar_mpo_registro,
            self.otimizador_amd.reativar_mpo_padrao,
        )
        adicionar_toggle(
            "Agendamento de GPU (HAGS)",
            "Ativa o HAGS. A alteração pode exigir reiniciar o computador.",
            self.otimizador_amd.configurar_hags_gpu,
            self.otimizador_amd.redefinir_hags_padrao,
        )

        adicionar_acao(
            "Limpeza de temporários e cache",
            "Remove ficheiros nas pastas temporárias configuradas pelo projeto. A limpeza não é reversível.",
            self.otimizador_sistema.limpeza_profunda_sistema,
            "A limpar ficheiros temporários...",
        )
        adicionar_toggle(
            "Otimizar prioridade de jogos (MMCSS)",
            "Guarda os valores atuais do Registo e permite restaurá-los ao desativar.",
            self.otimizador_sistema.otimizar_mmcss_jogos,
            self.otimizador_sistema.restaurar_mmcss_jogos,
        )
        adicionar_toggle(
            "Aplicar DNS Cloudflare",
            "Guarda o DNS atual dos adaptadores físicos ativos e restaura-o ao desativar.",
            self.otimizador_rede.alterar_dns_cloudflare,
            self.otimizador_rede.restaurar_dns,
        )
        adicionar_toggle(
            "Otimizar rato",
            "Guarda as definições atuais do rato e restaura-as ao desativar.",
            self.otimizador_mouse_teclado.otimizar_mouse,
            self.otimizador_mouse_teclado.restaurar_mouse,
        )

        lista.addStretch()
        area.setWidget(conteudo)
        layout.addWidget(area, 1)
        return pagina

    def _criar_pagina_ficheiros(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(14)

        cartao = self._criar_cartao()
        cartao_layout = QVBoxLayout(cartao)
        cartao_layout.setContentsMargins(18, 18, 18, 18)
        cartao_layout.setSpacing(12)

        titulo = QLabel("Copiar pastas para outra unidade")
        titulo.setStyleSheet("font-size: 13pt; font-weight: 600;")
        explicacao = QLabel(
            "Escolhe uma pasta de origem e uma pasta de destino. A pasta de origem "
            "será copiada para dentro do destino; não será movida nem apagada. "
            "Para evitar sobrescritas, a cópia é recusada se já existir uma pasta "
            "com o mesmo nome no destino. Ligações simbólicas são ignoradas."
        )
        explicacao.setObjectName("muted")
        explicacao.setWordWrap(True)
        cartao_layout.addWidget(titulo)
        cartao_layout.addWidget(explicacao)

        self.campo_origem = self._criar_campo_pasta(
            cartao_layout, "Pasta de origem (por exemplo, unidade SSD)"
        )
        self.campo_destino = self._criar_campo_pasta(
            cartao_layout, "Pasta de destino (por exemplo, unidade HD)"
        )

        self.barra_copia = QProgressBar()
        self.barra_copia.setRange(0, 100)
        self.barra_copia.setValue(0)
        self.estado_copia = QLabel("Pronto para copiar.")
        self.estado_copia.setObjectName("muted")
        self.estado_copia.setWordWrap(True)
        self.botao_copiar = QPushButton("Iniciar cópia segura")
        self.botao_copiar.setObjectName("primaryButton")
        self.botao_copiar.clicked.connect(self._iniciar_copia)
        cartao_layout.addWidget(self.barra_copia)
        cartao_layout.addWidget(self.estado_copia)
        cartao_layout.addWidget(self.botao_copiar)
        layout.addWidget(cartao)
        layout.addStretch()
        return pagina

    def _criar_campo_pasta(self, layout, placeholder):
        linha = QHBoxLayout()
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setClearButtonEnabled(True)
        botao = QPushButton("Selecionar...")
        botao.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        botao.clicked.connect(
            lambda *_, entrada=campo, texto=placeholder:
            self._selecionar_pasta(entrada, texto)
        )
        linha.addWidget(campo, 1)
        linha.addWidget(botao)
        layout.addLayout(linha)
        return campo

    def _criar_pagina_logs(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 4, 0, 0)
        self.consola_logs = QPlainTextEdit()
        self.consola_logs.setReadOnly(True)
        self.consola_logs.setPlaceholderText(
            "As mensagens de atividade e erros serão apresentadas aqui."
        )
        layout.addWidget(self.consola_logs)
        return pagina

    @staticmethod
    def _criar_cartao():
        cartao = QFrame()
        cartao.setObjectName("card")
        cartao.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        return cartao

    def atualizar_metricas(self):
        if psutil is None:
            for dados in self.metricas.values():
                dados["valor"].setText("Indisponível")
                dados["detalhe"].setText("Instale a dependência psutil para ativar métricas.")
                dados["barra"].setValue(0)
            self.label_atualizacao.setText("psutil não está instalado.")
            return

        uso_cpu = None
        try:
            uso_cpu = psutil.cpu_percent(interval=None)
            self.metricas["cpu"]["valor"].setText(f"{uso_cpu:.0f}%")
            self.metricas["cpu"]["detalhe"].setText("Utilização atual")
            self.metricas["cpu"]["barra"].setValue(round(uso_cpu))
        except (OSError, RuntimeError) as erro:
            self.metricas["cpu"]["valor"].setText("Indisponível")
            self.metricas["cpu"]["detalhe"].setText(str(erro))
            logger.warning("Não foi possível ler a utilização da CPU: %s", erro)

        temperatura = self._obter_temperatura()
        self.metricas["temperature"]["valor"].setText(
            f"{temperatura:.1f} °C" if temperatura is not None else "Indisponível"
        )
        self.metricas["temperature"]["detalhe"].setText(
            "Temperatura do sistema"
            if temperatura is not None
            else "Sensor térmico não exposto pelo sistema."
        )

        for letra in ("c", "d"):
            try:
                disco = psutil.disk_usage(f"{letra.upper()}:\\")
                usado_percentagem = round(disco.percent)
                usados_gb = (disco.total - disco.free) / (1024**3)
                total_gb = disco.total / (1024**3)
                livre_gb = disco.free / (1024**3)
                self.metricas[letra]["valor"].setText(f"{usado_percentagem}% usado")
                self.metricas[letra]["detalhe"].setText(
                    f"{usados_gb:.1f} GB usados de {total_gb:.1f} GB · "
                    f"{livre_gb:.1f} GB livres"
                )
                self.metricas[letra]["barra"].setValue(usado_percentagem)
            except (OSError, PermissionError, ValueError) as erro:
                self.metricas[letra]["valor"].setText("Indisponível")
                self.metricas[letra]["detalhe"].setText(
                    f"Unidade não encontrada ou inacessível: {erro}"
                )
                self.metricas[letra]["barra"].setValue(0)

        self.label_atualizacao.setText(
            f"Métricas atualizadas automaticamente a cada 2 segundos · "
            + (f"CPU {uso_cpu:.0f}%" if uso_cpu is not None else "CPU indisponível")
        )

    @staticmethod
    def _obter_temperatura():
        if psutil is None:
            return None
        obter_sensores = getattr(psutil, "sensors_temperatures", None)
        if not callable(obter_sensores):
            return None
        try:
            sensores = obter_sensores(fahrenheit=False)
            if not sensores:
                return None
            for leituras in sensores.values():
                for leitura in leituras:
                    atual = getattr(leitura, "current", None)
                    if atual is not None:
                        valor = float(atual)
                        if math.isfinite(valor):
                            return valor
        except (
            AttributeError,
            OSError,
            RuntimeError,
            NotImplementedError,
            TypeError,
            ValueError,
        ):
            logger.debug("Leitura de temperatura indisponível nesta plataforma.")
        return None

    def _alternar_otimizacao(
        self, cartao, ativar, funcao_ativar, funcao_desativar
    ):
        estado_anterior = cartao.estado
        tarefa = funcao_ativar if ativar else funcao_desativar
        texto = (
            "A ativar a otimização..."
            if ativar
            else "A restaurar a configuração..."
        )
        self._iniciar_tarefa(
            tarefa,
            cartao.botao,
            texto,
            cartao=cartao,
            estado_anterior=estado_anterior,
            estado_pretendido=ativar,
        )

    def _executar_acao(self, cartao, tarefa, texto):
        self._iniciar_tarefa(tarefa, cartao.botao, texto)

    def _iniciar_tarefa(
        self,
        tarefa,
        botao,
        mensagem,
        cartao=None,
        estado_anterior=None,
        estado_pretendido=None,
    ):
        if self._worker is not None and self._worker.isRunning():
            if cartao is not None:
                cartao.definir_estado(estado_anterior)
            self.atualizar_status("Aguarde que a operação atual termine.")
            return

        if cartao is not None and estado_pretendido is not None:
            cartao.definir_estado(estado_pretendido)
        self._botao_em_execucao = botao
        self._cartao_em_execucao = cartao
        self._estado_anterior_toggle = estado_anterior
        self._toggle_pretendido = estado_pretendido
        botao.setEnabled(False)
        if cartao is not None:
            cartao.botao.setText("A processar...")
        self.atualizar_status(mensagem)

        self._worker = TarefaWorker(tarefa)
        self._worker.resultado.connect(self._resultado_tarefa)
        self._worker.finished.connect(self._finalizar_tarefa)
        self._worker.start()

    def _resultado_tarefa(self, sucesso, mensagem):
        self.atualizar_status(mensagem)
        if sucesso:
            logger.info(mensagem)
            if self._cartao_em_execucao is not None:
                self._cartao_em_execucao.definir_estado(self._toggle_pretendido)
        else:
            logger.error(mensagem)
            if self._cartao_em_execucao is not None:
                self._cartao_em_execucao.definir_estado(
                    self._estado_anterior_toggle
                )

    def _finalizar_tarefa(self):
        if self._botao_em_execucao is not None:
            self._botao_em_execucao.setEnabled(True)
        self._botao_em_execucao = None
        self._cartao_em_execucao = None
        self._estado_anterior_toggle = None
        self._toggle_pretendido = None
        self._worker = None

    def _selecionar_pasta(self, campo, titulo):
        pasta = QFileDialog.getExistingDirectory(self, titulo, campo.text())
        if pasta:
            campo.setText(pasta)

    def _iniciar_copia(self):
        origem = self.campo_origem.text().strip()
        destino = self.campo_destino.text().strip()
        if not origem or not destino:
            QMessageBox.warning(
                self,
                "Pastas em falta",
                "Seleciona uma pasta de origem e uma pasta de destino.",
            )
            return
        if self._worker is not None and self._worker.isRunning():
            self.atualizar_status("Aguarde que a operação atual termine.")
            return

        self.barra_copia.setValue(0)
        self.botao_copiar.setEnabled(False)
        self.atualizar_status("A preparar a cópia...")
        self.estado_copia.setText("A preparar a cópia...")
        self._botao_em_execucao = self.botao_copiar
        self._worker = CopiaPastasWorker(origem, destino)
        self._worker.progresso.connect(self._atualizar_progresso_copia)
        self._worker.resultado.connect(self._resultado_copia)
        self._worker.finished.connect(self._finalizar_tarefa)
        self._worker.start()

    def _atualizar_progresso_copia(self, valor, mensagem):
        self.barra_copia.setValue(valor)
        self.estado_copia.setText(mensagem)

    def _resultado_copia(self, sucesso, mensagem):
        self.atualizar_status(mensagem)
        self.estado_copia.setText(mensagem)
        if sucesso:
            logger.info(mensagem)
        else:
            logger.error(mensagem)

    def adicionar_log(self, mensagem):
        self.consola_logs.appendPlainText(mensagem)
        cursor = self.consola_logs.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.consola_logs.setTextCursor(cursor)

    def atualizar_status(self, mensagem):
        self.label_status.setText(mensagem)

    def closeEvent(self, evento):
        if self._worker is not None and self._worker.isRunning():
            QMessageBox.information(
                self,
                "Operação em curso",
                "Aguarda que a operação em curso termine antes de fechar a aplicação.",
            )
            evento.ignore()
            return
        self.metrics_timer.stop()
        logger.removeHandler(self.log_handler)
        self.log_handler.close()
        super().closeEvent(evento)


class QtLogBridge(QObject):
    mensagem = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    def __init__(self, ponte):
        super().__init__()
        self.ponte = ponte

    def emit(self, registro):
        try:
            self.ponte.mensagem.emit(self.format(registro))
        except RuntimeError:
            self.handleError(registro)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(NOME_APLICACAO)
    app.setApplicationVersion(VERSAO)
    janela = OtimizadorPyQt()
    janela.show()
    sys.exit(app.exec())
