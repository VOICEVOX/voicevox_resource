"""
必要なライブラリのインストール:
pip install opencv-python Pillow numpy matplotlib

実行例:
python find_crop.py --big large.png --small template.png --output face.png

期待される標準出力:
```
big 読み込みサイズ: 4093×3473
small 読み込みサイズ: 2271×2271
グレースケール後 big: shape=(4093,3473), dtype=uint8, min=0, max=255
グレースケール後 small: shape=(2271,2271), dtype=uint8, min=0, max=255
相関マップ: shape=(1823,1203), min=0.12, max=0.67 at (x=925,y=825)
Crop → x=925, y=825, w=2271, h=2271
```

生成ファイル:
```
- face.png        （切り抜き結果PNG、透過保持）
```
"""

import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def parse_args():
    # コマンドライン引数のパーサー設定（日本語ヘルプ）
    parser = argparse.ArgumentParser(
        description="画像からテンプレート領域を検出して切り抜くスクリプト"
    )
    parser.add_argument("--big", required=True, type=Path, help="大きい画像のパス")
    parser.add_argument(
        "--small", required=True, type=Path, help="小さいテンプレート画像のパス"
    )
    parser.add_argument("--output", required=True, type=Path, help="出力PNGの保存パス")
    return parser.parse_args()


def preprocess(path: Path, name: str):
    # RGBA画像を読み込み
    img_rgba = Image.open(path).convert("RGBA")
    w, h = img_rgba.size
    print(f"{name} 読み込みサイズ: {w}×{h}")

    # 白背景で合成しグレースケール化
    white_bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(white_bg, img_rgba)
    gray = comp.convert("L")
    arr = np.array(gray)
    print(
        f"グレースケール後 {name}: shape={arr.shape}, dtype={arr.dtype}, min={arr.min()}, max={arr.max()}"
    )
    return arr, img_rgba


def main():
    args = parse_args()

    # 画像の前処理
    big_gray, big_rgba = preprocess(args.big, "big")
    small_gray, _ = preprocess(args.small, "small")

    # テンプレートマッチング実行
    corr = cv2.matchTemplate(big_gray, small_gray, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corr)
    x, y = max_loc
    h_corr, w_corr = corr.shape

    print(
        f"相関マップ: shape=({w_corr},{h_corr}), min={min_val:.2f}, max={max_val:.2f} at (x={x},y={y})"
    )

    # 検出領域の切り抜きと保存
    sw, sh = small_gray.shape[::-1]
    print(f"Crop x={x}, y={y}, w={sw}, h={sh}")
    crop = big_rgba.crop((x, y, x + sw, y + sh))
    crop.save(args.output)


if __name__ == "__main__":
    main()
