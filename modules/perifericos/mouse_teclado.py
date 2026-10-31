"""Otimizações de teclado, rato e latência de entrada."""

import ctypes
import json
import subprocess
import winreg

from config import DIRETORIO_DADOS_APLICACAO
from logger import logger


class OtimizadorMouseTeclado:
    """Configura entrada de teclado e rato com cópia restaurável do rato."""

    @staticmethod
    def _is_admin():
        try:
            autorizado = bool(ctypes.windll.shell32.IsUserAnAdmin())
            logger.info("Verificação de privilégios de administrador: %s", autorizado)
            return autorizado
        except Exception as erro:
            logger.error("Erro ao verificar privilégios de administrador: %s", erro)
            return False

    @staticmethod
    def otimizar_teclado():
        try:
            caminho = r"Control Panel\Accessibility\Keyboard Response"
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                for nome, valor in (
                    ("Flags", "2"),
                    ("AutoRepeatDelay", "200"),
                    ("AutoRepeatRate", "6"),
                ):
                    winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, valor)
            logger.info("Resposta do teclado otimizada.")
            return True, "Teclado otimizado com sucesso."
        except Exception as erro:
            logger.error("Erro ao otimizar teclado: %s", erro)
            return False, f"Erro ao otimizar teclado: {erro}"

    @staticmethod
    def otimizar_velocidade_teclado_geral():
        try:
            caminho = r"Control Panel\Keyboard"
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                winreg.SetValueEx(chave, "KeyboardDelay", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(chave, "KeyboardSpeed", 0, winreg.REG_SZ, "31")
            logger.info("Velocidade geral do teclado otimizada.")
            return True, "Velocidade geral do teclado otimizada."
        except Exception as erro:
            logger.error("Erro ao otimizar velocidade do teclado: %s", erro)
            return False, f"Erro ao otimizar velocidade geral do teclado: {erro}"

    @staticmethod
    def otimizar_mouse():
        caminho = r"Control Panel\Mouse"
        nomes = ("MouseSpeed", "MouseThreshold1", "MouseThreshold2")
        backup = DIRETORIO_DADOS_APLICACAO / "mouse_backup.json"
        backup_criado = False
        try:
            if backup.exists():
                mensagem = "Existe uma cópia anterior do rato; restaura-a antes de aplicar novamente."
                logger.error(mensagem)
                return False, mensagem
            valores = {}
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, caminho, 0, winreg.KEY_QUERY_VALUE
            ) as chave:
                for nome in nomes:
                    try:
                        valor, tipo = winreg.QueryValueEx(chave, nome)
                        valores[nome] = {"value": valor, "type": tipo}
                    except FileNotFoundError:
                        valores[nome] = {"value": None, "type": None}
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            with backup.open("x", encoding="utf-8") as arquivo:
                json.dump(valores, arquivo, ensure_ascii=False)
            backup_criado = True
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                for nome in nomes:
                    winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, "0")
            logger.info("Aceleração do rato removida; backup criado em %s.", backup)
            return True, "A aceleração do mouse foi removida."
        except Exception as erro:
            if backup_criado:
                try:
                    OtimizadorMouseTeclado.restaurar_mouse()
                except Exception as erro_restauracao:
                    logger.error("Falha na restauração automática do rato: %s", erro_restauracao)
            logger.error("Erro ao otimizar rato: %s", erro)
            return False, f"Erro ao otimizar mouse: {erro}"

    @staticmethod
    def restaurar_mouse():
        caminho = r"Control Panel\Mouse"
        backup = DIRETORIO_DADOS_APLICACAO / "mouse_backup.json"
        try:
            if not backup.exists():
                mensagem = "Não existe uma cópia anterior das definições do rato."
                logger.error(mensagem)
                return False, mensagem
            with backup.open("r", encoding="utf-8") as arquivo:
                valores = json.load(arquivo)
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                for nome, entrada in valores.items():
                    if entrada.get("type") is None:
                        try:
                            winreg.DeleteValue(chave, nome)
                        except FileNotFoundError:
                            pass
                    else:
                        winreg.SetValueEx(
                            chave, nome, 0, entrada["type"], entrada["value"]
                        )
            backup.unlink()
            logger.info("Definições anteriores do rato restauradas.")
            return True, "Definições anteriores do rato restauradas."
        except Exception as erro:
            logger.error("Erro ao restaurar definições do rato: %s", erro)
            return False, f"Erro ao restaurar as definições do rato: {erro}"

    @staticmethod
    def ativar_modo_jogo_windows():
        try:
            if not OtimizadorMouseTeclado._is_admin():
                mensagem = "Erro: Necessário privilégios de Administrador."
                logger.error(mensagem)
                return mensagem
            resultado = subprocess.run(
                [
                    "reg",
                    "add",
                    r"HKCU\Software\Microsoft\GameBar",
                    "/v",
                    "AutoGameModeEnabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            logger.info("Modo de Jogo do Windows ativado.")
            return "✅ Modo de Jogo ativado com sucesso."
        except Exception as erro:
            logger.error("Erro ao ativar Modo de Jogo: %s", erro)
            return f"Erro ao ativar Modo de Jogo: {erro}"

    @staticmethod
    def otimizar_resposta_sistema():
        try:
            if not OtimizadorMouseTeclado._is_admin():
                mensagem = "Erro: Necessário privilégios de Administrador."
                logger.error(mensagem)
                return mensagem
            resultado = subprocess.run(
                [
                    "reg",
                    "add",
                    r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                    "/v",
                    "SystemResponsiveness",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            logger.info("Resposta de sistema ajustada para menor latência.")
            return "✅ Prioridade de resposta do sistema ajustada para latência mínima."
        except Exception as erro:
            logger.error("Erro ao ajustar resposta do sistema: %s", erro)
            return f"Erro ao ajustar resposta do sistema: {erro}"

    @staticmethod
    def executar_tudo():
        try:
            resultados = (
                OtimizadorMouseTeclado.otimizar_teclado(),
                OtimizadorMouseTeclado.otimizar_velocidade_teclado_geral(),
                OtimizadorMouseTeclado.otimizar_mouse(),
            )
            sucesso = all(resultado[0] for resultado in resultados)
            if not sucesso:
                raise RuntimeError("; ".join(resultado[1] for resultado in resultados if not resultado[0]))
            logger.info("Otimizações de mouse e teclado concluídas.")
            return True, "Otimizações de mouse e teclado concluídas."
        except Exception as erro:
            logger.error("Erro ao executar otimizações de mouse e teclado: %s", erro)
            return False, f"Erro ao otimizar mouse e teclado: {erro}"
