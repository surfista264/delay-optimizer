import os
import sys
from pathlib import Path


NOME_APLICACAO = "Windows Ultimate Optimizer"
VERSAO = "0.3.1"
NOME_FICHEIRO_LOG = "otimizador.log"

SERVICO_DIAGTRACK = "DiagTrack"
SERVICO_SYSMAIN = "SysMain"
SERVICOS_MONITORIZADOS = (SERVICO_DIAGTRACK, SERVICO_SYSMAIN)

if getattr(sys, "frozen", False):
    DIRETORIO_APLICACAO = Path(sys.executable).resolve().parent
else:
    DIRETORIO_APLICACAO = Path(__file__).resolve().parent

CAMINHO_LOG = DIRETORIO_APLICACAO / NOME_FICHEIRO_LOG

_DIRETORIO_WINDOWS = Path(
    os.environ.get("SystemRoot") or os.environ.get("WINDIR") or r"C:\Windows"
)
_DIRETORIO_TEMP_UTILIZADOR = (
    Path(os.environ["TEMP"]) if os.environ.get("TEMP") else None
)

CAMINHOS_LIMPEZA = tuple(
    caminho
    for caminho in (
        _DIRETORIO_TEMP_UTILIZADOR,
        _DIRETORIO_WINDOWS / "Temp",
        _DIRETORIO_WINDOWS / "Prefetch",
    )
    if caminho is not None
)

DIRETORIO_DADOS_APLICACAO = (
    Path(
        os.environ.get("LOCALAPPDATA")
        or Path.home() / "AppData" / "Local"
    )
    / NOME_APLICACAO.replace(" ", "")
)
FICHEIRO_BACKUP_DIAGTRACK = DIRETORIO_DADOS_APLICACAO / "diagtrack_backup.json"
FICHEIRO_BACKUP_TCP = DIRETORIO_DADOS_APLICACAO / "tcp_global_backup.txt"
