from datetime import datetime, timedelta
from typing import Optional, Union
import logging
from dateutil import parser
import re

class DateUtils:
    """日付処理ユーティリティクラス"""
    
    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
        
        # 相対日付キーワード
        self.relative_dates = {
            'today': 0,
            'yesterday': 1,
            'tomorrow': -1,
            'last week': 7,
            'next week': -7,
            'last month': 30,
            'next month': -30
        }

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

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        様々な形式の日付文字列をパース
        
        Args:
            date_str (str): 日付文字列
            
        Returns:
            Optional[datetime]: パースされた日付。失敗時はNone
        """
        if not date_str:
            return None
            
        # 相対日付の処理
        relative_date = self._parse_relative_date(date_str.lower())
        if relative_date:
            return relative_date
            
        try:
            # 一般的な日付形式のパース
            date = parser.parse(date_str, fuzzy=True)
            return date.replace(tzinfo=None)
        except Exception as e:
            self.logger.warning(f"日付のパースに失敗: {date_str} - {e}")
            return None

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """
        相対日付の文字列をパース
        
        Args:
            date_str (str): 相対日付を表す文字列
            
        Returns:
            Optional[datetime]: パースされた日付。失敗時はNone
        """
        if date_str in self.relative_dates:
            days = self.relative_dates[date_str]
            return datetime.now() - timedelta(days=days)
        return None

    def format_date(self, date: datetime, format_str: str = '%Y-%m-%d') -> str:
        """
        日付を指定された形式の文字列に変換
        
        Args:
            date (datetime): 変換する日付
            format_str (str): 出力形式
            
        Returns:
            str: フォーマットされた日付文字列
        """
        try:
            return date.strftime(format_str)
        except Exception as e:
            self.logger.error(f"日付のフォーマットに失敗: {date} - {e}")
            return ''

    def validate_date_range(self, start_date: Union[str, datetime],
                          end_date: Union[str, datetime]) -> bool:
        """
        日付範囲の妥当性を検証
        
        Args:
            start_date: 開始日（文字列またはdatetime）
            end_date: 終了日（文字列またはdatetime）
            
        Returns:
            bool: 日付範囲が有効な場合True
        """
        try:
            # 文字列の場合はパース
            if isinstance(start_date, str):
                start_date = self.parse_date(start_date)
            if isinstance(end_date, str):
                end_date = self.parse_date(end_date)
                
            if not start_date or not end_date:
                return False
                
            return start_date <= end_date
            
        except Exception as e:
            self.logger.error(f"日付範囲の検証に失敗: {e}")
            return False

    def get_date_range(self, start_date: Optional[Union[str, datetime]] = None,
                      end_date: Optional[Union[str, datetime]] = None) -> tuple:
        """
        検索用の日付範囲を取得
        
        Args:
            start_date: 開始日（文字列またはdatetime）
            end_date: 終了日（文字列またはdatetime）
            
        Returns:
            tuple: (開始日, 終了日)のタプル
        """
        # 文字列の場合はパース
        if isinstance(start_date, str):
            start_date = self.parse_date(start_date)
        if isinstance(end_date, str):
            end_date = self.parse_date(end_date)
            
        if not start_date and not end_date:
            # デフォルトは当日
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return today, today + timedelta(days=1)
            
        if start_date and not end_date:
            # 開始日のみ指定の場合、終了日は当日
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            
        return start_date, end_date

    def is_valid_date_format(self, date_str: str) -> bool:
        """
        日付文字列が有効な形式かチェック
        
        Args:
            date_str (str): チェックする日付文字列
            
        Returns:
            bool: 有効な形式の場合True
        """
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
            r'^\d{4}\.\d{2}\.\d{2}$',  # YYYY.MM.DD
            r'^\d{4}年\d{2}月\d{2}日$'  # YYYY年MM月DD日
        ]
        
        return any(re.match(pattern, date_str) for pattern in patterns)

    def normalize_date(self, date_str: str) -> str:
        """
        日付文字列を標準形式（YYYY-MM-DD）に正規化
        
        Args:
            date_str (str): 正規化する日付文字列
            
        Returns:
            str: 正規化された日付文字列
        """
        try:
            date = self.parse_date(date_str)
            if date:
                return self.format_date(date)
            return ''
        except Exception as e:
            self.logger.error(f"日付の正規化に失敗: {date_str} - {e}")
            return ''