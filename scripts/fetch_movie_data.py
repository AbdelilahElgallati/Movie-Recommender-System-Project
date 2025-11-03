# scripts/fetch_movie_data.py
import pandas as pd
import time
import os
import sys
import requests 
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

def clean_title(title):
    """Clean movie title by removing year in parentheses and stripping"""
    if isinstance(title, str):
        return title.rsplit(' (', 1)[0].strip().lower()
    return ''

def create_session_with_retries():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def search_tmdb_movie(title, year, api_key, session):
    """Search TMDB API for movie and return poster path"""
    try:
        # Use search API to find the movie
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': title,
            'year': year if pd.notna(year) else None
        }
        
        response = session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                first_result = data['results'][0]
                poster_path = first_result.get('poster_path')
                overview = first_result.get('overview', '')
                
                return poster_path, overview
        elif response.status_code == 429:
            # Rate limit hit, wait and retry
            print("  Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return search_tmdb_movie(title, year, api_key, session)
        elif response.status_code == 401:
            print("  ERROR: Invalid API key. Please check your TMDB_API_KEY in config.py")
            return None, None
            
    except requests.exceptions.Timeout:
        print(f"  Timeout for '{title}', skipping...")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"  Connection error for '{title}', waiting 30 seconds...")
        time.sleep(30)
        return None, None
    except Exception as e:
        print(f"  Error searching TMDB for '{title}': {e}")
        return None, None
    
    return None, None

def save_progress(all_movies_df, output_path):
    """Save current progress to CSV"""
    all_movies_df.to_csv(output_path, index=False)

