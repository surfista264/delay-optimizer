import customtkinter as ctk
import threading
from perifericos import (
    OtimizadorPerifericos,
    OtimizadorRede,
    OtimizadorSistema
)

# Configuração global do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class OtimizadorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Windows Ultimate Optimizer")
        self.geometry("480x560")
        self.resizable(False, False)

        # --- Título Principal ---
        self.titulo = ctk.CTkLabel(
            self, 
            text="⚡ Otimizador de Sistema & Periféricos", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        self.titulo.pack(pady=(25, 5))

        self.subtitulo = ctk.CTkLabel(
            self, 
            text="Clique na otimização que deseja aplicar:", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        )
        self.subtitulo.pack(pady=(0, 25))

        # --- Botões Individuais ---
        self.btn_perifericos = self.criar_botao(
            "⌨ Otimizar Periféricos (Teclado, Rato e Áudio)", 
            lambda: self.executar_acao_botao(self.btn_perifericos, OtimizadorPerifericos.executar_tudo, "✔ Periféricos Otimizados!")
        )
        
        self.btn_rede = self.criar_botao(
            "🌐 Otimizar Rede & DNS (Cloudflare)", 
            lambda: self.executar_acao_botao(self.btn_rede, OtimizadorRede.otimizar_adaptador_rede, "✔ Rede e DNS Otimizados!")
        )

        self.btn_sistema = self.criar_botao(
            "🚀 Otimização Avançada do Sistema & Limpeza", 
            lambda: self.executar_acao_botao(self.btn_sistema, OtimizadorSistema.executar_tudo, "✔ Sistema Otimizado!")
        )

        # Botão Mestre
        self.btn_tudo = self.criar_botao(
            "⭐ Executar TODAS as Otimizações", 
            lambda: self.executar_acao_botao(self.btn_tudo, self.executar_tudo_global, "✔ Todas as Otimizações Aplicadas!"),
            cor_fundo="#16a085", cor_hover="#1abc9c"
        )

        # --- Status Geral no Rodapé ---
        self.label_status = ctk.CTkLabel(
            self, 
            text="Sistema pronto e à espera de comandos.", 
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
            text_color="gray60"
        )
        self.label_status.pack(pady=(35, 0))

    def criar_botao(self, texto, comando, cor_fundo=None, cor_hover=None):
        """Padroniza a criação dos botões da interface"""
        kwargs = {
            "master": self,
            "text": texto,
            "command": comando,
            "width": 420,
            "height": 45,
            "font": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            "corner_radius": 8
        }
        if cor_fundo and cor_hover:
            kwargs["fg_color"] = cor_fundo
            kwargs["hover_color"] = cor_hover

        btn = ctk.CTkButton(**kwargs)
        btn.pack(pady=8)
        return btn

    def executar_tudo_global(self):
        """Executa todas as classes em sequência"""
        OtimizadorPerifericos.executar_tudo()
        OtimizadorRede.otimizar_adaptador_rede()
        OtimizadorSistema.executar_tudo()

    def executar_acao_botao(self, botao, funcao_alvo, mensagem_sucesso):
        """Altera o estado do botão específico enquanto executa a tarefa em segundo plano"""
        texto_original = botao.cget("text")
        
        def tarefa():
            try:
                # Desativa o botão e muda o visual para indicar processamento
                botao.configure(state="disabled", fg_color="#f39c12", text="A processar...")
                self.label_status.configure(text=f"A executar: {texto_original}", text_color="#f1c40f")
                
                # Executa a função lógica real
                funcao_alvo()
                
                # Sucesso: muda o botão para verde com mensagem de concluído
                botao.configure(fg_color="#27ae60", text=mensagem_sucesso)
                self.label_status.configure(text=mensagem_sucesso, text_color="#2ecc71")
            
            except Exception as e:
                botao.configure(fg_color="#c0392b", text="❌ Erro na Otimização")
                self.label_status.configure(text=f"Erro: {str(e)}", text_color="#e74c3c")
            
            finally:
                # Restaura o botão original após 3 segundos
                self.after(3000, lambda: self.restaurar_botao(botao, texto_original))

        threading.Thread(target=tarefa, daemon=True).start()

    def restaurar_botao(self, botao, texto_original):
        """Volta o botão ao estado padrão"""
        try:
            botao.configure(state="normal", text=texto_original, fg_color=("#3b8ed0", "#1f6aa5"))
        except Exception:
            pass

if __name__ == "__main__":
    app = OtimizadorApp()
    app.mainloop()