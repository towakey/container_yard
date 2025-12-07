# -*- coding: utf-8 -*-

import os
import json
import csv
import shutil
import sys
from datetime import datetime
import db

# フォルダパス設定
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORT_FOLDER = os.path.join(SCRIPT_DIR, 'import')
LOG_FOLDER = os.path.join(SCRIPT_DIR, 'log')
DB_FILE = os.path.join(SCRIPT_DIR, 'container_yard.db')

def ensure_folders():
    """必要なフォルダが存在することを確認"""
    os.makedirs(IMPORT_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)

def move_to_log(csv_path, config_path, base_name):
    """処理済みファイルをlogフォルダに移動"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 新しいファイル名を生成
    new_csv_name = f"{base_name}_{timestamp}.csv"
    new_config_name = f"{base_name}_{timestamp}.json"
    
    new_csv_path = os.path.join(LOG_FOLDER, new_csv_name)
    new_config_path = os.path.join(LOG_FOLDER, new_config_name)
    
    try:
        shutil.move(csv_path, new_csv_path)
        shutil.move(config_path, new_config_path)
        print(f"ファイルをlogフォルダに移動しました:")
        print(f"  CSV: {new_csv_name}")
        print(f"  設定: {new_config_name}")
        return True
    except Exception as e:
        print(f"エラー: ファイルの移動に失敗しました - {e}")
        return False

def load_config(config_file):
    """設定ファイルを読み込み"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"設定ファイル読み込みエラー: {e}", file=sys.stderr)
        return None

def validate_config(config):
    """設定ファイルの必須項目をチェック"""
    required_keys = ['table_name', 'csv_settings', 'column_mappings']
    for key in required_keys:
        if key not in config:
            print(f"設定ファイルに必須項目 '{key}' がありません", file=sys.stderr)
            return False
    
    # CSV設定の必須項目
    csv_required = ['encoding', 'delimiter', 'has_header']
    for key in csv_required:
        if key not in config['csv_settings']:
            print(f"CSV設定に必須項目 '{key}' がありません", file=sys.stderr)
            return False
    
    return True

def get_csv_files():
    """importフォルダ内のCSVファイルと対応する設定ファイルのペアを取得"""
    csv_files = []
    
    if not os.path.exists(IMPORT_FOLDER):
        print(f"警告: importフォルダが存在しません: {IMPORT_FOLDER}")
        return csv_files
    
    files = os.listdir(IMPORT_FOLDER)
    
    for file in files:
        if file.lower().endswith('.csv'):
            base_name = os.path.splitext(file)[0]
            csv_path = os.path.join(IMPORT_FOLDER, file)
            config_path = os.path.join(IMPORT_FOLDER, f"{base_name}.json")
            
            if os.path.exists(config_path):
                csv_files.append((csv_path, config_path, base_name))
            else:
                print(f"警告: {file} に対応する設定ファイルが見つかりません: {base_name}.json")
    
    return csv_files

def read_csv_data(csv_path, config):
    """CSVデータを読み込み"""
    csv_settings = config['csv_settings']
    encoding = csv_settings['encoding']
    delimiter = csv_settings['delimiter']
    has_header = csv_settings['has_header']
    
    try:
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            
            # ヘッダー行を処理
            headers = []
            if has_header:
                headers = next(reader)
            
            # データ行を読み込み
            data = []
            for row in reader:
                data.append(row)
            
            return headers, data
    except Exception as e:
        print(f"CSV読み込みエラー: {e}", file=sys.stderr)
        return None, None

def create_table_from_config(config):
    """設定ファイルからテーブルを作成"""
    table_name = config['table_name']
    column_mappings = config['column_mappings']
    
    # カラム定義を準備
    columns = []
    for mapping in column_mappings:
        col_def = {
            'name': mapping['db_column'],
            'type': mapping['data_type']
        }
        columns.append(col_def)
    
    # テーブルを作成
    if db.create_import_table(table_name, columns):
        print(f"テーブル '{table_name}' を作成しました")
        return True
    else:
        print(f"テーブル '{table_name}' の作成に失敗しました", file=sys.stderr)
        return False

