"""Ponto de entrada do sistema inteligente de CFTV.

Execute na raiz do projeto: streamlit run app.py
"""
from pathlib import Path
import streamlit as st

from components.sidebar import mostrar_sidebar
from views.visao_geral import mostrar_visao_geral
from views.buscar_eventos import mostrar_busca
from views.videos import mostrar_pagina_videos
from views.relatorios import mostrar_relatorios
from services.banco import carregar_eventos
from services.video import listar_videos

BASE = Path(__file__).resolve().parent

st.set_page_config(
    page_title="CFTV | Central Inteligente",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos em arquivo separado: edite assets/style.css.
css = (BASE / "assets" / "style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Estado mantido entre as interações do Streamlit.
for chave, padrao in {
    "pagina": "Visão geral",
    "resultados": None,
    "evento_ativo": None,
    "video_aberto": None,
}.items():
    if chave not in st.session_state:
        st.session_state[chave] = padrao

# Carrega informações do banco e arquivos locais.
eventos, erro = carregar_eventos()
arquivos = listar_videos()
nomes_indexados = sorted({evento[0] for evento in eventos})
# Inclui também os MP4 locais sem eventos indexados.
nomes_gravacoes = sorted(set(nomes_indexados) | {arquivo.name for arquivo in arquivos})
classes = sorted({evento[1] for evento in eventos})

mostrar_sidebar(erro)
pagina = st.session_state.pagina
st.title(pagina)
st.caption("Sistema inteligente de indexação e recuperação de eventos em gravações de CFTV")

if erro:
    st.error(erro)
    st.stop()

# Indicadores visíveis em todas as páginas.
a, b, c, d = st.columns(4)
a.metric("📹 Vídeos indexados", len(nomes_indexados))
b.metric("📋 Eventos registrados", len(eventos))
c.metric("🔎 Classes detectadas", len(classes))
d.metric("🎞️ Arquivos disponíveis", len(arquivos))

# Mantém a navegação personalizada (sem a navegação automática do Streamlit).
if pagina == "Visão geral":
    mostrar_visao_geral(eventos, arquivos)
elif pagina == "Buscar eventos":
    mostrar_busca(eventos, classes, nomes_gravacoes)
elif pagina == "Vídeos":
    mostrar_pagina_videos(arquivos)
elif pagina == "Relatórios":
    mostrar_relatorios(eventos)
