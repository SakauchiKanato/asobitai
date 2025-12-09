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