from PIL import Image
import os

assets = ['icon.jpg', 'adaptive-icon.jpg', 'favicon.jpg', 'splash-icon.jpg']
assets_dir = r'c:\Users\mathe\Documents\GitHub\crowdsourced-civic-issue-and-resolution-system\mobile\assets'

for asset in assets:
    img_path = os.path.join(assets_dir, asset)
    if os.path.exists(img_path):
        img = Image.open(img_path)
        new_path = os.path.join(assets_dir, asset.replace('.jpg', '.png'))
        img.save(new_path, 'PNG')
        print(f"Converted {asset} to {new_path}")
    else:
        print(f"File not found: {img_path}")
