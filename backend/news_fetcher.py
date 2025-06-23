import aiohttp
import feedparser
import os
import re
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

class NewsFetcher:
    def __init__(self):
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.brave_base_url = "https://api.search.brave.com/res/v1/news/search"
        
        # English RSS feeds (free articles only)
        self.english_rss_feeds = [
            "https://rss.cnn.com/rss/edition.rss",  # CNN
            "https://www.theguardian.com/world/rss",  # The Guardian World
            "https://www.theguardian.com/business/rss",  # The Guardian Business
            "https://feeds.npr.org/1001/rss.xml",  # NPR News
            "https://api.axios.com/feed/",  # Axios
            "https://slate.com/feeds/all.rss",  # Slate
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",  # NYT World (free)
            "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",  # NYT Business (free)
            "https://feeds.reuters.com/reuters/topNews",  # Reuters
            "https://feeds.bbci.co.uk/news/rss.xml"  # BBC
        ]
        
        # Japanese RSS feeds for local news
        self.japanese_rss_feeds = [
            "https://www.nhk.or.jp/rss/news/cat0.xml",  # NHK 主要ニュース
            "https://news.yahoo.co.jp/rss/topics/top-picks.xml",  # Yahoo!ニュース トピックス
            "https://www.asahi.com/rss/asahi/newsheadlines.rdf",  # 朝日新聞
            "https://mainichi.jp/rss/etc/mainichi-newsheadlines.rss",  # 毎日新聞
            "http://www.yomiuri.co.jp/rss/news.xml",  # 読売新聞
            "https://feeds.sankei.com/news/main/world",  # 産経新聞
            "https://www.nikkei.com/news/category/?bn=0103&uah=DF_CATEGORY_NEWEST",  # 日経(政治)
            "https://toyokeizai.net/list/feed/rss",  # 東洋経済オンライン
            "https://diamond.jp/list/feed/rss"  # ダイヤモンド・オンライン
        ]
        
        # Brave API queries for comprehensive coverage
        self.brave_queries = [
            "breaking news today politics economy",
            "technology AI fintech news",
            "financial markets economy news",
            "Japan business politics news"
        ]
    
    async def fetch_rss_news(self, limit: int = 6) -> List[Dict]:
        """Fetch news from both English and Japanese RSS feeds"""
        all_articles = []
        english_limit = int(limit * 0.7)  # 70% English sources
        japanese_limit = limit - english_limit  # 30% Japanese sources
        
        # Fetch English articles (to be translated)
        english_articles = await self._fetch_from_feeds(self.english_rss_feeds, english_limit, "en")
        japanese_articles = await self._fetch_from_feeds(self.japanese_rss_feeds, japanese_limit, "ja")
        
        all_articles.extend(english_articles)
        all_articles.extend(japanese_articles)
        
        return all_articles[:limit]
    
    async def _fetch_from_feeds(self, feeds: List[str], limit: int, language: str) -> List[Dict]:
        """Helper method to fetch articles from a list of RSS feeds"""
        articles = []
        articles_per_feed = max(1, limit // len(feeds))
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                feed_articles = 0
                
                for entry in feed.entries:
                    if feed_articles >= articles_per_feed:
                        break
                        
                    # Clean description and handle HTML
                    description = entry.get("description", "")
                    if description:
                        # Remove HTML tags and clean text
                        description = re.sub(r'<[^>]+>', '', description)
                        description = re.sub(r'\s+', ' ', description).strip()
                        description = description[:400]  # Limit length
                    
                    article = {
                        "title": entry.get("title", ""),
                        "description": description,
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.get("title", "Unknown"),
                        "source_type": "rss",
                        "language": language,
                        "thumbnail": ""
                    }
                    articles.append(article)
                    feed_articles += 1
                    
                    if len(articles) >= limit:
                        break
                        
            except Exception as e:
                print(f"Error fetching RSS from {feed_url}: {e}")
                continue
                
            if len(articles) >= limit:
                break
        
        return articles
    
    async def fetch_brave_news(self, limit: int = 4) -> List[Dict]:
        """Fetch trending/breaking news from Brave API"""
        if not self.brave_api_key:
            print("Warning: BRAVE_API_KEY not set, skipping Brave API news")
            return []
        
        all_articles = []
        
        async with aiohttp.ClientSession() as session:
            for query in self.brave_queries:
                try:
                    headers = {
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                        "X-Subscription-Token": self.brave_api_key
                    }
                    
                    params = {
                        "q": query,
                        "count": limit // len(self.brave_queries),
                        "freshness": "pd",  # Past day
                        "text_decorations": False,
                        "search_lang": "en",
                        "country": "US"
                    }
                    
                    async with session.get(self.brave_base_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get("results", [])
                            
                            for article in articles:
                                formatted_article = {
                                    "title": article.get("title", ""),
                                    "description": article.get("description", ""),
                                    "link": article.get("url", ""),
                                    "published": article.get("age", ""),
                                    "source": article.get("profile", {}).get("name", "Unknown"),
                                    "source_type": "brave_api",
                                    "language": "en",  # Brave API returns English results
                                    "thumbnail": article.get("thumbnail", {}).get("src", "")
                                }
                                all_articles.append(formatted_article)
                        else:
                            print(f"Brave API error for query '{query}': {response.status}")
                
                except Exception as e:
                    print(f"Error fetching from Brave API for query '{query}': {e}")
                    continue
        
        return all_articles[:limit]
    
    async def fetch_news(self, limit: int = 10) -> List[Dict]:
        """Fetch news from both RSS and Brave API sources"""
        rss_limit = int(limit * 0.6)  # 60% from RSS (more reliable)
        brave_limit = limit - rss_limit  # 40% from Brave API (breaking news)
        
        # Fetch from both sources concurrently
        rss_task = self.fetch_rss_news(rss_limit)
        brave_task = self.fetch_brave_news(brave_limit)
        
        rss_articles, brave_articles = await asyncio.gather(rss_task, brave_task)
        
        # Combine and deduplicate articles
        all_articles = []
        seen_titles = set()
        
        # Add RSS articles first (more reliable)
        for article in rss_articles:
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                all_articles.append(article)
        
        # Add Brave API articles (skip duplicates)
        for article in brave_articles:
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                all_articles.append(article)
        
        return all_articles[:limit]