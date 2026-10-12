from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.predict(
    source="videos/teste.mp4",
    save=True,
    classes=[0, 2, 3],
    conf=0.40
)

print("Processamento concluído.")