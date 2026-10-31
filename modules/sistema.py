"""Ajustes de desempenho, limpeza e MMCSS do Windows."""

import ctypes
import datetime
import json
import os
import shutil
import subprocess
import winreg

from config import CAMINHOS_LIMPEZA, DIRETORIO_DADOS_APLICACAO, SERVICO_SYSMAIN
from logger import logger


class OtimizadorSistema:
    """Reúne otimizações do plano de energia e perfil multimídia do Windows."""

    _plano_anterior_guid = None

    @staticmethod
    def obter_plano_atual():
        try:
            resultado = subprocess.run(
                ["powercfg", "-getactivescheme"],
                capture_output=True,
                text=True,
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or "powercfg falhou.")
            for parte in resultado.stdout.strip().split():
                if "-" in parte and len(parte) == 36:
                    logger.info("Plano de energia atual obtido: %s", parte)
                    return parte
            raise RuntimeError("Não foi possível identificar o GUID do plano ativo.")
        except Exception as erro:
            logger.error("Erro ao consultar plano de energia: %s", erro)
            return None

    @staticmethod
    def ativar_desempenho_maximo():
        try:
            OtimizadorSistema._plano_anterior_guid = (
                OtimizadorSistema.obter_plano_atual()
            )
            guid_ultimate = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            duplicacao = subprocess.run(
                ["powercfg", "-duplicatescheme", guid_ultimate],
                capture_output=True,
                text=True,
                check=False,
            )
            alvo_guid = guid_ultimate
            if duplicacao.returncode == 0:
                for parte in duplicacao.stdout.split():
                    if "-" in parte and len(parte) == 36:
                        alvo_guid = parte
                        break

            ativacao = subprocess.run(
                ["powercfg", "-setactive", alvo_guid],
                capture_output=True,
                text=True,
                check=False,
            )
            if ativacao.returncode != 0:
                raise RuntimeError(ativacao.stderr.strip() or "Falha ao ativar o plano.")
            logger.info("Plano de desempenho máximo ativado.")
            return True, "Modo Desempenho Máximo ativado com sucesso!"
        except Exception as erro:
            logger.error("Erro ao ativar desempenho máximo: %s", erro)
            return False, f"Erro ao ativar desempenho máximo: {erro}"

    @staticmethod
    def reverter_plano_energia():
        try:
            guid = (
                OtimizadorSistema._plano_anterior_guid
                or "381b4222-f694-41f0-9685-ff5bb260df2e"
            )
            resultado = subprocess.run(
                ["powercfg", "-setactive", guid],
                capture_output=True,
                text=True,
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or "Falha ao restaurar plano.")
            OtimizadorSistema._plano_anterior_guid = None
            logger.info("Plano de energia anterior restaurado.")
            return True, "Plano de energia anterior restaurado com sucesso!"
        except Exception as erro:
            logger.error("Erro ao reverter plano de energia: %s", erro)
            return False, f"Erro ao reverter plano: {erro}"

    @staticmethod
    def desativar_sysmain():
        try:
            for comando in (
                ["sc", "stop", SERVICO_SYSMAIN],
                ["sc", "config", SERVICO_SYSMAIN, "start=", "disabled"],
            ):
                resultado = subprocess.run(
                    comando, capture_output=True, text=True, check=False
                )
                if resultado.returncode != 0 and "stop" not in comando:
                    raise RuntimeError(
                        resultado.stderr.strip() or resultado.stdout.strip()
                    )
            logger.info("Serviço SysMain desativado.")
            return True, "Serviço SysMain desativado."
        except Exception as erro:
            logger.error("Erro ao desativar SysMain: %s", erro)
            return False, f"Erro ao desativar SysMain: {erro}"

    @staticmethod
    def ativar_hags():
        try:
            caminho = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, caminho, 0, winreg.KEY_SET_VALUE
            ) as chave:
                winreg.SetValueEx(chave, "HwSchMode", 0, winreg.REG_DWORD, 2)
            logger.info("HAGS ativado.")
            return True, "HAGS ativado com sucesso."
        except Exception as erro:
            logger.error("Erro ao ativar HAGS: %s", erro)
            return False, f"Erro ao ativar HAGS: {erro}"

    @staticmethod
    def limpeza_profunda_sistema():
        erros = []
        try:
            for pasta in CAMINHOS_LIMPEZA:
                if not os.path.exists(pasta):
                    continue
                for nome in os.listdir(pasta):
                    caminho = os.path.join(pasta, nome)
                    try:
                        if os.path.isfile(caminho) or os.path.islink(caminho):
                            os.unlink(caminho)
                        elif os.path.isdir(caminho):
                            shutil.rmtree(caminho)
                    except OSError as erro:
                        erros.append(f"{caminho}: {erro}")
            if erros:
                raise OSError("; ".join(erros))
            logger.info("Limpeza profunda do sistema concluída.")
            return True, "Limpeza profunda concluída!"
        except Exception as erro:
            logger.error("Erro na limpeza profunda: %s", erro)
            return False, f"Erro na limpeza: {erro}"

    @staticmethod
    def executar_tudo():
        try:
            operacoes = (
                OtimizadorSistema.desativar_sysmain(),
                OtimizadorSistema.ativar_hags(),
                OtimizadorSistema.limpeza_profunda_sistema(),
                OtimizadorSistema.ativar_desempenho_maximo(),
            )
            falhas = [mensagem for sucesso, mensagem in operacoes if not sucesso]
            if falhas:
                raise RuntimeError("; ".join(falhas))
            logger.info("Otimizações gerais do sistema concluídas.")
            return True, "Todas as otimizações do sistema foram aplicadas!"
        except Exception as erro:
            logger.error("Erro ao executar otimizações do sistema: %s", erro)
            return False, f"Erro ao otimizar sistema: {erro}"

    @staticmethod
    def otimizar_mmcss_jogos():
        caminho = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\System Profile"
        caminho_games = caminho + r"\Tasks\Games"
        backup = DIRETORIO_DADOS_APLICACAO / "mmcss_backup.json"
        valores = {
            caminho: {
                "SystemResponsiveness": (winreg.REG_DWORD, 0),
                "NetworkThrottlingIndex": (winreg.REG_DWORD, 0xFFFFFFFF),
            },
            caminho_games: {
                "GPU Priority": (winreg.REG_DWORD, 8),
                "Priority": (winreg.REG_DWORD, 6),
                "Scheduling Category": (winreg.REG_SZ, "High"),
            },
        }
        backup_criado = False
        try:
            if backup.exists():
                mensagem = "Existe uma cópia MMCSS anterior; restaura-a antes de aplicar novamente."
                logger.error(mensagem)
                return False, mensagem
            anteriores = {}
            for chave, configuracoes in valores.items():
                atuais = {}
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, chave, 0, winreg.KEY_QUERY_VALUE
                ) as registro:
                    for nome in configuracoes:
                        try:
                            valor, tipo = winreg.QueryValueEx(registro, nome)
                            atuais[nome] = {"value": valor, "type": tipo}
                        except FileNotFoundError:
                            atuais[nome] = {"value": None, "type": None}
                anteriores[chave] = atuais

            DIRETORIO_DADOS_APLICACAO.mkdir(parents=True, exist_ok=True)
            with backup.open("x", encoding="utf-8") as arquivo:
                json.dump(anteriores, arquivo, ensure_ascii=False)
            backup_criado = True
            for chave, configuracoes in valores.items():
                with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, chave) as registro:
                    for nome, (tipo, valor) in configuracoes.items():
                        winreg.SetValueEx(registro, nome, 0, tipo, valor)
            logger.info("Ajustes MMCSS para jogos aplicados.")
            return True, "Perfis MMCSS e prioridade de jogos otimizados. Os valores anteriores foram guardados para restauração."
        except Exception as erro:
            if backup_criado:
                resultado = OtimizadorSistema.restaurar_mmcss_jogos()
                if not resultado[0]:
                    logger.error("Falha na restauração automática do MMCSS: %s", resultado[1])
            logger.error("Erro ao configurar MMCSS: %s", erro)
            return False, f"Erro ao configurar MMCSS: {erro}"

    @staticmethod
    def restaurar_mmcss_jogos():
        backup = DIRETORIO_DADOS_APLICACAO / "mmcss_backup.json"
        try:
            if not backup.exists():
                mensagem = "Não existe uma cópia anterior das definições MMCSS."
                logger.error(mensagem)
                return False, mensagem
            with backup.open("r", encoding="utf-8") as arquivo:
                valores = json.load(arquivo)
            if not isinstance(valores, dict) or not valores:
                raise ValueError("A cópia das definições MMCSS está inválida.")
            for caminho, entradas in valores.items():
                with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, caminho) as registro:
                    for nome, entrada in entradas.items():
                        tipo = entrada.get("type")
                        if tipo is None:
                            try:
                                winreg.DeleteValue(registro, nome)
                            except FileNotFoundError:
                                pass
                        else:
                            winreg.SetValueEx(registro, nome, 0, tipo, entrada["value"])
            backup.unlink()
            logger.info("Configuração MMCSS anterior restaurada.")
            return True, "Definições MMCSS anteriores restauradas."
        except Exception as erro:
            logger.error("Erro ao restaurar MMCSS: %s", erro)
            return False, f"Erro ao restaurar as definições MMCSS: {erro}"


