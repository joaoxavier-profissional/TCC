"""Indexa um vídeo MP4 local com YOLO e salva eventos no SQLite.

Uso: python indexar_video.py teste.mp4
"""
import argparse
from pathlib import Path

from services.config import BANCO, BASE, VIDEOS
from services.indexacao import agrupar_deteccoes, salvar_eventos


CLASSES = {0: "pessoa", 2: "carro", 3: "motocicleta"}


def detectar_video(caminho, modelo):
    """Extrai classes detectadas por segundo; não altera o banco."""
    import cv2

    captura = cv2.VideoCapture(str(caminho))
    if not captura.isOpened():
        captura.release()
        raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho.name}")
    try:
        fps = captura.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            raise RuntimeError("FPS inválido: não é possível calcular os horários.")
        deteccoes = set()
        indice = 0
        while True:
            sucesso, frame = captura.read()
            if not sucesso:
                break
            segundo = int(indice / fps)
            predicao = modelo.predict(
                frame, classes=list(CLASSES), conf=0.40, verbose=False
            )[0]
            for caixa in predicao.boxes:
                classe_id = int(caixa.cls[0])
                if classe_id in CLASSES:
                    deteccoes.add((segundo, CLASSES[classe_id]))
            indice += 1
        if indice == 0:
            raise RuntimeError("Vídeo vazio ou sem frames legíveis.")
        return sorted(deteccoes)
    finally:
        captura.release()


def main():
    parser = argparse.ArgumentParser(description="Indexação de gravações CFTV")
    parser.add_argument("video", help="Nome do MP4 existente na pasta videos/")
    parser.add_argument("--modelo", default="yolo11n.pt", help="Arquivo .pt local")
    args = parser.parse_args()

    # Evita aceitar caminhos arbitrários fora da pasta videos/.
    if Path(args.video).name != args.video or not args.video.lower().endswith(".mp4"):
        parser.error("Informe somente o nome do arquivo MP4, por exemplo teste.mp4.")
    caminho = (VIDEOS / args.video).resolve()
    if not caminho.is_file() or caminho.parent != VIDEOS.resolve():
        parser.error("Vídeo não encontrado na pasta videos/.")

    pesos = Path(args.modelo)
    if not pesos.is_absolute():
        pesos = BASE / pesos
    if not pesos.is_file():
        parser.error(f"Modelo não encontrado: {pesos}. Não será feito download automático.")

    from ultralytics import YOLO

    print(f"Processando {caminho.name} ...")
    modelo = YOLO(str(pesos))
    deteccoes = detectar_video(caminho, modelo)
    eventos = agrupar_deteccoes(deteccoes, tolerancia=2)
    print(f"Detecções por segundo: {len(deteccoes)} | Eventos: {len(eventos)}")
    quantidade = salvar_eventos(BANCO, caminho.name, eventos)
    print(f"Indexação concluída: {quantidade} eventos de {caminho.name} no SQLite.")
    print("Eventos de outras gravações foram preservados.")


if __name__ == "__main__":
    main()
