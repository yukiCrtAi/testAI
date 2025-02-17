import argparse
from datetime import datetime
import sys
import logging
from typing import Optional, Tuple
from src.scrapers.rss import RSSScaper
from src.utils.date_utils import DateUtils
from src.utils.output import OutputManager

def setup_logging():
    """ロギングの設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def parse_date(date_str: Optional[str], date_utils: DateUtils) -> Optional[datetime]:
    """
    日付文字列をパース
    
    Args:
        date_str (Optional[str]): 日付文字列
        date_utils (DateUtils): 日付ユーティリティ
        
    Returns:
        Optional[datetime]: パースされた日付
    """
    if not date_str:
        return None
        
    date = date_utils.parse_date(date_str)
    if not date:
        raise ValueError(f"無効な日付形式です: {date_str}")
    return date

def validate_dates(start_date: Optional[str], end_date: Optional[str],
                  date_utils: DateUtils) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    日付の妥当性を検証
    
    Args:
        start_date (Optional[str]): 開始日
        end_date (Optional[str]): 終了日
        date_utils (DateUtils): 日付ユーティリティ
        
    Returns:
        Tuple[Optional[datetime], Optional[datetime]]: パースされた開始日と終了日
    """
    parsed_start = parse_date(start_date, date_utils)
    parsed_end = parse_date(end_date, date_utils)
    
    if parsed_end and not parsed_start:
        raise ValueError("終了日のみの指定はできません。開始日も指定してください。")
        
    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("開始日は終了日より前の日付を指定してください。")
        
    return parsed_start, parsed_end

def search_news(args: argparse.Namespace, logger: logging.Logger):
    """
    ニュース記事の検索を実行
    
    Args:
        args (argparse.Namespace): コマンドライン引数
        logger (logging.Logger): ロガー
    """
    date_utils = DateUtils()
    scraper = RSSScaper()
    output_manager = OutputManager()
    
    try:
        # 日付の検証
        start_date, end_date = validate_dates(args.start_date, args.end_date, date_utils)
        
        # 検索実行
        results = scraper.search(args.keyword, start_date, end_date)
        
        # 結果の出力
        if results:
            output_manager.print_results(results)
            output_manager.save_results(results, args.keyword)
        else:
            logger.info("検索条件に一致する記事は見つかりませんでした。")
            
    except Exception as e:
        logger.error(f"検索処理中にエラーが発生しました: {e}")
        sys.exit(1)

def add_site(args: argparse.Namespace, logger: logging.Logger):
    """
    サイトを追加
    
    Args:
        args (argparse.Namespace): コマンドライン引数
        logger (logging.Logger): ロガー
    """
    scraper = RSSScaper()
    try:
        if scraper.add_site(args.name, args.url):
            logger.info(f"サイトを追加しました: {args.name}")
        else:
            logger.error("サイトの追加に失敗しました")
            sys.exit(1)
    except Exception as e:
        logger.error(f"サイト追加中にエラーが発生しました: {e}")
        sys.exit(1)

def delete_site(args: argparse.Namespace, logger: logging.Logger):
    """
    サイトを削除
    
    Args:
        args (argparse.Namespace): コマンドライン引数
        logger (logging.Logger): ロガー
    """
    scraper = RSSScaper()
    try:
        if scraper.delete_site(args.name, args.url):
            logger.info(f"サイトを削除しました: {args.name}")
        else:
            logger.error("サイトの削除に失敗しました")
            sys.exit(1)
    except Exception as e:
        logger.error(f"サイト削除中にエラーが発生しました: {e}")
        sys.exit(1)

def main():
    """メイン処理"""
    logger = setup_logging()
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='ニュース記事スクレイピングツール')
    subparsers = parser.add_subparsers(dest='command', help='実行する機能')
    
    # 検索コマンド
    search_parser = subparsers.add_parser('search', help='ニュース記事を検索')
    search_parser.add_argument('keyword', help='検索キーワード')
    search_parser.add_argument('--start-date', help='検索開始日 (YYYY-MM-DD)')
    search_parser.add_argument('--end-date', help='検索終了日 (YYYY-MM-DD)')
    
    # サイト追加コマンド
    add_parser = subparsers.add_parser('add', help='サイトを追加')
    add_parser.add_argument('name', help='サイト名')
    add_parser.add_argument('url', help='サイトのURL')
    
    # サイト削除コマンド
    del_parser = subparsers.add_parser('del', help='サイトを削除')
    del_parser.add_argument('name', help='サイト名')
    del_parser.add_argument('url', help='サイトのURL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # コマンドに応じた処理を実行
    if args.command == 'search':
        search_news(args, logger)
    elif args.command == 'add':
        add_site(args, logger)
    elif args.command == 'del':
        delete_site(args, logger)

if __name__ == '__main__':
    main()