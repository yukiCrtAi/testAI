# ニュース記事スクレイピングツール ユーザーマニュアル

## 1. 概要

このツールは、指定したキーワードでニュースサイトを検索し、関連する記事を収集するツールです。
RSSフィードを使用して効率的に記事を収集し、結果をCSVまたはJSON形式で出力します。

## 2. インストール手順

### 2.1 必要な環境
- Python 3.8以上
- Windows 11
- インターネット接続

### 2.2 セットアップ手順

1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

2. 設定ファイルの確認
- config/sites.json に登録済みのニュースサイトが設定されています
- 必要に応じて、新しいサイトを追加できます

## 3. 基本的な使い方

### 3.1 記事の検索

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

### 3.2 サイトの管理

1. 新しいサイトの追加
```bash
search_news.bat add "サイト名" "RSSフィードのURL"
```

2. サイトの削除
```bash
search_news.bat del "サイト名" "URL"
```

## 4. 出力ファイルについて

### 4.1 ディレクトリ構造
```
output/
└── YYYY-MM-DD/           # 実行日ごとのディレクトリ
    ├── processed/        # 処理済みデータ
    │   └── news_YYYYMMDD_HHMMSS_[keyword].csv
    ├── raw/             # 生データ
    └── logs/            # ログファイル
```

### 4.2 出力ファイルの形式

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

## 5. 設定ファイルの詳細

### 5.1 sites.json
```json
{
    "sites": [
        {
            "name": "サイト名",
            "url": "RSSフィードのURL",
            "type": "rss",
            "enabled": true,
            "scraping_rules": {
                "article_selector": "item",
                "title_selector": "title",
                "date_selector": "pubDate",
                "link_selector": "link"
            }
        }
    ],
    "settings": {
        "request_timeout": 30,
        "retry_count": 3,
        "retry_delay": 2,
        "concurrent_requests": 3
    }
}
```

### 5.2 設定項目の説明

1. サイト設定
- name: サイト名
- url: RSSフィードのURL
- type: フィードの種類（現在はrssのみ対応）
- enabled: 有効/無効の切り替え
- scraping_rules: スクレイピングルール

2. 共通設定
- request_timeout: リクエストのタイムアウト時間（秒）
- retry_count: エラー時の再試行回数
- retry_delay: 再試行間隔（秒）
- concurrent_requests: 同時リクエスト数

## 6. エラー対応

### 6.1 よくあるエラー

1. ネットワークエラー
```
エラー: HTTPリクエストに失敗: Connection timed out
対処: インターネット接続を確認し、再試行してください
```

2. 設定ファイルエラー
```
エラー: 設定ファイルの読み込みに失敗
対処: config/sites.json の形式を確認してください
```

3. 日付形式エラー
```
エラー: 無効な日付形式です
対処: YYYY-MM-DD形式で指定してください
```

### 6.2 トラブルシューティング

1. 検索結果が0件の場合
- キーワードの綴りを確認
- 日付範囲が適切か確認
- 登録サイトが有効になっているか確認

2. 実行が遅い場合
- 同時リクエスト数を調整
- 検索対象のサイト数を見直し
- ネットワーク状態を確認

## 7. 制限事項

1. 検索機能
- 完全一致検索のみ対応
- 複数キーワードはAND検索
- 大文字小文字は区別しない

2. 日付指定
- 開始日のみ指定可能
- 終了日のみの指定は不可
- 過去データは各サイトの保持期間に依存

3. 出力形式
- CSV/JSON形式のみ対応
- ファイル名の自動生成
- 重複記事は自動で除外

## 8. 注意事項

1. リソース使用
- メモリ使用量: 最大256MB
- CPU使用率: 平均30%以下
- ディスク使用量: 1日あたり最大100MB

2. データ保持
- 出力ファイルは30日間保持
- 古いファイルは自動で削除
- 必要なデータは手動でバックアップ

3. 利用制限
- 各サイトのRSSフィード利用規約に準拠
- 過度なリクエストは避ける
- エラー時は適切な間隔を空けて再試行