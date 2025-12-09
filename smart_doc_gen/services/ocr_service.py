import cv2
import numpy as np
import matplotlib.pyplot as plt

def process_three_marks(image_path):
    # 1. 画像読み込み
    img = cv2.imread(image_path)
    if img is None:
        return None, "画像が読み込めません"
    
    output_img = img.copy()

    # BGR -> HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. 赤色抽出
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    # 3. 膨張処理（線をくっつけて塊にする）
    kernel = np.ones((5, 5), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel, iterations=2)

    # 4. 輪郭検出
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # ゴミ除去
        if area < 200: 
            continue

        # --- 特徴量の計算 ---
        
        # A. 縦横比 (Aspect Ratio)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        
        # B. 円形度 (Circularity)
        # 1.0に近いほど綺麗な円、複雑な形や細長い形は0に近づく
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0: continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # --- 判定ロジック ---
        
        label = ""
        color = (0, 0, 0)

        # 1. まず「チェック」を弾く
        # 横に長すぎる(>1.5) か 縦に長すぎる(<0.7) 場合
        if aspect_ratio > 1.5 or aspect_ratio < 0.7:
            label = "Check"
            color = (0, 165, 255) # オレンジ
        
        # 2. 残った「正方形っぽいもの」の中で、マルとバツを分ける
        else:
            # 円形度が高い -> マル
            # バツは中心から四方に腕が伸びているため、面積に対して周囲長が長く、円形度が低くなる
            if circularity > 0.35:  # 手書きの丸は歪んでいるので閾値は甘めに
                label = "Circle"
                color = (255, 0, 0) # 青
            else:
                label = "Cross"
                color = (0, 0, 255) # 赤

        # 描画
        cv2.rectangle(output_img, (x, y), (x + w, y + h), color, 3)
        cv2.putText(output_img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return output_img, "Success"

# 実行
processed_image, msg = process_three_marks("/Users/mihiraryouta/ハッカソン/学内ハッカソン/asobitai/smart_doc_gen/services/sample2.png")

if processed_image is not None:
    plt.figure(figsize=(12, 12))
    plt.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()