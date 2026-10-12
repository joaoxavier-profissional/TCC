"""Pesquisa de detecções com filtros temporais e reprodução."""
import streamlit as st
from services.busca import filtrar_eventos
from services.video import mostrar_video


@st.fragment
def _painel_resultados(resultados):
    """Atualiza seleção e reprodutor sem reinicializar os filtros."""
    coluna_lista, coluna_video = st.columns([1, 1.45], gap="medium")
    with coluna_lista:
        st.markdown("**Resultados da pesquisa**")
        with st.container(key="resultados_rolagem", border=False):
            if not resultados:
                st.info("Nenhum evento encontrado. Tente ampliar os filtros.")
            for i, (video, classe, inicio, fim) in enumerate(resultados):
                with st.container(border=True):
                    texto, botao = st.columns([3, 1])
                    with texto:
                        st.markdown(f"**{classe.capitalize()}**")
                        st.caption(f"{video} | {inicio} até {fim}")
                    with botao:
                        if st.button("▶", key=f"evento_{i}", help="Assistir ao evento"):
                            st.session_state.evento_ativo = i
                            st.rerun(scope="fragment")
    with coluna_video:
        st.markdown("**Reprodução do evento**")
        indice = st.session_state.evento_ativo
        if indice is not None and 0 <= indice < len(resultados):
            video, classe, inicio, fim = resultados[indice]
            mostrar_video(video, inicio)
            st.caption(f"🎞️ {video} | {classe.capitalize()} | {inicio} até {fim}")
        else:
            st.info("Selecione um evento à esquerda para assistir à gravação.")


def mostrar_busca(eventos, classes, nomes_indexados):
    st.subheader("Pesquisar detecções")
    st.caption("Os horários são relativos ao início de cada gravação (HH:MM:SS).")

    with st.form("form_busca_eventos"):
        filtro1, filtro2 = st.columns(2)
        with filtro1:
            classe_filtro = st.selectbox("Tipo de objeto", ["Todas"] + classes)
        with filtro2:
            video_filtro = st.selectbox("Gravação", ["Todos"] + nomes_indexados)

        usar_intervalo = st.checkbox("Filtrar por intervalo de tempo")
        tempo1, tempo2, ordem = st.columns([1, 1, 1.2])
        with tempo1:
            inicio_texto = st.text_input("De (HH:MM:SS)", value="00:00:00", disabled=not usar_intervalo)
        with tempo2:
            fim_texto = st.text_input("Até (HH:MM:SS)", value="00:01:00", disabled=not usar_intervalo)
        with ordem:
            ordenacao = st.selectbox("Ordenar por", ["Horário (crescente)", "Horário (decrescente)", "Classe (A–Z)", "Gravação (A–Z)"])
        pesquisar = st.form_submit_button("🔎 Pesquisar", type="primary", use_container_width=True)

    if pesquisar:
        from services.video import segundos
        try:
            inicio = segundos(inicio_texto) if usar_intervalo else None
            fim = segundos(fim_texto) if usar_intervalo else None
            if usar_intervalo and (not all(0 <= int(x) < 60 for x in inicio_texto.split(":")[1:]) or not all(0 <= int(x) < 60 for x in fim_texto.split(":")[1:])):
                raise ValueError("Minutos e segundos devem estar entre 00 e 59.")
            novos_resultados = filtrar_eventos(eventos, classe_filtro, video_filtro, inicio, fim, ordenacao)
        except (ValueError, TypeError):
            st.error("Intervalo inválido. Use HH:MM:SS, com início menor ou igual ao fim.")
        else:
            st.session_state.resultados = novos_resultados
            st.session_state.evento_ativo = None

    resultados = st.session_state.resultados
    if resultados is None:
        st.info("Escolha os filtros e clique em Pesquisar.")
        return

    total_videos = len({e[0] for e in resultados})
    a, b = st.columns(2)
    a.metric("Resultados encontrados", len(resultados))
    b.metric("Gravações com resultados", total_videos)
    _painel_resultados(resultados)
