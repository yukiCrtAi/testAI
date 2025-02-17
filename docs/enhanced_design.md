# ニュース記事スクレイピングツール 強化版設計書

## 1. システム概要

### 1.1 目的
指定したキーワードと日付範囲でWebサイトの情報をスクレイピングし、ニュース記事一覧を収集・出力するツール

### 1.2 主要機能
1. 検索機能（search）
   ```bash
   # 基本検索（当日の記事）
   search_news.bat search "キーワード"
   
   # 日付範囲指定
   search_news.bat search "キーワード" --start-date YYYY-MM-DD --end-date YYYY-MM-DD
   ```

2. サイト管理機能
   ```bash
   # サイト追加
   search_news.bat add "サイト名" "URL"
   
   # サイト削除
   search_news.bat del "サイト名" "URL"
   ```

## 2. 詳細設計

### 2.1 検索機能の強化
1. キーワード検索
   - AND検索対応（スペース区切りで複数キーワード）
   - 正規表現対応
   - 大文字小文字の区別オプション

2. 日付処理
   - タイムゾーン対応（JST基準）
   - 様々な日付形式の自動認識
   - 相対日付指定（"yesterday", "last week"等）

3. 結果のフィルタリング
   - 重複記事の除外（URL/タイトルベース）
   - スパムフィルター
   - 関連度によるソート

### 2.2 出力管理
1. ディレクトリ構造
   ```
   output/
   ├── YYYY-MM-DD/              # 実行日ディレクトリ
   │   ├── raw/                 # 生データ
   │   ├── processed/           # 加工済みデータ
   │   └── logs/                # ログファイル
   └── archive/                 # 過去データ
   ```

2. ファイル命名規則
   ```
   news_YYYYMMDD_HHMMSS_[keyword]_[count].csv
   ```

3. 出力形式
   - CSV（デフォルト）
   - JSON（オプション）
   - Excel（オプション）

### 2.3 エラー処理の強化
1. ネットワークエラー
   ```python
   class NetworkError(Exception):
       def __init__(self, site_name, url, retry_count):
           self.site_name = site_name
           self.url = url
           self.retry_count = retry_count
           super().__init__(f"Network error for {site_name}: {url} (retry: {retry_count})")
   ```

2. パース処理エラー
   ```python
   class ParseError(Exception):
       def __init__(self, site_name, content_type, reason):
           self.site_name = site_name
           self.content_type = content_type
           self.reason = reason
           super().__init__(f"Parse error for {site_name}: {content_type} - {reason}")
   ```

3. リトライメカニズム
   ```python
   class RetryHandler:
       def __init__(self, max_retries=3, delay=2):
           self.max_retries = max_retries
           self.delay = delay
           
       async def execute(self, func, *args):
           for i in range(self.max_retries):
               try:
                   return await func(*args)
               except Exception as e:
                   if i == self.max_retries - 1:
                       raise
                   await asyncio.sleep(self.delay * (i + 1))
   ```

### 2.4 パフォーマンス最適化
1. 非同期処理
   ```python
   class AsyncNewsCollector:
       def __init__(self, max_concurrent=3):
           self.semaphore = asyncio.Semaphore(max_concurrent)
           
       async def collect(self, sites):
           tasks = [self.fetch_site(site) for site in sites]
           return await asyncio.gather(*tasks)
           
       async def fetch_site(self, site):
           async with self.semaphore:
               # サイトからのデータ取得
   ```

2. キャッシュ管理
   ```python
   class CacheManager:
       def __init__(self, cache_dir, max_age_hours=24):
           self.cache_dir = cache_dir
           self.max_age = timedelta(hours=max_age_hours)
           
       def get_cached_data(self, key):
           # キャッシュデータの取得
           
       def store_cache(self, key, data):
           # データのキャッシュ保存
   ```

