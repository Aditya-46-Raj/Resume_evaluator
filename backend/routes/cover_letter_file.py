# backend/routes/cover_letter_file.py

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import pdfplumber
import docx

from transformers import pipeline

cover_letter_file_api = Blueprint('cover_letter_file_api', __name__)

# Load NLP model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path, extension):
    if extension == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif extension == 'docx':
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""

@cover_letter_file_api.route('/upload_cover_letter', methods=["POST"])
def upload_cover_letter():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(file_path)

        ext = filename.rsplit('.', 1)[1].lower()
        text = extract_text(file_path, ext)

        if not text.strip():
            return jsonify({"error": "Could not extract text from file"}), 400

        # Evaluate with the model
        labels = ["professional", "clear", "grammatically correct", "persuasive", "generic", "informal"]
        result = classifier(text, labels)
        scores = {label: round(score * 100, 2) for label, score in zip(result['labels'], result['scores'])}

        positive_traits = ["professional", "clear", "grammatically correct", "persuasive"]
        negative_traits = ["generic", "informal"]

        positive_score = sum([scores.get(trait, 0) for trait in positive_traits]) / len(positive_traits)
        negative_score = sum([scores.get(trait, 0) for trait in negative_traits]) / len(negative_traits)

        final_score = round(positive_score - (negative_score * 0.5), 2)

        suggestions = []
        if scores.get("generic", 0) > 50:
            suggestions.append("Make your letter more specific to the company or role.")
        if scores.get("informal", 0) > 50:
            suggestions.append("Use a more professional tone.")
        if scores.get("persuasive", 0) < 50:
            suggestions.append("Try to make your achievements more convincing.")

        return jsonify({
            "score": final_score,
            "detailed_scores": scores,
            "suggestions": suggestions
        })

    return jsonify({"error": "Unsupported file format"}), 400
