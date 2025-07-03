import streamlit as st
import PyPDF2
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Text preprocessing
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# Extract text from PDF
@st.cache_data
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
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
def plot_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

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

    st.subheader("🔍 Analysis Results")
    st.metric("Keyword Match Score", f"{score_kw:.2f}%")
    st.metric("Semantic Similarity", f"{score_semantic:.2f}%")

    st.subheader("🧠 Suggestions: Add These Keywords")
    if missing_keywords:
        st.write(", ".join(sorted(missing_keywords)[:15]))
    else:
        st.success("Great! Your resume already contains most key terms.")

    st.subheader("📊 Word Cloud from Your Resume")
    plot_wordcloud(resume_text)

    st.subheader("📊 Word Cloud from Job Description")
    plot_wordcloud(jd_text)

    st.success("✅ Analysis complete. Make suggested improvements for better ATS compatibility!")
else:
    st.info("Please upload a resume and paste a job description to start the analysis.")
