import sys
from PyQt6.QtWidgets import QApplication
from interface_pyqt import OtimizadorPyQt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    janela = OtimizadorPyQt()
    janela.show()
    sys.exit(app.exec())