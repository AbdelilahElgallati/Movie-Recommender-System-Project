# import pandas as pd
# import numpy as np
# import os  
# import json 

# from config import Config

# def load_users():
#     if not os.path.exists(Config.USERS_FILE_PATH):
#         return []
#     try:
#         with open(Config.USERS_FILE_PATH, 'r') as f:
#             users_data = json.load(f)
        
#         def ensure_int_ids(obj):
#             if isinstance(obj, list):
#                 return [ensure_int_ids(item) for item in obj]
#             elif isinstance(obj, dict):
#                 return {key: ensure_int_ids(value) if key == 'id' else value for key, value in obj.items()}
#             else:
#                 return obj
        
#         return ensure_int_ids(users_data)
#     except json.JSONDecodeError:
#         return []

# def save_users(users_data):
#     def convert_to_native(obj):
#         if isinstance(obj, (np.integer, pd.Int64Dtype)):
#             return int(obj)
#         elif isinstance(obj, (np.floating, pd.Float64Dtype)):
#             return float(obj)
#         elif isinstance(obj, (np.bool_, pd.BooleanDtype)):
#             return bool(obj)
#         elif isinstance(obj, (list, tuple)):
#             return [convert_to_native(item) for item in obj]
#         elif isinstance(obj, dict):
#             return {key: convert_to_native(value) for key, value in obj.items()}
#         elif isinstance(obj, pd.Series):
#             return convert_to_native(obj.to_dict())
#         else:
#             return obj

#     users_data_native = convert_to_native(users_data)
    
#     with open(Config.USERS_FILE_PATH, 'w') as f:
#         json.dump(users_data_native, f, indent=4)

# def get_next_available_user_id():
#     try:
#         u_cols = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
#         users_df = pd.read_csv(Config.USERS_PATH, sep='|', names=u_cols, encoding='latin-1')
#         max_dataset_id = int(users_df['user_id'].max())
#     except Exception as e:
#         print(f"Attention: Impossible de lire {Config.USERS_PATH}. Utilise 943 par défaut. Erreur: {e}")
#         max_dataset_id = 943
        
#     new_users = load_users()
#     if not new_users:
#         max_new_user_id = 0
#     else:
#         ids = [user['id'] for user in new_users if 'id' in user]
#         max_new_user_id = max(ids) if ids else 0
        
#     return max(max_dataset_id, max_new_user_id) + 1

import pandas as pd
import numpy as np
import os  
import json 

from config import Config

# Chemin vers le nouveau fichier JSON pour les notes
USER_RATINGS_PATH = os.path.join(Config.BASE_DIR, 'user_ratings.json')

def load_users():
    if not os.path.exists(Config.USERS_FILE_PATH):
        return []
    try:
        with open(Config.USERS_FILE_PATH, 'r') as f:
            users_data = json.load(f)
        
        def ensure_int_ids(obj):
            if isinstance(obj, list):
                return [ensure_int_ids(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: ensure_int_ids(value) if key == 'id' else value for key, value in obj.items()}
            else:
                return obj
        
        return ensure_int_ids(users_data)
    except json.JSONDecodeError:
        return []

def save_users(users_data):
    def convert_to_native(obj):
        if isinstance(obj, (np.integer, pd.Int64Dtype)):
            return int(obj)
        elif isinstance(obj, (np.floating, pd.Float64Dtype)):
            return float(obj)
        elif isinstance(obj, (np.bool_, pd.BooleanDtype)):
            return bool(obj)
        elif isinstance(obj, (list, tuple)):
            return [convert_to_native(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_to_native(value) for key, value in obj.items()}
        elif isinstance(obj, pd.Series):
            return convert_to_native(obj.to_dict())
        else:
            return obj

    users_data_native = convert_to_native(users_data)
    
    with open(Config.USERS_FILE_PATH, 'w') as f:
        json.dump(users_data_native, f, indent=4)

def get_next_available_user_id():
    try:
        u_cols = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
        users_df = pd.read_csv(Config.USERS_PATH, sep='|', names=u_cols, encoding='latin-1')
        max_dataset_id = int(users_df['user_id'].max())
    except Exception as e:
        print(f"Attention: Impossible de lire {Config.USERS_PATH}. Utilise 943 par défaut. Erreur: {e}")
        max_dataset_id = 943
        
    new_users = load_users()
    if not new_users:
        max_new_user_id = 0
    else:
        ids = [user['id'] for user in new_users if 'id' in user]
        max_new_user_id = max(ids) if ids else 0
        
    return max(max_dataset_id, max_new_user_id) + 1

# --- NOUVELLES FONCTIONS ---

def load_user_ratings():
    """Charge le dictionnaire des notes utilisateurs depuis user_ratings.json"""
    if not os.path.exists(USER_RATINGS_PATH):
        return {}
    try:
        with open(USER_RATINGS_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_user_ratings(ratings_data):
    """Sauvegarde le dictionnaire des notes utilisateurs dans user_ratings.json"""
    with open(USER_RATINGS_PATH, 'w') as f:
        json.dump(ratings_data, f, indent=4)