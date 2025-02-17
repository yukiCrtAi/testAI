from typing import List, Dict, Optional
import os
import pandas as pd
from datetime import datetime
import logging
import json
from pathlib import Path

class OutputManager:
    """出力管理クラス"""
    
    def __init__(self, base_output_dir: str = 'output'):
        """
        出力管理クラスの初期化
        
        Args:
            base_output_dir (str): 基本出力ディレクトリ
        """
        self.base_output_dir = base_output_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
        self._ensure_output_dir()

    def _setup_logging(self):
        """ロギングの設定"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _ensure_output_dir(self):
        """出力ディレクトリの作成"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.output_dir = os.path.join(self.base_output_dir, today)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # サブディレクトリの作成
        for subdir in ['raw', 'processed', 'logs']:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)

    def save_results(self, results: List[Dict], keyword: str,
                    format: str = 'csv') -> Optional[str]:
        """
        検索結果を保存
        
        Args:
            results (List[Dict]): 保存する検索結果
            keyword (str): 検索キーワード
            format (str): 出力形式（'csv' または 'json'）
            
        Returns:
            Optional[str]: 保存したファイルのパス
        """
        if not results:
            self.logger.warning("保存する結果がありません")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'news_{timestamp}_{keyword}'
        
        try:
            if format.lower() == 'csv':
                return self._save_to_csv(results, filename)
            elif format.lower() == 'json':
                return self._save_to_json(results, filename)
            else:
                self.logger.error(f"未対応の出力形式: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"結果の保存に失敗: {e}")
            return None

    def _save_to_csv(self, results: List[Dict], base_filename: str) -> Optional[str]:
        """
        結果をCSVファイルに保存
        
        Args:
            results (List[Dict]): 保存する結果
            base_filename (str): ベースファイル名
            
        Returns:
            Optional[str]: 保存したファイルのパス
        """
        try:
            filepath = os.path.join(self.output_dir, 'processed', f'{base_filename}.csv')
            df = pd.DataFrame(results)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"結果をCSVファイルに保存しました: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"CSVファイルの保存に失敗: {e}")
            return None

    def _save_to_json(self, results: List[Dict], base_filename: str) -> Optional[str]:
        """
        結果をJSONファイルに保存
        
        Args:
            results (List[Dict]): 保存する結果
            base_filename (str): ベースファイル名
            
        Returns:
            Optional[str]: 保存したファイルのパス
        """
        try:
            filepath = os.path.join(self.output_dir, 'processed', f'{base_filename}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"結果をJSONファイルに保存しました: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"JSONファイルの保存に失敗: {e}")
            return None

    def save_raw_data(self, data: str, source: str) -> Optional[str]:
        """
        生データを保存
        
        Args:
            data (str): 保存するデータ
            source (str): データのソース
            
        Returns:
            Optional[str]: 保存したファイルのパス
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'raw_{timestamp}_{source}.txt'
            filepath = os.path.join(self.output_dir, 'raw', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
                
            self.logger.info(f"生データを保存しました: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生データの保存に失敗: {e}")
            return None

    def print_results(self, results: List[Dict]):
        """
        結果を表示
        
        Args:
            results (List[Dict]): 表示する結果
        """
        if not results:
            print("\n検索結果が見つかりませんでした。")
            return

        print(f"\n合計記事数: {len(results)}")
        print("\n=== 検索結果 ===")
        
        for i, article in enumerate(results, 1):
            print(f"\n記事 {i}:")
            print(f"サイト名: {article['サイト名']}")
            print(f"掲載日: {article['掲載日']}")
            print(f"タイトル: {article['タイトル']}")
            print(f"URL: {article['URL']}")
            print("-" * 50)

    def cleanup_old_files(self, days: int = 30):
        """
        古いファイルを削除
        
        Args:
            days (int): 保持する日数
        """
        try:
            current = datetime.now()
            base_path = Path(self.base_output_dir)
            
            for path in base_path.glob('*/*'):
                if not path.is_file():
                    continue
                    
                file_time = datetime.fromtimestamp(path.stat().st_mtime)
                age = (current - file_time).days
                
                if age > days:
                    path.unlink()
                    self.logger.info(f"古いファイルを削除しました: {path}")
                    
        except Exception as e:
            self.logger.error(f"ファイルのクリーンアップに失敗: {e}")