from flask import Flask, render_template, request, send_file, url_for
import os
import datetime 
from services import excel_service, API_service 
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# ルーティング

@app.route('/')
def index():
    return render_template('index.html', title='Smart Doc Gen')

@app.route('/upload', methods=['POST'])
def upload():
    # 画像ファイルのチェック
    if 'target_image' not in request.files:
        return "画像ファイルがありません", 400
    image_file = request.files['target_image']
    if image_file.filename == '':
        return "画像ファイルが選択されていません", 400

    # Excelテンプレートのチェック
    template_path = None
    if 'template_file' in request.files:
        temp_file = request.files['template_file']
        if temp_file.filename != '':
            ext = os.path.splitext(temp_file.filename)[1]
            if not ext: ext = ".xlsx"
            timestamp_name = f"temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamp_name)
            temp_file.save(template_path)
    
    # テンプレートがない場合
    if template_path is None:
        template_path = "assets/templates/default.xlsx"
    
    # 画像を保存
    ext_img = os.path.splitext(image_file.filename)[1]
    if not ext_img: ext_img = ".jpg"
    img_filename = f"image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext_img}"
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
    image_file.save(filepath)
    
    try:
        # AI解析 
        AI_results = API_service.analyze_image(filepath)
        
        # フォーム情報の取得
        units = request.form.getlist('units')
        # 氏名を取得する
        student_name = request.form.get('student_name')
        
        # Excel生成
        # student_name を渡す
        output_path = excel_service.create_from_yolo(AI_results, units, template_path, student_name)

    except Exception as e:
        return f"処理中にエラーが発生しました: {str(e)}", 500
    
    # 6. 結果画面を表示
    result_filename = os.path.basename(output_path)
    
    return render_template(
        'result.html', 
        filename=result_filename,
        download_link=url_for('download', filename=result_filename),
        result_count=len(AI_results)
    )

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)