import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import BarChart, Reference
import os
from datetime import datetime
from collections import defaultdict

# 出力先のディレクトリ
OUTPUT_DIR = "output"

def create_report(grading_data_list):
    """
    採点データを受け取り、単元別分析グラフ付きのExcelを作成する
    """
    
    # 1. Excel新規作成
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "採点結果"

    # --- 罫線の定義 ---
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # 2. ヘッダー作成
    headers = ["問", "単元", "採点結果", "判定"]
    ws.append(headers)

    # ヘッダーデザイン
    header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border

    # 3. データ書き込み & 単元別集計
    correct_count = 0
    
    # 単元ごとのスコアを集計するための辞書
    # 形式: {"単元名": [正解数, 全問題数]}
    unit_stats = defaultdict(lambda: [0, 0])

    for item in grading_data_list:
        q_num = item.get("num", "-")
        unit = item.get("unit", "未設定")
        mark = item.get("result", "?")

        # 判定
        status = "不正解"
        if mark == "◯":
            status = "正解"
            correct_count += 1
            unit_stats[unit][0] += 1 # 単元の正解数を+1
        elif mark == "△":
            status = "部分点"
            unit_stats[unit][0] += 0.5 # 部分点は0.5として計算
        
        unit_stats[unit][1] += 1 # 単元の問題数を+1

        # 行に追加
        row_data = [f"問{q_num}", unit, mark, status]
        ws.append(row_data)

        # デザイン適用
        current_row = ws.max_row
        # 罫線を引く
        for col in range(1, 5):
            ws.cell(row=current_row, column=col).border = thin_border
        
        # 色付け
        result_cell = ws.cell(row=current_row, column=3)
        result_cell.alignment = Alignment(horizontal="center")
        if mark == "◯":
            result_cell.font = Font(color="FF0000", bold=True)
        elif mark == "❌":
            result_cell.font = Font(color="0000FF", bold=True)

    # 4. 合計行
    total_questions = len(grading_data_list)
    ws.append(["合計", "", f"{correct_count} / {total_questions}", ""])
    ws.cell(row=ws.max_row, column=3).font = Font(bold=True)

    # 列幅調整
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15

    # ==========================================
    # 📊 ここから分析グラフ機能
    # ==========================================

    # 5. 分析用データを右側（F列〜）に作る
    # ※ここはグラフの元データになるので重要！
    ws["F1"] = "単元別分析"
    ws["F1"].font = Font(bold=True, size=14)

    # 分析表のヘッダー
    ws["F3"] = "単元名"
    ws["G3"] = "正答率(%)"
    
    row_idx = 4
    for unit_name, stats in unit_stats.items():
        score = stats[0] # 正解数
        total = stats[1] # 問題数
        rate = (score / total) * 100 if total > 0 else 0
        
        ws.cell(row=row_idx, column=6, value=unit_name) # F列: 単元名
        ws.cell(row=row_idx, column=7, value=rate)      # G列: パーセント
        row_idx += 1

    # 6. 棒グラフを作成
    chart = BarChart()
    chart.type = "col" # 縦棒グラフ
    chart.style = 10   # 色のスタイル
    chart.title = "単元ごとの得意・不得意"
    chart.y_axis.title = "正答率 (%)"
    chart.x_axis.title = "単元"

    # データ範囲（G列の数値）
    data = Reference(ws, min_col=7, min_row=3, max_row=row_idx-1)
    # ラベル範囲（F列の単元名）
    cats = Reference(ws, min_col=6, min_row=4, max_row=row_idx-1)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    # グラフの大きさ調整
    chart.height = 10 # 高さ
    chart.width = 15  # 幅

    # グラフを配置 (F列のデータの横、I列あたりに置く)
    ws.add_chart(chart, "I3")

    # ==========================================

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"score_report_{timestamp}.xlsx"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, filename)

    wb.save(save_path)
    print(f"Excel作成完了: {save_path}")

    return save_path

# --- 動作確認用 ---
if __name__ == "__main__":
    # いろいろな単元が混ざったデータでテスト
    test_data = [
        {"num": 1, "unit": "計算", "result": "◯"},
        {"num": 2, "unit": "計算", "result": "◯"},
        {"num": 3, "unit": "計算", "result": "❌"}, # 計算は2/3正解
        {"num": 4, "unit": "関数", "result": "❌"},
        {"num": 5, "unit": "関数", "result": "❌"}, # 関数は0/2正解（苦手！）
        {"num": 6, "unit": "図形", "result": "◯"}, # 図形は1/1正解（得意！）
    ]
    
    create_report(test_data)