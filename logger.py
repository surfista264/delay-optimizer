import logging
from logging import Logger

from config import CAMINHO_LOG


def configurar_logger() -> logging.Logger:
    """Configura uma única saída para o ficheiro de log da aplicação."""
    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.INFO)

    if not any(
        getattr(handler, "_windows_optimizer_file_handler", False)
        for handler in logger_raiz.handlers
    ):
        handler_ficheiro = logging.FileHandler(CAMINHO_LOG, encoding="utf-8")
        handler_ficheiro.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
        )
        setattr(handler_ficheiro, "_windows_optimizer_file_handler", True)
        logger_raiz.addHandler(handler_ficheiro)

    return logger_raiz


def obter_logger(nome: str | None = None) -> Logger:
    configurar_logger()
    return logging.getLogger(nome)


logger = obter_logger(__name__)
