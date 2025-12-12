import os
import json
import google.generativeai as genai
from PIL import Image, ImageOps


# ★重要: APIキー

MY_API_KEY = "AIzaSyBqm429BKLB0Eei2eAbHHBMC_NeKByjtHs" 

genai.configure(api_key=MY_API_KEY)

# 「2.5-flash」
MODEL_NAME = "gemini-2.5-flash"

def clean_json_text(text):
    text = text.replace("```json", "").replace("```", "")
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def analyze_image(image_path):
    # デバッグ表示
    print(f"★ 使用モデル: {MODEL_NAME}")
    file_name = os.path.basename(image_path)
    print(f"--- [AI解析開始] 画像: {file_name} ---")

    if not os.path.exists(image_path):
        print("画像ファイルが見つかりません。")
        return []

    try:
        # 1. 画像読み込み
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img) 
        if img.mode != 'RGB': img = img.convert('RGB')
        width, height = img.size
        print(f"   画像サイズ: {width}x{height}")
    except Exception as e:
        print(f"画像読み込みエラー: {e}")
        return []

    # 2. プロンプト
    prompt = """
    Analyze this image and detect ALL handwritten red/colored ink grading marks.
    Classify each element into one of these types:
    - "TARGET": For grading marks (Circle, Cross, Triangle, Checkmark).
    - "IGNORE": For numbers, text comments, or underlines.
    
    Output a JSON list with these fields:
    - "type": "TARGET" or "IGNORE"
    - "mark_name": "Circle", "Cross", "Triangle", "Checkmark"
    - "box_2d": [ymin, xmin, ymax, xmax] (scale 0-1000)
    """

    # 3. AI実行
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )

        response = model.generate_content([prompt, img])
        
        json_text = clean_json_text(response.text)
        marks_data = json.loads(json_text)
        
        print(f"   -> AI検出生データ数: {len(marks_data)} 個")

        # 4. 変換ロジック
        label_map = {"Circle": "◯", "Cross": "❌", "Triangle": "△", "Checkmark": "❌"}
        ignore_keywords = ["score", "number", "text", "digit", "点", "文字"]
        results = []

        for item in marks_data:
            if item.get("type") == "IGNORE": continue
            label_eng = item.get('mark_name', '')
            if any(kw in label_eng.lower() for kw in ignore_keywords): continue

            symbol = label_map.get(label_eng, "?")
            box = item.get('box_2d', [])
            if len(box) != 4: continue
            
            ymin, xmin, ymax, xmax = box
            y_pixel = (ymin / 1000) * height
            x_pixel = (xmin / 1000) * width

            results.append({
                "class": symbol,
                "y": y_pixel,
                "x": x_pixel,
                "confidence": 1.0     
            })

        print(f"   -> フィルタ後の有効データ数: {len(results)} 個")
        return results

    except Exception as e:
        print(f"❌ AI解析エラー: {e}")
        return []
