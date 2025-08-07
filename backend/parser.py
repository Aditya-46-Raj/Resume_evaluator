# backend/parser.py
import re
import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not found"  # Default value if no name is found

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not found"  # Default value if no email is found

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,}\d', text)
    return match.group(0) if match else "Not found"  # Default value if no phone is found

def extract_skills(text):
    skills_list = ['Python', 'Java', 'C++', 'SQL', 'TensorFlow', 'Keras', 'React', 'Flask']
    found = []
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found.append(skill)
    return found if found else ["Not found"]  # Return default value if no skills are found

def parse_resume(pdf_path):
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Return a dictionary with default values if necessary
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }

