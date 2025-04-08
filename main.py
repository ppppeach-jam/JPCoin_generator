import os
import random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from tqdm import tqdm

# ====== 設定 ======
OUTPUT_DIR = "output"
NUM_IMAGES = 10
IMAGE_SIZE = (480, 640)
COIN_DIR = "assets"
BACKGROUND_DIR = "backgrounds"
COIN_COUNTS = {
    "1yen": (0, 10),
    "5yen": (0, 5),
    "10yen": (0, 10),
    "50yen": (0, 5),
    "100yen": (0, 10),
    "500yen": (0, 5),
}
COIN_VALUES = {
    "1yen": 1,
    "5yen": 5,
    "10yen": 10,
    "50yen": 50,
    "100yen": 100,
    "500yen": 500,
}

# ====== データ準備 ======
def load_coin_images(coin_dir):
    coin_images = {}
    for coin_type in os.listdir(coin_dir):
        paths = [os.path.join(coin_dir, coin_type, f) for f in os.listdir(os.path.join(coin_dir, coin_type)) if f.endswith(".png")]
        if paths:
            coin_images[coin_type] = paths
    return coin_images

def load_backgrounds(bg_dir):
    return [os.path.join(bg_dir, f) for f in os.listdir(bg_dir) if f.endswith(".jpg") or f.endswith(".png")]

coin_images = load_coin_images(COIN_DIR)
background_images = load_backgrounds(BACKGROUND_DIR)

# ====== 画像生成 ======
def add_shadow(image, offset=(5,5), background_color=0):
    shadow = Image.new("RGBA", image.size, (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.bitmap(offset, image, fill=(0,0,0,80))
    blurred_shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(blurred_shadow, image)

def paste_coin(bg_img, coin_img, position):
    bg_img.paste(coin_img, position, coin_img)

def generate_image(idx):
    bg_path = random.choice(background_images)
    bg = Image.open(bg_path).convert("RGBA").resize(IMAGE_SIZE)

    label_counts = {}
    total_value = 0

    for coin_type, (min_count, max_count) in COIN_COUNTS.items():
        count = random.randint(min_count, max_count)
        label_counts[coin_type] = count
        total_value += count * COIN_VALUES[coin_type]

        for _ in range(count):
            coin_path = random.choice(coin_images[coin_type])
            coin = Image.open(coin_path).convert("RGBA")
            angle = random.randint(0, 360)
            coin = coin.rotate(angle, expand=True)
            # scale = random.uniform(0.4, 0.7)
            scale = 0.5
            coin = coin.resize((int(coin.width * scale), int(coin.height * scale)))
            coin = add_shadow(coin)
            x = random.randint(0, IMAGE_SIZE[0] - coin.width)
            y = random.randint(0, IMAGE_SIZE[1] - coin.height)
            paste_coin(bg, coin, (x, y))

    image_filename = os.path.join(OUTPUT_DIR, "images", f"img_{idx:05d}.png")
    label_filename = os.path.join(OUTPUT_DIR, "labels", f"img_{idx:05d}.txt")

    bg.convert("RGB").save(image_filename)

    with open(label_filename, 'w') as f:
        for coin_type in COIN_COUNTS:
            f.write(f"{coin_type}: {label_counts[coin_type]}\n")
        f.write(f"total: {total_value}\n")

# ====== 実行 ======
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)

for i in tqdm(range(NUM_IMAGES)):
    generate_image(i)

print("✅ 生成完了")
