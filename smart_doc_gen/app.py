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
    # 1. ファイルのアップロード確認
    if 'target_image' not in request.files:
        return "ファイルがありません", 400
    
    file = request.files['target_image']
    if file.filename == '':
        return "ファイルが選択されていません", 400
    
    # 2. ファイルを一時保存
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # 3. OCR解析 (YOLOを使用)
    yolo_results = ocr_service.analyze_image(filepath)
    
    # 4. 解析結果をY座標でソート (上から順に)
    sorted_results = sorted(yolo_results, key=lambda x: x['y_center'])
    
    # 5. 単元情報の取得
    # フォームから単元情報を取得（複数選択に対応）
    units = request.form.getlist('units')
    
    # 6. create_reportに渡すデータ形式に変換
    grading_data = []
    for i, result in enumerate(sorted_results):
        # 問題番号は1から始める
        problem_num = i + 1
        
        # 単元名の設定 (単元情報が存在すればそれを使用、インデックスがない場合はNone)
        unit = units[i] if i < len(units) else None
        
        grading_data.append({
            "num": problem_num,
            "unit": unit,
            "result": result['mark']  # ◯, ❌, △ などのマーク
        })
    
    # 7. Excel生成
    output_path = excel_service.create_report(grading_data)
    
    # 8. 結果画面を表示
    return render_template(
        'result.html', 
        download_link=output_path,
        filename=os.path.basename(output_path),
        result_count=len(grading_data)
    )

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)