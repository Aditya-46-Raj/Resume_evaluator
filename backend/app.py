from nlp_utils import get_cover_letter_feedback  # Import the function from nlp_utils.py

from job_matcher import match_resume_to_job

# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import parse_resume
from grammar_check import check_grammar
from ats_score import evaluate_ats
import os

from routes.cover_letter import cover_letter_api
from routes.cover_letter_file import cover_letter_file_api

from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)

# cover_letter call
app.register_blueprint(cover_letter_api)
# cover_letter_file call
app.register_blueprint(cover_letter_file_api)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "Resume Evaluator API is running."})

# New route ats score check
@app.route('/ats_score', methods=['POST'])
def ats_score():
    data = request.get_json()
    
    if 'resume' not in data or 'job_description' not in data:
        return jsonify({"error": "resume and job_description fields are required"}), 400

    try:
        result = evaluate_ats(data['resume'], data['job_description'])
        return jsonify({"success": True, "ats_result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# New route gramar check
@app.route('/check_grammar', methods=['POST'])
def grammar_check():
    data = request.get_json()

    if 'text' not in data:
        return jsonify({"error": "Text field is required"}), 400

    try:
        corrections = check_grammar(data['text'])
        return jsonify({"success": True, "corrections": corrections})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        result = parse_resume(filepath)
        return jsonify({"success": True, "parsed_data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/analyze_cover_letter', methods=['POST'])
def analyze_cover_letter():
    data = request.get_json()

    cover_text = data.get('text', '')
    if not cover_text:
        return jsonify({'error': 'No cover letter text provided'}), 400

    feedback = get_cover_letter_feedback(cover_text)
    return jsonify({'feedback': feedback})


@app.route('/match_job_role', methods=['POST'])
def match_job_role():
    data = request.get_json()
    resume_text = data.get('resume', '')
    job_title = data.get('job_title', '')

    if not resume_text or not job_title:
        return jsonify({"error": "Both resume and job_title are required"}), 400

    result = match_resume_to_job(resume_text, job_title)
    if result:
        return jsonify({"success": True, "match": result})
    else:
        return jsonify({"success": False, "error": "Job title not found in database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
