# 🎬 Movie Recommender System Project

A content-based movie recommender system built with Python, Streamlit, and machine learning. This project suggests movies similar to a selected title based on genres, keywords, cast, and crew information.

## 🚀 Features

- **Interactive Web App**: User-friendly interface built with Streamlit.
- **Content-Based Recommendations**: Suggests movies similar to your favorite.
- **Data-Driven**: Utilizes TMDB 5000 movies and credits datasets.
- **Custom Styling**: Modern, visually appealing frontend.

## 🧠 How It Works

- The model processes movie metadata (genres, keywords, cast, crew) to create a feature vector for each movie.
- Cosine similarity is computed between movies.
- When a user selects a movie, the app recommends the most similar titles.