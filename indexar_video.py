import cv2
import csv
from ultralytics import YOLO

VIDEO = "videos/teste.mp4"

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(VIDEO)

fps = cap.get(cv2.CAP_PROP_FPS)

frame_atual = 0

nomes_pt = {
    0: "pessoa",
    2: "carro",
    3: "motocicleta"
}

# Guarda as classes encontradas em cada segundo
deteccoes_por_segundo = {}

print("Analisando vídeo...")

while True:
    sucesso, frame = cap.read()

    if not sucesso:
        break

    tempo_segundos = frame_atual / fps
    segundo = int(tempo_segundos)

    resultado = model.predict(
        frame,
        classes=[0, 2, 3],
        conf=0.40,
        verbose=False
    )[0]

    if segundo not in deteccoes_por_segundo:
        deteccoes_por_segundo[segundo] = set()

    for caixa in resultado.boxes:

        classe = int(caixa.cls[0])

        if classe in nomes_pt:
            deteccoes_por_segundo[segundo].add(classe)

    frame_atual += 1

cap.release()

deteccoes = []

for segundo in sorted(deteccoes_por_segundo.keys()):

    horas = segundo // 3600
    minutos = (segundo % 3600) // 60
    segundos = segundo % 60

    timestamp = f"{horas:02}:{minutos:02}:{segundos:02}"

    for classe in sorted(deteccoes_por_segundo[segundo]):

        nome = nomes_pt[classe]

        deteccoes.append([timestamp, nome])

        print(f"{timestamp} | {nome}")

with open("deteccoes.csv", "w", newline="", encoding="utf-8") as arquivo:

    escritor = csv.writer(arquivo)

    escritor.writerow(["timestamp", "classe"])
    escritor.writerows(deteccoes)

print()
print("Processamento concluído.")
print("Arquivo deteccoes.csv criado.")