"""Compatibilidade para imports legados do backend de otimização.

As implementações novas vivem nos módulos especializados em ``modules/``.
"""

from modules.perifericos.audio import OtimizadorAudio
from modules.perifericos.gpu_amd import OtimizadorAMD as OtimizadorAMDBackend
from modules.perifericos.mouse_teclado import (
    OtimizadorMouseTeclado as RedutorInputLagBackend,
)
from modules.perifericos.mouse_teclado import OtimizadorMouseTeclado
from modules.privacidade import OtimizadorPrivacidade as OtimizadorPrivacidadeBackend
from modules.rede import OtimizadorRede
from modules.sistema import (
    AuditorInstalacaoWindows,
    GestorDeErrosBackend,
    OtimizadorSistema,
)


class OtimizadorPerifericos(OtimizadorMouseTeclado):
    """Alias legado que também expõe a rotina de prioridade de áudio."""

    otimizar_prioridade_audio = staticmethod(OtimizadorAudio.otimizar_prioridade_audio)

    @staticmethod
    def executar_tudo():
        resultados = (
            OtimizadorMouseTeclado.otimizar_teclado(),
            OtimizadorMouseTeclado.otimizar_velocidade_teclado_geral(),
            OtimizadorMouseTeclado.otimizar_mouse(),
            OtimizadorAudio.otimizar_prioridade_audio(),
        )
        falhas = [mensagem for sucesso, mensagem in resultados if not sucesso]
        if falhas:
            return False, "; ".join(falhas)
        return True, "Otimizações de periféricos concluídas."


class OtimizadorKernelAvancado:
    """Mantém nomes antigos, delegando nas novas categorias."""

    ativar_msi_mode_gpu = staticmethod(OtimizadorAMDBackend.ativar_msi_mode_gpu)
    otimizar_mmcss_jogos = staticmethod(OtimizadorSistema.otimizar_mmcss_jogos)
    restaurar_mmcss_jogos = staticmethod(OtimizadorSistema.restaurar_mmcss_jogos)


OtimizadorRedeAvancado = OtimizadorRede

__all__ = [
    "OtimizadorAMDBackend",
    "OtimizadorAudio",
    "AuditorInstalacaoWindows",
    "GestorDeErrosBackend",
    "OtimizadorKernelAvancado",
    "OtimizadorPerifericos",
    "OtimizadorPrivacidadeBackend",
    "OtimizadorRede",
    "OtimizadorRedeAvancado",
    "OtimizadorSistema",
    "RedutorInputLagBackend",
]
