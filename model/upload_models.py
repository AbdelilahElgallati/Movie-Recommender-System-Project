from huggingface_hub import upload_file
import os


upload_file(
    path_or_fileobj="similarity.pkl",
    path_in_repo="similarity.pkl",
    repo_id="AbdelilahElgallati/Movie-Recommender-System",
    repo_type="space",
    token = os.getenv("HF_TOKEN")
)