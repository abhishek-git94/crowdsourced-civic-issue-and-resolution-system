from ultralytics import YOLO

model = YOLO("yolov8_civic.pt")

result = model("test.jpg")   # put any sample image
result[0].show()