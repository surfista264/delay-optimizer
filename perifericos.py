import os
import shutil
import subprocess
import winreg

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
            print("✔ Aceleração do rato removida com sucesso!")
        except Exception as e:
            print(f"Erro ao otimizar rato: {e}")

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


class OtimizadorRede:
    @staticmethod
    def alterar_dns_cloudflare():
        try:
            # IPv4
            subprocess.run('netsh interface ip set dns name="Ethernet" source="static" address="1.1.1.1"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ip add dns name="Ethernet" address="1.0.0.1" index=2', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ip set dns name="Wi-Fi" source="static" address="1.1.1.1"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ip add dns name="Wi-Fi" address="1.0.0.1" index=2', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # IPv6
            subprocess.run('netsh interface ipv6 set dns name="Ethernet" source="static" address="2606:4700:4700::1111"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ipv6 add dns name="Ethernet" address="2606:4700:4700::1001" index=2', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ipv6 set dns name="Wi-Fi" source="static" address="2606:4700:4700::1111"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('netsh interface ipv6 add dns name="Wi-Fi" address="2606:4700:4700::1001" index=2', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("✔ DNS Cloudflare (IPv4 e IPv6) configurado!")
        except Exception as e:
            print(f"Erro ao alterar DNS: {e}")

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


class OtimizadorSistema:
    @staticmethod
    def desativar_sysmain():
        try:
            subprocess.run("sc stop SysMain", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("sc config SysMain start= disabled", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✔ Serviço SysMain desativado.")
        except Exception as e:
            print(f"Erro ao desativar SysMain: {e}")

    @staticmethod
    def ativar_hags():
        try:
            hags_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hags_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)
            print("✔ HAGS ativado com sucesso.")
        except Exception as e:
            print(f"Erro ao ativar HAGS: {e}")

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
            print("✔ Limpeza profunda concluída!")
        except Exception as e:
            print(f"Erro na limpeza: {e}")

    @classmethod
    def executar_tudo(cls):
        cls.desativar_sysmain()
        cls.ativar_hags()
        cls.limpeza_profunda_sistema()