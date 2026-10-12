"""Localização de gravações, miniaturas e reprodução."""
from pathlib import Path
import cv2
import streamlit as st
from services.config import VIDEOS

def segundos(horario):
    """

    Converte HH:MM:SS para segundos.

    Exemplo:

    00:00:12 -> 12

    """
    partes = str(horario).split(':')
    if len(partes) != 3:
        raise ValueError('Horário inválido')
    h, m, s = map(int, partes)
    return h * 3600 + m * 60 + s

def listar_videos():
    """

    Lista os vídeos MP4 existentes na pasta videos.

    """
    if not VIDEOS.is_dir():
        return []
    return sorted(VIDEOS.glob('*.mp4'))

def caminho_video(nome):
    """

    Monta o caminho de um vídeo local.

    """
    return VIDEOS / Path(nome).name

@st.cache_data(show_spinner=False)
def obter_miniatura(caminho, instante, modificacao):
    """

    Extrai um frame do vídeo usando OpenCV.

    O resultado será usado como imagem do card.

    'modificacao' ajuda o cache a perceber quando

    o arquivo de vídeo foi alterado.

    """
    captura = cv2.VideoCapture(caminho)
    if not captura.isOpened():
        captura.release()
        return None
    captura.set(cv2.CAP_PROP_POS_MSEC, instante * 1000)
    sucesso, frame = captura.read()
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        sucesso, frame = captura.read()
    captura.release()
    if not sucesso:
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    altura, largura = frame.shape[:2]
    if largura / altura > 16 / 9:
        largura_corte = int(altura * 16 / 9)
        x = (largura - largura_corte) // 2
        frame = frame[:, x:x + largura_corte]
    else:
        altura_corte = int(largura * 9 / 16)
        y = (altura - altura_corte) // 2
        frame = frame[y:y + altura_corte, :]
    frame = cv2.resize(frame, (640, 360))
    return frame

def mostrar_video(nome, inicio='00:00:00'):
    """

    Reproduz o vídeo no horário do evento.

    """
    caminho = caminho_video(nome)
    if not caminho.is_file():
        st.warning(f'Vídeo não encontrado: {caminho.name}')
        return
    try:
        st.video(str(caminho), start_time=segundos(inicio))
    except ValueError:
        st.error('Horário do evento inválido.')
