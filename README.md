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

### 🐳 Docker (Local/Cloud)
```bash
# 1. Copy production environment template
cp .env.production .env.local

# 2. Fill in your actual credentials in .env.local
# - Groq API Key
# - Database URL
# - Email/LinkedIn/WhatsApp credentials

# 3. Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8001
# Health Check: http://localhost:80/api/health
```

### 🚂 Railway (Recommended)
**Quick Setup**: Use the provided Railway configuration files
- `railway.toml` - Railway service configuration
- `docker-compose.railway.yml` - Railway Docker setup
- `.env.railway` - Environment variables template

**Steps**:
1. Connect repository to [Railway](https://railway.app)
2. Add PostgreSQL service
3. Set environment variables from `.env.railway`
4. Deploy automatically

**Environment Variables Required**:
- `DATABASE_URL` - PostgreSQL connection string (Railway provides)
- `GROQ_API_KEY` - Groq API key
- `VITE_API_URL` - Frontend API URL (auto-configured)

**Service URLs**:
- Frontend: `https://your-app-name.railway.app`
- Backend: `https://your-backend-name.railway.app`

📖 **Full Guide**: See `RAILWAY_DEPLOYMENT.md` for detailed instructions

### ⚡ Vercel (Serverless)
**Frontend**: Static site deployment
- `vercel.json` - Frontend configuration
- Build: `npm run build` → Deploy `dist/`

**Backend**: Serverless API functions  
- `vercel-backend.json` - Backend configuration
- `backend/api/index.py` - Vercel handler

**Limitations**: 
- Database connections not recommended for serverless
- Better for low-traffic, bursty workloads

### ☁️ AWS ECS
Use the provided `Dockerfile` files for production:
- Push images to Amazon ECR
- Deploy with ECS Fargate
- Use RDS PostgreSQL for database

**Configuration**: See `DEPLOYMENT.md` for complete AWS setup



---


## 📝 Notes



- No hardcoded secrets anywhere — everything is driven by `.env`

- AI responses are written to read naturally, with no "as an AI" traces

- Broadcast simulation mode lets you demo all features without external API keys

- Sources can be toggled on/off from the Sources admin panel without restarting

