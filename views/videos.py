"""Biblioteca de vídeos locais."""
import streamlit as st
from components.cards import card_video

def mostrar_pagina_videos(arquivos):
    st.subheader('Biblioteca de gravações')
    if arquivos:
        colunas = st.columns(3)
        for i, arquivo in enumerate(arquivos):
            with colunas[i % 3]:
                card_video(arquivo, f'biblioteca_{i}')
    else:
        st.info('Nenhum vídeo MP4 encontrado.')
