"""Biblioteca de vídeos e fluxo de upload/indexação em janela modal."""
import sqlite3

import streamlit as st

from components.cards import card_video
from services.config import BANCO, BASE, VIDEOS
from services.diagnostico_interface import testar_deteccao
from services.indexacao import agrupar_deteccoes, salvar_eventos
from services.upload_video import guardar_upload
from services.video import listar_videos
from indexar_video import detectar_video


@st.cache_resource(show_spinner="Carregando YOLO local...")
def _modelo_local(caminho_modelo):
    from ultralytics import YOLO
    return YOLO(str(caminho_modelo))


def _modelo():
    pesos = BASE / "yolo11n.pt"
    if not pesos.is_file():
        raise FileNotFoundError("Modelo yolo11n.pt não encontrado na raiz do projeto.")
    return _modelo_local(str(pesos))


@st.dialog("Adicionar e processar gravação", width="large")
def _modal_video():
    """Upload, diagnóstico e indexação em um único modal.

    Os widgets dentro do dialog atualizam apenas o modal.
    A indexação completa recarrega a página ao finalizar para atualizar KPIs.
    """
    st.caption("Envie um arquivo MP4, teste a detecção ou indexe uma gravação existente.")

    st.markdown("#### 1. Adicionar gravação")
    arquivo = st.file_uploader(
        "Selecione um arquivo MP4",
        type=["mp4"],
        accept_multiple_files=False,
        key="modal_upload_mp4",
    )

    if arquivo is not None:
        st.caption(f"{arquivo.name} · {arquivo.size / (1024 * 1024):.1f} MB")
        if st.button("Adicionar à biblioteca", type="primary", key="modal_salvar_mp4"):
            try:
                arquivo.seek(0)
                destino = guardar_upload(arquivo, arquivo.name, VIDEOS)
                import cv2

                captura = cv2.VideoCapture(str(destino))
                try:
                    valido = captura.isOpened() and captura.read()[0]
                finally:
                    captura.release()
                if not valido:
                    destino.unlink(missing_ok=True)
                    raise ValueError("O arquivo não contém um vídeo MP4 legível.")
            except (OSError, ValueError) as erro:
                st.error(f"Falha ao adicionar gravação: {erro}")
            else:
                st.session_state["modal_video_selecionado"] = destino.name
                st.session_state["modal_gravacao_processamento"] = destino.name
                st.session_state["modal_video_adicionado"] = (
                    f"{destino.name} foi adicionado à biblioteca."
                )
                # Mantém o modal aberto e atualiza o seletor de vídeos.
                st.rerun(scope="fragment")

    if aviso := st.session_state.pop("modal_video_adicionado", None):
        st.success(aviso)

    st.divider()
    st.markdown("#### 2. Testar detecção ou indexar")

    disponiveis = listar_videos()
    if not disponiveis:
        st.info("Ainda não existem gravações na biblioteca.")
        return

    nomes = [video.name for video in disponiveis]
    selecionado = st.session_state.get("modal_video_selecionado")
    indice = nomes.index(selecionado) if selecionado in nomes else 0
    nome = st.selectbox(
        "Gravação",
        nomes,
        index=indice,
        key="modal_gravacao_processamento",
    )
    caminho = VIDEOS / nome

    with st.expander("Diagnóstico rápido (não altera o SQLite)", expanded=True):
        st.caption(
            "Amostra aproximadamente 1 frame por segundo nos primeiros 30 segundos "
            "com confiança de 10%. Inclui bicicleta para investigar possíveis "
            "confusões com motocicleta."
        )
        if st.button("Testar detecção", key="modal_testar_deteccao"):
            try:
                with st.spinner("Analisando frames amostrados..."):
                    frames, classes = testar_deteccao(caminho, _modelo())
                st.success(f"Teste concluído: {frames} frames analisados.")
                if frames:
                    colunas = st.columns(4)
                    for coluna, classe in zip(
                        colunas, ("pessoa", "bicicleta", "carro", "motocicleta")
                    ):
                        coluna.metric(classe.capitalize(), classes.get(classe, 0))
                    st.caption(
                        "Contagens de caixas por frame, não de objetos únicos. "
                        "Não representam precisão nem recall."
                    )
                else:
                    st.warning("Não foi possível ler frames no trecho analisado.")
            except (OSError, RuntimeError, ValueError) as erro:
                st.error(f"Falha no teste: {erro}")

    with st.expander("Indexação completa", expanded=False):
        st.caption(
            "Analisa todos os frames com confiança de 40% e atualiza somente "
            "os eventos deste vídeo no SQLite. Os eventos de outros vídeos "
            "são preservados."
        )
        confirmar = st.checkbox(
            f"Confirmo a reindexação de {nome}",
            key=f"modal_confirmar_{nome}",
        )
        if st.button(
            "Executar indexação completa",
            type="primary",
            disabled=not confirmar,
            key="modal_indexacao_completa",
        ):
            try:
                with st.spinner("Processando todos os frames com YOLO..."):
                    deteccoes = detectar_video(caminho, _modelo())
                    eventos = agrupar_deteccoes(deteccoes, tolerancia=2)
                    quantidade = salvar_eventos(BANCO, nome, eventos)
            except (OSError, RuntimeError, ValueError, sqlite3.Error) as erro:
                st.error(f"Falha na indexação: {erro}")
            else:
                st.session_state["aviso_video"] = (
                    f"Indexação concluída para {nome}: {quantidade} eventos. "
                    "As outras gravações foram preservadas."
                )
                st.session_state.resultados = None
                st.session_state.evento_ativo = None
                # Atualiza contadores e biblioteca e fecha o modal.
                st.rerun()

    if st.button("Concluir e voltar à biblioteca", key="modal_concluir"):
        st.rerun()


def mostrar_botao_adicionar_video():
    """Botão compacto de acesso ao modal, exibido no cabeçalho da página."""
    if st.button(
        "Adicionar vídeo MP4",
        type="primary",
        use_container_width=True,
        key="abrir_modal_video",
    ):
        _modal_video()


def mostrar_pagina_videos(arquivos):
    """Exibe somente a biblioteca: ações de upload ficam no cabeçalho."""
    if aviso := st.session_state.pop("aviso_video", None):
        st.success(aviso)

    arquivos = listar_videos()
    if arquivos:
        colunas = st.columns(3)
        for i, video in enumerate(arquivos):
            with colunas[i % 3]:
                card_video(video, f"biblioteca_{i}")
    else:
        st.info(
            "Nenhum vídeo MP4 encontrado. Clique em Adicionar vídeo MP4 para começar."
        )
