# Container Yard - CSVインポートWEBアプリ

CSVファイルを設定ファイルに基づいてSQLiteデータベースにインポートするWEBアプリケーションです。

## 機能概要

- importフォルダに配置されたCSVファイルとJSON設定ファイルを自動検出
- 設定ファイルに基づいて動的にSQLiteテーブルを作成
- データ型変換とカラムマッピングを実行
- 処理完了後、ファイルをlogフォルダに移動
- Webインターフェースから簡単操作

## ファイル構成

```
container_yard/
├── index.py          # メインWebインターフェース
├── csv_import.py     # CSVインポート実行スクリプト
├── db.py            # データベース操作モジュール
├── import/          # CSV・設定ファイル配置フォルダ
├── log/             # 処理済みファイル保存フォルダ
└── container_yard.db # SQLiteデータベースファイル
```

## 使用方法

### 1. CSVファイルの準備

インポートしたいCSVファイルを準備します。

### 2. 設定ファイルの作成

CSVファイルと同じ名前で`.json`拡張子の設定ファイルを作成します。

**設定ファイルの例：**
```json
{
  "table_name": "employees",
  "csv_settings": {
    "encoding": "utf-8",
    "delimiter": ",",
    "has_header": true
  },
  "column_mappings": [
    {
      "csv_column": "ID",
      "db_column": "id",
      "data_type": "INTEGER"
    },
    {
      "csv_column": "名前",
      "db_column": "name",
      "data_type": "TEXT"
    },
    {
      "csv_column": "年齢",
      "db_column": "age",
      "data_type": "INTEGER"
    },
    {
      "csv_column": "部署",
      "db_column": "department",
      "data_type": "TEXT"
    },
    {
      "csv_column": "入社日",
      "db_column": "hire_date",
      "data_type": "TEXT"
    }
  ]
}
```

### 3. ファイルの配置

作成したCSVファイルと設定ファイルを`import`フォルダに配置します。

### 4. インポート実行

Webブラウザで`index.py`にアクセスし、「CSVインポート実行」ボタンをクリックします。

### 5. 結果確認

処理完了後、ファイルは`log`フォルダにタイムスタンプ付きで移動されます。Web画面で処理結果と履歴を確認できます。

## 設定ファイルの詳細

### table_name
- 作成するデータベーステーブル名
- 英数字とアンダースコア使用

### csv_settings
- `encoding`: CSVファイルの文字コード（utf-8, shift_jisなど）
- `delimiter`: 区切り文字（, ; \tなど）
- `has_header`: ヘッダー行の有無（true/false）

### column_mappings
CSVカラムとデータベースカラムのマッピング情報
- `csv_column`: CSVファイルのカラム名
- `db_column`: データベースのカラム名
- `data_type`: データ型（TEXT, INTEGER, REAL）

## サポートされているデータ型

- **TEXT**: 文字列データ
- **INTEGER**: 整数データ
- **REAL**: 浮動小数点数データ

## コマンドラインでの実行

Webインターフェースを使用せず、コマンドラインから直接実行することも可能です：

```bash
python csv_import.py
```

## 動作環境

- Python 3.6以上
- SQLite3（Python標準ライブラリ）
- Webサーバー（Apache/nginxなど）- CGI対応

## セットアップ

### Webサーバーの設定

1. プロジェクトフォルダをWebサーバーのドキュメントルートに配置
2. Python CGIスクリプトとして実行できるよう設定
3. フォルダの書き込み権限を設定（import, logフォルダ）

### Apacheの場合の設定例

```apache
<Directory "/path/to/container_yard">
    Options +ExecCGI
    AddHandler cgi-script .py
    Require all granted
</Directory>
```

## トラブルシューティング

### ファイルが検出されない
- CSVファイルと設定ファイルの名前が一致しているか確認
- ファイルがimportフォルダに配置されているか確認

### インポートが失敗する
- 設定ファイルのJSON形式が正しいか確認
- CSVファイルの文字コードが設定と一致しているか確認
- カラムマッピングがCSVのヘッダーと一致しているか確認

### データベースエラー
- container_yard.dbファイルの書き込み権限を確認
- ディスク容量に空きがあるか確認

## サンプルデータ

`import/sample_data.csv`と`import/sample_data.json`にサンプルデータが含まれています。参考にしてください。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。