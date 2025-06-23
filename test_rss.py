#!/usr/bin/env python3
"""
Quick test script to verify RSS feeds are working
"""
import asyncio
import sys
import os
sys.path.append('backend')

from backend.news_fetcher import NewsFetcher

async def test_rss_only():
    print("🧪 Testing RSS feeds (no API keys required)...")
    
    fetcher = NewsFetcher()
    
    try:
        # Test RSS feeds only
        rss_articles = await fetcher.fetch_rss_news(limit=5)
        
        print(f"\n✅ Successfully fetched {len(rss_articles)} RSS articles")
        
        if rss_articles:
            print("\n📰 Sample articles:")
            for i, article in enumerate(rss_articles[:3], 1):
                print(f"\n{i}. 【{article['source']}】")
                print(f"   Title: {article['title'][:80]}...")
                print(f"   Language: {article['language']}")
                print(f"   Source Type: {article['source_type']}")
        
        # Test language distribution
        english_count = len([a for a in rss_articles if a['language'] == 'en'])
        japanese_count = len([a for a in rss_articles if a['language'] == 'ja'])
        
        print(f"\n📊 Language distribution:")
        print(f"   English articles: {english_count}")
        print(f"   Japanese articles: {japanese_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RSS: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rss_only())
    if success:
        print("\n🎉 RSS test completed successfully!")
        print("💡 Next step: Add your API keys to .env file to test full pipeline")
    else:
        print("\n💥 RSS test failed. Check your internet connection.")