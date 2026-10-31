# ⚡ Windows Ultimate Optimizer (`0 delay`) - v0.2.0

Um utilitário de otimização e limpeza para Windows, desenvolvido em **Python** com uma interface gráfica baseada em **PyQt6** e estruturado com **Programação Orientada a Objetos (POO)**.

O objetivo principal deste software é reduzir a latência de periféricos, otimizar a rede, ajustar prioridades de sistema e limpar ficheiros temporários de forma simples, segura e modular.

---

## 🚀 Funcionalidades

O projeto está dividido em módulos especializados:

*   `main.py`: inicialização da aplicação e da interface.
*   `interface_pyqt.py`: interface gráfica PyQt6.
*   `modules/`: módulos de otimização organizados por categoria:
    *   `sistema.py`: plano de energia, limpeza e ajustes MMCSS.
    *   `rede.py`: DNS, adaptadores e TCP/IP.
    *   `privacidade.py`: telemetria, diagnóstico e ID de publicidade.
    *   `perifericos/gpu_amd.py`: MPO, HAGS e modo MSI da GPU.
    *   `perifericos/mouse_teclado.py`: rato, teclado e latência de entrada.
    *   `perifericos/audio.py`: prioridade de áudio e multimédia.
*   `perifericos.py`: fachada de compatibilidade para imports antigos do backend.
*   `config.py`: metadados, serviços monitorizados e caminhos padrão.
*   `logger.py`: configuração centralizada do ficheiro `otimizador.log`.

*   ⌨ **Periféricos:**
    *   Otimização da resposta e velocidade do teclado.
    *   Remoção total da aceleração do rato (*mouse acceleration*) para maior precisão.
    *   Ajustes de prioridade de áudio e perfis de baixa latência para headsets (focado em desempenho e jogos).
*   🌐 **Rede & Conectividade:**
    *   Configuração automática de DNS seguro e rápido da Cloudflare (IPv4 e IPv6).
    *   Limpeza de cache DNS (`ipconfig /flushdns`) e reposição de sockets (`netsh winsock reset`).
    *   Otimização avançada de parâmetros do adaptador de rede.
*   🚀 **Sistema & Limpeza:**
    *   Desativação de serviços desnecessários do Windows (como o *SysMain*).
    *   Ativação do HAGS (*Hardware-Accelerated GPU Scheduling*).
    *   Limpeza profunda de ficheiros temporários (`%TEMP%`, `C:\Windows\Temp` e `Prefetch`).

---

## 🛠️ Tecnologias Utilizadas

*   **Python 3.x**
*   **PyQt6** (Interface gráfica)
*   **Módulo `winreg`** (Modificações seguras no Registo do Windows)
*   **Multithreading** (Para garantir fluidez na interface durante os processos)
*   **PyInstaller** (Para a compilação do executável `.exe`)

## ▶️ Executar a partir do código

Instala as dependências utilizadas pelo projeto (`PyQt6`, `watchdog` e `psutil`) e inicia a aplicação com:

```powershell
python main.py
```

O `psutil` alimenta as métricas de CPU e armazenamento do dashboard. Sem esta dependência, a interface continua a iniciar, mas essas métricas são apresentadas como indisponíveis.

Para reiniciar automaticamente durante o desenvolvimento, executa `python run.py`.
Os registos são escritos em `otimizador.log`, junto dos ficheiros da aplicação.
Os backups das configurações são guardados no diretório de dados local do utilizador.

## Usar os módulos na interface

Cada categoria exporta uma classe com métodos estáticos. A interface pode manter
uma instância por categoria e passar os métodos diretamente aos workers:

```python
from modules import (
    OtimizadorAMD,
    OtimizadorAudio,
    OtimizadorMouseTeclado,
    OtimizadorPrivacidade,
    OtimizadorRede,
    OtimizadorSistema,
)

self.otimizador_sistema = OtimizadorSistema()
self.otimizador_rede = OtimizadorRede()
self.otimizador_privacidade = OtimizadorPrivacidade()
self.otimizador_amd = OtimizadorAMD()
self.otimizador_mouse_teclado = OtimizadorMouseTeclado()
self.otimizador_audio = OtimizadorAudio()

# Os métodos são estáticos, portanto funcionam via instância ou diretamente na classe.
tarefa = self.otimizador_sistema.ativar_desempenho_maximo
```

---

## 📦 Como Usar o Executável

1. Vai à aba **Releases** deste repositório e descarrega a versão mais recente (`.exe`).
2. Como o programa altera chaves de registo e limpa diretórios do sistema, clica com o **botão direito** no ficheiro e seleciona **"Executar como Administrador"**.
3. Escolhe a otimização pretendida diretamente na interface gráfica!

---

## 🔮 Planos Futuros

*   Adicionar novas opções de otimização para o sistema.
*   Implementar uma aba de logs detalhados em tempo real para acompanhar cada alteração.
*   Melhorias contínuas na interface e desempenho geral.

---

## 👨‍💻 Autor & Contacto

Desenvolvido por **Diego Silva Ribeiro** (*surfista264*).

*   GitHub: [surfista264](https://github.com/surfista264)