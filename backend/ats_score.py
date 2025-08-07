# backend/ats_score.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load model once (lightweight version for speed)
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

def tfidf_similarity(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)

def embedding_similarity(resume_text, jd_text):
    embeddings = sbert_model.encode([resume_text, jd_text], convert_to_tensor=True)
    score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return round(score * 100, 2)

def get_missing_keywords(resume_text, jd_text):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    keywords = jd_words - resume_words
    common = resume_words & jd_words
    return list(keywords), list(common)

def evaluate_ats(resume_text, jd_text):
    tfidf_score = tfidf_similarity(resume_text, jd_text)
    embed_score = embedding_similarity(resume_text, jd_text)
    missing, matched = get_missing_keywords(resume_text, jd_text)

    return {
        "tfidf_score": tfidf_score,
        "embedding_score": embed_score,
        "missing_keywords": missing[:20],  # Limit to top 20
        "matched_keywords": matched[:20]
    }
