# 🧠 Pulse — AI News Aggregation & Broadcasting Dashboard

> Aggregates AI news from 20+ sources, deduplicates with Groq LLM, displays in a clean dashboard, and lets you broadcast stories via Email, LinkedIn, WhatsApp, Blog, and Newsletter.

---

## 🏗️ Architecture

```
[20+ RSS / APIs / HN / arXiv]
          ↓
   [Fetcher Workers]          runs every 15 min (configurable)
          ↓
 [Normaliser & Deduplicator]  hash → Jaccard → Groq semantic check
          ↓
    [PostgreSQL DB]           sources / news_items / favorites / broadcast_logs
          ↓
   [FastAPI Backend]          REST API — /api/news, /favorites, /broadcast, /sources
          ↓
  [React Frontend]            Feed tab · Favorites tab · Sources admin
          ↓
 [Groq-Powered Broadcast]     Email (SMTP) · LinkedIn · WhatsApp · Blog · Newsletter
```

---

## ⚡ Quick Start (Docker)

### 1. Clone & configure

```bash
git clone <repo>
cd ai-news-dashboard
cp .env.example .env
```

Edit `.env` — the only **required** value is your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here   # https://console.groq.com
```

### 2. Start everything

```bash
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| Backend  | http://localhost:8000      |
| API docs | http://localhost:8000/docs |

On first boot the backend seeds all 20 sources and kicks off ingestion automatically.

---

## 🔧 Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start a local Postgres then:
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ainews
export GROQ_API_KEY=your_key_here

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

---

## 📁 Project Structure

```
ai-news-dashboard/
├── backend/
│   ├── main.py                     # FastAPI app entry
│   ├── config.py                   # All settings via .env (no hardcoding)
│   ├── database.py                 # Async SQLAlchemy engine + session
│   ├── models.py                   # ORM models (5 tables)
│   ├── schemas.py                  # Pydantic v2 request/response models
│   ├── groq_service.py             # Groq LLM: summarise, caption, score, dedup
│   ├── ingestion/
│   │   ├── sources_registry.py     # All 20 sources in one place
│   │   ├── fetcher.py              # RSS, HN API, arXiv fetchers
│   │   ├── deduplicator.py         # Hash → Jaccard → Groq dedup pipeline
│   │   └── scheduler.py           # Async ingestion scheduler
│   └── routers/
│       ├── news.py                 # GET /news, POST /news/refresh
│       ├── favorites.py            # Favorites CRUD
│       ├── broadcast.py            # Multi-platform broadcast
│       └── sources.py              # Sources management
│
├── frontend/
│   └── src/
│       ├── App.jsx                 # Route definitions
│       ├── components/
│       │   ├── Layout.jsx          # Sidebar + navigation
│       │   ├── NewsCard.jsx        # Story card with favorite + broadcast
│       │   ├── SearchBar.jsx       # Search, sort, category filter
│       │   └── BroadcastModal.jsx  # Platform picker + AI content preview
│       ├── pages/
│       │   ├── FeedPage.jsx        # Main news feed
│       │   ├── FavoritesPage.jsx   # Saved stories + broadcast actions
│       │   └── SourcesPage.jsx     # Toggle source active/inactive
│       ├── hooks/
│       │   ├── useNews.js          # News fetch, pagination, favorites toggle
│       │   └── useFavorites.js     # Favorites state
│       └── utils/api.js            # Axios API client
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤖 Groq AI Features

All AI features use the Groq API (configurable model, default `llama3-8b-8192`):

| Feature | Where used |
|---------|------------|
| **Article summarisation** | Every ingested story gets a plain-English 2–3 sentence summary |
| **Impact scoring** | Each story scored 1–10 for significance |
| **Semantic deduplication** | Borderline near-duplicate titles confirmed via LLM |
| **LinkedIn caption** | Full post generated when broadcasting to LinkedIn |
| **Newsletter blurb** | Snappy 1–2 sentence blurb for newsletter broadcasts |
| **Email body** | HTML email body enriched with Groq-written content |

If `GROQ_API_KEY` is not set, AI features are silently skipped — ingestion still works.

---

## 📡 News Sources (20+)

| Category | Sources |
|----------|---------|
| Labs | OpenAI, Google AI, Meta AI, Anthropic, DeepMind, Microsoft AI, Stability AI |
| Media | TechCrunch AI, VentureBeat AI, The Verge, Wired AI, MIT Tech Review |
| Research | arXiv cs.AI, arXiv cs.LG, PapersWithCode |
| Community | Hacker News (AI filter), Reddit r/MachineLearning, Hugging Face Blog |
| VC / Products | Y Combinator Blog, Product Hunt AI |

---

## 📣 Broadcast Platforms

| Platform | Behaviour |
|----------|-----------|
| **Email** | Real send via SMTP if credentials set; simulated otherwise |
| **LinkedIn** | Groq-written post generated; copy-paste or connect OAuth token |
| **WhatsApp** | Message text generated; connect Twilio/WhatsApp Business API |
| **Blog** | Markdown snippet generated for CMS import |
| **Newsletter** | Blurb generated for Mailchimp/Substack |

All broadcasts are logged to the `broadcast_logs` table.

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `sources` | Registered news sources |
| `news_items` | Normalised stories with dedup flag, AI summary, impact score |
| `favorites` | User-saved stories |
| `broadcast_logs` | Full audit log of every broadcast action |
| `users` | Optional multi-user support |

---

## 🚀 Deployment

### Render / Fly.io

1. Push to GitHub
2. Create a Postgres instance (Render managed DB or Fly Postgres)
3. Set `DATABASE_URL` and `GROQ_API_KEY` as environment variables
4. Deploy backend as a web service (`uvicorn main:app --host 0.0.0.0 --port 8000`)
5. Deploy frontend as a static site (`npm run build`, serve `dist/`)

### AWS ECS

Use the provided `Dockerfile` files. Push images to ECR, run via ECS Fargate with an RDS Postgres instance.

---

## 📝 Notes

- No hardcoded secrets anywhere — everything is driven by `.env`
- AI responses are written to read naturally, with no "as an AI" traces
- Broadcast simulation mode lets you demo all features without external API keys
- Sources can be toggled on/off from the Sources admin panel without restarting
