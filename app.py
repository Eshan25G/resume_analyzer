import streamlit as st
import fitz  # PyMuPDF

from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
import torch
import spacy
import base64
from io import BytesIO
import altair as alt

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load spaCy for NER
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


# Text preprocessing
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# Extract text from PDF using pdfplumber
@st.cache_data
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype='pdf') as doc:
        text = ''
        for page in doc:
            text += page.get_text()
    return text


# Calculate keyword match score
def keyword_match_score(resume_text, jd_text):
    resume_words = set(clean_text(resume_text).split())
    jd_words = set(clean_text(jd_text).split())
    match = resume_words & jd_words
    return len(match) / len(jd_words) * 100, list(jd_words - resume_words)

# Calculate semantic similarity
def semantic_similarity(resume, jd):
    emb1 = model.encode(resume, convert_to_tensor=True)
    emb2 = model.encode(jd, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(emb1, emb2)[0][0]) * 100

# Generate word cloud
def plot_wordcloud(text, title):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(title, fontsize=16)
    ax.axis('off')
    st.pyplot(fig)

# Extract named entities from resume
def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'PERSON', 'SKILL']]
    return entities

# Generate skill chart
def skill_bar_chart(resume_text, jd_text):
    resume_words = clean_text(resume_text).split()
    jd_words = clean_text(jd_text).split()
    all_words = set(jd_words)
    data = []
    for word in all_words:
        data.append({
            'Skill': word,
            'In Resume': resume_words.count(word),
            'In JD': jd_words.count(word)
        })
    chart = alt.Chart(alt.Data(values=data)).transform_filter(
        alt.datum['In JD'] > 1
    ).mark_bar().encode(
        x='Skill',
        y='In Resume',
        color='In JD:Q',
        tooltip=['Skill', 'In Resume', 'In JD']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

# Download button for text report
def generate_report(resume_text, jd_text, score_kw, score_sem, missing):
    report = f"Resume Match Report\n\n"
    report += f"Keyword Match Score: {score_kw:.2f}%\n"
    report += f"Semantic Similarity: {score_sem:.2f}%\n\n"
    report += f"Missing Keywords: {', '.join(missing[:15])}\n\n"
    return report

def get_download_link(text):
    b = BytesIO()
    b.write(text.encode())
    b.seek(0)
    b64 = base64.b64encode(b.read()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="resume_report.txt">📥 Download Analysis Report</a>'

# Streamlit UI
st.set_page_config(page_title="Resume Ranker AI", layout="wide")
st.title("📄 Resume Ranker AI - Match Your Resume to Any Job!")

col1, col2 = st.columns(2)

with col1:
    uploaded_resume = st.file_uploader("Upload Your Resume (PDF only)", type=["pdf"])

with col2:
    job_description = st.text_area("Paste the Job Description", height=300)

if uploaded_resume and job_description:
    with st.spinner('Analyzing...'):
        resume_text = extract_text_from_pdf(uploaded_resume)
        jd_text = job_description

        score_kw, missing_keywords = keyword_match_score(resume_text, jd_text)
        score_semantic = semantic_similarity(resume_text, jd_text)
        named_entities = extract_entities(resume_text)

    st.subheader("🔍 Analysis Results")
    st.metric("Keyword Match Score", f"{score_kw:.2f}%")
    st.metric("Semantic Similarity", f"{score_semantic:.2f}%")

    st.subheader("🧠 Suggestions: Add These Keywords")
    if missing_keywords:
        st.write(", ".join(sorted(missing_keywords)[:15]))
    else:
        st.success("Great! Your resume already contains most key terms.")

    st.subheader("📊 Skill Chart (Resume vs Job Description)")
    skill_bar_chart(resume_text, jd_text)

    st.subheader("📊 Word Cloud from Your Resume")
    plot_wordcloud(resume_text, "Resume Word Cloud")

    st.subheader("📊 Word Cloud from Job Description")
    plot_wordcloud(jd_text, "Job Description Word Cloud")

    st.subheader("🏷️ Named Entities in Resume (Organizations, Skills, etc.)")
    if named_entities:
        st.write(named_entities)
    else:
        st.info("No named entities detected.")

    st.markdown(get_download_link(generate_report(resume_text, jd_text, score_kw, score_semantic, missing_keywords)), unsafe_allow_html=True)

    st.success("✅ Analysis complete. Use the report to improve your resume for ATS!")
else:
    st.info("Please upload a resume and paste a job description to start the analysis.")