def fetch_all_movie_data():
    print("Loading MovieLens u.item data...")
    i_cols = ['movie_id', 'movie_title', 'release date', 'video release date',
              'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation',
              "Children's", 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
              'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
              'Thriller', 'War', 'Western']
    
    # Check if enriched file already exists
    if os.path.exists(Config.ENRICHED_MOVIES_PATH):
        print(f"\nFound existing enriched data at {Config.ENRICHED_MOVIES_PATH}")
        print("Loading existing data to resume from where we left off...")
        all_movies_df = pd.read_csv(Config.ENRICHED_MOVIES_PATH)
        
        # Count what we already have
        existing_posters = all_movies_df['poster_url'].notna().sum()
        existing_real_posters = all_movies_df[
            all_movies_df['poster_url'].notna() & 
            ~all_movies_df['poster_url'].str.contains('placehold.co', na=False)
        ].shape[0]
        existing_overviews = (all_movies_df['overview'] != 'Description not available.').sum()
        
        print(f"Existing data: {existing_real_posters} real posters, {existing_overviews} descriptions")
        print("Will only fetch missing data...\n")
        
    else:
        print("No existing enriched data found. Starting fresh...\n")
        all_movies_df = pd.read_csv(
            Config.DATA_PATH, 
            sep='|', 
            names=i_cols, 
            encoding='latin-1', 
            index_col=False
        )
        
        GENRE_COLS = Config.GENRE_COLS
        all_movies_df['genres_list'] = all_movies_df.apply(
            lambda row: [col for col in GENRE_COLS if row[col] == 1], axis=1
        )

        # Extract release year from 'release date'
        all_movies_df['release_date'] = pd.to_datetime(all_movies_df['release date'], errors='coerce')
        all_movies_df['release_year'] = all_movies_df['release_date'].dt.year.astype('Int64')
        all_movies_df['clean_title'] = all_movies_df['movie_title'].apply(clean_title)

        all_movies_df['poster_url'] = None
        all_movies_df['overview'] = 'Description not available.'

        print("Loading local TMDB CSV for enrichment from 'Dataset/tmdb_5000_movies.csv'...")
        try:
            tmdb_df = pd.read_csv('Dataset/tmdb_5000_movies.csv')
            print("Available columns in TMDB data:", tmdb_df.columns.tolist())
            
            # Clean TMDB titles and extract year
            tmdb_df['clean_title'] = tmdb_df['title'].apply(clean_title)
            tmdb_df['release_date'] = pd.to_datetime(tmdb_df['release_date'], errors='coerce')
            tmdb_df['release_year'] = tmdb_df['release_date'].dt.year.astype('Int64')
            
            # Drop duplicates, keep first
            tmdb_df = tmdb_df.drop_duplicates(subset=['clean_title', 'release_year'], keep='first')
            
            csv_overview_matches = 0
            
            # First pass: Get overviews from CSV
            for idx, row in all_movies_df.iterrows():
                ml_title = row['clean_title']
                ml_year = row['release_year']
                
                # Match on clean title and year
                match = tmdb_df[(tmdb_df['clean_title'] == ml_title) & (tmdb_df['release_year'] == ml_year)]
                
                if match.empty and pd.notna(ml_year):
                    # Fallback: match on title only, closest year within ±2
                    close_matches = tmdb_df[tmdb_df['clean_title'] == ml_title]
                    if not close_matches.empty:
                        close_matches = close_matches.copy()
                        close_matches['year_diff'] = np.abs(close_matches['release_year'] - ml_year)
                        close_matches = close_matches[close_matches['year_diff'] <= 2]
                        if not close_matches.empty:
                            match = close_matches[close_matches['year_diff'] == close_matches['year_diff'].min()]
                
                # If still no match, try title-only match (no year filtering)
                if match.empty:
                    match = tmdb_df[tmdb_df['clean_title'] == ml_title]
                    if not match.empty:
                        match = match.head(1)
                
                if not match.empty:
                    tmdb_row = match.iloc[0]
                    
                    # Set overview (description) from CSV
                    overview = tmdb_row.get('overview')
                    if pd.notna(overview) and overview and str(overview).strip():
                        all_movies_df.at[idx, 'overview'] = overview
                        csv_overview_matches += 1

            print(f"CSV matching completed: {csv_overview_matches} movies with descriptions")

        except Exception as e:
            print(f"Error loading or processing TMDB CSV: {e}")
            import traceback
            traceback.print_exc()

    # Second pass: Fetch posters from TMDB API if available
    if hasattr(Config, 'TMDB_API_KEY') and Config.TMDB_API_KEY:
        print("\nFetching posters from TMDB API...")
        
        # Find movies that need poster/overview fetching
        needs_fetch = all_movies_df[
            (all_movies_df['poster_url'].isna()) | 
            (all_movies_df['poster_url'].str.contains('placehold.co', na=False)) |
            (all_movies_df['overview'] == 'Description not available.')
        ]
        
        total_to_fetch = len(needs_fetch)
        print(f"Found {total_to_fetch} movies that need data from API")
        
        if total_to_fetch == 0:
            print("All movies already have data! Nothing to fetch.")
        else:
            print("Note: Saving progress every 50 movies. Safe to stop with Ctrl+C.\n")
            
            session = create_session_with_retries()
            api_poster_matches = 0
            api_overview_matches = 0
            processed_count = 0
            
            try:
                for idx, row in needs_fetch.iterrows():
                    title = row['movie_title'].rsplit(' (', 1)[0].strip()
                    year = row.get('release_year')
                    
                    poster_path, overview = search_tmdb_movie(title, year, Config.TMDB_API_KEY, session)
                    
                    if poster_path:
                        all_movies_df.at[idx, 'poster_url'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        api_poster_matches += 1
                    
                    if overview and (pd.isna(row['overview']) or row['overview'] == 'Description not available.'):
                        all_movies_df.at[idx, 'overview'] = overview
                        api_overview_matches += 1
                    
                    processed_count += 1
                    
                    # Progress indicator and save every 50 movies
                    if processed_count % 50 == 0:
                        print(f"  Processed {processed_count}/{total_to_fetch} movies (Total: {api_poster_matches} posters, {api_overview_matches} descriptions)")
                        print("  Saving progress...")
                        save_progress(all_movies_df, Config.ENRICHED_MOVIES_PATH)
                    
                    # Rate limiting: Be conservative with API
                    time.sleep(0.3)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Saving progress...")
                save_progress(all_movies_df, Config.ENRICHED_MOVIES_PATH)
                print(f"Progress saved! Run the script again to continue from where you left off.")
                return
            except Exception as e:
                print(f"\n\nError occurred: {e}")
                print("Saving progress before exiting...")
                save_progress(all_movies_df, Config.ENRICHED_MOVIES_PATH)
                print(f"Progress saved! Run the script again to continue.")
                raise
            
            print(f"\nAPI fetching completed:")
            print(f"  - {api_poster_matches} posters fetched from API")
            print(f"  - {api_overview_matches} additional descriptions from API")
    else:
        print("\nTMDB API key not configured. Skipping poster fetching.")
        print("To enable poster fetching, add TMDB_API_KEY to your config.py")

    # Fallback to placeholders for missing posters
    placeholder_count = 0
    for idx, row in all_movies_df.iterrows():
        if pd.isna(row['poster_url']) or not row['poster_url']:
            all_movies_df.at[idx, 'poster_url'] = f"https://placehold.co/500x750/1e293b/94a3b8?text={row['movie_title'].replace(' ', '+')}"
            placeholder_count += 1

    print(f"\n{placeholder_count} movies using placeholder posters")

    # Clean up temporary columns if they exist
    all_movies_df.drop(['clean_title', 'release_year', 'release_date'], axis=1, inplace=True, errors='ignore')

    # Final save
    save_progress(all_movies_df, Config.ENRICHED_MOVIES_PATH)
    print(f"\nData saved to {Config.ENRICHED_MOVIES_PATH}")
    
    # Summary
    total_real_posters = all_movies_df[
        all_movies_df['poster_url'].notna() & 
        ~all_movies_df['poster_url'].str.contains('placehold.co', na=False)
    ].shape[0]
    total_descriptions = (all_movies_df['overview'] != 'Description not available.').sum()
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total movies: {len(all_movies_df)}")
    print(f"Movies with real posters: {total_real_posters}")
    print(f"Movies with descriptions: {total_descriptions}")
    print(f"Movies with placeholders: {len(all_movies_df) - total_real_posters}")

if __name__ == '__main__':
    fetch_all_movie_data()