import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
import shutil
import os
from datetime import datetime

OUTPUT_DIR = "output"

def create_from_yolo(yolo_results, unit_list, template_path):
    """
    ★新機能: YOLOの生データを受け取って、Excelを作成する便利関数
    
    Args:
        yolo_results (list): YOLOから来たデータ [{'class': '◯', 'y': 500}, ...]
        unit_list (list): ユーザーが画面で選んだ単元のリスト ["計算", "関数"...]
        template_path (str): テンプレートExcelのパス
    """
    
    # 1. YOLOのデータを「Y座標（上からの位置）」順に並べ替える
    # これをやらないと、下の問題が「問1」になってしまう！
    # 'y' というキーに入っている数値が小さい順（＝上にある順）にソート
    sorted_yolo = sorted(yolo_results, key=lambda item: item.get('y', 0))

    # 2. create_report が読める形式（辞書リスト）に変換する
    formatted_data = []
    
    for i, item in enumerate(sorted_yolo):
        # 単元リストからi番目の単元を取る（もし足りなければ「未設定」）
        unit_name = unit_list[i] if i < len(unit_list) else "未設定"
        
        # 変換
        formatted_data.append({
            "num": i + 1,            # 0スタートなので+1して問番号にする
            "unit": unit_name,       # 単元名
            "result": item.get('class', '?') # ◯か❌か
        })
    
    # 3. 既存の最強関数を呼び出す
    return create_report(formatted_data, template_path)


def create_report(grading_data_list, template_path):
    """
    (既存のロジック) ユーザーのExcelレイアウトを解析し、書き込む関数
    """
    
    # --- 準備 ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"score_report_{timestamp}.xlsx"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(template_path):
        print(f"【エラー】テンプレートが見つかりません: {template_path}")
        return None

    shutil.copy(template_path, save_path)
    wb = openpyxl.load_workbook(save_path)
    ws = wb.active

    # --- 1. ヘッダー行を探す ---
    header_row = None
    col_map = {} 

    for r in range(1, 21):
        # 行の値を全部つなげてチェック
        row_values = [str(ws.cell(row=r, column=c).value or "") for c in range(1, 20)]
        row_text = "".join(row_values)
        
        if "問" in row_text or "No" in row_text or "判定" in row_text or "Status" in row_text:
            header_row = r
            for c in range(1, 20):
                val = str(ws.cell(row=r, column=c).value or "")
                if "問" in val or "No" in val: col_map["num"] = c
                elif "単元" in val or "ジャンル" in val or "Unit" in val: col_map["unit"] = c
                elif "結果" in val or "Result" in val or "マーク" in val: col_map["result"] = c
                elif "判定" in val or "Status" in val or "正解" in val: col_map["status"] = c
            break
    
    if header_row is None:
        print("【警告】ヘッダーが見つかりませんでした。")
        return save_path

    # --- 2. 書き込み ---
    current_row = header_row + 1
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    unit_stats = {} 

    for item in grading_data_list:
        q_num = item.get("num", "-")
        unit = item.get("unit", "未設定")
        mark = item.get("result", "?")

        status = "不正解"
        if mark == "◯": status = "正解"
        elif mark == "△": status = "部分点"
        
        if unit not in unit_stats: unit_stats[unit] = [0, 0]
        if mark == "◯": unit_stats[unit][0] += 1
        unit_stats[unit][1] += 1

        # 列マップに従って書き込み
        if "num" in col_map:
            cell = ws.cell(row=current_row, column=col_map["num"])
            cell.value = f"問{q_num}" if isinstance(q_num, int) else q_num
            cell.border = thin_border
        
        if "unit" in col_map:
            cell = ws.cell(row=current_row, column=col_map["unit"])
            cell.value = unit
            cell.border = thin_border

        if "result" in col_map:
            cell = ws.cell(row=current_row, column=col_map["result"])
            cell.value = mark
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")
            if mark == "◯": cell.font = Font(color="FF0000", bold=True)
            elif mark == "❌": cell.font = Font(color="0000FF", bold=True)

        if "status" in col_map:
            cell = ws.cell(row=current_row, column=col_map["status"])
            cell.value = status
            cell.border = thin_border

        current_row += 1

    # --- 3. グラフ作成 ---
    max_used_col = max(col_map.values()) if col_map else 5
    graph_start_col = max_used_col + 2 

    row_idx = 1
    ws.cell(row=row_idx, column=graph_start_col, value="単元")
    ws.cell(row=row_idx, column=graph_start_col+1, value="正答率")
    row_idx += 1

    for u_name, stats in unit_stats.items():
        rate = (stats[0] / stats[1]) * 100 if stats[1] > 0 else 0
        ws.cell(row=row_idx, column=graph_start_col, value=u_name)
        ws.cell(row=row_idx, column=graph_start_col+1, value=rate)
        row_idx += 1
    
    chart = BarChart()
    chart.title = "単元別正答率"
    data = Reference(ws, min_col=graph_start_col+1, min_row=1, max_row=row_idx-1)
    cats = Reference(ws, min_col=graph_start_col, min_row=2, max_row=row_idx-1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, f"{openpyxl.utils.get_column_letter(graph_start_col)}10")

    wb.save(save_path)
    print(f"Excel作成完了: {save_path}")
    return save_path

# --- 動作確認用（YOLOシミュレーション） ---
if __name__ == "__main__":
    
    # 1. YOLOからこんなデータが来たとする（順番バラバラ！）
    # 'y' は画像の縦の位置（小さいほど上）
    raw_yolo_data = [
        {'class': '❌', 'y': 800, 'confidence': 0.9}, # 問3（一番下）
        {'class': '◯', 'y': 100, 'confidence': 0.9}, # 問1（一番上）
        {'class': '◯', 'y': 400, 'confidence': 0.8}, # 問2（真ん中）
    ]
    
    # 2. ユーザーが画面で選んだ単元リスト
    user_selected_units = ["計算", "関数", "図形"]
    
    # 3. あなたの自作テンプレート
    my_file = "assets/templates/test.xlsx" 

    if os.path.exists(my_file):
        # ★ここが変更点！ 新しい関数を使う
        create_from_yolo(raw_yolo_data, user_selected_units, my_file)
    else:
        # ダミー作成
        wb_dummy = openpyxl.Workbook()
        ws_dummy = wb_dummy.active
        ws_dummy.append(["判定(Status)", "結果(Result)", "ジャンル(Unit)", "No."])
        wb_dummy.save(my_file)
        print("ダミー作成。もう一度実行してください。")