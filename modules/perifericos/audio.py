"""Ajustes de prioridade para áudio e multimédia."""

import winreg

from logger import logger


class OtimizadorAudio:
    """Ajusta as prioridades de processamento de áudio no perfil Games."""

    @staticmethod
    def otimizar_prioridade_audio():
        try:
            caminho = (
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia"
                r"\SystemProfile\Tasks\Games"
            )
            configuracoes = {
                "Affinity": (winreg.REG_DWORD, 0),
                "Background Priority": (winreg.REG_SZ, "High"),
                "Latency": (winreg.REG_SZ, "Low"),
                "Scheduled": (winreg.REG_SZ, "Use CIO"),
                "SFIO Priority": (winreg.REG_SZ, "High"),
            }
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                for nome, (tipo, valor) in configuracoes.items():
                    winreg.SetValueEx(chave, nome, 0, tipo, valor)
            logger.info("Prioridade de áudio e tarefas multimídia otimizada.")
            return True, "Prioridade de áudio e headset otimizadas."
        except Exception as erro:
            logger.error("Erro ao otimizar prioridade de áudio: %s", erro)
            return False, f"Erro ao otimizar áudio: {erro}"
