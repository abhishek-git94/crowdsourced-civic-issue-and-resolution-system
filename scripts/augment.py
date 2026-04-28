import os
import cv2
import random
import shutil
import albumentations as A


BASE_PATH = "C:\\Users\\mathe\\OneDrive\\Documents\\civic_dataset\\train"
IMAGE_DIR = os.path.join(BASE_PATH, "images")
LABEL_DIR = os.path.join(BASE_PATH, "labels")

# Augmentation pipeline (low-light + rain + blur)

transform = A.Compose([
    A.RandomBrightnessContrast(
        brightness_limit=(-0.7, -0.3),   # 🔥 strong dark
        contrast_limit=(-0.4, 0.4),
        p=0.9
    ),
    A.GaussNoise(p=0.6),
    A.MotionBlur(blur_limit=7, p=0.5),

    A.RandomShadow(p=0.6),   # 🌑 night shadows
    A.RandomFog(p=0.4),      # 🌫️ fog
    A.RandomRain(p=0.5),     # 🌧️ rain
])
images = [img for img in os.listdir(IMAGE_DIR) if img.endswith(('.jpg', '.png'))]

# Select 50% randomly
selected_images = random.sample(images, int(0.5 * len(images)))

print(f"Total images: {len(images)}")
print(f"Augmenting: {len(selected_images)} images")

for img_name in selected_images:
    img_path = os.path.join(IMAGE_DIR, img_name)
    label_name = os.path.splitext(img_name)[0] + ".txt"
    label_path = os.path.join(LABEL_DIR, label_name)

    # Read image
    image = cv2.imread(img_path)

    if image is None:
        continue

    # Apply augmentation
    augmented = transform(image=image)
    aug_image = augmented["image"]

    # New names
    new_img_name = "aug_" + img_name
    new_label_name = "aug_" + label_name

    # Save augmented image
    cv2.imwrite(os.path.join(IMAGE_DIR, new_img_name), aug_image)

    # Copy label
    if os.path.exists(label_path):
        shutil.copy(label_path, os.path.join(LABEL_DIR, new_label_name))

print("✅ 50% Augmentation Completed Successfully!")