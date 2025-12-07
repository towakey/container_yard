# -*- coding: utf-8 -*-

import sqlite3
import os
import json
from datetime import datetime
import sys

# データベースファイルパス
DB_PATH = os.path.join(os.path.dirname(__file__), 'container_yard.db')

def init_database():
    """データベースを初期化し、必要なテーブルを作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # タスク管理用テーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'CONTINUE',
            create_date TEXT,
            update_date TEXT,
            complete_date TEXT,
            pinned INTEGER DEFAULT 0,
            category TEXT,
            group_category TEXT,
            content TEXT,
            tags TEXT,  -- JSON形式で保存
            担当者 TEXT,
            大分類 TEXT,
            中分類 TEXT,
            小分類 TEXT,
            regular TEXT DEFAULT 'Regular',
            report_flag INTEGER DEFAULT 0
        )
    ''')
    
    # CSVインポート用の動的テーブル作成関数を追加
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS import_tables (
            table_name TEXT PRIMARY KEY,
            columns TEXT NOT NULL,  -- JSON形式でカラム定義を保存
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """データベース接続を取得"""
    return sqlite3.connect(DB_PATH)

def fetch_one(task_id):
    """タスクを1件取得"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        result = dict(row)
        # tagsをJSONからリストに変換
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        else:
            result['tags'] = []
        return result
    
    return None

def fetch_all():
    """全タスクを取得"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tasks ORDER BY update_date DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        # tagsをJSONからリストに変換
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        else:
            result['tags'] = []
        results.append(result)
    
    return results

def insert(task_dict):
    """タスクを挿入"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # tagsをJSONに変換
    tags_json = json.dumps(task_dict.get('tags', []), ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO tasks (
            id, name, status, create_date, update_date, complete_date,
            pinned, category, group_category, content, tags, 担当者,
            大分類, 中分類, 小分類, regular, report_flag
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task_dict.get('id'),
        task_dict.get('name'),
        task_dict.get('status', 'CONTINUE'),
        task_dict.get('create_date'),
        task_dict.get('update_date'),
        task_dict.get('complete_date'),
        int(task_dict.get('pinned', False)),
        task_dict.get('category'),
        task_dict.get('group_category'),
        task_dict.get('content'),
        tags_json,
        task_dict.get('担当者'),
        task_dict.get('大分類'),
        task_dict.get('中分類'),
        task_dict.get('小分類'),
        task_dict.get('regular', 'Regular'),
        int(task_dict.get('report_flag', False))
    ))
    
    conn.commit()
    conn.close()

def update(task_id, task_dict):
    """タスクを更新"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # tagsをJSONに変換
    tags_json = json.dumps(task_dict.get('tags', []), ensure_ascii=False)
    
    cursor.execute('''
        UPDATE tasks SET 
            name = ?, status = ?, create_date = ?, update_date = ?,
            complete_date = ?, pinned = ?, category = ?, group_category = ?,
            content = ?, tags = ?, 担当者 = ?, 大分類 = ?, 中分類 = ?,
            小分類 = ?, regular = ?, report_flag = ?
        WHERE id = ?
    ''', (
        task_dict.get('name'),
        task_dict.get('status'),
        task_dict.get('create_date'),
        task_dict.get('update_date'),
        task_dict.get('complete_date'),
        int(task_dict.get('pinned', False)),
        task_dict.get('category'),
        task_dict.get('group_category'),
        task_dict.get('content'),
        tags_json,
        task_dict.get('担当者'),
        task_dict.get('大分類'),
        task_dict.get('中分類'),
        task_dict.get('小分類'),
        task_dict.get('regular', 'Regular'),
        int(task_dict.get('report_flag', False)),
        task_id
    ))
    
    conn.commit()
    conn.close()

def delete(task_id):
    """タスクを削除"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()

# CSVインポート用の関数
def create_import_table(table_name, columns):
    """CSVインポート用の動的テーブルを作成"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # カラム定義をJSONで保存
    columns_json = json.dumps(columns, ensure_ascii=False)
    
    # テーブル作成SQLを生成
    column_defs = []
    for col in columns:
        column_defs.append(f"{col['name']} {col['type']}")
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
    
    try:
        cursor.execute(create_sql)
        
        # テーブル情報を保存
        cursor.execute('''
            INSERT OR REPLACE INTO import_tables (table_name, columns, created_at)
            VALUES (?, ?, ?)
        ''', (table_name, columns_json, datetime.now().isoformat()))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"テーブル作成エラー: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_csv_data(table_name, data):
    """CSVデータをテーブルに挿入"""
    if not data:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # プレースホルダーを生成
    placeholders = ', '.join(['?' for _ in data[0]])
    
    try:
        cursor.executemany(f'INSERT INTO {table_name} VALUES ({placeholders})', data)
        conn.commit()
        return True
    except Exception as e:
        print(f"データ挿入エラー: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        conn.close()

def get_import_tables():
    """インポート用テーブルの一覧を取得"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM import_tables ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        # columnsをJSONから辞書に変換
        if result.get('columns'):
            try:
                result['columns'] = json.loads(result['columns'])
            except:
                result['columns'] = []
        results.append(result)
    
    return results

def get_table_data(table_name, limit=100):
    """指定テーブルのデータを取得"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT ?', (limit,))
        rows = cursor.fetchall()
        
        results = [dict(row) for row in rows]
        return results
    except Exception as e:
        print(f"データ取得エラー: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()

# データベース初期化
if __name__ == '__main__':
    init_database()
    print("データベースを初期化しました。")
