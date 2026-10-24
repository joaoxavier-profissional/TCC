"""Cabeçalho, navegação e status do menu lateral."""
import streamlit as st

def mostrar_sidebar(erro):
    with st.sidebar:
        with st.container(key='sidebar_logo'):
            st.title('CFTV')
            st.caption('CENTRAL INTELIGENTE')
            st.divider()
        with st.container(key='sidebar_menu'):
            paginas = ['Visão geral', 'Buscar eventos', 'Vídeos', 'Relatórios']
            for nome in paginas:
                ativo = st.session_state.pagina == nome
                if st.button(nome, key=f'menu_{nome}', type='primary' if ativo else 'secondary', use_container_width=True):
                    st.session_state.pagina = nome
                    st.rerun()
        with st.container(key='sidebar_status'):
            st.divider()
            st.caption('SISTEMA DE INDEXAÇÃO')
            if erro:
                st.error('Banco indisponível')
            else:
                st.success('● Banco conectado')
            st.caption('Projeto de TCC | Visão Computacional')
