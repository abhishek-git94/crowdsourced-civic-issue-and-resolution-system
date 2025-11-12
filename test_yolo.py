from ultralytics import YOLO
import requests
from PIL import Image

print("=" * 60)
print("🧪 TESTING YOLO")
print("=" * 60)

# Step 1: Load YOLO
print("\n📦 Loading YOLO model...")
model = YOLO('yolov8n.pt')
print("✅ YOLO loaded!")

# Step 2: Download test image
print("\n📥 Downloading test image...")
img_url = "https://ultralytics.com/images/bus.jpg"
response = requests.get(img_url)
with open('test_bus.jpg', 'wb') as f:
    f.write(response.content)
print("✅ Test image downloaded!")

# Step 3: Run detection
print("\n🔍 Running detection...")
results = model('test_bus.jpg')
print("✅ Detection complete!")

# Step 4: Show results
print("\n📊 DETECTION RESULTS:")
print("-" * 60)

for result in results:
    boxes = result.boxes
    print(f"Total objects detected: {len(boxes)}")
    print()
    
    for i, box in enumerate(boxes, 1):
        class_id = int(box.cls[0])
        class_name = result.names[class_id]
        confidence = float(box.conf[0])
        
        print(f"{i}. Object: {class_name}")
        print(f"   Confidence: {confidence:.2%}")
        print()

print("=" * 60)
print("🎉 YOLO is working perfectly!")
print("=" * 60)