import pandas as pd
from helper import clean_text
from sentence_transformers import SentenceTransformer, util
import torch
import os

# Load transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_dataset(csv_file):
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=['Section', 'Title', 'Description'])  # Remove incomplete rows
    return df

def semantic_match_sections(text, df, threshold=0.4):  # Lower threshold for more recall
    text = clean_text(text)
    text_embedding = model.encode(text, convert_to_tensor=True)

    # Prepare all section texts
    section_texts = []
    section_data = []

    for _, row in df.iterrows():
        title = str(row['Title']).strip()
        desc = str(row['Description']).strip()
        section_str = f"{row['Section']} - {title}. {desc}"
        section_texts.append(clean_text(section_str))
        section_data.append({
            "section": row['Section'],
            "title": title,
            "description": desc,
            "category": row.get('category', 'General')
        })

    # Encode all section texts in one go
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)

    # Compute cosine similarity with input
    cosine_scores = util.cos_sim(text_embedding, section_embeddings)[0]

    # Filter by threshold
    results = []
    for score, data in zip(cosine_scores, section_data):
        if score.item() > threshold:
            data['score'] = round(score.item(), 2)
            results.append(data)

    # Sort by score descending and return top 5
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]

def recommend_sections(text, ipc_file=None, bns_file=None):
    base_path = os.path.join(os.path.dirname(__file__), 'static', 'resources')
    ipc_file = ipc_file or os.path.join(base_path, 'ipc_ds.csv')
    bns_file = bns_file or os.path.join(base_path, 'bns_ds.csv')

    ipc_df = load_dataset(ipc_file)
    bns_df = load_dataset(bns_file)

    ipc_matches = semantic_match_sections(text, ipc_df)
    bns_matches = semantic_match_sections(text, bns_df)

    return ipc_matches, bns_matches
