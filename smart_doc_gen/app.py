
from flask import Flask, render_template, request, send_file, url_for
import os
from services import ocr_service, excel_service
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# フォルダがなければ作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

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
    if 'template_file' in request.files:
        temp_file = request.files['template_file']
        if temp_file.filename != '':
            temp_filename = secure_filename(temp_file.filename)
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            temp_file.save(template_path)
    
    # テンプレートがない場合はデフォルトを使用
    if template_path is None:
        template_path = "assets/templates/default.xlsx"  # デフォルトパス
    
    # 画像を保存
    filename = secure_filename(image_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(filepath)
    
    # 3. OCR解析 (YOLO)
    yolo_results = ocr_service.analyze_image(filepath)
    
    # 4. 単元情報の取得
    units = request.form.getlist('units')
    
    # 5. Excel生成
    try:
        output_path = excel_service.create_from_yolo(yolo_results, units, template_path)
    except Exception as e:
        return f"Excel作成中にエラーが発生しました: {str(e)}", 500
    
    # 6. 結果画面を表示
    return render_template(
        'result.html', 
        download_link=output_path,
        filename=os.path.basename(output_path),
        result_count=len(yolo_results)
    )

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )


from flask import Flask, render_template, request
import os

app = Flask(__name__)

# トップページ表示
@app.route('/')
def index():
    return render_template('index.html')

# ファイルアップロード（仮）
@app.route('/upload', methods=['POST'])
def upload():
    return "アップロード機能はまだ実装されていませんが、通信は成功しました！"

if __name__ == '__main__':
    app.run(debug=True)