from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import os
import json
from urllib.parse import urlparse

class BaseScraper(ABC):
    """
    スクレイパーの基本クラス
    全てのスクレイパー実装の基底クラスとなります
    """
    
    def __init__(self, config_path: str = 'config/sites.json'):
        """
        スクレイパーの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self._setup_logging()  # 先にロギングを設定
        self.config = self._load_config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def _setup_logging(self):
        """ロギングの設定"""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_config(self) -> Dict:
        """
        設定ファイルの読み込み
        
        Returns:
            Dict: 設定情報
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"設定ファイルが見つかりません: {self.config_path}")
                return {"sites": []}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info(f"設定を読み込みました: {len(config.get('sites', []))}サイト")
                return config
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗: {e}")
            return {"sites": []}

    def validate_date_range(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> bool:
        """
        日付範囲の検証
        
        Args:
            start_date (datetime, optional): 開始日
            end_date (datetime, optional): 終了日
            
        Returns:
            bool: 日付範囲が有効な場合True
        """
        if end_date and not start_date:
            self.logger.error("終了日のみの指定はできません")
            return False
            
        if start_date and end_date and start_date > end_date:
            self.logger.error("開始日は終了日より前の日付を指定してください")
            return False
            
        return True

    def get_date_range(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> tuple:
        """
        検索用の日付範囲を取得
        
        Args:
            start_date (datetime, optional): 開始日
            end_date (datetime, optional): 終了日
            
        Returns:
            tuple: (開始日, 終了日)
        """
        if not start_date and not end_date:
            # デフォルトは当日
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return today, today + timedelta(days=1)
            
        if start_date and not end_date:
            # 開始日のみ指定の場合、終了日は当日
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            
        return start_date, end_date

    def validate_url(self, url: str) -> bool:
        """
        URLの検証
        
        Args:
            url (str): 検証するURL
            
        Returns:
            bool: URLが有効な場合True
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            self.logger.error(f"無効なURL: {url} - {e}")
            return False

    @abstractmethod
    def search(self, keyword: str, start_date: Optional[datetime] = None,
              end_date: Optional[datetime] = None) -> List[Dict]:
        """
        記事の検索
        
        Args:
            keyword (str): 検索キーワード
            start_date (datetime, optional): 検索開始日
            end_date (datetime, optional): 検索終了日
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        pass

    def add_site(self, name: str, url: str) -> bool:
        """
        サイトの追加
        
        Args:
            name (str): サイト名
            url (str): サイトのURL
            
        Returns:
            bool: 追加に成功した場合True
        """
        try:
            if not self.validate_url(url):
                return False
                
            if any(site['url'] == url for site in self.config['sites']):
                self.logger.warning(f"URLが重複しています: {url}")
                return False
                
            if any(site['name'] == name for site in self.config['sites']):
                self.logger.warning(f"サイト名が重複しています: {name}")
                return False
                
            self.config['sites'].append({
                'name': name,
                'url': url,
                'enabled': True
            })
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"サイトを追加しました: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"サイト追加に失敗: {e}")
            return False

    def delete_site(self, name: str, url: str) -> bool:
        """
        サイトの削除
        
        Args:
            name (str): サイト名
            url (str): サイトのURL
            
        Returns:
            bool: 削除に成功した場合True
        """
        try:
            original_count = len(self.config['sites'])
            self.config['sites'] = [
                site for site in self.config['sites']
                if not (site['name'] == name and site['url'] == url)
            ]
            
            if len(self.config['sites']) == original_count:
                self.logger.warning(f"指定されたサイトが見つかりません: {name}")
                return False
                
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"サイトを削除しました: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"サイト削除に失敗: {e}")
            return False