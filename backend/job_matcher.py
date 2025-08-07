from sentence_transformers import SentenceTransformer, util
import numpy as np

sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Dummy job description database (can replace with actual scraping later)
job_descriptions = {
    "data analyst": "Looking for Data Analyst with skills in Python, SQL, Excel, data visualization, statistics, communication, dashboards.",
    "backend developer": "Requires backend dev with experience in Node.js, Python, REST APIs, MongoDB, Flask, and scalable architecture.",
    "ml engineer": "Machine learning engineer needed with strong Python, TensorFlow, PyTorch, ML models, deployment, and AWS skills."
}

def get_job_description_from_title(title: str):
    title = title.lower()
    for key in job_descriptions:
        if key in title:
            return job_descriptions[key]
    return None

def match_resume_to_job(resume_text: str, job_title: str):
    jd_text = get_job_description_from_title(job_title)
    if not jd_text:
        return None

    embeddings = sbert_model.encode([resume_text, jd_text], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    missing = list(jd_words - resume_words)

    return {
        "job_title": job_title,
        "job_description": jd_text,
        "semantic_score": round(similarity * 100, 2),
        "missing_keywords": missing[:20]
    }
