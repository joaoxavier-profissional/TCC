"""Diagnóstico de motocicletas no YOLO, sem alterar cftv.db.

Exemplo:
 python diagnostico_motos.py videoplayback.mp4 --inicio 0 --duracao 120
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

from services.config import BASE, VIDEOS

CLASSES_INTERESSE = {0: "pessoa", 1: "bicicleta", 2: "carro", 3: "motocicleta"}
LIMITES = (0.10, 0.20, 0.30, 0.40)


def resumir_limiares(registros, limites=LIMITES):
    """Conta detecções de caixas (não objetos únicos) por classe e limite."""
    resultado = {limite: Counter() for limite in limites}
    for registro in registros:
        for limite in limites:
            if registro["confianca"] >= limite:
                resultado[limite][registro["classe"]] += 1
    return resultado


def analisar_video(caminho, pesos, inicio, duracao, passo, saida, max_imagens):
    import cv2
    from ultralytics import YOLO

    modelo = YOLO(str(pesos))
    captura = cv2.VideoCapture(str(caminho))
    if not captura.isOpened():
        captura.release()
        raise RuntimeError(f"Não foi possível abrir {caminho.name}")
    registros = []
    quadros_lidos = 0
    imagens = 0
    saida.mkdir(parents=True, exist_ok=True)
    try:
        fps = captura.get(cv2.CAP_PROP_FPS)
        total_frames = captura.get(cv2.CAP_PROP_FRAME_COUNT)
        if fps <= 0:
            raise RuntimeError("FPS inválido.")
        duracao_total = total_frames / fps if total_frames > 0 else None
        tempo = inicio
        fim = inicio + duracao
        if duracao_total is not None:
            fim = min(fim, duracao_total)
        while tempo < fim:
            # Selecionar frames evita processar cada quadro e reduz tempo de execução.
            captura.set(cv2.CAP_PROP_POS_FRAMES, int(tempo * fps))
            sucesso, frame = captura.read()
            if not sucesso:
                print(f"Frame não lido em {tempo:.1f}s; ignorando.")
                tempo += passo
                continue
            quadros_lidos += 1
            # NÃO filtrar classes aqui: queremos observar possíveis confusões.
            resultado = modelo.predict(frame, conf=0.10, verbose=False)[0]
            relevantes = []
            for caixa in resultado.boxes:
                classe_id = int(caixa.cls[0])
                confianca = float(caixa.conf[0])
                nome = str(modelo.names.get(classe_id, classe_id))
                registro = {
                    "tempo_s": round(tempo, 2),
                    "classe_id": classe_id,
                    "classe": CLASSES_INTERESSE.get(classe_id, nome),
                    "confianca": round(confianca, 5),
                }
                registros.append(registro)
                if classe_id in (1, 3):
                    relevantes.append((caixa, registro))
            if relevantes and imagens < max_imagens:
                marcado = frame.copy()
                for caixa, registro in relevantes:
                    x1, y1, x2, y2 = [int(v) for v in caixa.xyxy[0].tolist()]
                    cv2.rectangle(marcado, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(marcado,
                                f'{registro["classe"]} {registro["confianca"]:.2f}',
                                (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 255, 255), 2)
                arquivo = saida / f"frame_{int(tempo * 1000):09}.jpg"
                cv2.imwrite(str(arquivo), marcado)
                imagens += 1
            tempo += passo
    finally:
        captura.release()

    csv_saida = saida / "deteccoes_diagnostico.csv"
    with csv_saida.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["tempo_s", "classe_id", "classe", "confianca"]
        )
        escritor.writeheader()
        escritor.writerows(registros)

    resumo = resumir_limiares(registros)
    print(f"Frames analisados: {quadros_lidos} | Caixas detectadas: {len(registros)}")
    print("Contagem de caixas por classe (não equivale a objetos únicos):")
    for limite, contagens in resumo.items():
        print(f"  confiança >= {limite:.2f}: "
              + ", ".join(f"{classe}={contagens[classe]}"
                          for classe in ("pessoa", "bicicleta", "carro", "motocicleta")))
    print(f"CSV gerado: {csv_saida}")
    print(f"Imagens com detecções de bicicleta/moto: {imagens} em {saida}")
    print("Banco SQLite não foi alterado.")


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico de motos em vídeo")
    parser.add_argument("video", help="Nome do MP4 dentro de videos/")
    parser.add_argument("--inicio", type=float, default=0, help="Segundo inicial")
    parser.add_argument("--duracao", type=float, default=120, help="Segundos a examinar")
    parser.add_argument("--passo", type=float, default=1, help="Intervalo entre frames amostrados")
    parser.add_argument("--max-imagens", type=int, default=8)
    parser.add_argument("--modelo", default="yolo11n.pt")
    args = parser.parse_args()
    if args.inicio < 0 or args.duracao <= 0 or args.passo <= 0 or args.max_imagens < 0:
        parser.error("Início >= 0; duração e passo > 0; max-imagens >= 0.")
    if Path(args.video).name != args.video or not args.video.lower().endswith(".mp4"):
        parser.error("Informe somente o nome de um arquivo .mp4 da pasta videos.")
    caminho = (VIDEOS / args.video).resolve()
    if caminho.parent != VIDEOS.resolve() or not caminho.is_file():
        parser.error("Vídeo não encontrado na pasta videos/.")
    pesos = Path(args.modelo)
    if not pesos.is_absolute():
        pesos = BASE / pesos
    if not pesos.is_file():
        parser.error("Pesos YOLO não encontrados localmente; download não será iniciado.")
    pasta = BASE / "diagnosticos" / caminho.stem
    print(f"Analisando {caminho.name} a partir de {args.inicio:g}s...")
    analisar_video(caminho, pesos, args.inicio, args.duracao,
                   args.passo, pasta, args.max_imagens)


if __name__ == "__main__":
    main()
