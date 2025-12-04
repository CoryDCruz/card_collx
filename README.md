# Card Collection Tracker

A web application for tracking and managing your sports card collection. Scan cards using your phone camera, catalog them, and use AI agents to discover average market prices.

## Features

- Scan cards using your iPhone camera
- Catalog and organize your collection
- AI-powered price discovery
- Mobile-first responsive design
- Progressive Web App (PWA) support (coming soon)

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **SQLite** - Database (can be upgraded to PostgreSQL)

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

5. Run the development server:
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

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/cards` - Get all cards
- `POST /api/cards` - Create a card manually
- `POST /api/cards/scan` - Scan a card image
- `GET /api/cards/{id}` - Get a specific card
- `GET /api/cards/{id}/price` - Get price information for a card

## Roadmap

- [ ] Implement database models and migrations
- [ ] Add image recognition for card scanning
- [ ] Build AI agent for price discovery
- [ ] Add user authentication
- [ ] Implement PWA features for offline support
- [ ] Add card search and filtering
- [ ] Implement price history tracking
- [ ] Add export functionality (CSV, PDF)

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT
