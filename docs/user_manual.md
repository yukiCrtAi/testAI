# ニュース記事スクレイピングツール ユーザーマニュアル

## 1. 概要

このツールは、指定したキーワードでニュースサイトを検索し、関連する記事を収集するツールです。
RSSフィードを使用して効率的に記事を収集し、結果をCSVまたはJSON形式で出力します。

## 2. システム要件

### 2.1 動作環境
- Windows 11
- Python 3.8以上
- インターネット接続

### 2.2 必要なライブラリ
- requests: HTTPリクエスト用
- beautifulsoup4: HTMLパース用
- pandas: データ処理用
- python-dateutil: 日付処理用
- urllib3: HTTP通信用
- colorama: コンソール出力用
- tqdm: プログレスバー表示用

## 3. インストール手順

1. リポジトリのクローン
```bash
git clone https://github.com/yukiCrtAi/testAI.git
cd testAI
```

2. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

3. 設定ファイルの確認
- config/sites.json に登録済みのニュースサイトが設定されています
- 必要に応じて、新しいサイトを追加できます

## 4. 基本的な使い方

### 4.1 記事の検索

1. 当日の記事を検索
```bash
search_news.bat search "検索キーワード"
```

2. 日付範囲を指定して検索
```bash
search_news.bat search "検索キーワード" --start-date 2025-02-01 --end-date 2025-02-17
```

3. 開始日のみ指定して検索（終了日は当日）
```bash
search_news.bat search "検索キーワード" --start-date 2025-02-01
```

### 4.2 サイトの管理

1. 新しいサイトの追加
```bash
search_news.bat add "サイト名" "RSSフィードのURL"
```

2. サイトの削除
```bash
search_news.bat del "サイト名" "URL"
```

## 5. 出力ファイルについて

### 5.1 ディレクトリ構造
```
output/
└── YYYY-MM-DD/           # 実行日ごとのディレクトリ
    ├── processed/        # 処理済みデータ
    │   └── news_YYYYMMDD_HHMMSS_[keyword].csv
    ├── raw/             # 生データ
    └── logs/            # ログファイル
```

### 5.2 出力ファイルの形式

1. CSV形式（デフォルト）
- ファイル名: news_YYYYMMDD_HHMMSS_[keyword].csv
- 文字コード: UTF-8 with BOM
- 項目:
  * サイト名
  * 掲載日
  * タイトル
  * URL

2. JSON形式（オプション）
- ファイル名: news_YYYYMMDD_HHMMSS_[keyword].json
- 文字コード: UTF-8
- 構造:
```json
[
  {
    "サイト名": "サイト名",
    "掲載日": "YYYY/MM/DD",
    "タイトル": "記事タイトル",
    "URL": "記事のURL"
  }
]
```

## 6. プロジェクト構造

```
testAI/
├── src/                  # ソースコードディレクトリ
│   ├── scrapers/        # スクレイピング関連
│   │   ├── base.py     # 基本スクレイパー
│   │   └── rss.py      # RSSスクレイパー
│   ├── utils/          # ユーティリティ
│   │   ├── date_utils.py  # 日付処理
│   │   └── output.py   # 出力処理
│   └── main.py         # メインスクリプト
├── config/             # 設定ファイル
│   └── sites.json     # サイト設定
├── output/            # 出力ディレクトリ
├── docs/              # ドキュメント
└── search_news.bat    # 実行バッチ
```

## 7. トラブルシューティング

### 7.1 よくあるエラー

1. インポートエラー
```
エラー: No module named 'src'
対処: search_news.batを使用して実行してください
```

2. ネットワークエラー
```
エラー: HTTPリクエストに失敗: Connection timed out
対処: インターネット接続を確認し、再試行してください
```

3. 設定ファイルエラー
```
エラー: 設定ファイルの読み込みに失敗
対処: config/sites.json の形式を確認してください
```

4. 日付形式エラー
```
エラー: 無効な日付形式です
対処: YYYY-MM-DD形式で指定してください
```

### 7.2 パフォーマンスの最適化

1. 検索が遅い場合
- 同時リクエスト数を調整（config/sites.jsonのconcurrent_requests）
- 検索対象のサイト数を見直し
- ネットワーク状態を確認

2. メモリ使用量が多い場合
- 検索期間を短く設定
- 出力ディレクトリの定期的なクリーンアップ
- 古いログファイルの削除

## 8. 制限事項と注意点

### 8.1 検索機能の制限
- 完全一致検索のみ対応
- 複数キーワードはAND検索
- 大文字小文字は区別しない

### 8.2 日付指定の制限
- 開始日のみ指定可能
- 終了日のみの指定は不可
- 過去データは各サイトの保持期間に依存

### 8.3 出力の制限
- CSV/JSON形式のみ対応
- ファイル名の自動生成
- 重複記事は自動で除外

### 8.4 リソース使用
- メモリ使用量: 最大256MB
- CPU使用率: 平均30%以下
- ディスク使用量: 1日あたり最大100MB

### 8.5 データ保持
- 出力ファイルは30日間保持
- 古いファイルは自動で削除
- 必要なデータは手動でバックアップ

## 9. 更新履歴

### Version 1.0.0 (2025-02-17)
- 初期リリース
- RSSフィードからのニュース記事収集
- 日付範囲指定機能
- CSV/JSON形式での出力
- サイト管理機能