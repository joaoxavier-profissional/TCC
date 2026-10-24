"""Teste rápido de detecção em frames amostrados (não modifica SQLite)."""
from collections import Counter


def testar_deteccao(caminho, modelo, inicio=0, duracao=30, passo=1, confianca=0.10):
    import cv2
    captura = cv2.VideoCapture(str(caminho))
    if not captura.isOpened():
        captura.release()
        raise RuntimeError("Não foi possível abrir o vídeo para o diagnóstico.")
    contagem = Counter()
    frames = 0
    try:
        fps = captura.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            raise RuntimeError("FPS inválido no vídeo.")
        total = captura.get(cv2.CAP_PROP_FRAME_COUNT)
        fim = min(inicio + duracao, total / fps) if total > 0 else inicio + duracao
        tempo = inicio
        while tempo < fim:
            captura.set(cv2.CAP_PROP_POS_FRAMES, int(tempo * fps))
            valido, frame = captura.read()
            if valido:
                frames += 1
                resultado = modelo.predict(frame, conf=confianca, verbose=False)[0]
                for caixa in resultado.boxes:
                    classe = int(caixa.cls[0])
                    if classe in (0, 1, 2, 3):
                        contagem[{0: "pessoa", 1: "bicicleta", 2: "carro", 3: "motocicleta"}[classe]] += 1
            tempo += passo
    finally:
        captura.release()
    return frames, contagem
