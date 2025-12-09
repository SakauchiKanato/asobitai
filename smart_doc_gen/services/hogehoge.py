import cv2
import numpy as np
import matplotlib.pyplot as plt

def process_merged_marks(image_path):
    # 1. 画像読み込み
    img = cv2.imread(image_path)
    if img is None:
        return None, "画像が読み込めません"
    
    # 結果描画用
    output_img = img.copy()

    # BGR -> HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. 赤色抽出（ここは同じ）
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    # 3. 【重要】膨張処理（Dilation）を追加
    # 5x5ピクセルのカーネルを使って、白い部分（赤色領域）を太らせて隙間を埋める
    # iterations=3 で3回繰り返して、しっかり結合させる
    kernel = np.ones((5, 5), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel, iterations=3)

    # 4. 輪郭検出（膨張させたマスクを使う）
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # 小さすぎるゴミ（ノイズ）を除去（閾値を少し上げる）
        if area < 500: 
            continue

        # 形状特徴量の計算
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h
        
        # 凸包とソリディティ
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0

        # --- 判定ロジック（サイズと形状で分ける） ---
        
        label = ""
        color = (0, 0, 255) # デフォルト赤 (BGR)

        # 判定A: はなまる（大きな塊で、正方形に近い）
        # 面積が非常に大きく、縦横比が1に近い場合
        # ※面積の閾値(例:5000)は画像の解像度に合わせて調整が必要です
        if area > 5000 and 0.7 < aspect_ratio < 1.3:
            label = "Hanamaru"
            color = (255, 0, 0) # 青枠 (BGR)
        
        # 判定B: チェックマーク（中くらいのサイズで、少し縦長や横長）
        # ソリディティが低め（L字型などは凹んでいるため）
        elif area > 500 and solidity < 0.8:
            label = "Check"
            color = (0, 165, 255) # オレンジ枠 (BGR)
            
        else:
            # それ以外は一旦「Mark」とする
            label = "Mark"
            color = (0, 255, 0) # 緑枠 (BGR)

        # 描画（元の画像の上に描く）
        # 認識範囲を少し調整（膨張させた分、枠が大きくなりがちなので少し内側に戻すイメージで描画しても良いが、ここではそのまま）
        cv2.rectangle(output_img, (x, y), (x + w, y + h), color, 3)
        
        # ラベル背景
        cv2.rectangle(output_img, (x, y - 30), (x + len(label)*15, y), color, -1)
        cv2.putText(output_img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return output_img, "Success"

# 実行（ファイル名は適切なものに変更してください）
target_image = "/Users/mihiraryouta/ハッカソン/学内ハッカソン/asobitai/smart_doc_gen/services/sample.png" # ここを image_1.png や image_2.png に変えて試してみてください
processed_image, msg = process_merged_marks(target_image)

if processed_image is not None:
    plt.figure(figsize=(12, 12))
    # OpenCV(BGR) -> Matplotlib(RGB)
    plt.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()
else:
    print(msg)