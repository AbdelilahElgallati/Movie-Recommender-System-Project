# MovieRec - Hybrid Movie Recommendation System

MovieRec is a full-stack web application (Flask + React) for personalized movie recommendations using an adaptive hybrid engine combining collaborative filtering, content-based filtering, and popularity models.

## Key Features

- **Adaptive Hybrid Engine:** Switches strategies based on user ratings (cold start, moderate, or active users).
- **User Authentication:** Account creation and login (stored in MongoDB).
- **Movie Rating System:** Rate movies 1-5 stars; saved in MongoDB.
- **Exploration:** Search by title, filter by genre, paginated browsing.
- **Movie Pages:** Synopsis, poster, cast, IMDb rating, similar movies (content-based).
- **User Profile:** Personalized recommendations with applied strategy.

## How It Works: Hybrid Engine

Switching strategy in `my_recommender/models/hybrid.py`:

1. **0 Ratings (Cold Start):** 100% Popularity (top-rated/popular movies).
2. **1–10 Ratings:** 70% Content-Based + 30% Popularity (similar to liked movies + relevance).
3. **11–30 Ratings:** 60% Collaborative + 30% Content-Based + 10% Popularity (user patterns + balance).
4. **31+ Ratings:** 80% Collaborative + 20% Content-Based (rich history + diversity).

## Tech Stack

- **Backend:** Flask, MongoDB (PyMongo), Pandas/NumPy/Scikit-learn/NLTK, Gunicorn, Flask-CORS.
- **Frontend:** React (TypeScript), Tailwind CSS, Lucide React.
- **Data:** MovieLens 100k (enriched via TMDB API), MongoDB (users/movies/ratings), Serialized models (.pkl).

## Project Structure

```
/
├── Dataset/              # u.data, u.item, u.user, movies_enriched.csv
├── models/               # cf_model.pkl, content_model.pkl, hybrid_system.pkl, popularity_model.pkl
├── my_recommender/       # API, database, models, utils
├── movie_recommender/    # React frontend (src/components, App.tsx, package.json)
├── scripts/              # fetch_movie_data.py, migrate_to_mongodb.py, train_models.py
├── Complete_Hybrid_Recommender_System.ipynb
├── config.py
├── requirements.txt
└── run.py
```

## Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js/npm
- MongoDB (running)
- TMDB API key

### Backend (Flask)

1. Clone repo: `git clone https://github.com/AbdelilahElgallati/Movie-Recommender-System-Project`.
2. Virtual env: `python -m venv venv`, activate, `pip install -r requirements.txt`.
3. Set TMDB_API_KEY in `config.py`.
4. Prepare data:
   - Download MovieLens 100k; place files in `Dataset/`.
   - Enrich: `python scripts/fetch_movie_data.py` (creates movies_enriched.csv).
   - Train models: Run `Complete_Hybrid_Recommender_System.ipynb`.
   - Migrate: `python scripts/migrate_to_mongodb.py`.
5. Run: `python run.py` (at http://127.0.0.1:5001).

### Frontend (React)
1. cd `cd movie_recommender`
2. In project root: `npm install`.
3. Run: `npm run dev` (at http://localhost:5173).

## API Endpoints

- `POST /api/login`: Log in.
- `POST /api/signup`: Create account.
- `GET /api/movies`: Movie list (search/filter/paginate).
- `GET /api/movie/<id>`: Movie details.
- `POST /api/rate`: Submit rating.
- `GET /api/user/<user_id>/ratings`: User ratings.
- `POST /api/recommend`: Hybrid recommendations.
- `GET /api/similar/<title>`: Similar movies.
- `GET /api/recommend/genre/<genre>`: Popular by genre.

## Database (MongoDB)

Collections: `users`, `movies`, `ratings`.

Features: Indexed queries, ACID transactions, scalable.

Migration: `python scripts/migrate_to_mongodb.py`.

## Documentation

- `PREPARATION_INTERVIEW.txt`: Interview guide.
- `PROJECT_STRUCTURE.md`: Structure overview.
- `MONGODB_SETUP.md`: MongoDB setup.

## Configuration

In `config.py` or env vars:

```python
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'movie_recommender'
```

Or set `MONGODB_URI`.