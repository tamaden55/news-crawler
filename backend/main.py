from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from news_fetcher import NewsFetcher
from summarizer import Summarizer
from tts import TTSService
import uvicorn
import asyncio

app = FastAPI(title="News Voice API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/audio", StaticFiles(directory="static/audio"), name="audio")

news_fetcher = NewsFetcher()
summarizer = Summarizer()
tts_service = TTSService()

@app.get("/")
async def root():
    return {"message": "News Voice API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/news")
async def get_news(limit: int = 10, skip_audio: bool = False):
    try:
        articles = await news_fetcher.fetch_news(limit=limit)
        
        processed_articles = []
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            try:
                # Always generate summary
                summary = await summarizer.summarize_article(article)
                article["summary"] = summary if summary else article["description"]
                
                # Generate audio unless skipped
                if not skip_audio and summary:
                    audio_filename = await tts_service.text_to_speech(summary)
                    if audio_filename:
                        article["audioUrl"] = tts_service.get_audio_url(audio_filename)
                
                processed_articles.append(article)
                
            except Exception as e:
                print(f"Error processing article '{article['title']}': {e}")
                # Add article without processing if there's an error
                article["summary"] = article.get("description", "")[:300]
                processed_articles.append(article)
        
        return {
            "articles": processed_articles,
            "total": len(processed_articles),
            "rss_count": len([a for a in processed_articles if a.get("source_type") == "rss"]),
            "api_count": len([a for a in processed_articles if a.get("source_type") == "brave_api"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/news/test")
async def test_news_sources():
    """Test endpoint to check news sources without processing"""
    try:
        rss_articles = await news_fetcher.fetch_rss_news(limit=5)
        brave_articles = await news_fetcher.fetch_brave_news(limit=3)
        
        return {
            "rss_articles": len(rss_articles),
            "brave_articles": len(brave_articles),
            "rss_sources": list(set([a["source"] for a in rss_articles])),
            "brave_sources": list(set([a["source"] for a in brave_articles])),
            "sample_rss": rss_articles[:2] if rss_articles else [],
            "sample_brave": brave_articles[:2] if brave_articles else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing sources: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)