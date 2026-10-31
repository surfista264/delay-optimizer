"""Módulos de otimização do Windows Ultimate Optimizer."""

from modules.privacidade import OtimizadorPrivacidade
from modules.rede import OtimizadorRede
from modules.sistema import OtimizadorSistema
from modules.perifericos.audio import OtimizadorAudio
from modules.perifericos.gpu_amd import OtimizadorAMD
from modules.perifericos.mouse_teclado import OtimizadorMouseTeclado

__all__ = [
    "OtimizadorAMD",
    "OtimizadorAudio",
    "OtimizadorMouseTeclado",
    "OtimizadorPrivacidade",
    "OtimizadorRede",
    "OtimizadorSistema",
]
