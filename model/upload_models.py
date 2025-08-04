from huggingface_hub import upload_file

upload_file(
    path_or_fileobj="similarity.pkl",
    path_in_repo="similarity.pkl",
    repo_id="AbdelilahElgallati/Movie-Recommender-System",
    repo_type="space",
    
    token="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"  
)



# from huggingface_hub import create_repo

# create_repo(
#     repo_id="AbdelilahElgallati/Movie-Recommender-System",
#     repo_type="space",
#     space_sdk="gradio",
#     private=False,
#     token="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"
# )