class AuditorInstalacaoWindows:
    """Rotinas de diagnóstico e recuperação mantidas do backend legado."""

    @staticmethod
    def _is_admin():
        try:
            autorizado = bool(ctypes.windll.shell32.IsUserAnAdmin())
            logger.info("Verificação de privilégios para manutenção: %s", autorizado)
            return autorizado
        except Exception as erro:
            logger.error("Erro ao verificar privilégios de manutenção: %s", erro)
            return False

    @staticmethod
    def varrer_erros_ocultos_kernel():
        try:
            comando = [
                "wevtutil",
                "qe",
                "System",
                "/q:*[System[(Level=1 or Level=2)]]",
                "/c:10",
                "/f:text",
            ]
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="replace",
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
            if resultado.stdout.strip():
                logger.info("Foram encontrados eventos de erro nos logs do Windows.")
                return f"⚠️ Foram detetados registos de erro no sistema:\n\n{resultado.stdout.strip()}"
            logger.info("Nenhum evento crítico encontrado nos logs do Windows.")
            return "✅ Nenhum erro crítico recente registado no kernel do sistema."
        except Exception as erro:
            logger.error("Erro ao consultar logs de diagnóstico: %s", erro)
            return f"Erro ao consultar os logs de diagnóstico: {erro}"

    @staticmethod
    def diagnosticar_e_reparar_instalacao():
        try:
            if not AuditorInstalacaoWindows._is_admin():
                mensagem = "Erro: É necessário privilégios de Administrador para reparar a instalação."
                logger.error(mensagem)
                return mensagem
            relatorio = []
            dism = subprocess.run(
                ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="replace",
                check=False,
            )
            if dism.returncode == 0:
                relatorio.append("• [DISM] Imagem do Windows verificada e reparada.")
            else:
                relatorio.append(
                    "• [DISM] A verificação terminou com erro: "
                    + (dism.stderr.strip() or dism.stdout.strip())
                )
            sfc = subprocess.run(
                ["sfc", "/scannow"],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="replace",
                check=False,
            )
            if sfc.returncode == 0:
                relatorio.append("• [SFC] Verificação de integridade concluída.")
            else:
                relatorio.append(
                    "• [SFC] A verificação terminou com erro: "
                    + (sfc.stderr.strip() or sfc.stdout.strip())
                )
            logger.info("Diagnóstico e reparação da instalação concluídos.")
            return "\n".join(relatorio)
        except Exception as erro:
            logger.error("Erro ao reparar instalação do Windows: %s", erro)
            return f"Erro durante o processo de reparação: {erro}"

    @staticmethod
    def primeiros_socorros_sistema():
        try:
            if not AuditorInstalacaoWindows._is_admin():
                mensagem = "Erro: Necessário privilégios de Administrador."
                logger.error(mensagem)
                return mensagem
            acoes = []
            for comando, descricao in (
                (["netsh", "winsock", "reset"], "Pilha de rede redefinida."),
                (["ipconfig", "/flushdns"], "Cache DNS limpa."),
            ):
                resultado = subprocess.run(
                    comando,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if resultado.returncode == 0:
                    acoes.append(f"• {descricao}")
                else:
                    raise RuntimeError(
                        resultado.stderr.strip() or resultado.stdout.strip()
                    )
            logger.info("Rotinas de primeiros socorros do sistema concluídas.")
            return "\n".join(acoes)
        except Exception as erro:
            logger.error("Erro nos primeiros socorros do sistema: %s", erro)
            return f"Erro ao aplicar correções automáticas: {erro}"


class GestorDeErrosBackend:
    """Regista notas de diagnóstico no histórico local de erros."""

    @staticmethod
    def criar_nota_de_correcao(
        nome_erro, detalhes_tecnicos, origem="Backend do Otimizador"
    ):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            relatorio = (
                f"\n## Registo de erro identificado - [{timestamp}]\n"
                f"- **Origem do problema:** {origem}\n"
                f"- **Descrição:** {nome_erro}\n"
                f"- **Detalhes técnicos / stack trace:**\n"
                f"```text\n{detalhes_tecnicos}\n```\n"
            )
            with open("historico_erros.md", "a", encoding="utf-8") as arquivo:
                arquivo.write(relatorio)
            logger.info("Nota de erro registada para %s.", nome_erro)
            return True, "Nota de correção registada em historico_erros.md."
        except Exception as erro:
            logger.error("Erro ao registar nota de correção: %s", erro)
            return False, f"Erro ao registar nota de correção: {erro}"
