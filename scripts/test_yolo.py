from ultralytics import YOLO

model = YOLO("yolov8_civic.pt")

result = model("test.jpg")   
result[0].show()