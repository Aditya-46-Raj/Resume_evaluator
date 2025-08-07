# backend/routes/cover_letter.py

from flask import Blueprint, request, jsonify
from transformers import pipeline

cover_letter_api = Blueprint('cover_letter_api', __name__)

# Load zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

@cover_letter_api.route('/evaluate_cover_letter', methods=["POST"])
def evaluate_cover_letter():
    data = request.json
    text = data.get("cover_letter", "")

    if not text.strip():
        return jsonify({"error": "Cover letter text is empty"}), 400

    # Define labels for evaluation
    labels = ["professional", "clear", "grammatically correct", "persuasive", "generic", "informal"]

    result = classifier(text, labels)

    scores = {label: round(score * 100, 2) for label, score in zip(result['labels'], result['scores'])}

    # Calculate weighted score
    positive_traits = ["professional", "clear", "grammatically correct", "persuasive"]
    negative_traits = ["generic", "informal"]

    positive_score = sum([scores.get(trait, 0) for trait in positive_traits]) / len(positive_traits)
    negative_score = sum([scores.get(trait, 0) for trait in negative_traits]) / len(negative_traits)

    final_score = round(positive_score - (negative_score * 0.5), 2)

    # Suggest improvements
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
