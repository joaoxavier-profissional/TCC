
import html
import math

import streamlit as st


# ==========================================
# CORES DOS EVENTOS
# ==========================================

CORES = {
    "pessoa": "#28d4bd",
    "carro": "#f4b58a",
    "motocicleta": "#70a8ff",
}

COR_PADRAO = "#b8a5ff"


# ==========================================
# CONVERSÃO DE HORÁRIOS
# ==========================================

def converter_segundos(horario):
    """
    Converte HH:MM:SS para segundos.

    Exemplos:
        00:00:06 -> 6
        00:01:30 -> 90
    """

    if horario is None:
        raise ValueError("O horário não pode ser None.")

    # Também aceita valores numéricos em segundos
    if isinstance(horario, (int, float)):
        if not math.isfinite(horario) or horario < 0:
            raise ValueError(f"Horário inválido: {horario}")
        return float(horario)

    partes = str(horario).strip().split(":")

    if len(partes) != 3:
        raise ValueError(f"Horário inválido: {horario}")

    try:
        horas, minutos, segundos = map(int, partes)
    except ValueError as erro:
        raise ValueError(
            f"Horário inválido: {horario}"
        ) from erro

    if (
        horas < 0
        or not 0 <= minutos < 60
        or not 0 <= segundos < 60
    ):
        raise ValueError(f"Horário inválido: {horario}")

    return horas * 3600 + minutos * 60 + segundos


# ==========================================
# LINHA DO TEMPO
# ==========================================

def mostrar_linha_tempo(eventos, duracao):
    """
    Exibe uma linha do tempo com os eventos detectados.

    Parâmetros:
        eventos: lista de tuplas
            (video, classe, inicio, fim)

        duracao: duração total do vídeo em segundos

    Retorno:
        Segundo selecionado no slider ou None.
    """

    # --------------------------------------
    # 1. VALIDAR DURAÇÃO
    # --------------------------------------

    if duracao is None:
        st.warning("Duração do vídeo indisponível.")
        return None

    try:
        duracao = float(duracao)
    except (TypeError, ValueError):
        st.warning("Duração do vídeo inválida.")
        return None

    if not math.isfinite(duracao) or duracao <= 0:
        st.warning("Não foi possível determinar a duração do vídeo.")
        return None

    if not eventos:
        st.info("Nenhum evento para exibir na linha do tempo.")
        return None

    # --------------------------------------
    # 2. PREPARAR AS FAIXAS DOS EVENTOS
    # --------------------------------------

    faixas = []
    classes_encontradas = set()

    for video, classe, inicio, fim in eventos:

        try:
            segundo_inicio = converter_segundos(inicio)
            segundo_fim = converter_segundos(fim)
        except (TypeError, ValueError) as erro:
            st.warning(
                f"Evento ignorado por horário inválido: {erro}"
            )
            continue

        if segundo_fim < segundo_inicio:
            st.warning(
                f"Evento ignorado: término anterior ao início "
                f"({inicio} até {fim})."
            )
            continue

        # Limita os horários à duração do vídeo
        inicio_limitado = max(
            0.0,
            min(float(segundo_inicio), duracao)
        )

        fim_limitado = max(
            inicio_limitado,
            min(float(segundo_fim), duracao)
        )

        # Converte os horários para porcentagem
        posicao = inicio_limitado / duracao * 100

        largura = (
            (fim_limitado - inicio_limitado)
            / duracao
            * 100
        )

        classe_normalizada = str(classe).strip().lower()

        cor = CORES.get(
            classe_normalizada,
            COR_PADRAO
        )

        classes_encontradas.add(classe_normalizada)

        descricao = html.escape(
            f"{classe}: {inicio} até {fim}",
            quote=True
        )

        faixas.append(
            f'<div class="timeline-evento" '
            f'style="left:{posicao:.4f}%;'
            f'width:{largura:.4f}%;'
            f'background:{cor};" '
            f'title="{descricao}"></div>'
        )

    if not faixas:
        st.info("Nenhum evento válido para exibir.")
        return None

    # --------------------------------------
    # 3. DESENHAR A LINHA DO TEMPO
    # --------------------------------------

    st.markdown(
        '<div class="timeline-trilha">'
        + "".join(faixas)
        + '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Duração total do vídeo: {duracao:.1f} segundos"
    )

    # --------------------------------------
    # 4. EXIBIR LEGENDA DAS CLASSES
    # --------------------------------------

    legenda = []

    for classe in sorted(classes_encontradas):

        cor = CORES.get(classe, COR_PADRAO)

        nome = html.escape(classe.capitalize())

        legenda.append(
            f'<span style="display:inline-flex;'
            f'align-items:center;gap:6px;'
            f'margin-right:16px;">'
            f'<span style="display:inline-block;'
            f'width:10px;height:10px;'
            f'border-radius:3px;'
            f'background:{cor};"></span>'
            f'{nome}</span>'
        )

    st.markdown(
        "".join(legenda),
        unsafe_allow_html=True
    )

    # --------------------------------------
    # 5. CONTROLE INTERATIVO
    # --------------------------------------

    instante = st.slider(
        "Posição no vídeo (segundos)",
        min_value=0,
        max_value=max(1, math.ceil(duracao)),
        step=1,
        key="timeline_posicao_teste"
    )

    st.write("Segundo selecionado:", instante)

    return instante