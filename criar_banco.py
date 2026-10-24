"""Importa eventos.csv para um vídeo sem apagar eventos de outros vídeos.

Uso: python criar_banco.py teste.mp4
"""
import argparse
import csv
from pathlib import Path

from services.config import BANCO, BASE, VIDEOS
from services.indexacao import salvar_eventos


def main():
    parser = argparse.ArgumentParser(description="Importar eventos CSV no SQLite")
    parser.add_argument("video", help="Nome do vídeo MP4 na pasta videos/")
    parser.add_argument("--csv", default="eventos.csv", help="CSV com classe,inicio,fim")
    args = parser.parse_args()

    if Path(args.video).name != args.video or not args.video.lower().endswith(".mp4"):
        parser.error("Informe somente o nome do MP4.")
    if not (VIDEOS / args.video).is_file():
        parser.error("Arquivo MP4 não encontrado em videos/.")

    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = BASE / csv_path
    with csv_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if not {"classe", "inicio", "fim"}.issubset(leitor.fieldnames or []):
            parser.error("O CSV deve conter classe,inicio,fim.")
        eventos = [(l["classe"], l["inicio"], l["fim"]) for l in leitor]

    quantidade = salvar_eventos(BANCO, args.video, eventos)
    print(f"{quantidade} eventos importados para {args.video}; demais vídeos preservados.")


if __name__ == "__main__":
    main()
