"""Otimizações de DNS, adaptadores e pilha TCP/IP."""

import base64
import json
import subprocess

import winreg

from config import DIRETORIO_DADOS_APLICACAO, FICHEIRO_BACKUP_TCP
from logger import logger


class OtimizadorRede:
    """Aplica ajustes de conectividade que podem ser revertidos por backup."""

    @staticmethod
    def _backup_tcp_path():
        try:
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            logger.info("Diretório de backup TCP/IP preparado.")
            return str(FICHEIRO_BACKUP_TCP)
        except Exception as erro:
            logger.error("Erro ao preparar backup TCP/IP: %s", erro)
            raise

    @staticmethod
    def _executar_powershell(script):
        try:
            codificado = base64.b64encode(script.encode("utf-16le")).decode("ascii")
            resultado = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-EncodedCommand",
                    codificado,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                raise RuntimeError(detalhe or "O comando PowerShell falhou.")
            logger.info("Comando PowerShell de rede executado.")
            return resultado.stdout.strip()
        except Exception as erro:
            logger.error("Erro ao executar PowerShell de rede: %s", erro)
            raise

    @staticmethod
    def _obter_dns_adaptadores_ativos():
        try:
            script = (
                "$ErrorActionPreference='Stop';"
                "$entradas=@(Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | "
                "ForEach-Object {$i=$_.ifIndex; "
                "Get-DnsClientServerAddress -InterfaceIndex $i | "
                "ForEach-Object {[pscustomobject]@{InterfaceIndex=$i;"
                "AddressFamily=[int]$_.AddressFamily;"
                "ServerAddresses=@($_.ServerAddresses)}}});"
                "if($entradas.Count -eq 0){throw 'Nenhum adaptador físico ativo.'};"
                "ConvertTo-Json -InputObject @($entradas) -Depth 4 -Compress"
            )
            dados = json.loads(OtimizadorRede._executar_powershell(script))
            if isinstance(dados, dict):
                dados = [dados]
            if not isinstance(dados, list) or not dados:
                raise ValueError("Não foi possível obter as definições DNS atuais.")
            logger.info("DNS atual obtido para %s entrada(s).", len(dados))
            return dados
        except Exception as erro:
            logger.error("Erro ao consultar DNS dos adaptadores: %s", erro)
            raise

    @staticmethod
    def _executar_troca_dns(entradas):
        try:
            dados = base64.b64encode(
                json.dumps(entradas).encode("utf-8")
            ).decode("ascii")
            script = (
                "$ErrorActionPreference='Stop';"
                f"$json=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{dados}'));"
                "$entradas=@(ConvertFrom-Json -InputObject $json);"
                "foreach($entrada in $entradas){"
                "if(@($entrada.ServerAddresses).Count -gt 0){"
                "Set-DnsClientServerAddress -InterfaceIndex ([int]$entrada.InterfaceIndex) "
                "-AddressFamily ([int]$entrada.AddressFamily) "
                "-ServerAddresses @($entrada.ServerAddresses) -ErrorAction Stop"
                "}else{Set-DnsClientServerAddress -InterfaceIndex ([int]$entrada.InterfaceIndex) "
                "-AddressFamily ([int]$entrada.AddressFamily) "
                "-ResetServerAddresses -ErrorAction Stop}}"
            )
            OtimizadorRede._executar_powershell(script)
            logger.info("Configuração DNS dos adaptadores atualizada.")
        except Exception as erro:
            logger.error("Erro ao alterar DNS: %s", erro)
            raise

    @staticmethod
    def alterar_dns_cloudflare():
        backup = DIRETORIO_DADOS_APLICACAO / "dns_backup.json"
        backup_criado = False
        try:
            if backup.exists():
                return False, "Existe uma cópia DNS anterior; restaura-a antes de aplicar novamente."
            anteriores = OtimizadorRede._obter_dns_adaptadores_ativos()
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            with backup.open("x", encoding="utf-8") as arquivo:
                json.dump(anteriores, arquivo, ensure_ascii=False)
            backup_criado = True
            novos = []
            for entrada in anteriores:
                familia = int(entrada["AddressFamily"])
                servidores = {
                    2: ["1.1.1.1", "1.0.0.1"],
                    23: ["2606:4700:4700::1111", "2606:4700:4700::1001"],
                }.get(familia)
                if servidores:
                    novos.append(
                        {
                            "InterfaceIndex": int(entrada["InterfaceIndex"]),
                            "AddressFamily": familia,
                            "ServerAddresses": servidores,
                        }
                    )
            if not novos:
                raise ValueError("Não foram encontradas interfaces IPv4 ou IPv6 ativas.")
            OtimizadorRede._executar_troca_dns(novos)
            logger.info("DNS Cloudflare aplicado.")
            return True, "DNS Cloudflare (IPv4 e IPv6) aplicado. As definições anteriores foram guardadas para restauração."
        except Exception as erro:
            if backup_criado:
                try:
                    with backup.open("r", encoding="utf-8") as arquivo:
                        OtimizadorRede._executar_troca_dns(json.load(arquivo))
                    backup.unlink()
                except Exception as erro_restauracao:
                    logger.error("Falha na restauração automática do DNS: %s", erro_restauracao)
            logger.error("Erro ao configurar DNS Cloudflare: %s", erro)
            return False, f"Erro ao configurar DNS: {erro}"

    @staticmethod
    def restaurar_dns():
        backup = DIRETORIO_DADOS_APLICACAO / "dns_backup.json"
        try:
            if not backup.exists():
                return False, "Não existe uma cópia anterior das definições DNS."
            with backup.open("r", encoding="utf-8") as arquivo:
                anteriores = json.load(arquivo)
            if not isinstance(anteriores, list) or not anteriores:
                raise ValueError("A cópia das definições DNS está inválida.")
            OtimizadorRede._executar_troca_dns(anteriores)
            backup.unlink()
            logger.info("Configuração DNS anterior restaurada.")
            return True, "Definições DNS anteriores restauradas."
        except Exception as erro:
            logger.error("Erro ao restaurar DNS: %s", erro)
            return False, f"Erro ao restaurar as definições DNS: {erro}"

    @staticmethod
    def otimizar_adaptador_rede():
        try:
            for comando in (
                ["ipconfig", "/flushdns"],
                ["netsh", "winsock", "reset"],
            ):
                resultado = subprocess.run(
                    comando, capture_output=True, text=True, check=False
                )
                if resultado.returncode != 0:
                    raise RuntimeError(
                        resultado.stderr.strip() or resultado.stdout.strip()
                    )
            caminho_base = (
                r"SYSTEM\CurrentControlSet\Control\Class"
                r"\{4d36e972-e325-11ce-bfc1-08002be10318}"
            )
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, caminho_base, 0, winreg.KEY_READ
            ) as base:
                indice = 0
                while True:
                    try:
                        subchave = winreg.EnumKey(base, indice)
                    except OSError:
                        break
                    indice += 1
                    caminho = f"{caminho_base}\\{subchave}"
                    try:
                        with winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE, caminho, 0, winreg.KEY_READ
                        ) as chave:
                            descricao, _ = winreg.QueryValueEx(chave, "DriverDesc")
                    except OSError:
                        continue
                    if not any(
                        termo in str(descricao).casefold()
                        for termo in ("controller", "adapter", "ethernet")
                    ):
                        continue
                    ajustes = (
                        "EnableEEE",
                        "AdvancedEEE",
                        "PowerSavingMode",
                        "GigaLite",
                        "EnablePME",
                        "InterruptModeration",
                    )
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE, caminho, 0, winreg.KEY_SET_VALUE
                    ) as chave:
                        for nome in ajustes:
                            try:
                                winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, "0")
                            except FileNotFoundError:
                                continue
            resultado_dns = OtimizadorRede.alterar_dns_cloudflare()
            if not resultado_dns[0]:
                raise RuntimeError(resultado_dns[1])
            logger.info("Adaptadores de rede otimizados.")
            return True, "Adaptador de rede otimizado com sucesso."
        except Exception as erro:
            logger.error("Erro ao otimizar adaptador de rede: %s", erro)
            return False, f"Erro ao otimizar adaptador de rede: {erro}"

    @staticmethod
    def aplicar_tweaks_tcp_ip():
        backup_path = FICHEIRO_BACKUP_TCP
        try:
            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            if not backup_path.exists():
                backup = subprocess.run(
                    ["netsh", "interface", "tcp", "dump"],
                    capture_output=True,
                    startupinfo=startupinfo,
                    check=False,
                )
                if backup.returncode != 0 or not backup.stdout.strip():
                    detalhe = (backup.stderr or backup.stdout).decode(
                        errors="replace"
                    ).strip()
                    raise RuntimeError(
                        f"Não foi possível guardar a configuração TCP/IP: {detalhe}"
                    )
                backup_path.write_bytes(backup.stdout)

            comandos = (
                ["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"],
                ["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"],
                ["netsh", "int", "tcp", "set", "global", "ecncapability=disabled"],
                ["netsh", "int", "tcp", "set", "global", "rss=enabled"],
                ["netsh", "int", "tcp", "set", "global", "timestamps=disabled"],
            )
            falhas = []
            for comando in comandos:
                resultado = subprocess.run(
                    comando,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=startupinfo,
                    check=False,
                )
                if resultado.returncode != 0:
                    falhas.append(
                        f"{comando[-1]}: "
                        f"{resultado.stderr.strip() or resultado.stdout.strip()}"
                    )
            if falhas:
                restauracao, mensagem = OtimizadorRede.restaurar_tweaks_tcp_ip()
                raise RuntimeError(
                    "; ".join(falhas)
                    + ("; " + mensagem if not restauracao else "; configuração anterior restaurada")
                )
            logger.info("Ajustes TCP/IP aplicados.")
            return True, "Pilha TCP/IP otimizada. A configuração original foi guardada para restauração."
        except Exception as erro:
            logger.error("Erro ao otimizar TCP/IP: %s", erro)
            return False, f"Erro ao otimizar rede: {erro}"

    @staticmethod
    def restaurar_tweaks_tcp_ip():
        backup_path = FICHEIRO_BACKUP_TCP
        try:
            if not backup_path.exists():
                return False, "Não existe uma cópia anterior da configuração TCP/IP para restaurar."
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            resultado = subprocess.run(
                ["netsh", "exec", str(backup_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            backup_path.unlink()
            logger.info("Configuração TCP/IP anterior restaurada.")
            return True, "Configuração TCP/IP anterior restaurada."
        except Exception as erro:
            logger.error("Erro ao restaurar TCP/IP: %s", erro)
            return False, f"Erro ao restaurar a configuração TCP/IP: {erro}"
