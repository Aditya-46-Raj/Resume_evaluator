import streamlit as st
import requests
import PyPDF2
import io

st.set_page_config(page_title="AI Resume Evaluator", layout="centered")

# Title of the Streamlit App
st.title("📄 AI-Powered Resume Evaluator")

# 📝 Page Selector
page = st.selectbox("Choose an option", ["Resume Evaluator", "Cover Letter Checker"])

# ------------------------- Resume Evaluator -------------------------
if page == "Resume Evaluator":
    # 📌 Upload Resume
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

    # 📌 Paste Job Description
    jd_input = st.text_area("Paste the Job Description", height=150)

    # Function to read PDF text
    def read_pdf(file):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    if uploaded_file is not None:
        resume_bytes = uploaded_file.read()
        text = read_pdf(io.BytesIO(resume_bytes))

        st.subheader("📍 Parsed Resume Info")
        with st.spinner("Parsing Resume..."):
            files = {'file': (uploaded_file.name, resume_bytes, 'application/pdf')}
            response = requests.post("http://localhost:5000/upload", files=files)

            if response.status_code == 200:
                parsed = response.json()["parsed_data"]
                st.json(parsed)
            else:
                st.error("Failed to parse resume.")

        # 📝 Grammar Check
        st.subheader("📝 Grammar Check")
        with st.spinner("Checking grammar..."):
            grammar_response = requests.post(
                "http://localhost:5000/check_grammar",
                json={"text": text}
            )
            if grammar_response.status_code == 200:
                grammar_issues = grammar_response.json()["corrections"]
                for issue in grammar_issues[:10]:  # Show top 10 only
                    st.warning(f"❌ {issue['error']} → 💡 Suggestions: {', '.join(issue['suggestions'])}")
            else:
                st.error("Grammar check failed.")

        # 📊 ATS Score (Resume vs JD)
        if jd_input:
            st.subheader("📊 ATS Score (Resume vs JD)")
            with st.spinner("Evaluating ATS score..."):
                ats_response = requests.post(
                    "http://localhost:5000/ats_score",
                    json={"resume": text, "job_description": jd_input}
                )
                if ats_response.status_code == 200:
                    ats = ats_response.json()["ats_result"]

                    # Safely access the values with .get() to avoid KeyError
                    tfidf_score = ats.get('tfidf_score', 'N/A')  # Default to 'N/A' if key doesn't exist
                    embedding_score = ats.get('embedding_score', 'N/A')  # Default to 'N/A'
                    
                    st.metric("TF-IDF Score", f"{tfidf_score}%")
                    st.metric("Semantic Score", f"{embedding_score}%")

                    missing_keywords = ats.get('missing_keywords', [])
                    matched_keywords = ats.get('matched_keywords', [])

                    st.write("🔍 Missing Keywords:", missing_keywords)
                    st.write("✅ Matched Keywords:", matched_keywords)
                else:
                    st.error("ATS scoring failed.")

# -------------------- Job Role Matcher --------------------
st.subheader("🧠 Match Resume to Job Role")

job_title = st.text_input("Enter Job Title (e.g., Data Analyst, ML Engineer)")

if st.button("Match with Job Role"):
    if text and job_title:
        with st.spinner("Matching..."):
            response = requests.post(
                "http://localhost:5000/match_job_role",
                json={"resume": text, "job_title": job_title}
            )

            if response.status_code == 200:
                result = response.json()["match"]
                st.metric("Semantic Similarity", f"{result['semantic_score']}%")
                st.write("🔍 Missing Keywords:", result["missing_keywords"])
                st.info("Job Description Used:")
                st.write(result["job_description"])
            else:
                st.error("Could not find matching job title.")
    else:
        st.warning("Please upload resume and enter a job title.")


# ------------------------- Cover Letter Checker -------------------------
elif page == "Cover Letter Checker":
    st.title("📝 Cover Letter Checker")

    cover_text = st.text_area("Paste your cover letter here", height=300)
    
    API_URL = "http://localhost:5000"  # Define the API URL here
    
    if st.button("Analyze"):
        if cover_text:
            with st.spinner("Analyzing..."):
                response = requests.post(f"{API_URL}/analyze_cover_letter", json={"text": cover_text})
                if response.status_code == 200:
                    result = response.json()["feedback"]

                    st.subheader("🔍 Feedback:")
                    st.write("**Grammar Issues:**", result["grammar_issues"])
                    st.write("**Readability Score:**", result["readability_score"])
                    st.write("**Word Count:**", result["word_count"])
                    st.write("**Suggestions:**", result["suggestions"])
                else:
                    st.error("Cover letter analysis failed.")
        else:
            st.warning("Please paste a cover letter.")
