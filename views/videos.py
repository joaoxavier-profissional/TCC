"""Biblioteca, upload e processamento local de vídeos pela interface."""
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


def mostrar_pagina_videos(arquivos):
    st.subheader("Adicionar gravação")
    st.caption("Adicione vídeos MP4 locais à biblioteca. Nenhum arquivo será sobrescrito.")
    arquivo = st.file_uploader("Selecione um vídeo MP4", type=["mp4"], accept_multiple_files=False)
    if arquivo is not None:
        st.caption(f"Arquivo selecionado: {arquivo.name} ({arquivo.size / 1024 / 1024:.1f} MB)")
        if st.button("Adicionar vídeo à biblioteca", type="primary"):
            try:
                arquivo.seek(0)
                destino = guardar_upload(arquivo, arquivo.name, VIDEOS)
                # Valida se é um MP4 legível; extensão sozinha não é suficiente.
                import cv2
                captura = cv2.VideoCapture(str(destino))
                try:
                    valido = captura.isOpened() and captura.read()[0]
                finally:
                    captura.release()
                if not valido:
                    destino.unlink(missing_ok=True)
                    raise ValueError("O arquivo não contém uma gravação MP4 legível.")
            except (OSError, ValueError) as erro:
                st.error(f"Não foi possível adicionar o vídeo: {erro}")
            else:
                st.session_state["aviso_video"] = f"Vídeo {destino.name} adicionado com sucesso."
                st.rerun()

    if aviso := st.session_state.pop("aviso_video", None):
        st.success(aviso)

    st.divider()
    st.subheader("Testar detecção e indexar")
    disponiveis = listar_videos()
    if not disponiveis:
        st.info("Adicione uma gravação MP4 para começar.")
    else:
        nome = st.selectbox("Selecione a gravação para processamento", [p.name for p in disponiveis])
        caminho = VIDEOS / nome

        st.markdown("**Diagnóstico rápido — não altera o banco de dados**")
        st.caption(
            "Analisa aproximadamente 1 frame por segundo nos primeiros 30 segundos. "
            "Usa confiança mínima de 10% e inclui bicicleta para investigar confusões com moto."
        )
        if st.button("🔎 Testar detecção", key="testar_ia"):
            try:
                with st.spinner("Analisando amostras de vídeo..."):
                    frames, classes = testar_deteccao(caminho, _modelo())
                st.success(f"Diagnóstico concluído: {frames} frames examinados.")
                if frames:
                    a, b, c, d = st.columns(4)
                    for coluna, classe in zip((a, b, c, d), ("pessoa", "bicicleta", "carro", "motocicleta")):
                        coluna.metric(classe.capitalize(), classes.get(classe, 0))
                    st.caption(
                        "As quantidades representam caixas identificadas nos frames amostrados, "
                        "não objetos únicos. Não medem precisão nem recall."
                    )
                else:
                    st.warning("Nenhum frame legível no trecho examinado.")
            except (OSError, RuntimeError, ValueError, sqlite3.Error) as erro:
                st.error(f"Falha no diagnóstico: {erro}")

        st.markdown("**Indexação completa — atualiza os eventos deste vídeo**")
        st.caption(
            "Processa todos os frames com confiança de 40%. Substitui apenas os eventos "
            "da gravação selecionada no SQLite, mantendo os de outras gravações."
        )
        confirmar = st.checkbox(f"Confirmo a reindexação de {nome}", key="confirmar_indexacao")
        if st.button("⚙️ Executar indexação completa", type="primary",
                     disabled=not confirmar, key="indexar_ia"):
            try:
                with st.spinner("Analisando todos os frames com YOLO. Não feche esta página."):
                    deteccoes = detectar_video(caminho, _modelo())
                    eventos = agrupar_deteccoes(deteccoes, tolerancia=2)
                    quantidade = salvar_eventos(BANCO, nome, eventos)
                st.session_state["aviso_video"] = (
                    f"Indexação concluída para {nome}: {quantidade} eventos armazenados. "
                    "As outras gravações foram preservadas."
                )
                st.session_state.resultados = None
                st.session_state.evento_ativo = None
                st.rerun()
            except (OSError, RuntimeError, ValueError) as erro:
                st.error(f"Não foi possível indexar o vídeo: {erro}. Eventos anteriores preservados se a gravação não chegou ao banco.")

    st.divider()
    st.subheader("Biblioteca de gravações")
    arquivos = listar_videos()
    if arquivos:
        colunas = st.columns(3)
        for i, video in enumerate(arquivos):
            with colunas[i % 3]:
                card_video(video, f"biblioteca_{i}")
    else:
        st.info("Nenhum vídeo MP4 encontrado.")
