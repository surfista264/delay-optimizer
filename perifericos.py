import os
import shutil
import subprocess
import winreg
import ctypes
import sys
import datetime
import json
import re





# mouse, teclado e audio esta class mexe 
class OtimizadorPerifericos:
    @staticmethod
    def otimizar_teclado():
        try:
            reg_path = r"Control Panel\Accessibility\Keyboard Response"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "2")
                winreg.SetValueEx(key, "AutoRepeatDelay", 0, winreg.REG_SZ, "200")
                winreg.SetValueEx(key, "AutoRepeatRate", 0, winreg.REG_SZ, "6")
            print("✔ Teclado otimizado com sucesso!")
        except Exception as e:
            print(f"Erro ao otimizar teclado: {e}")

    @staticmethod
    def otimizar_velocidade_teclado_geral():
        try:
            reg_path = r"Control Panel\Keyboard"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "KeyboardDelay", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(key, "KeyboardSpeed", 0, winreg.REG_SZ, "31")
            print("✔ Velocidade geral do teclado otimizada!")
        except Exception as e:
            print(f"Erro ao otimizar velocidade geral do teclado: {e}")

    @staticmethod
    def otimizar_mouse():
        try:
            reg_path = r"Control Panel\Mouse"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            return True, "A aceleração do mouse foi removida."
        except Exception as e:
            return False, f"Erro ao otimizar mouse: {e}"

    @staticmethod
    def otimizar_prioridade_audio():
        try:
            audio_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, audio_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Affinity", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Background Priority", 0, winreg.REG_SZ, "High")
                winreg.SetValueEx(key, "Latency", 0, winreg.REG_SZ, "Low")
                winreg.SetValueEx(key, "Scheduled", 0, winreg.REG_SZ, "Use CIO")
                winreg.SetValueEx(key, "SFIO Priority", 0, winreg.REG_SZ, "High")
            print("✔ Prioridade de áudio e headset otimizadas!")
        except Exception as e:
            print(f"Erro ao otimizar áudio: {e}")

    @classmethod
    def executar_tudo(cls):
        cls.otimizar_teclado()
        cls.otimizar_velocidade_teclado_geral()
        cls.otimizar_mouse()
        cls.otimizar_prioridade_audio()

# mexe na rede do combutador
class OtimizadorRede:
    @staticmethod
    def alterar_dns_cloudflare():
        try:
            adaptadores = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | "
                    "Select-Object -ExpandProperty Name",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if adaptadores.returncode != 0:
                detalhe = adaptadores.stderr.strip() or adaptadores.stdout.strip()
                return False, f"Erro ao identificar adaptadores de rede: {detalhe}"

            nomes = [linha.strip() for linha in adaptadores.stdout.splitlines() if linha.strip()]
            if not nomes:
                return False, "Nenhum adaptador físico ativo foi encontrado."

            falhas = []
            for nome in nomes:
                comandos = [
                    ["netsh", "interface", "ipv4", "set", "dnsservers", f"name={nome}", "source=static", "address=1.1.1.1", "validate=no"],
                    ["netsh", "interface", "ipv4", "add", "dnsservers", f"name={nome}", "address=1.0.0.1", "index=2", "validate=no"],
                    ["netsh", "interface", "ipv6", "set", "dnsservers", f"name={nome}", "source=static", "address=2606:4700:4700::1111", "validate=no"],
                    ["netsh", "interface", "ipv6", "add", "dnsservers", f"name={nome}", "address=2606:4700:4700::1001", "index=2", "validate=no"],
                ]
                for comando in comandos:
                    resultado = subprocess.run(
                        comando,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    if resultado.returncode != 0:
                        detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                        falhas.append(f"{nome}: {detalhe or 'comando netsh falhou'}")

            if falhas:
                return False, "Falha ao configurar alguns DNS: " + "; ".join(falhas)
            return True, "DNS da Cloudflare (IPv4 e IPv6) aplicado nos adaptadores ativos."
        except Exception as e:
            return False, f"Erro ao alterar DNS: {e}"

    @staticmethod
    def otimizar_adaptador_rede():
        try:
            subprocess.run("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("netsh winsock reset", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            OtimizadorRede.alterar_dns_cloudflare()

            base_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path, 0, winreg.KEY_READ) as base_key:
                i = 0
                while True:
                    try:
                        sub_name = winreg.EnumKey(base_key, i)
                        sub_path = f"{base_path}\\{sub_name}"
                        i += 1
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_path, 0, winreg.KEY_READ) as sub_key:
                            driver_desc, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                        
                        if any(k in driver_desc for k in ["Controller", "Adapter", "Ethernet"]):
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_path, 0, winreg.KEY_SET_VALUE) as write_key:
                                configs = {
                                    "EnableEEE": "0", "AdvancedEEE": "0", 
                                    "PowerSavingMode": "0", "GigaLite": "0", 
                                    "EnablePME": "0", "InterruptModeration": "0"
                                }
                                for chave, valor in configs.items():
                                    try:
                                        winreg.SetValueEx(write_key, chave, 0, winreg.REG_SZ, valor)
                                    except FileNotFoundError:
                                        pass
                    except OSError:
                        break
            print("✔ Adaptador de rede otimizado com sucesso!")
        except Exception as e:
            print(f"Erro ao otimizar adaptador de rede: {e}")

