import pandas as pd
import numpy as np

def enrich_recs_with_posters(recs_list, all_movies_df, id_col_idx, title_col_idx, other_cols_indices):
    enriched_recs = []
    for rec in recs_list:
        movie_id = rec[id_col_idx]
        title = rec[title_col_idx]
        
        # --- This line now works, as all_movies_df is passed in ---
        movie_data = all_movies_df[all_movies_df['movie_id'] == movie_id]
        
        poster_url = None
        overview = "Description not available."
        
        if not movie_data.empty:
            movie_row = movie_data.iloc[0]
            poster_url = movie_row['poster_url']
            overview = movie_row.get('overview', "Description not available.")
            
            if pd.isna(poster_url) or not poster_url:
                # Create a placeholder image based on movie title
                poster_url = f"https://placehold.co/500x750/1e293b/94a3b8?text={title.replace(' ', '+')}"
        
        rec_dict = { 
            "movie_id": int(movie_id), 
            "title": title, 
            "poster_url": poster_url,
            "overview": overview
        }
        
        for key, idx in other_cols_indices.items():
            rec_dict[key] = rec[idx]
            
        enriched_recs.append(rec_dict)
    
    return enriched_recs