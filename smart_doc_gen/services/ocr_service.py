import os
import json
import re
import google.generativeai as genai
from PIL import Image, ImageOps
import typing_extensions as typing

# ★ここにGeminiのAPIキーを設定してください
# 環境変数から読み込むか、直書きしてください
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

genai.configure(api_key=API_KEY)

# 高速・安価で、かつ画像認識に強い最新モデル
MODEL_NAME = "models/gemini-1.5-flash"

def clean_json_text(text):
    """Markdown記法を取り除き、純粋なJSON文字列にする"""
    text = text.replace("```json", "").replace("```", "")
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def analyze_image(image_path):
    """
    Gemini APIを使用して画像から採点マークを抽出し、
    app.py（Excel生成機能）で使える形式のリストを返す関数
    """
    file_name = os.path.basename(image_path)
    print(f"--- [AI解析開始] 画像: {file_name} ---")

    if not os.path.exists(image_path):
        print("画像ファイルが見つかりません。")
        return []

    try:
        # 1. 画像読み込みと前処理
        img = Image.open(image_path)
        
        # スマホ写真の向きを自動補正（これがないと座標が狂います）
        img = ImageOps.exif_transpose(img)

        # RGB変換
        if img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size
        print(f"   画像サイズ: {width}x{height}")

    except Exception as e:
        print(f"画像読み込みエラー: {e}")
        return []

    # 2. プロンプト（AIへの命令）
    prompt = """
    Analyze this image and detect ALL handwritten red/colored ink grading marks.
    Classify each element into one of these types:

    - "TARGET": For grading marks.
      Target types: 
      - Circle (丸)
      - Cross (バツ)
      - Triangle (三角)
      - Checkmark (チェック/レ点)

    - "IGNORE": For numbers (scores like 10, 50), text comments, or underlines.

    Output a JSON list with these fields:
    - "type": "TARGET" or "IGNORE"
    - "mark_name": "Circle", "Cross", "Triangle", "Checkmark", or "Score/Text"
    - "box_2d": [ymin, xmin, ymax, xmax] (scale 0-1000)
    """

    # 3. AI生成実行
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    results = []
    
    try:
        response = model.generate_content([prompt, img])
        
        json_text = clean_json_text(response.text)
        marks_data = json.loads(json_text)
        
        print(f"   -> AI検出生データ数: {len(marks_data)} 個")

        # 4. データをアプリ用に変換 & フィルタリング
        # ★ここを変更: Checkmark を '❌' (不正解) にマッピング
        label_map = {
            "Circle": "◯",
            "Cross": "❌",
            "Triangle": "△",
            "Checkmark": "❌"  # チェックマークもバツ扱いにする
        }

        ignore_keywords = ["score", "number", "text", "digit", "点", "文字"]

        for item in marks_data:
            # (A) IGNORE判定をスキップ
            if item.get("type") == "IGNORE":
                continue

            label_eng = item.get('mark_name', '')
            
            # (B) キーワードフィルタ
            if any(kw in label_eng.lower() for kw in ignore_keywords):
                continue

            # 記号の変換（辞書にないものは '?' にする）
            symbol = label_map.get(label_eng, "?")
            
            # 座標変換
            box = item.get('box_2d', [])
            if len(box) != 4: continue
            
            ymin, xmin, ymax, xmax = box

            # 0-1000スケール -> ピクセル座標へ変換
            y_pixel = (ymin / 1000) * height
            x_pixel = (xmin / 1000) * width

            results.append({
                "class": symbol,      # ◯, ❌ (チェック含む), △
                "y": y_pixel,
                "x": x_pixel,
                "confidence": 1.0     
            })

        print(f"   -> フィルタ後の有効データ数: {len(results)} 個")

    except Exception as e:
        print(f"AI解析中にエラーが発生しました: {e}")
        return []

    return results