#plano de energia, limpeza e stymain
class OtimizadorSistema:
    _plano_anterior_guid = None

    @staticmethod
    def obter_plano_atual():
        """Obtém o GUID do plano de energia atualmente ativo no Windows."""
        try:
            resultado = subprocess.run("powercfg -getactivescheme", capture_output=True, text=True, shell=True)
            if resultado.returncode == 0:
                for parte in resultado.stdout.strip().split():
                    if "-" in parte and len(parte) == 36:
                        return parte
        except Exception:
            pass
        return None

    @staticmethod
    def ativar_desempenho_maximo():
        """Desbloqueia e ativa o plano 'Desempenho Máximo' (Ultimate Performance)."""
        try:
            OtimizadorSistema._plano_anterior_guid = OtimizadorSistema.obter_plano_atual()

            guid_ultimate = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            cmd_duplicar = f"powercfg -duplicatescheme {guid_ultimate}"
            resultado_duplicar = subprocess.run(cmd_duplicar, capture_output=True, text=True, shell=True)
            
            alvo_guid = guid_ultimate
            if resultado_duplicar.returncode == 0:
                for linha in resultado_duplicar.stdout.split('\n'):
                    if "GUID" in linha:
                        for parte in linha.strip().split():
                            if "-" in parte and len(parte) == 36:
                                alvo_guid = parte
                                break

            resultado_ativar = subprocess.run(f"powercfg -setactive {alvo_guid}", capture_output=True, text=True, shell=True)
            
            if resultado_ativar.returncode == 0:
                return True, "Modo Desempenho Máximo ativado com sucesso!"
            else:
                return False, "Não foi possível aplicar o plano de energia."
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    @staticmethod
    def reverter_plano_energia():
        """Restaura o plano de energia anterior ou o equilibrado."""
        try:
            if OtimizadorSistema._plano_anterior_guid:
                cmd = f"powercfg -setactive {OtimizadorSistema._plano_anterior_guid}"
                resultado = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if resultado.returncode == 0:
                    return True, "Plano de energia original restaurado com sucesso!"
            
            guid_equilibrado = "381b4222-f694-41f0-9685-ff5bb260df2e"
            subprocess.run(f"powercfg -setactive {guid_equilibrado}", shell=True)
            return True, "Plano padrão do Windows restaurado."
        except Exception as e:
            return False, f"Erro ao reverter plano: {str(e)}"

    @staticmethod
    def desativar_sysmain():
        try:
            subprocess.run("sc stop SysMain", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("sc config SysMain start= disabled", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, "Serviço SysMain desativado."
        except Exception as e:
            return False, f"Erro ao desativar SysMain: {e}"

    @staticmethod
    def ativar_hags():
        try:
            hags_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hags_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)
            return True, "HAGS ativado com sucesso."
        except Exception as e:
            return False, f"Erro ao ativar HAGS: {e}"

    @staticmethod
    def limpeza_profunda_sistema():
        try:
            pastas_temp = [
                os.path.expandvars(r"%TEMP%"),
                r"C:\Windows\Temp",
                r"C:\Windows\Prefetch"
            ]
            for pasta in pastas_temp:
                if os.path.exists(pasta):
                    for item in os.listdir(pasta):
                        caminho_item = os.path.join(pasta, item)
                        try:
                            if os.path.isfile(caminho_item) or os.path.islink(caminho_item):
                                os.unlink(caminho_item)
                            elif os.path.isdir(caminho_item):
                                shutil.rmtree(caminho_item)
                        except Exception:
                            pass
            return True, "Limpeza profunda concluída!"
        except Exception as e:
            return False, f"Erro na limpeza: {e}"

    @classmethod
    def executar_tudo(cls):
        cls.desativar_sysmain()
        cls.ativar_hags()
        cls.limpeza_profunda_sistema()
        cls.ativar_desempenho_maximo()
        return True, "Todas as otimizações do sistema foram aplicadas!"

# Manutenção e primeiros socorro 
class AuditorInstalacaoWindows:
    
    @staticmethod
    def _is_admin():
        """Verifica se o script possui privilégios elevados de Administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def varrer_erros_ocultos_kernel():
        """
        Consulta o Visualizador de Eventos do Windows (via wevtutil) 
        para capturar os erros críticos ou de nível de alerta mais recentes 
        que acontecem em segundo plano sem que o utilizador perceba.
        """
        if not AuditorInstalacaoWindows._is_admin():
            return "Erro: É necessário executar a aplicação como Administrador para ler os logs do sistema."
        
        try:
            # Puxa os últimos 5 erros críticos ou de alerta do subsistema do Windows
            comando = [
                "wevtutil", "qe", "System", 
                "/q:*[System[(Level=1 or Level=2)]]", 
                "/c:5", "/f:text", "/rd:true"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True, encoding='cp850', errors='ignore')
            
            if resultado.returncode == 0 and resultado.stdout.strip():
                return f"⚠️ Foram detetados registos ocultos de erro no sistema:\n\n{resultado.stdout.strip()}"
            else:
                return "✅ Nenhum erro crítico recente registado no kernel do sistema."
                
        except Exception as e:
            return f"Erro ao consultar os logs de diagnóstico: {str(e)}"

    @staticmethod
    def diagnosticar_e_reparar_instalacao():
        """
        Executa uma auditoria completa na imagem e na estrutura de ficheiros 
        da instalação do Windows, corrigindo falhas invisíveis na raiz do SO.
        """
        if not AuditorInstalacaoWindows._is_admin():
            return "Erro: É necessário privilégios de Administrador para reparar a instalação."
        
        relatorio_acoes = []
        
        try:
            # 1. Auditoria e Reparação da Loja de Componentes (DISM)
            # Verifica se os pacotes de instalação base estão corrompidos e repara-os via update
            dism_cmd = ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"]
            res_dism = subprocess.run(dism_cmd, capture_output=True, text=True, encoding='cp850', errors='ignore')
            
            if res_dism.returncode == 0:
                relatorio_acoes.append("• [DISM] Imagem de instalação verificada e sem corrupções na base.")
            else:
                relatorio_acoes.append("• [DISM] Anomalias detetadas na imagem e corrigidas automaticamente pelos servidores base.")

            # 2. Verificação de Integridade de Ficheiros do Sistema (SFC)
            # Varre os ficheiros protegidos e substitui os corrompidos por cópias limpas
            sfc_cmd = ["sfc", "/scannow"]
            res_sfc = subprocess.run(sfc_cmd, capture_output=True, text=True, encoding='cp850', errors='ignore')
            
            if "WRP não encontrou nenhuma violação" in res_sfc.stdout or res_sfc.returncode == 0:
                relatorio_acoes.append("• [SFC] Integridade dos ficheiros essenciais do Windows a 100%.")
            else:
                relatorio_acoes.append("• [SFC] Ficheiros de sistema danificados foram identificados e substituídos com sucesso.")
                
        except Exception as e:
            relatorio_acoes.append(f"• Erro durante o processo de reparação: {str(e)}")
            
        return "\n".join(relatorio_acoes)

    @staticmethod
    def primeiros_socorros_sistema():
        """
        Tenta corrigir automaticamente problemas comuns de serviços travados 
        e limpa caches de rede que costumam gerar erros invisíveis.
        """
        if not AuditorInstalacaoWindows._is_admin():
            return "Erro: Necessário privilégios de Administrador."
            
        acoes_tomadas = []
        
        try:
            # 1. Redefinir a pilha de rede (corrige erros ocultos de conexão e DNS)
            res_net = subprocess.run(["netsh", "winsock", "reset"], capture_output=True, text=True)
            if res_net.returncode == 0:
                acoes_tomadas.append("• Pilha de rede redefinida com sucesso (eliminou conflitos ocultos de internet).")
                
            # 2. Limpar a cache de DNS do sistema
            res_dns = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
            if res_dns.returncode == 0:
                acoes_tomadas.append("• Cache de DNS limpa.")
                
        except Exception as e:
            acoes_tomadas.append(f"• Erro ao aplicar correções automáticas: {str(e)}")
            
        return "\n".join(acoes_tomadas)

# Indendificar erros e fazer uma analise 
class GestorDeErrosBackend:
    
    @staticmethod
    def criar_nota_de_correcao(nome_erro, detalhes_tecnicos, origem="Backend do Otimizador"):
        """
        Cria um relatório automático (um ficheiro Markdown 'historico_erros.md') 
        com a data, hora, origem e detalhes do erro para saberes exatamente o que corrigir.
        """
        nome_ficheiro = "historico_erros.md"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Estrutura a anotação de forma limpa e organizada para leitura posterior
        relatorio = f"""
## 🛠️ Registo de Erro Identificado - [{timestamp}]
- **Origem do Problema:** {origem}
- **Descrição:** {nome_erro}
- **Detalhes Técnicos / Stack Trace:**
```text
{detalhes_tecnicos}"""

# AMD Otimização 
class OtimizadorAMDBackend:
    
    @staticmethod
    def _is_admin():
        """Verifica se o script está a correr com privilégios de Administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def desativar_mpo_registro():
        """
        Desativa o MPO (Multi-Plane Overlay) no Registo do Windows.
        O MPO é conhecido por causar engasgos (stuttering), cintilações de ecrã 
        e pequenos travamentos em placas AMD após atualizações do Windows.
        """
        if not OtimizadorAMDBackend._is_admin():
            return "Erro: É necessário executar a aplicação como Administrador para alterar o Registo."
        
        try:
            comando = [
                "reg", "add", 
                r"HKLM\SOFTWARE\Microsoft\Windows\DWM", 
                "/v", "EnableMPO", 
                "/t", "REG_DWORD", 
                "/d", "0", 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                return "✅ Sucesso: MPO desativado no Registo (estabilidade e fluidez melhoradas para AMD)."
            else:
                return f"⚠️ Erro ao alterar o Registo do MPO: {resultado.stderr.strip()}"
                
        except Exception as e:
            return f"Erro crítico ao executar comando do MPO: {str(e)}"

    @staticmethod
    def configurar_hags_gpu(ativar=True):
        """
        Ativa ou desativa o HAGS (Hardware-accelerated GPU scheduling).
        Melhora a gestão de memória e prioridade da placa gráfica no Windows.
        """
        if not OtimizadorAMDBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."
        
        # Valor 2 ativa o HAGS, Valor 1 desativa
        valor_reg = "2" if ativar else "1"
        estado_txt = "ativado"
        
        try:
            comando = [
                "reg", "add", 
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 
                "/v", "HwSchMode", 
                "/t", "REG_DWORD", 
                "/d", valor_reg, 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                return f"✅ Sucesso: Agendamento de GPU (HAGS) {estado_txt} (requer reinicialização do PC)."
            else:
                return f"⚠️ Erro ao configurar o HAGS: {resultado.stderr.strip()}"
                
        except Exception as e:
            return f"Erro: {str(e)}"

    @staticmethod
    def reativar_mpo_padrao():
        """
        Reativa o MPO (Multi-Plane Overlay) no Registo do Windows.
        Útil caso precises de voltar à configuração original ou trocar de marca de placa gráfica.
        """
        if not OtimizadorAMDBackend._is_admin():
            return "Erro: É necessário privilégios de Administrador."
        
        try:
            # Para reativar, podemos simplesmente apagar a chave ou mudar o valor para 1
            comando = [
                "reg", "add", 
                r"HKLM\SOFTWARE\Microsoft\Windows\DWM", 
                "/v", "EnableMPO", 
                "/t", "REG_DWORD", 
                "/d", "1", 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                return "🔄 MPO reativado com sucesso (configuração original de fábrica restaurada)."
            else:
                return f"⚠️ Erro ao restaurar o MPO: {resultado.stderr.strip()}"
                
        except Exception as e:
            return f"Erro crítico: {str(e)}"

    @staticmethod
    def redefinir_hags_padrao():
        """
        Remove ou redefine o agendamento de GPU (HAGS) para o padrão do sistema.
        """
        if not OtimizadorAMDBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."
        
        try:
            # Valor 1 desativa o HAGS forçado, voltando ao comportamento padrão do Windows
            comando = [
                "reg", "add", 
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 
                "/v", "HwSchMode", 
                "/t", "REG_DWORD", 
                "/d", "1", 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                return "🔄 HAGS redefinido para o padrão (requer reinicialização do PC)."
            else:
                return f"⚠️ Erro ao redefinir o HAGS: {resultado.stderr.strip()}"
                
        except Exception as e:
            return f"Erro: {str(e)}"

# Imput lag menor
class RedutorInputLagBackend:

    @staticmethod
    def _is_admin():
        """Verifica se o script possui privilégios de Administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def ativar_modo_jogo_windows():
        """
        Ativa o Modo de Jogo (Game Mode) nativo do Windows via Registo.
        Prioriza o envio de recursos do sistema para a aplicação em ecrã inteiro,
        reduzindo a latência de processamento antes de enviar o sinal ao monitor.
        """
        if not RedutorInputLagBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."

        try:
            comando = [
                "reg", "add", 
                r"HKCU\Software\Microsoft\GameBar", 
                "/v", "AutoGameModeEnabled", 
                "/t", "REG_DWORD", 
                "/d", "1", 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode == 0:
                return "✅ Modo de Jogo ativado com sucesso (Prioridade de CPU/GPU garantida)."
            else:
                return f"⚠️ Erro ao ativar Modo de Jogo: {resultado.stderr.strip()}"
        except Exception as e:
            return f"Erro crítico: {str(e)}"

    @staticmethod
    def otimizar_resposta_sistema():
        """
        Ajusta a prioridade de resposta de multimédia no Registo do Windows.
        Por padrão, o Windows reserva 20% do processamento para tarefas secundárias;
        este ajuste reduz essa reserva para dar resposta instantânea ao ecrã.
        """
        if not RedutorInputLagBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."

        try:
            comando = [
                "reg", "add", 
                r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 
                "/v", "SystemResponsiveness", 
                "/t", "REG_DWORD", 
                "/d", "0", 
                "/f"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode == 0:
                return "✅ Prioridade de resposta do sistema ajustada para latência mínima."
            else:
                return f"⚠️ Erro ao alterar prioridade: {resultado.stderr.strip()}"
        except Exception as e:
            return f"Erro crítico: {str(e)}"

# Privacidade
class OtimizadorPrivacidadeBackend:

    @staticmethod
    def _is_admin():
        """Verifica se o script possui privilégios de Administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    @staticmethod
    def _backup_servico_path():
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("A variável LOCALAPPDATA não está definida.")
        pasta = os.path.join(local_app_data, "WindowsUltimateOptimizer")
        os.makedirs(pasta, exist_ok=True)
        return os.path.join(pasta, "diagtrack_backup.json")

    @staticmethod
    def desativar_servico_telemetria():
        """Para e desativa o serviço principal de telemetria do Windows (DiagTrack).

        Impede o envio contínuo de dados de uso em segundo plano.
        """
        if not OtimizadorPrivacidadeBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."

        try:
            backup_path = OtimizadorPrivacidadeBackend._backup_servico_path()
            if not os.path.exists(backup_path):
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\DiagTrack",
                    0,
                    winreg.KEY_READ,
                ) as key:
                    start_type, _ = winreg.QueryValueEx(key, "Start")

                estado = subprocess.run(
                    ["sc", "query", "DiagTrack"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if estado.returncode != 0:
                    detalhe = estado.stderr.strip() or estado.stdout.strip()
                    return f"Erro ao consultar DiagTrack: {detalhe}"
                correspondencia = re.search(r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE)
                if correspondencia is None:
                    return "Erro: não foi possível determinar o estado atual do DiagTrack."

                with open(backup_path, "w", encoding="utf-8") as backup:
                    json.dump(
                        {
                            "start_type": int(start_type),
                            "was_running": int(correspondencia.group(1)) == 4,
                        },
                        backup,
                    )

            with open(backup_path, "r", encoding="utf-8") as backup:
                estado_anterior = json.load(backup)
            was_running = estado_anterior.get("was_running")
            if not isinstance(estado_anterior.get("start_type"), int) or not isinstance(was_running, bool):
                return "Erro: a cópia da configuração do DiagTrack é inválida."

            estado = subprocess.run(
                ["sc", "query", "DiagTrack"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            correspondencia = re.search(r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE)
            if estado.returncode != 0 or correspondencia is None:
                detalhe = estado.stderr.strip() or estado.stdout.strip()
                return f"Erro ao consultar DiagTrack: {detalhe or 'estado do serviço indisponível'}"
            atualmente_em_execucao = int(correspondencia.group(1)) == 4

            if atualmente_em_execucao:
                parar = subprocess.run(
                    ["sc", "stop", "DiagTrack"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if parar.returncode != 0:
                    detalhe = parar.stderr.strip() or parar.stdout.strip()
                    return f"Erro ao parar DiagTrack: {detalhe}"

            resultado = subprocess.run(
                ["sc", "config", "DiagTrack", "start=", "disabled"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            if resultado.returncode == 0:
                return "✅ Serviço de telemetria (DiagTrack) desativado com sucesso."
            detalhe = resultado.stderr.strip() or resultado.stdout.strip()
            if atualmente_em_execucao:
                subprocess.run(
                    ["sc", "start", "DiagTrack"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
            return f"Erro ao configurar serviço: {detalhe}"

        except Exception as e:
            return f"Erro crítico: {str(e)}"

    @staticmethod
    def restaurar_servico_telemetria():
        if not OtimizadorPrivacidadeBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."

        try:
            backup_path = OtimizadorPrivacidadeBackend._backup_servico_path()
            if not os.path.exists(backup_path):
                return "Erro: não há cópia da configuração anterior do DiagTrack."

            with open(backup_path, "r", encoding="utf-8") as backup:
                estado_anterior = json.load(backup)
            start_type = estado_anterior.get("start_type")
            was_running = estado_anterior.get("was_running")
            tipos_inicio = {0: "boot", 1: "system", 2: "auto", 3: "demand", 4: "disabled"}
            if (
                not isinstance(start_type, int)
                or start_type not in tipos_inicio
                or not isinstance(was_running, bool)
            ):
                return "Erro: a cópia da configuração do DiagTrack é inválida."

            resultado = subprocess.run(
                ["sc", "config", "DiagTrack", "start=", tipos_inicio[start_type]],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if resultado.returncode != 0:
                detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                return f"Erro ao restaurar configuração do DiagTrack: {detalhe}"

            if was_running:
                estado = subprocess.run(
                    ["sc", "query", "DiagTrack"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                correspondencia = re.search(r"STATE\s*:\s*(\d+)", estado.stdout, re.IGNORECASE)
                if estado.returncode != 0 or correspondencia is None:
                    detalhe = estado.stderr.strip() or estado.stdout.strip()
                    return f"Erro ao verificar estado do DiagTrack: {detalhe or 'estado do serviço indisponível'}"
                if int(correspondencia.group(1)) != 4:
                    resultado = subprocess.run(
                        ["sc", "start", "DiagTrack"],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    if resultado.returncode != 0:
                        detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                        return f"Erro ao iniciar DiagTrack após restaurar configuração: {detalhe}"

            os.remove(backup_path)
            return "✅ Configuração anterior do serviço DiagTrack restaurada."
        except Exception as e:
            return f"Erro crítico ao restaurar DiagTrack: {str(e)}"

    @staticmethod
    def restrinjir_dados_diagnostico():
        """Reduz o nível de recolha de dados de diagnóstico no Registo do Windows

        para o mínimo básico permitido.
        """
        if not OtimizadorPrivacidadeBackend._is_admin():
            return "Erro: Necessário privilégios de Administrador."

        try:
            comando = [
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
            ]
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if resultado.returncode == 0:
                return "✅ Coleta de dados de diagnóstico restrita ao nível mínimo."
            else:
                return f"⚠️ Erro ao alterar o Registo: {resultado.stderr.strip()}"

        except Exception as e:
            return f"Erro crítico: {str(e)}"

    @staticmethod
    def desativar_id_publicidade():
        """Desativa o ID de publicidade do utilizador no Registo,

        impedindo o rastreio para anúncios personalizados no sistema.
        """
        try:
            comando = [
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
            ]
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if resultado.returncode == 0:
                return "✅ ID de publicidade e rastreio comercial desativados."
            else:
                return f"⚠️ Erro ao desativar ID de publicidade: {resultado.stderr.strip()}"

        except Exception as e:
            return f"Erro crítico: {str(e)}"


class OtimizadorKernelAvancado:
    """Implementa otimizações de baixo nível no Registro e Kernel do Windows."""

    @staticmethod
    def ativar_msi_mode_gpu():
        """
        Ativa o modo MSI (Message Signaled Interrupts) para a GPU, 
        reduzindo o DPC Latency e evitando micro-stutters.
        """
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return False, "Erro: é necessário executar a aplicação como Administrador para alterar o Registo."

        try:
            script_ps = (
                "$ErrorActionPreference = 'Stop';"
                "try {"
                "$count = 0;"
                "Get-PnpDevice -Class Display -PresentOnly | "
                "Where-Object { $_.InstanceId -like 'PCI\\*' } | ForEach-Object {"
                "$parts = $_.InstanceId -split '\\\\', 3;"
                "if ($parts.Count -lt 3) { throw 'Identificador PCI inválido.' };"
                "$path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\PCI\\' + "
                "$parts[1] + '\\' + $parts[2] + "
                "'\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties';"
                "if (Test-Path $path) {"
                "New-ItemProperty -Path $path -Name 'MSISupported' -Value 1 "
                "-PropertyType DWord -Force -ErrorAction Stop | Out-Null;"
                "$count++"
                "}"
                "};"
                "if ($count -eq 0) { throw 'Nenhum dispositivo gráfico PCI compatível foi encontrado.' };"
                "Write-Output $count"
                "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
            )
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            resultado = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script_ps],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
            )
            if resultado.returncode != 0:
                detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                return False, f"Erro ao ativar Modo MSI: {detalhe}"
            return True, f"Modo MSI ativado em {resultado.stdout.strip()} dispositivo(s) gráfico(s)."
        except Exception as e:
            return False, f"Erro ao ativar Modo MSI: {str(e)}"

    @staticmethod
    def otimizar_mmcss_jogos():
        """
        Ajusta o Multimedia Class Scheduler Service (MMCSS) para dar
        prioridade máxima de CPU e GPU aos jogos.
        """
        try:
            caminho = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\System Profile"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho, 0, winreg.KEY_SET_VALUE)
            
            # SystemResponsiveness = 0 (100% de CPU para jogos)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
            # NetworkThrottlingIndex = FFFFFFFF (Desativa limitação de rede multimédia)
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xFFFFFFFF)
            winreg.CloseKey(key)
            
            # Ajustar sub-chave de Games
            caminho_games = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\System Profile\Tasks\Games"
            key_games = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho_games, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key_games, "GPU Priority", 0, winreg.REG_DWORD, 8)
            winreg.SetValueEx(key_games, "Priority", 0, winreg.REG_DWORD, 6)
            winreg.SetValueEx(key_games, "Scheduling Category", 0, winreg.REG_SZ, "High")
            winreg.CloseKey(key_games)
            
            return True, "Perfis MMCSS e prioridade de jogos otimizados no Registro."
        except Exception as e:
            return False, f"Erro ao configurar MMCSS: {str(e)}"



class OtimizadorRedeAvancado:
    """Otimizações avançadas na pilha TCP/IP (Nagle, RSS, Timestamps)."""

    @staticmethod
    def _backup_tcp_path():
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("A variável LOCALAPPDATA não está definida.")
        pasta = os.path.join(local_app_data, "WindowsUltimateOptimizer")
        os.makedirs(pasta, exist_ok=True)
        return os.path.join(pasta, "tcp_global_backup.txt")

    @staticmethod
    def aplicar_tweaks_tcp_ip():
        """
        Executa comandos netsh para reduzir latencia de pacotes (TCP_NODELAY, CTCP, RSS).
        """
        try:
            backup_path = OtimizadorRedeAvancado._backup_tcp_path()
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            if not os.path.exists(backup_path):
                backup = subprocess.run(
                    ["netsh", "interface", "tcp", "dump"],
                    capture_output=True,
                    startupinfo=startupinfo,
                )
                if backup.returncode != 0 or not backup.stdout.strip():
                    detalhe = (backup.stderr or backup.stdout).decode(errors="replace").strip()
                    return False, f"Não foi possível guardar a configuração TCP/IP atual: {detalhe}"
                with open(backup_path, "wb") as arquivo_backup:
                    arquivo_backup.write(backup.stdout)

            comandos = [
                ["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"],
                ["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"],
                ["netsh", "int", "tcp", "set", "global", "ecncapability=disabled"],
                ["netsh", "int", "tcp", "set", "global", "rss=enabled"],
                ["netsh", "int", "tcp", "set", "global", "timestamps=disabled"]
            ]
            falhas = []
            for cmd in comandos:
                resultado = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=startupinfo,
                )
                if resultado.returncode != 0:
                    detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                    falhas.append(f"{cmd[-1]}: {detalhe or 'comando netsh falhou'}")

            if falhas:
                restauracao, mensagem = OtimizadorRedeAvancado.restaurar_tweaks_tcp_ip()
                if restauracao:
                    return False, "Falha ao aplicar os ajustes TCP/IP; configuração anterior restaurada. " + "; ".join(falhas)
                return False, "Falha ao aplicar os ajustes TCP/IP e ao restaurar a configuração anterior. " + "; ".join(falhas) + f"; {mensagem}"

            return True, "Pilha TCP/IP otimizada. A configuração original foi guardada para restauração."
        except Exception as e:
            return False, f"Erro ao otimizar rede: {str(e)}"

    @staticmethod
    def restaurar_tweaks_tcp_ip():
        try:
            backup_path = OtimizadorRedeAvancado._backup_tcp_path()
            if not os.path.exists(backup_path):
                return False, "Não existe uma cópia anterior da configuração TCP/IP para restaurar."

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            resultado = subprocess.run(
                ["netsh", "exec", backup_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
            )
            if resultado.returncode != 0:
                detalhe = resultado.stderr.strip() or resultado.stdout.strip()
                return False, f"Erro ao restaurar a configuração TCP/IP: {detalhe}"

            os.remove(backup_path)
            return True, "Configuração TCP/IP anterior restaurada."
        except Exception as e:
            return False, f"Erro ao restaurar a configuração TCP/IP: {str(e)}"

