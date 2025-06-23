import { useState, useEffect } from 'react';
import Head from 'next/head';

interface Article {
  title: string;
  description: string;
  link: string;
  published: string;
  source: string;
  source_type: string;
  language: string;
  summary?: string;
  audioUrl?: string;
  thumbnail?: string;
}

interface NewsResponse {
  articles: Article[];
  total: number;
  rss_count: number;
  api_count: number;
}

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPlaying, setCurrentPlaying] = useState<string | null>(null);
  const [stats, setStats] = useState<{total: number, rss_count: number, api_count: number} | null>(null);

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js');
    }
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const response = await fetch('/api/news?limit=10');
      const data: NewsResponse = await response.json();
      setArticles(data.articles || data as any); // Handle both old and new format
      if ('total' in data) {
        setStats({
          total: data.total,
          rss_count: data.rss_count,
          api_count: data.api_count
        });
      }
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  };

  const playAudio = (audioUrl: string, articleId: string) => {
    if (currentPlaying) {
      const currentAudio = document.getElementById(currentPlaying) as HTMLAudioElement;
      currentAudio?.pause();
    }
    
    const audio = document.getElementById(articleId) as HTMLAudioElement;
    if (audio) {
      audio.play();
      setCurrentPlaying(articleId);
    }
  };

  return (
    <>
      <Head>
        <title>VoiceNews - ニュース音声アプリ</title>
        <meta name="description" content="ニュース記事を音声で聞けるPWAアプリ" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#1976d2" />
      </Head>

      <main style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', color: '#1976d2' }}>📻 VoiceNews</h1>
        
        {stats && (
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '20px', 
            padding: '10px', 
            backgroundColor: '#f0f0f0', 
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            記事総数: {stats.total} | RSS: {stats.rss_count} | API: {stats.api_count}
          </div>
        )}
        
        {loading ? (
          <div style={{ textAlign: 'center' }}>読み込み中...</div>
        ) : (
          <div>
            {articles.map((article, index) => (
              <div key={index} style={{ 
                border: '1px solid #ddd', 
                borderRadius: '8px', 
                padding: '16px', 
                margin: '16px 0',
                backgroundColor: '#f9f9f9'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                  <h3 style={{ color: '#333', margin: '0', flex: 1 }}>{article.title}</h3>
                  {article.thumbnail && (
                    <img 
                      src={article.thumbnail} 
                      alt="" 
                      style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '4px', marginLeft: '12px' }}
                    />
                  )}
                </div>
                
                <div style={{ display: 'flex', gap: '12px', marginBottom: '8px', fontSize: '12px', color: '#888' }}>
                  <span>📰 {article.source}</span>
                  <span>
                    {article.source_type === 'rss' ? '📡 RSS' : '🔍 API'}
                  </span>
                  <span>
                    {article.language === 'en' ? '🇺🇸 EN→JP' : '🇯🇵 JP'}
                  </span>
                  <span>{article.published}</span>
                </div>
                
                <p style={{ lineHeight: '1.6', color: '#333' }}>
                  {article.summary || article.description}
                </p>
                
                {article.audioUrl && (
                  <div style={{ marginTop: '12px' }}>
                    <audio 
                      id={`audio-${index}`}
                      controls 
                      preload="metadata"
                      onEnded={() => setCurrentPlaying(null)}
                      style={{ width: '100%' }}
                    >
                      <source src={article.audioUrl} type="audio/mpeg" />
                    </audio>
                  </div>
                )}
                
                <div style={{ marginTop: '12px' }}>
                  <a 
                    href={article.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ 
                      color: '#1976d2', 
                      textDecoration: 'none', 
                      fontSize: '14px',
                      padding: '6px 12px',
                      border: '1px solid #1976d2',
                      borderRadius: '4px',
                      display: 'inline-block'
                    }}
                  >
                    元記事を読む →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}