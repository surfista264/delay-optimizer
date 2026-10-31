"""Ajustes de telemetria, diagnóstico e identificador de publicidade."""

import ctypes
import json
import re
import subprocess
import winreg

from config import (
    DIRETORIO_DADOS_APLICACAO,
    FICHEIRO_BACKUP_DIAGTRACK,
    SERVICO_DIAGTRACK,
)
from logger import logger


class OtimizadorPrivacidade:
    """Controla as definições de privacidade do Windows."""

    @staticmethod
    def _backup_servico_path():
        try:
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            logger.info("Diretório de backup DiagTrack preparado.")
            return str(FICHEIRO_BACKUP_DIAGTRACK)
        except Exception as erro:
            logger.error("Erro ao preparar backup DiagTrack: %s", erro)
            raise

    @staticmethod
    def _is_admin():
        try:
            autorizado = bool(ctypes.windll.shell32.IsUserAnAdmin())
            logger.info("Verificação de privilégios de administrador: %s", autorizado)
            return autorizado
        except Exception as erro:
            logger.error("Erro ao verificar privilégios: %s", erro)
            return False

    @staticmethod
    def desativar_servico_telemetria():
        try:
            if not OtimizadorPrivacidade._is_admin():
                logger.error("Privilégios administrativos necessários para DiagTrack.")
                return "Erro: Necessário privilégios de Administrador."
            backup = FICHEIRO_BACKUP_DIAGTRACK
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                caminho_registro = rf"SYSTEM\CurrentControlSet\Services\{SERVICO_DIAGTRACK}"
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    caminho_registro,
                    0,
                    winreg.KEY_READ,
                ) as chave:
                    start_type, _ = winreg.QueryValueEx(chave, "Start")
                estado = subprocess.run(
                    ["sc", "query", SERVICO_DIAGTRACK],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                if estado.returncode != 0:
                    raise RuntimeError(estado.stderr.strip() or estado.stdout.strip())
                correspondencia = re.search(
                    r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE
                )
                if correspondencia is None:
                    raise RuntimeError("Não foi possível determinar o estado do DiagTrack.")
                with backup.open("x", encoding="utf-8") as arquivo:
                    json.dump(
                        {
                            "start_type": int(start_type),
                            "was_running": int(correspondencia.group(1)) == 4,
                        },
                        arquivo,
                    )
            with backup.open("r", encoding="utf-8") as arquivo:
                anterior = json.load(arquivo)
            if (
                not isinstance(anterior.get("start_type"), int)
                or not isinstance(anterior.get("was_running"), bool)
            ):
                raise ValueError("A cópia da configuração do DiagTrack é inválida.")

            estado = subprocess.run(
                ["sc", "query", SERVICO_DIAGTRACK],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            atual = re.search(r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE)
            if estado.returncode != 0 or atual is None:
                raise RuntimeError(estado.stderr.strip() or "Estado do serviço indisponível.")
            if int(atual.group(1)) == 4:
                parar = subprocess.run(
                    ["sc", "stop", SERVICO_DIAGTRACK],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                if parar.returncode != 0:
                    raise RuntimeError(parar.stderr.strip() or parar.stdout.strip())
            resultado = subprocess.run(
                ["sc", "config", SERVICO_DIAGTRACK, "start=", "disabled"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            logger.info("Serviço DiagTrack desativado; backup guardado em %s.", backup)
            return "✅ Serviço de telemetria (DiagTrack) desativado com sucesso."
        except Exception as erro:
            logger.error("Erro ao desativar DiagTrack: %s", erro)
            return f"Erro ao desativar DiagTrack: {erro}"

    @staticmethod
    def restaurar_servico_telemetria():
        try:
            if not OtimizadorPrivacidade._is_admin():
                logger.error("Privilégios administrativos necessários para restaurar DiagTrack.")
                return "Erro: Necessário privilégios de Administrador."
            backup = FICHEIRO_BACKUP_DIAGTRACK
            if not backup.exists():
                logger.error("Backup de DiagTrack não encontrado.")
                return "Erro: não há cópia da configuração anterior do DiagTrack."
            with backup.open("r", encoding="utf-8") as arquivo:
                anterior = json.load(arquivo)
            start_type = anterior.get("start_type")
            was_running = anterior.get("was_running")
            tipos_inicio = {0: "boot", 1: "system", 2: "auto", 3: "demand", 4: "disabled"}
            if (
                not isinstance(start_type, int)
                or start_type not in tipos_inicio
                or not isinstance(was_running, bool)
            ):
                raise ValueError("A cópia da configuração do DiagTrack é inválida.")
            resultado = subprocess.run(
                [
                    "sc",
                    "config",
                    SERVICO_DIAGTRACK,
                    "start=",
                    tipos_inicio[start_type],
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            if was_running:
                estado = subprocess.run(
                    ["sc", "query", SERVICO_DIAGTRACK],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                correspondencia = re.search(
                    r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE
                )
                if estado.returncode != 0 or correspondencia is None:
                    raise RuntimeError(
                        estado.stderr.strip()
                        or "Não foi possível consultar o estado do DiagTrack."
                    )
                if int(correspondencia.group(1)) != 4:
                    iniciar = subprocess.run(
                        ["sc", "start", SERVICO_DIAGTRACK],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        check=False,
                    )
                    if iniciar.returncode != 0:
                        raise RuntimeError(
                            iniciar.stderr.strip() or iniciar.stdout.strip()
                        )
            backup.unlink()
            logger.info("Configuração do DiagTrack restaurada.")
            return "✅ Configuração anterior do serviço DiagTrack restaurada."
        except Exception as erro:
            logger.error("Erro ao restaurar DiagTrack: %s", erro)
            return f"Erro ao restaurar DiagTrack: {erro}"

    @staticmethod
    def restringir_dados_diagnostico():
        try:
            if not OtimizadorPrivacidade._is_admin():
                logger.error("Privilégios administrativos necessários para restringir telemetria.")
                return "Erro: Necessário privilégios de Administrador."
            resultado = subprocess.run(
                [
                    "reg",
                    "add",
                    r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                    "/v",
                    "AllowTelemetry",
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
            logger.info("Nível de dados de diagnóstico restringido.")
            return "✅ Coleta de dados de diagnóstico restrita ao nível mínimo."
        except Exception as erro:
            logger.error("Erro ao restringir dados de diagnóstico: %s", erro)
            return f"Erro ao restringir dados de diagnóstico: {erro}"

    @staticmethod
    def restrinjir_dados_diagnostico():
        try:
            logger.info("Usando o nome legado restrinjir_dados_diagnostico.")
            return OtimizadorPrivacidade.restringir_dados_diagnostico()
        except Exception as erro:
            logger.error("Erro no alias legado de telemetria: %s", erro)
            return f"Erro ao restringir dados de diagnóstico: {erro}"

    @staticmethod
    def desativar_id_publicidade():
        try:
            resultado = subprocess.run(
                [
                    "reg",
                    "add",
                    r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                    "/v",
                    "Enabled",
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
            logger.info("ID de publicidade desativado.")
            return "✅ ID de publicidade e rastreio comercial desativados."
        except Exception as erro:
            logger.error("Erro ao desativar ID de publicidade: %s", erro)
            return f"Erro ao desativar ID de publicidade: {erro}"
