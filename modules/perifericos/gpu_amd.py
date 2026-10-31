"""Ajustes de GPU, vídeo AMD, HAGS, MPO e modo MSI."""

import ctypes
import subprocess

from logger import logger


class OtimizadorAMD:
    """Aplica ajustes de vídeo e interrupções da GPU no Windows."""

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
    def _alterar_registro(caminho, nome, tipo, valor):
        try:
            resultado = subprocess.run(
                [
                    "reg",
                    "add",
                    caminho,
                    "/v",
                    nome,
                    "/t",
                    tipo,
                    "/d",
                    str(valor),
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
            logger.info("Registro atualizado: %s\\%s", caminho, nome)
            return True
        except Exception as erro:
            logger.error("Erro ao atualizar %s\\%s: %s", caminho, nome, erro)
            raise

    @staticmethod
    def desativar_mpo_registro():
        try:
            if not OtimizadorAMD._is_admin():
                logger.error("Privilégios administrativos necessários para desativar MPO.")
                return "Erro: É necessário executar a aplicação como Administrador para alterar o Registo."
            OtimizadorAMD._alterar_registro(
                r"HKLM\SOFTWARE\Microsoft\Windows\DWM",
                "EnableMPO",
                "REG_DWORD",
                0,
            )
            logger.info("MPO desativado.")
            return "✅ Sucesso: MPO desativado no Registo."
        except Exception as erro:
            logger.error("Erro ao desativar MPO: %s", erro)
            return f"Erro ao desativar MPO: {erro}"

    @staticmethod
    def reativar_mpo_padrao():
        try:
            if not OtimizadorAMD._is_admin():
                logger.error("Privilégios administrativos necessários para reativar MPO.")
                return "Erro: É necessário privilégios de Administrador."
            OtimizadorAMD._alterar_registro(
                r"HKLM\SOFTWARE\Microsoft\Windows\DWM",
                "EnableMPO",
                "REG_DWORD",
                1,
            )
            logger.info("MPO reativado.")
            return "🔄 MPO reativado com sucesso."
        except Exception as erro:
            logger.error("Erro ao reativar MPO: %s", erro)
            return f"Erro ao reativar MPO: {erro}"

    @staticmethod
    def configurar_hags_gpu(ativar=True):
        try:
            if not OtimizadorAMD._is_admin():
                logger.error("Privilégios administrativos necessários para alterar HAGS.")
                return "Erro: Necessário privilégios de Administrador."
            valor = 2 if ativar else 1
            OtimizadorAMD._alterar_registro(
                r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "HwSchMode",
                "REG_DWORD",
                valor,
            )
            estado = "ativado" if ativar else "desativado"
            logger.info("HAGS %s; reinicialização recomendada.", estado)
            return f"✅ Agendamento de GPU (HAGS) {estado} (requer reinicialização do PC)."
        except Exception as erro:
            logger.error("Erro ao configurar HAGS: %s", erro)
            return f"Erro ao configurar HAGS: {erro}"

    @staticmethod
    def redefinir_hags_padrao():
        try:
            if not OtimizadorAMD._is_admin():
                logger.error("Privilégios administrativos necessários para redefinir HAGS.")
                return "Erro: Necessário privilégios de Administrador."
            OtimizadorAMD._alterar_registro(
                r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "HwSchMode",
                "REG_DWORD",
                1,
            )
            logger.info("HAGS redefinido para a configuração padrão.")
            return "🔄 HAGS redefinido para o padrão (requer reinicialização do PC)."
        except Exception as erro:
            logger.error("Erro ao redefinir HAGS: %s", erro)
            return f"Erro ao redefinir HAGS: {erro}"

    @staticmethod
    def ativar_msi_mode_gpu():
        try:
            if not OtimizadorAMD._is_admin():
                mensagem = "Erro: é necessário executar a aplicação como Administrador."
                logger.error(mensagem)
                return False, mensagem
            script = (
                "$ErrorActionPreference='Stop';$count=0;"
                "Get-PnpDevice -Class Display -PresentOnly | "
                "Where-Object {$_.InstanceId -like 'PCI\\*'} | ForEach-Object {"
                "$parts=$_.InstanceId -split '\\\\',3;"
                "if($parts.Count -lt 3){throw 'Identificador PCI inválido.'};"
                "$path='HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\PCI\\'+$parts[1]+'\\'+"
                "$parts[2]+'\\Device Parameters\\Interrupt Management\\"
                "MessageSignaledInterruptProperties';"
                "if(Test-Path $path){New-ItemProperty -Path $path -Name MSISupported "
                "-Value 1 -PropertyType DWord -Force -ErrorAction Stop | Out-Null;$count++}};"
                "if($count -eq 0){throw 'Nenhum dispositivo gráfico PCI compatível foi encontrado.'};"
                "Write-Output $count"
            )
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            resultado = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            logger.info("Modo MSI ativado em %s GPU(s).", resultado.stdout.strip())
            return True, f"Modo MSI ativado em {resultado.stdout.strip()} dispositivo(s) gráfico(s)."
        except Exception as erro:
            logger.error("Erro ao ativar modo MSI na GPU: %s", erro)
            return False, f"Erro ao ativar Modo MSI: {erro}"
