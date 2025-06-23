# 📻 VoiceNews - ニュース音声アプリ

国内外のニュース記事を自動要約・音声化し、PWA形式で提供するアプリケーションです。

## 🚀 機能

- **ニュース自動収集**: RSS フィードから主要メディアの記事を取得
- **AI要約**: OpenAI GPT を使用して記事を300-500文字で要約
- **音声合成**: 要約テキストを日本語音声（MP3）に変換
- **PWA対応**: オフライン再生、ホーム画面追加が可能
- **レスポンシブデザイン**: PC・スマートフォンに対応

## 📁 プロジェクト構成

```
news-crawler/
├── backend/              # FastAPI バックエンド
│   ├── main.py           # API エントリーポイント
│   ├── news_fetcher.py   # ニュース収集
│   ├── summarizer.py     # AI要約・翻訳
│   ├── tts.py            # 音声合成
│   └── static/audio/     # 音声ファイル保存
├── frontend/             # Next.js PWA フロントエンド
│   ├── pages/            # ページコンポーネント
│   ├── public/           # 静的ファイル・PWA設定
│   └── styles/           # スタイルシート
├── requirements.txt      # Python 依存関係
└── .env.example          # 環境変数テンプレート
```

## 🛠 セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
# .env ファイルを編集して OpenAI API キーを設定
```

### 2. バックエンドの起動

```bash
# Python 依存関係をインストール
pip install -r requirements.txt

# FastAPI サーバーを起動
cd backend
python main.py
```

### 3. フロントエンドの起動

```bash
# Node.js 依存関係をインストール
cd frontend
npm install

# 開発サーバーを起動
npm run dev
```

## 🌐 アクセス

- フロントエンド: http://localhost:3000
- API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 📱 PWA インストール

1. ブラウザでアプリにアクセス
2. アドレスバーの「インストール」ボタンをクリック
3. ホーム画面にアプリアイコンが追加されます

## 🔧 技術スタック

**バックエンド**:
- FastAPI (Python)
- OpenAI GPT-3.5/4
- gTTS (Google Text-to-Speech)
- feedparser

**フロントエンド**:
- Next.js (React)
- TypeScript
- Service Worker (PWA)

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

Issue や Pull Request をお待ちしています！