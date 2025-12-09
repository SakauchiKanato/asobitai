import cv2
import numpy as np
import matplotlib.pyplot as plt

def process_sample_image(image_path):
    # 1. 画像の読み込み
    img = cv2.imread(image_path)
    if img is None:
        return None, "画像の読み込みに失敗しました。"
    
    # BGRからHSVへ変換（色の抽出をしやすくするため）
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. 赤色の抽出（範囲定義）
    # 赤色は色相(Hue)が0付近と180付近に分かれているため2回マスクを作成
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # ノイズ除去（小さな点を消す）
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 3. 輪郭の検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_img = img.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50: # 小さすぎるノイズは無視
            continue

        # 4. 形状の判定（円形度を利用）
        # 円形度 = 4 * π * 面積 / (周囲長)^2
        # 正円＝1.0, 複雑な形や線＝0に近い値
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
            
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # 輪郭を囲む矩形を取得
        x, y, w, h = cv2.boundingRect(cnt)

        # 判定ロジック（手書きなのでしきい値は緩めに0.3〜0.4程度）
        if circularity > 0.4: 
            # 「マル」と判定 -> 青枠
            color = (255, 0, 0) # Blue (BGR)
            label = "Circle"
        else:
            # 「チェック/バツ/その他」と判定 -> 赤枠
            color = (0, 0, 255) # Red (BGR)
            label = "Check/Other"

        # 描画
        cv2.rectangle(output_img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(output_img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return output_img, "Success"

# 実行
processed_image, msg = process_sample_image("/Users/mihiraryouta/ハッカソン/学内ハッカソン/asobitai/smart_doc_gen/services/sample.png")

# 結果の表示
if processed_image is not None:
    # OpenCVはBGR、MatplotlibはRGBなので変換して表示
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()