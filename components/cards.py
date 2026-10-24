"""Componente reutilizável para exibir gravações."""
from html import escape
import streamlit as st
from services.video import obter_miniatura

def card_video(arquivo, chave):
    with st.container(border=True):
        st.markdown(f'\n\n            <div class="titulo-video" title="{escape(arquivo.name, quote=True)}">\n\n                {escape(arquivo.name, quote=True)}\n\n            </div>\n\n            ', unsafe_allow_html=True)
        aberto = st.session_state.video_aberto == arquivo.name
        if aberto:
            st.video(str(arquivo))
            if st.button('Fechar reprodução', key=f'fechar_{chave}', use_container_width=True):
                st.session_state.video_aberto = None
                st.rerun()
        else:
            imagem = obter_miniatura(str(arquivo), 1, arquivo.stat().st_mtime_ns)
            if imagem is not None:
                st.image(imagem, use_container_width=True)
            else:
                st.info('Miniatura indisponível.')
            if st.button('Reproduzir', key=f'abrir_{chave}', use_container_width=True):
                st.session_state.video_aberto = arquivo.name
                st.rerun()
