import streamlit as st
import pickle
import pandas as pd
import requests

# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    body {
        background-color: #121212;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main > div {
        padding-top: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .stSelectbox > div > div > div {
        background-color: #1c2526;
        border-radius: 12px;
        border: 1px solid #2c3e50;
        color: #e0e0e0;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div > div:hover {
        border-color: #1e90ff;
        box-shadow: 0 0 8px rgba(30, 144, 255, 0.3);
    }

    .movie-card {
        background: linear-gradient(145deg, #1c2526, #2c3e50);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.6rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        text-align: center;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
        border: 1px solid #2c3e50;
        overflow: hidden;
    }

    .movie-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 14px 40px rgba(30, 144, 255, 0.3);
        border-color: #1e90ff;
    }

    .movie-title {
        font-size: 1rem;
        font-weight: 600;
        color: #f5f5f5;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
        text-align: center;
        line-height: 1.3;
        min-height: 2.6rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-section {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #1e90ff 0%, #ff4b1f 100%);
        border-radius: 24px;
        margin-bottom: 2.5rem;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
        z-index: 0;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        position: relative;
        z-index: 1;
    }

    .hero-subtitle {
        font-size: 1.4rem;
        opacity: 0.95;
        margin-bottom: 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }

    .recommendation-header {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #f5f5f5;
        margin: 2.5rem 0 1.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
    }

    .selected-movie {
        background: linear-gradient(90deg, #1e90ff, #00b7eb);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1.2rem 0;
        font-weight: 600;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(30, 144, 255, 0.3);
    }

    .stButton > button {
        background: linear-gradient(45deg, #ff4b1f, #ff9068);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.8rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.4s ease;
        box-shadow: 0 6px 20px rgba(255, 75, 31, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 75, 31, 0.5);
        background: linear-gradient(45deg, #ff9068, #ff4b1f);
    }

    .loading-text {
        text-align: center;
        font-size: 1.3rem;
        color: #00b7eb;
        font-weight: 600;
        margin: 2.5rem 0;
    }

    .footer {
        text-align: center;
        color: #b0bec5;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1.5rem 0;
        background: #1c2526;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        movies = pickle.load(open('../model/movie_list.pkl', 'rb'))
        similarity = pickle.load(open('../model/similarity.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError:
        st.error("Model files not found. Please ensure movie_list.pkl and similarity.pkl are in the correct directory.")
        st.stop()

movies, similarity = load_data()
movies_list = movies['title'].values

@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750/2a2a2a/ffffff?text=No+Poster+Available"
    except Exception as e:
        return "https://via.placeholder.com/500x750/2a2a2a/ffffff?text=Error+Loading+Poster"

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:  
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎬 Movie Recommender</div>
    <div class="hero-subtitle">Discover your next cinematic adventure</div>
</div>
""", unsafe_allow_html=True)

# Main content in columns for better layout
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.markdown("### 🔍 Select Your Movie")
    
    selected_movie = st.selectbox(
        'Type or select a movie to get personalized recommendations:',
        movies_list,
        index=0,
        help="Start typing to search for movies in our database"
    )
    
    if selected_movie:
        st.markdown(f"""
        <div class="selected-movie">
            🎭 Selected Movie: {selected_movie}
        </div>
        """, unsafe_allow_html=True)
    
    get_recommendations = st.button('🚀 Get Recommendations', type="primary")

# Recommendations section
if get_recommendations and selected_movie:
    with st.spinner('🎬 Finding perfect recommendations for you...'):
        names, posters = recommend(selected_movie)
    
    if names and posters:
        st.markdown('<div class="recommendation-header">🌟 Recommended Movies for You</div>', 
                   unsafe_allow_html=True)
        
        cols = st.columns(5, gap="medium")
        
        for i, (name, poster, col) in enumerate(zip(names, posters, cols)):
            with col:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" style="width: 100%; height: 320px; object-fit: cover; border-radius: 12px; margin-bottom: 12px;">
                    <div class="movie-title">{name}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem; background-color: #1c2526; border-radius: 12px; margin: 2rem 0;">
            <h3 style="color: #ff4b1f;">😔 No recommendations available</h3>
            <p style="color: #e0e0e0;">Try selecting a different movie from our database.</p>
        </div>
        """, unsafe_allow_html=True)

elif get_recommendations and not selected_movie:
    st.warning("⚠️ Please select a movie first to get recommendations!")

# Footer
st.markdown("""
<div class="footer">
    🎬 Powered by Machine Learning & TMDB API<br>
    Made with Abdelilah Elgallati
</div>
""", unsafe_allow_html=True)