def map_csv_data(headers, data, config):
    """CSVデータをデータベースカラムにマッピング"""
    column_mappings = config['column_mappings']
    
    # CSVカラム名からDBカラム名へのマッピングを作成
    csv_to_db = {}
    for mapping in column_mappings:
        csv_column = mapping['csv_column']
        db_column = mapping['db_column']
        csv_to_db[csv_column] = db_column
    
    # ヘッダーがある場合、カラムインデックスを取得
    header_to_index = {}
    if headers:
        for i, header in enumerate(headers):
            header_to_index[header] = i
    
    # データを変換
    mapped_data = []
    for row in data:
        mapped_row = []
        
        for mapping in column_mappings:
            csv_column = mapping['csv_column']
            data_type = mapping['data_type']
            
            # 値を取得
            value = ""
            if headers:
                # ヘッダーがある場合、カラム名で検索
                if csv_column in header_to_index:
                    idx = header_to_index[csv_column]
                    if idx < len(row):
                        value = row[idx]
            else:
                # ヘッダーがない場合、順番で取得
                idx = len(mapped_row)
                if idx < len(row):
                    value = row[idx]
            
            # データ型に応じて変換
            if data_type.upper() == 'INTEGER':
                try:
                    value = int(value) if value.strip() else 0
                except ValueError:
                    value = 0
            elif data_type.upper() == 'REAL':
                try:
                    value = float(value) if value.strip() else 0.0
                except ValueError:
                    value = 0.0
            else:
                # TEXT型の場合はそのまま
                value = str(value)
            
            mapped_row.append(value)
        
        mapped_data.append(mapped_row)
    
    return mapped_data

def import_csv_file(csv_info):
    """単一のCSVファイルをインポート"""
    print(f"\n=== {csv_info[0]} のインポートを開始 ===")
    
    # 設定ファイルを読み込み
    config = load_config(csv_info[1])
    if not config:
        return False
    
    # 設定を検証
    if not validate_config(config):
        return False
    
    # CSVデータを読み込み
    headers, data = read_csv_data(csv_info[0], config)
    if headers is None or data is None:
        return False
    
    print(f"CSVデータ: {len(data)} 行を読み込みました")
    
    # テーブルを作成
    if not create_table_from_config(config):
        return False
    
    # データをマッピング
    mapped_data = map_csv_data(headers, data, config)
    
    # データベースに挿入
    if db.insert_csv_data(config['table_name'], mapped_data):
        print(f"{len(mapped_data)} 行をデータベースに挿入しました")
        
        # ファイルをlogフォルダに移動
        if move_to_log(csv_info[0], csv_info[1], csv_info[2]):
            return True
        else:
            return False
    else:
        print("データベースへの挿入に失敗しました", file=sys.stderr)
        return False

def main():
    """メイン処理"""
    print("CSVインポートツールを開始します")
    print(f"importフォルダ: {IMPORT_FOLDER}")
    print(f"logフォルダ: {LOG_FOLDER}")
    print()
    
    # フォルダを確認
    ensure_folders()
    
    # データベースを初期化
    db.init_database()
    
    # インポート対象のファイルを取得
    csv_files = get_csv_files()
    
    if not csv_files:
        print("インポート対象のファイルがありません")
        print("importフォルダにCSVファイルと対応するJSON設定ファイルを配置してください")
        return
    
    print(f"{len(csv_files)} 組のファイルが見つかりました")
    
    # 各ファイルをインポート
    success_count = 0
    for csv_info in csv_files:
        if import_csv_file(csv_info):
            success_count += 1
    
    print(f"\n=== インポート完了 ===")
    print(f"成功: {success_count}/{len(csv_files)} ファイル")

if __name__ == '__main__':
    main()
