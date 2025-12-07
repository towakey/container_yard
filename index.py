import sys
import io
import os
import subprocess
import json
from datetime import datetime

# Set stdout to UTF-8 to handle Japanese characters correctly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# CSVインポート関連のパス
SCRIPT_PATH = os.path.dirname(__file__)
IMPORT_FOLDER = os.path.join(SCRIPT_PATH, 'import')
LOG_FOLDER = os.path.join(SCRIPT_PATH, 'log')

# CGIフォームデータを取得
import cgi
form = cgi.FieldStorage()
mode = form.getfirst("mode", '')

# CSVインポート実行機能
if mode == 'import':
    print("Content-type: text/html; charset=UTF-8\n")
    print("""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CSVインポート実行中</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>CSVインポート実行中...</h1>
        <div class="progress mb-3">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
        </div>
        <pre class="bg-light p-3 rounded">
""")
    
    try:
        # CSVインポートスクリプトを実行
        result = subprocess.run([sys.executable, 'csv_import.py'], 
                              cwd=SCRIPT_PATH,
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        # 出力を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"エラー: {result.stderr}")
        
        if result.returncode == 0:
            print("\n✅ インポートが正常に完了しました！")
        else:
            print(f"\n❌ インポートが失敗しました (終了コード: {result.returncode})")
            
    except Exception as e:
        print(f"実行エラー: {e}")
    
    print("""
        </pre>
        <div class="mt-3">
            <a href="index.py" class="btn btn-primary">戻る</a>
        </div>
    </div>
</body>
</html>
""")
    sys.exit(0)

print("Content-type: text/html; charset=UTF-8\n")
print("""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Container Yard - CSVインポートツール</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .container { max-width: 1200px; }
        .file-list { max-height: 300px; overflow-y: auto; }
        .log-entry { border-left: 4px solid #007bff; padding-left: 15px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">Container Yard - CSVインポートツール</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>CSVインポート実行</h3>
                    </div>
                    <div class="card-body">
                        <p class="text-muted">
                            importフォルダにCSVファイルと対応するJSON設定ファイルを配置してから実行ボタンを押してください。
                        </p>
                        <form method="post">
                            <input type="hidden" name="mode" value="import">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-upload"></i> CSVインポート実行
                            </button>
                        </form>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h3>importフォルダのファイル</h3>
                    </div>
                    <div class="card-body">
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>インポート履歴</h3>
                    </div>
                    <div class="card-body">
                        <div class="file-list">
""")

# importフォルダのファイル一覧を表示
if os.path.exists(IMPORT_FOLDER):
    files = os.listdir(IMPORT_FOLDER)
    if files:
        for file in sorted(files):
            file_path = os.path.join(IMPORT_FOLDER, file)
            file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"                            <div class='d-flex justify-content-between align-items-center p-2 border-bottom'>")
            print(f"                                <span><i class='bi bi-file-earmark'></i> {file}</span>")
            print(f"                                <small class='text-muted'>{file_size} bytes - {file_time}</small>")
            print(f"                            </div>")
    else:
        print("                            <p class='text-muted'>ファイルがありません</p>")
else:
    print("                            <p class='text-muted'>importフォルダが存在しません</p>")

print("""
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h3>logフォルダの履歴</h3>
                    </div>
                    <div class="card-body">
                        <div class="file-list">
""")

# logフォルダのファイル一覧を表示
if os.path.exists(LOG_FOLDER):
    files = os.listdir(LOG_FOLDER)
    if files:
        # タイムスタンプでソート（新しい順）
        files_with_time = []
        for file in files:
            file_path = os.path.join(LOG_FOLDER, file)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                files_with_time.append((file, file_time))
        
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        for file, file_time in files_with_time[:20]:  # 最新20件を表示
            file_path = os.path.join(LOG_FOLDER, file)
            file_size = os.path.getsize(file_path)
            formatted_time = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
            file_type = "CSV" if file.endswith('.csv') else "設定" if file.endswith('.json') else "その他"
            
            print(f"                            <div class='log-entry'>")
            print(f"                                <div class='d-flex justify-content-between align-items-center'>")
            print(f"                                    <span><i class='bi bi-file-earmark-check'></i> {file}</span>")
            print(f"                                    <span class='badge bg-secondary'>{file_type}</span>")
            print(f"                                </div>")
            print(f"                                <small class='text-muted'>{file_size} bytes - {formatted_time}</small>")
            print(f"                            </div>")
    else:
        print("                            <p class='text-muted'>処理済みファイルがありません</p>")
else:
    print("                            <p class='text-muted'>logフォルダが存在しません</p>")

print("""
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h3>使用方法</h3>
                    </div>
                    <div class="card-body">
                        <ol>
                            <li><strong>CSVファイルを準備:</strong> インポートしたいCSVファイルを用意します</li>
                            <li><strong>設定ファイルを作成:</strong> CSVファイルと同じ名前で.json拡張子の設定ファイルを作成します</li>
                            <li><strong>ファイルを配置:</strong> CSVファイルと設定ファイルをimportフォルダに配置します</li>
                            <li><strong>インポート実行:</strong> 「CSVインポート実行」ボタンをクリックします</li>
                            <li><strong>結果確認:</strong> 処理完了後、ファイルはlogフォルダに移動されます</li>
                        </ol>
                        
                        <h5 class="mt-3">設定ファイルの例:</h5>
                        <pre class="bg-light p-3 rounded"><code>{
  "table_name": "employees",
  "csv_settings": {
    "encoding": "utf-8",
    "delimiter": ",",
    "has_header": true
  },
  "column_mappings": [
    {
      "csv_column": "名前",
      "db_column": "name",
      "data_type": "TEXT"
    }
  ]
}</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
