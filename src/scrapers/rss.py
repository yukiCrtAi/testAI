from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from .base import BaseScraper
from ..utils.date_utils import DateUtils

# SSL証明書の警告を無効化
urllib3.disable_warnings(InsecureRequestWarning)

class RSSScaper(BaseScraper):
    """RSSフィードからニュース記事を取得するスクレイパー"""
    
    def __init__(self, config_path: str = 'config/sites.json'):
        """
        RSSスクレイパーの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        super().__init__(config_path)
        self.date_utils = DateUtils()
        self.results = []

    def search(self, keyword: str, start_date: Optional[datetime] = None,
              end_date: Optional[datetime] = None) -> List[Dict]:
        """
        キーワードと日付範囲で記事を検索
        
        Args:
            keyword (str): 検索キーワード
            start_date (datetime, optional): 検索開始日
            end_date (datetime, optional): 検索終了日
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        if not self.validate_date_range(start_date, end_date):
            return []

        start_date, end_date = self.get_date_range(start_date, end_date)
        self.logger.info(f"検索期間: {start_date.strftime('%Y/%m/%d')} から {end_date.strftime('%Y/%m/%d')} まで")
        
        total_articles = 0
        self.results = []
        
        # RSS対応サイトのみフィルタリング
        rss_sites = [site for site in self.config['sites'] 
                    if site.get('type') == 'rss' and site.get('enabled', True)]
        
        self.logger.info(f"検索対象RSSサイト数: {len(rss_sites)}")
        
        for site in rss_sites:
            try:
                self.logger.info(f"\n{site['name']} からの記事を取得中...")
                content = self._get_feed_content(site['url'])
                if not content:
                    continue

                items = self._parse_feed(content, site['scraping_rules'])
                site_articles = 0

                for item in items:
                    try:
                        if not self._validate_article(item):
                            continue

                        # キーワードでフィルタリング
                        if not self._keyword_matches(item['title'], keyword):
                            continue

                        # 日付でフィルタリング
                        article_date = self.date_utils.parse_date(item['date'])
                        if not article_date:
                            continue
                            
                        if not (start_date <= article_date <= end_date):
                            continue

                        self.results.append({
                            'サイト名': site['name'],
                            '掲載日': article_date.strftime('%Y/%m/%d'),
                            'タイトル': item['title'],
                            'URL': item['link']
                        })
                        site_articles += 1
                        total_articles += 1
                        
                    except Exception as e:
                        self.logger.warning(f"記事の解析中にエラー: {e}")
                        continue

                self.logger.info(f"{site['name']}から {site_articles} 件の関連記事を見つけました")
                time.sleep(self.config.get('settings', {}).get('retry_delay', 2))

            except Exception as e:
                self.logger.error(f"予期せぬエラー ({site['url']}): {e}")
                continue

        # 重複を除去して日付順にソート
        unique_results = []
        seen_urls = set()
        for result in sorted(self.results, key=lambda x: x['掲載日'], reverse=True):
            if result['URL'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['URL'])
        
        self.results = unique_results
        self.logger.info(f"\n合計 {len(self.results)} 件の記事が見つかりました")
        return self.results

    def _get_feed_content(self, url: str) -> Optional[bytes]:
        """
        フィードの内容を取得
        
        Args:
            url (str): フィードのURL
            
        Returns:
            Optional[bytes]: フィードの内容
        """
        retry_count = self.config.get('settings', {}).get('retry_count', 3)
        timeout = self.config.get('settings', {}).get('request_timeout', 30)
        
        for i in range(retry_count):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=timeout,
                    verify=False
                )
                response.raise_for_status()
                return response.content
            except Exception as e:
                self.logger.warning(f"フィード取得エラー (試行 {i+1}/{retry_count}): {e}")
                if i < retry_count - 1:
                    time.sleep(self.config.get('settings', {}).get('retry_delay', 2))
                continue
        return None

    def _parse_feed(self, content: bytes, rules: Dict) -> List[Dict]:
        """
        フィードをパース
        
        Args:
            content (bytes): フィードの内容
            rules (Dict): スクレイピングルール
            
        Returns:
            List[Dict]: パースされた記事のリスト
        """
        if not content:
            return []

        try:
            soup = BeautifulSoup(content, 'html.parser')
            items = []
            
            for item in soup.find_all(rules.get('article_selector', 'item')):
                try:
                    title = item.find(rules.get('title_selector', 'title'))
                    link = item.find(rules.get('link_selector', 'link'))
                    date = item.find(rules.get('date_selector', 'pubDate'))
                    
                    if title and link:
                        items.append({
                            'title': title.get_text(strip=True),
                            'link': link.get('href') or link.get_text(strip=True),
                            'date': date.get_text(strip=True) if date else ''
                        })
                        
                except Exception as e:
                    self.logger.warning(f"記事のパース中にエラー: {e}")
                    continue
                    
            return items
            
        except Exception as e:
            self.logger.error(f"フィードのパース中にエラー: {e}")
            return []

    def _validate_article(self, article: Dict) -> bool:
        """
        記事の妥当性をチェック
        
        Args:
            article (Dict): チェックする記事
            
        Returns:
            bool: 記事が有効な場合True
        """
        return all([
            article.get('title'),
            article.get('link'),
            self.validate_url(article['link'])
        ])

    def _keyword_matches(self, text: str, keyword: str) -> bool:
        """
        キーワードマッチング
        
        Args:
            text (str): 検索対象のテキスト
            keyword (str): 検索キーワード
            
        Returns:
            bool: キーワードが一致する場合True
        """
        if not text or not keyword:
            return False
            
        # キーワードを空白で分割し、すべての単語が含まれているかチェック
        keywords = keyword.lower().split()
        text_lower = text.lower()
        
        return all(kw in text_lower for kw in keywords)