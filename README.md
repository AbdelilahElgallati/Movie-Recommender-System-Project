# MovieRec - Hybrid Movie Recommendation System

**MovieRec** is a full-stack web application (Flask + React) that provides personalized movie recommendations. The core of the project is an **adaptive hybrid recommendation engine** combining **collaborative filtering**, **content-based filtering**, and **popularity models** to dynamically tailor suggestions for each user.

## 🚀 Key Features

* **Adaptive Hybrid Engine (Switching):** Automatically selects the optimal recommendation strategy based on how many ratings a user has (cold start, moderate, or active users).
* **User Authentication:** Full account creation and login system to manage user profiles (stored in `users.json`).
* **Movie Rating System:** Users can rate movies from 1 to 5 stars; ratings are saved persistently (`u.data`).
* **Exploration & Discovery:**

  * Search movies by title.
  * Filter by genre.
  * Paginated movie browsing.
* **Detailed Movie Pages:** Show synopsis, poster, cast, IMDb rating, and **similar movies** (content-based).
* **User Profile Page:** Logged-in users can view personalized recommendations and see which hybrid strategy was applied.

## 🧠 How It Works: The Hybrid Engine

The system uses a **“switching” strategy** (defined in `my_recommender/models/hybrid.py`) to decide which recommendation method to apply:

1. **New User (0 ratings) — *Cold Start***

   * **Strategy:** 100% **Popularity Model**
   * **Logic:** Displays top-rated and most popular movies to engage the new user.

2. **Beginner User (1–10 ratings)**

   * **Strategy:** 70% **Content-Based** + 30% **Popularity**
   * **Logic:** Analyzes genres/tags of liked movies to find similar ones; popularity ensures relevance.

3. **Moderate User (11–30 ratings)**

   * **Strategy:** 60% **Collaborative Filtering** + 30% **Content-Based** + 10% **Popularity**
   * **Logic:** Begins leveraging patterns from similar users while maintaining content and popularity balance.

4. **Active User (31+ ratings)**

   * **Strategy:** 80% **Collaborative Filtering** + 20% **Content-Based**
   * **Logic:** Relies mostly on collaborative filtering, which performs best with rich rating history. Content adds diversity and serendipity.

## 🛠️ Tech Stack

* **Backend:**

  * **Framework:** Flask
  * **ML Models:** Pandas, NumPy, Scikit-learn (TF-IDF, Cosine Similarity), NLTK (stemming)
  * **Server:** Gunicorn (for production), Flask-CORS
* **Frontend:**

  * **Library:** React
  * **Language:** TypeScript
  * **Styling:** Tailwind CSS
  * **Icons:** Lucide React
* **Data:**

  * **Base Dataset:** MovieLens 100k (`u.data`, `u.item`, `u.user`)
  * **Enriched Data:** TMDB API (`scripts/fetch_movie_data.py`)
  * **User Storage:** `users.json`
  * **Models:** Serialized `.pkl` files (Pickle)

## 📁 Simplified Project Structure

```
/
├── Dataset/
│   ├── u.data
│   ├── u.item
│   ├── u.user
│   └── movies_enriched.csv
│
├── models/
│   ├── cf_model.pkl
│   ├── content_model.pkl
│   ├── hybrid_system.pkl
│   └── popularity_model.pkl
│
├── my_recommender/
│   ├── api/
│   ├── models/
│   ├── utils/
│   └── __init__.py
│
├── scripts/
│   └── fetch_movie_data.py
│
├── src/
│   ├── components/
│   └── App.tsx
│
├── Complete_Hybrid_Recommender_System.ipynb
├── config.py
├── requirements.txt
├── run.py
└── users.json
```

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### Prerequisites

* Python (3.9+ recommended)
* Node.js and npm (for React frontend)
* TMDB API key

### 1. Backend Setup (Flask)

1. **Clone the repository:**

   ```bash
   git clone [PROJECT_URL]
   cd [PROJECT_NAME]
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows

   pip install -r requirements.txt
   ```

3. **Configure your API key:**

   * Open `config.py`.
   * Replace `TMDB_API_KEY` with your own TMDB API key.

4. **Prepare Data and Models:**

   * **Step A:** Download the **MovieLens 100k** dataset (`ml-100k.zip`).
     Extract and place `u.data`, `u.item`, and `u.user` into the `Dataset/` folder.
   * **Step B:** Enrich data with TMDB posters and summaries:

     ```bash
     python scripts/fetch_movie_data.py
     ```

     This will generate `Dataset/movies_enriched.csv`.
   * **Step C:** Open and execute `Complete_Hybrid_Recommender_System.ipynb` to train and save models (`.pkl` files) in the `models/` folder.

5. **Run the Flask server:**

   ```bash
   python run.py
   ```

   The backend will be available at **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

### 2. Frontend Setup (React)

> *Note: Standard setup for a Vite-based React project.*

1. Open a new terminal and navigate to the project root (where `src/` is located).
2. Install Node dependencies:

   ```bash
   npm install
   ```
3. Start the development server:

   ```bash
   npm run dev
   ```

   React will run at **[http://localhost:5173](http://localhost:5173)**

Then open `http://localhost:5173` in your browser to use the app.

## 🌐 API Endpoints Overview

* `POST /api/login` — Log in a user.
* `POST /api/signup` — Create a new user account.
* `GET /api/movies` — Retrieve movie list (search, filter, pagination).
* `GET /api/movie/<id>` — Get movie details.
* `POST /api/rate` — Submit a movie rating.
* `POST /api/recommend` — Get hybrid recommendations for a given `user_id`.
* `GET /api/similar/<title>` — Fetch content-based similar movies.
* `GET /api/recommend/genre/<genre>` — Get popular movies by genre.
