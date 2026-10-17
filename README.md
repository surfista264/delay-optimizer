# ⚡ Windows Ultimate Optimizer (`0 delay`) - v0.1.0

Um utilitário de otimização e limpeza de alta performance para Windows, desenvolvido em **Python** com uma interface gráfica moderna baseada em **CustomTkinter** e estruturado com **Programação Orientada a Objetos (POO)**.

O objetivo principal deste software é reduzir a latência de periféricos, otimizar a rede, ajustar prioridades de sistema e limpar ficheiros temporários de forma simples, segura e modular.

---

## 🚀 Funcionalidades da Versão (v0.1.0)

O projeto está dividido em módulos especializados:

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
*   **CustomTkinter** (Interface gráfica moderna em modo escuro)
*   **Módulo `winreg`** (Modificações seguras no Registo do Windows)
*   **Multithreading** (Para garantir fluidez na interface durante os processos)
*   **PyInstaller** (Para a compilação do executável `.exe`)

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