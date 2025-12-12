from flask import Flask, render_template, request, send_file, url_for
import os
import datetime # ★追加：日時を使うために必要
# servicesフォルダからそれぞれの担当ファイルを読み込む
from services import ocr_service, excel_service
from werkzeug.utils import secure_filename

app = Flask(__name__)
# セキュリティキー
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
# 保存先の設定
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# フォルダがなければ自動作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# -------------------------------------------------
# ルーティング
# -------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html', title='Smart Doc Gen')

@app.route('/upload', methods=['POST'])
def upload():
    # 1. 画像ファイルのチェック
    if 'target_image' not in request.files:
        return "画像ファイルがありません", 400
    image_file = request.files['target_image']
    if image_file.filename == '':
        return "画像ファイルが選択されていません", 400

    # 2. Excelテンプレートのチェック
    template_path = None
    
    # ★修正ポイント：日本語ファイル名対策
    # secure_filenameを使うと日本語が消えるので、日時を使ってリネームする
    if 'template_file' in request.files:
        temp_file = request.files['template_file']
        
        # ファイル名が空じゃない（＝選択されている）場合のみ処理
        if temp_file.filename != '':
            # 拡張子 (.xlsx) だけ安全に取り出す
            ext = os.path.splitext(temp_file.filename)[1]
            if not ext: ext = ".xlsx"
            
            # 現在時刻を使って「temp_20251212_123456.xlsx」のような名前にする
            timestamp_name = f"temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            # 保存
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamp_name)
            temp_file.save(template_path)
            print(f"★テンプレートを受信・保存しました: {template_path}")

    # テンプレートがない場合はデフォルトを使用
    if template_path is None:
        print("★テンプレートがアップロードされなかったため、デフォルトを使用します")
        template_path = "assets/templates/default.xlsx"
    
    # 画像を保存
    # 画像も同様にリネームしておくと安全ですが、一旦そのままsecure_filenameで
    filename = secure_filename(image_file.filename)
    if not filename: # 万が一日本語だけで空になった場合の対策
        filename = f"image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(filepath)
    
    try:
        # 3. OCR解析
        yolo_results = ocr_service.analyze_image(filepath)
        
        # 4. フォーム情報の取得
        units = request.form.getlist('units')
        student_name = request.form.get('student_name')
        
        # 5. Excel生成
        output_path = excel_service.create_from_yolo(yolo_results, units, template_path, student_name)

        # エラーチェック
        if output_path is None:
            # 念のため、excel_serviceがNoneを返した場合のフェイルセーフ
            return "エラー: Excel生成に失敗しました（パスがNoneです）。", 500

    except Exception as e:
        return f"処理中にエラーが発生しました: {str(e)}", 500
    
    # 6. 結果画面を表示
    result_filename = os.path.basename(output_path)
    
    return render_template(
        'result.html', 
        filename=result_filename,
        # ダウンロード用のURLを渡す
        download_link=url_for('download', filename=result_filename),
        result_count=len(yolo_results)
    )

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )

# -------------------------------------------------
# 起動スイッチ
# -------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)