3. メモリ最適化
   ```python
   class MemoryOptimizedParser:
       def __init__(self, chunk_size=1024):
           self.chunk_size = chunk_size
           
       def parse_large_file(self, file_path):
           for chunk in self.read_chunks(file_path):
               # チャンク単位での処理
   ```

### 2.5 セキュリティ対策
1. 入力検証
   ```python
   class InputValidator:
       @staticmethod
       def validate_keyword(keyword):
           if len(keyword) > 100:
               raise ValidationError("Keyword too long")
           if re.search(r'[<>]', keyword):
               raise ValidationError("Invalid characters in keyword")
   ```

2. URLサニタイズ
   ```python
   class URLSanitizer:
       @staticmethod
       def sanitize(url):
           parsed = urllib.parse.urlparse(url)
           if parsed.scheme not in ['http', 'https']:
               raise ValidationError("Invalid URL scheme")
   ```

3. ファイルパス検証
   ```python
   class PathValidator:
       @staticmethod
       def validate_output_path(path):
           if '..' in path or path.startswith('/'):
               raise ValidationError("Invalid path")
   ```

## 3. テスト計画

### 3.1 単体テスト
1. 日付処理
   ```python
   class TestDateProcessor:
       def test_date_parsing(self):
           processor = DateProcessor()
           assert processor.parse("2025-02-17") == datetime(2025, 2, 17)
           assert processor.parse("yesterday") == datetime.now() - timedelta(days=1)
   ```

2. キーワード処理
   ```python
   class TestKeywordProcessor:
       def test_keyword_splitting(self):
           processor = KeywordProcessor()
           assert processor.split("AI 機械学習") == ["AI", "機械学習"]
   ```

### 3.2 統合テスト
1. 検索フロー
   ```python
   class TestSearchFlow:
       def test_complete_search(self):
           result = execute_search("AI", "2025-02-17", "2025-02-18")
           assert len(result) > 0
           assert all(isinstance(item, NewsItem) for item in result)
   ```

2. 出力処理
   ```python
   class TestOutputProcess:
       def test_file_creation(self):
           output = OutputManager()
           result = output.save_results(test_data)
           assert os.path.exists(result.file_path)
   ```

### 3.3 パフォーマンステスト
1. 負荷テスト
   ```python
   class TestPerformance:
       def test_large_dataset(self):
           start_time = time.time()
           result = process_large_dataset()
           duration = time.time() - start_time
           assert duration < 30  # 30秒以内
   ```

2. メモリ使用
   ```python
   class TestMemoryUsage:
       def test_memory_consumption(self):
           tracker = MemoryTracker()
           process_data()
           assert tracker.peak_usage < 256 * 1024 * 1024  # 256MB以内
   ```

## 4. 実装フェーズ計画

### 4.1 フェーズ分割
1. 基本機能実装（2日）
   - コマンドライン引数処理
   - 基本的なスクレイピング
   - CSV出力

2. 機能強化（3日）
   - 日付範囲処理
   - 非同期処理
   - エラーハンドリング

3. 最適化（2日）
   - パフォーマンスチューニング
   - メモリ最適化
   - キャッシュ実装

4. テスト・デバッグ（3日）
   - 単体テスト作成
   - 統合テスト作成
   - バグ修正

### 4.2 品質基準
1. コードカバレッジ
   - 単体テスト: 90%以上
   - 統合テスト: 80%以上

2. パフォーマンス
   - 検索応答時間: 3秒以内
   - メモリ使用量: 256MB以下
   - CPU使用率: 30%以下

3. 信頼性
   - エラー発生率: 0.1%以下
   - 可用性: 99.9%以上

### 4.3 デプロイメント計画
1. 環境構築
   - Python 3.8以上
   - 必要なライブラリ
   - 設定ファイル

2. 初期設定
   - 出力ディレクトリ作成
   - ログ設定
   - 初期サイト登録

3. 動作確認
   - 基本機能テスト
   - エラーケーステスト
   - パフォーマンステスト