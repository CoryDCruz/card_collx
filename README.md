# Card Collection Tracker

A web application for tracking and managing your sports card collection. Scan cards using your phone camera, catalog them, and use AI agents to discover average market prices.

## Features

- ✅ Scan cards using your iPhone camera
- ✅ **AI-powered metadata extraction** via OpenAI Vision API (GPT-4o)
  - Automatically extracts: player name, year, brand, card number, set name, sport
- ✅ Image upload, processing, and storage with automatic optimization
- ✅ Catalog and organize your collection
- ✅ Mobile-first responsive design
- ✅ **Full cloud deployment** — Vercel frontend, Render backend, Supabase DB + storage
- ✅ **Card collection display** — responsive grid with images and metadata
- 🚧 eBay price research (service scaffolded, API keys pending)
- 🚧 Front/back card scanning for complete metadata (coming soon)
- 🚧 Progressive Web App (PWA) support (coming soon)

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **SQLite** - Database (can be upgraded to PostgreSQL)
- **OpenAI Vision API** - GPT-4o for automatic card metadata extraction
- **Pillow** - Image processing and optimization
- **aiofiles** - Async file I/O

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client

## Project Structure

```
card_collx/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── db/           # Database setup
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 20+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

5. **Add your OpenAI API key** to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ENABLE_VISION_EXTRACTION=true
   ```
   Get your API key from: https://platform.openai.com/api-keys

6. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## Development

### Running Both Servers

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### API Endpoints

**Operational:**
- `GET /` - API info
- `GET /health` - Health check
- `GET /api/cards` - Get all cards
- `POST /api/cards` - Create a card manually
- `POST /api/cards/scan` - Upload and scan a card image (with automatic image processing)
- `GET /api/cards/{id}` - Get a specific card
- `PUT /api/cards/{id}` - Update a card
- `DELETE /api/cards/{id}` - Delete a card (with automatic image cleanup)
- `GET /uploads/{card_id}/{filename}` - Serve uploaded card images

**Placeholder (AI integration needed):**
- `GET /api/cards/{id}/price` - Get price information for a card

## Roadmap

### ✅ Completed
- [x] Database models and migrations
- [x] Image processing and storage system
  - Cloud-ready storage abstraction layer
  - Automatic image optimization (resize, compression)
  - Static file serving
- [x] **OpenAI Vision API integration** for automatic card metadata extraction
  - Extracts player name, year, brand, card number, set name, sport
  - GPT-4o Vision with low-detail mode (~$0.004/card)
- [x] Full cloud deployment (Vercel + Render + Supabase)
- [x] Mobile camera support via iPhone
- [x] Frontend card collection display with responsive grid
- [x] eBay price research service scaffolded (awaiting API keys)

### 🚧 In Progress / Next Steps
1. **eBay Price Research** - Integrate eBay Browse API for sold listings
   - OAuth token flow and API client
   - Search sold listings by card metadata
   - Calculate average market value from recent sales

2. **Front/Back Card Scanning** - Complete metadata capture
   - Support multiple images per card
   - Scan front (player image, basic info) and back (stats, card number, serial)
   - Combine metadata from both sides for complete information

### 📋 Future Enhancements
- [ ] User authentication
- [ ] PWA features for offline support
- [ ] Card search and filtering
- [ ] Price history tracking
- [ ] Export functionality (CSV, PDF)

## Deployment

The app is fully deployed to the cloud:

- **Frontend**: https://card-collx.vercel.app (Vercel)
- **Backend**: https://card-collx.onrender.com (Render, free tier)
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase S3-compatible storage

### Local Development with ngrok (optional)

For local backend development while using the Vercel frontend, you can use ngrok to expose your local backend.

### Current Setup

- **Frontend**: https://card-collx.vercel.app (Vercel)
- **Backend**: Local with ngrok tunnel

### Starting a New Session

Each time you restart, ngrok generates a new URL. Follow these steps:

#### 1. Start Backend & ngrok

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2: Start ngrok tunnel
ngrok http 8000
```

Copy the ngrok URL from the terminal output:
```
Forwarding    https://abc123xyz.ngrok-free.app -> http://localhost:8000
```

#### 2. Update Backend CORS

Edit `backend/.env` to allow your ngrok URL:
```bash
ALLOWED_ORIGINS=["http://localhost:5173","https://YOUR-NEW-NGROK-URL.ngrok-free.app","https://card-collx.vercel.app"]
```

Restart the backend to apply changes.

#### 3. Update Vercel Environment Variable

**Via Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select your **card-collx** project
3. Navigate to **Settings** → **Environment Variables**
4. Find `VITE_API_URL`
5. Click **Edit** and update to: `https://YOUR-NEW-NGROK-URL.ngrok-free.app/api`
6. Click **Save**
7. Click **Redeploy** when prompted

**Via Vercel CLI:**
```bash
cd frontend
vercel env rm VITE_API_URL production
vercel env add VITE_API_URL production
# Enter: https://YOUR-NEW-NGROK-URL.ngrok-free.app/api
vercel --prod
```

### Avoiding ngrok URL Changes

**Option 1: ngrok Static URL** ($8/month)
- Get a permanent URL like `https://yourapp.ngrok.app`
- Never changes, no need to update Vercel

**Option 2: Deploy Backend to Cloud** (Free/Cheap)
- **Railway**: Free $5/month credit (~150 hours runtime)
- **Render**: Free tier (spins down after inactivity)
- **Fly.io**: Free tier available

Then both frontend and backend have permanent URLs.

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT
