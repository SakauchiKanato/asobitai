# Smart Doc Generator 📄✨

**採点済みテストの集計を、AIで全自動化。**
スマホで撮影した答案用紙の画像をアップロードするだけで、AIが「◯・❌・△」を認識し、成績集計済みのExcelレポート（グラフ付き）を自動生成するDXツールです。

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Web_App-green)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-purple)

## 🚀 主な機能 (Features)

* **📷 高精度AI認識 (Gemini 2.5 Flash)**
    * 最新のGoogle Geminiモデルを使用し、手書きの「◯」「❌」「△」「レ点」を高精度に検出・分類します。
    * 画像の向きが回転していても自動補正します。
* **📊 Excelレポート自動生成**
    * 集計結果をExcelファイル(.xlsx)に出力。
    * **単元ごとの正答率グラフ** を自動で作成し、苦手分野を一目で可視化します。
* **🎨 テンプレート対応**
    * 独自のExcelフォーマット（テンプレート）をアップロードして使用可能。
    * テンプレートがない場合は、自動で新規作成する機能も搭載。
* **💻 モダンなUI**
    * 直感的なドラッグ＆ドロップ対応のアップロード画面。
    * レスポンシブ対応の美しいデザイン。

## 🛠 使用技術 (Tech Stack)

* **Backend:** Python 3.12, Flask
* **AI/OCR:** Google Generative AI (Gemini 2.5 Flash)
* **Excel操作:** OpenPyXL
* **Frontend:** HTML5, CSS3 (Custom Design)
* **Infrastructure:** Git

## 📦 インストール手順 (Installation)

### 1. リポジトリのクローン
```bash
git clone [https://github.com/SakauchiKanato/asobitai.git](https://github.com/SakauchiKanato/asobitai.git)
cd asobitai/smart_doc_gen
2. 仮想環境の作成と有効化 (推奨)
Bash

# Mac / Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
3. 依存ライブラリのインストール
Bash

pip install flask google-generativeai openpyxl pillow werkzeug
4. APIキーの設定
services/ocr_service.py を開き、Google GeminiのAPIキーを設定してください。

Python

# services/ocr_service.py
MY_API_KEY = "あなたのAPIキーをここに貼り付け"
▶️ 実行方法 (Usage)
アプリケーションを起動します。

Bash

python app.py
ブラウザで http://127.0.0.1:5000 にアクセスします。

「採点後の画像」 をアップロードします。

必要に応じて 「Excelテンプレート」 や 「氏名」 を入力します。

「レポートを生成する」 ボタンをクリック！

解析完了後、作成されたExcelファイルをダウンロードできます。

📂 ディレクトリ構成
Plaintext

smart_doc_gen/
├── app.py                  # アプリケーションのエントリーポイント
├── services/
│   ├── ocr_service.py      # AI解析ロジック (Gemini 2.5)
│   └── excel_service.py    # Excel生成・グラフ作成ロジック
├── templates/
│   ├── index.html          # アップロード画面
│   └── result.html         # 結果・ダウンロード画面
├── static/
│   ├── css/style.css       # デザインスタイルシート
│   └── js/script.js        # フロントエンドの挙動
├── uploads/                # アップロードされた一時ファイル
├── output/                 # 生成されたExcelファイル
└── assets/
    └── templates/          # デフォルトテンプレート置き場
👨‍💻 Author
Kanato Sakauchi (Backend & Git Management)

Team Asobitai

© 2025 Smart Doc Generator Project
