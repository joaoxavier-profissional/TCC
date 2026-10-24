"""Dashboard de gravações e eventos recentes."""
import streamlit as st
from components.cards import card_video

def mostrar_visao_geral(eventos, arquivos):
    st.subheader('Gravações disponíveis')
    if arquivos:
        colunas = st.columns(3)
        for i, arquivo in enumerate(arquivos):
            with colunas[i % 3]:
                card_video(arquivo, f'geral_{i}')
    else:
        st.info('Nenhum vídeo MP4 encontrado na pasta videos.')
    st.subheader('Eventos indexados')
    if eventos:
        colunas = st.columns(3)
        for i, (video, classe, inicio, fim) in enumerate(eventos[-6:][::-1]):
            with colunas[i % 3]:
                with st.container(border=True):
                    st.markdown(f'**{classe.capitalize()}**')
                    st.caption(f'{video}')
                    st.caption(f'{inicio} até {fim}')
    else:
        st.info('Nenhum evento cadastrado.')
