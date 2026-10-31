import sys

from PyQt6.QtWidgets import QApplication

from config import NOME_APLICACAO, VERSAO
from interface_pyqt import OtimizadorPyQt
from logger import configurar_logger

if __name__ == "__main__":
    configurar_logger()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(NOME_APLICACAO)
    app.setApplicationVersion(VERSAO)
    
    janela = OtimizadorPyQt()
    janela.show()
    sys.exit(app.exec())