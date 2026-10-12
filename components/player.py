
import base64
import html
import json
from pathlib import Path

import streamlit.components.v1 as components


CAMINHO_CSS = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "player.css"
)

CORES = {
    "pessoa": "#28d4bd",
    "carro": "#f4b58a",
    "motocicleta": "#70a8ff",
}

COR_PADRAO = "#b8a5ff"


def converter_segundos(horario):
    """Converte HH:MM:SS ou número para segundos."""

    if isinstance(horario, (int, float)):
        return float(horario)

    partes = str(horario).strip().split(":")

    if len(partes) != 3:
        raise ValueError(f"Horário inválido: {horario}")

    horas, minutos, segundos = map(int, partes)

    return horas * 3600 + minutos * 60 + segundos


def mostrar_player(caminho_video, inicio=0, eventos=None):
    """
    Exibe o player personalizado com marcações de eventos.

    eventos: lista de tuplas no formato
        (video, classe, inicio, fim)
    """

    caminho = Path(caminho_video)

    if not caminho.is_file():
        return False

    # Incorpora o vídeo no HTML (adequado para testes pequenos).
    dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
    video_src = f"data:video/mp4;base64,{dados}"

    nome = html.escape(caminho.name)
    css_player = CAMINHO_CSS.read_text(encoding="utf-8")

    # --------------------------------------
    # PREPARAR EVENTOS PARA O JAVASCRIPT
    # --------------------------------------

    eventos_js = []

    for evento in eventos or []:
        video, classe, horario_inicio, horario_fim = evento

        # Não mistura eventos de gravações diferentes.
        if video != caminho.name:
            continue

        try:
            segundo_inicio = converter_segundos(horario_inicio)
            segundo_fim = converter_segundos(horario_fim)
        except (TypeError, ValueError):
            continue

        if segundo_inicio < 0 or segundo_fim < segundo_inicio:
            continue

        classe_normalizada = str(classe).strip().lower()

        eventos_js.append({
            "classe": str(classe),
            "inicio": segundo_inicio,
            "fim": segundo_fim,
            "cor": CORES.get(classe_normalizada, COR_PADRAO),
        })

    # json.dumps cria dados seguros para leitura pelo JavaScript.
    dados_eventos = json.dumps(eventos_js).replace("<", "\\u003c")
    dados_inicio = json.dumps(max(0, converter_segundos(inicio)))

    codigo_html = """
    <style>
    __CSS_PLAYER__
    </style>

    <div class="player" id="player">
        <video id="video" preload="metadata">
            <source src="__VIDEO_SRC__" type="video/mp4">
        </video>

        <div class="titulo">📹 __NOME__</div>

        <div class="controles">
            <div class="legenda-eventos" id="legenda-eventos"></div>

            <div class="area-progresso">
                <div
                    id="marcacoes"
                    class="marcacoes"
                    aria-label="Eventos detectados"
                ></div>

                <input
                    type="range"
                    id="progresso"
                    class="progresso"
                    min="0"
                    max="100"
                    value="0"
                    step="0.1"
                    aria-label="Posição no vídeo"
                >
            </div>

            <div class="botoes">
                <button id="play" title="Reproduzir">▶</button>

                <span class="tempo" id="tempo">
                    00:00 / 00:00
                </span>

                <span class="espaco"></span>

                <button id="fullscreen" title="Tela cheia">
                    ⛶
                </button>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById("video");
        const progresso = document.getElementById("progresso");
        const play = document.getElementById("play");
        const tempo = document.getElementById("tempo");
        const fullscreen = document.getElementById("fullscreen");
        const player = document.getElementById("player");
        const marcacoes = document.getElementById("marcacoes");

        const inicio = __INICIO__;
        const eventos = __EVENTOS__;


        const legendaEventos = document.getElementById("legenda-eventos");

        function desenharLegenda() {
            legendaEventos.innerHTML = "";

            // Evita repetir classes
            const classes = new Map();

            eventos.forEach((evento) => {
                const classe = evento.classe.trim().toLowerCase();

                if (!classes.has(classe)) {
                    classes.set(classe, evento.cor);
                }
            });

            classes.forEach((cor, classe) => {
                const item = document.createElement("span");
                item.className = "legenda-item";

                const marcador = document.createElement("span");
                marcador.className = "legenda-cor";
                marcador.style.backgroundColor = cor;

                const nome = document.createElement("span");
                nome.textContent =
                    classe.charAt(0).toUpperCase() + classe.slice(1);

                item.appendChild(marcador);
                item.appendChild(nome);

                legendaEventos.appendChild(item);
            });
        }


        function formatarTempo(segundos) {
            if (!Number.isFinite(segundos)) return "00:00";

            const minutos = Math.floor(segundos / 60);
            const restantes = Math.floor(segundos % 60);

            return String(minutos).padStart(2, "0") + ":" +
                   String(restantes).padStart(2, "0");
        }

        function atualizarInterface() {
            progresso.value = video.currentTime || 0;

            tempo.textContent =
                formatarTempo(video.currentTime) +
                " / " +
                formatarTempo(video.duration);
        }

        // ----------------------------------
        // MARCAÇÕES DAS DETECÇÕES
        // ----------------------------------

        function desenharEventos() {
            marcacoes.innerHTML = "";

            const duracao = video.duration;

            if (!Number.isFinite(duracao) || duracao <= 0) {
                return;
            }

            eventos.forEach((evento) => {
                const inicioEvento = Math.max(
                    0,
                    Math.min(evento.inicio, duracao)
                );

                const fimEvento = Math.max(
                    inicioEvento,
                    Math.min(evento.fim, duracao)
                );

                const posicao = inicioEvento / duracao * 100;
                const largura = (
                    (fimEvento - inicioEvento) / duracao * 100
                );

                const faixa = document.createElement("button");

                faixa.type = "button";
                faixa.className = "marcacao-evento";
                faixa.style.left = posicao + "%";
                faixa.style.width = Math.max(largura, 0.4) + "%";
                faixa.style.backgroundColor = evento.cor;

                faixa.title =
                    evento.classe + " — " +
                    formatarTempo(evento.inicio) + " até " +
                    formatarTempo(evento.fim);

                faixa.setAttribute(
                    "aria-label",
                    "Ir para evento: " + faixa.title
                );

                faixa.addEventListener("click", (e) => {
                    e.stopPropagation();

                    video.currentTime = inicioEvento;
                    atualizarInterface();

                    // O clique posiciona o vídeo.
                    // Se estiver pausado, inicia a reprodução.
                    if (video.paused) {
                        video.play().catch(console.error);
                    }
                });

                marcacoes.appendChild(faixa);
            });
        }

        video.addEventListener("loadedmetadata", () => {
            progresso.max = video.duration;

            video.currentTime = Math.min(
                inicio,
                video.duration
            );

            desenharEventos();
            desenharLegenda();
            atualizarInterface();
        });

        video.addEventListener("timeupdate", atualizarInterface);

        video.addEventListener("play", () => {
            play.textContent = "❚❚";
        });

        video.addEventListener("pause", () => {
            play.textContent = "▶";
        });

        play.addEventListener("click", () => {
            if (video.paused) {
                video.play().catch(console.error);
            } else {
                video.pause();
            }
        });

        progresso.addEventListener("input", () => {
            video.currentTime = Number(progresso.value);
            atualizarInterface();
        });

        fullscreen.addEventListener("click", () => {
            if (!document.fullscreenElement) {
                player.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });
    </script>
    """

    codigo_html = (
        codigo_html
        .replace("__CSS_PLAYER__", css_player)
        .replace("__VIDEO_SRC__", video_src)
        .replace("__NOME__", nome)
        .replace("__INICIO__", dados_inicio)
        .replace("__EVENTOS__", dados_eventos)
    )

    components.html(
        codigo_html,
        height=520,
        scrolling=False
    )

    return True
