import openai
from typing import Dict
import os

class Summarizer:
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            self.client = openai.OpenAI(api_key=openai_key)
            self.use_ai = True
        else:
            self.client = None
            self.use_ai = False
            print("⚠️  OpenAI API key not set - using simple text processing instead")
    
    async def summarize_article(self, article: Dict) -> str:
        """Summarize article with translation if needed"""
        try:
            if not self.use_ai:
                return await self._simple_processing(article)
            
            language = article.get('language', 'en')
            
            if language == 'en':
                # English article - translate and summarize
                return await self._translate_and_summarize_english(article)
            else:
                # Japanese article - summarize only
                return await self._summarize_japanese(article)
        
        except Exception as e:
            print(f"Error processing article: {e}")
            return article['description'][:400] + "..."
    
    async def _simple_processing(self, article: Dict) -> str:
        """Free fallback - basic text processing without AI"""
        language = article.get('language', 'en')
        title = article['title']
        description = article['description']
        source = article['source']
        
        if language == 'en':
            # Simple English summary (no translation)
            summary = f"【{source}】{title}"
            if description:
                summary += f" - {description[:200]}..."
            return summary
        else:
            # Japanese article - simple truncation
            summary = f"【{source}】{title}"
            if description:
                summary += f" - {description[:300]}..."
            return summary
    
    async def _translate_and_summarize_english(self, article: Dict) -> str:
        """Translate English article to Japanese and summarize"""
        try:
            prompt = f"""
            以下の英語ニュース記事を日本語に翻訳し、300-500文字で要約してください。
            
            要件:
            1. 自然で読みやすい日本語に翻訳
            2. 重要なポイントを簡潔にまとめる
            3. 音声で聞いても理解しやすい文章構成
            4. 日本経済新聞の読者層に適した内容
            5. 固有名詞や専門用語は適切に日本語化
            
            タイトル: {article['title']}
            記事内容: {article['description']}
            情報源: {article['source']}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error translating and summarizing English article: {e}")
            return f"【{article['source']}】{article['title']} - 詳細は元記事をご確認ください。"
    
    async def _summarize_japanese(self, article: Dict) -> str:
        """Summarize Japanese article"""
        try:
            prompt = f"""
            以下の日本語ニュース記事を300-500文字で要約してください。
            
            要件:
            1. 重要なポイントを簡潔にまとめる
            2. 音声で聞いても理解しやすい自然な日本語
            3. 日本経済新聞の読者層に適した内容
            4. 政治・経済・技術分野の専門用語は適切に説明
            
            タイトル: {article['title']}
            記事内容: {article['description']}
            情報源: {article['source']}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error summarizing Japanese article: {e}")
            return f"【{article['source']}】{article['title']} - {article['description'][:300]}..."