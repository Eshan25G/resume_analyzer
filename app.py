pip install -U spacy
import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import base64
from datetime import datetime
import json
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import PyPDF2
import docx
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade
import requests
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
@st.cache_resource
def download_nltk_data():
    try:
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        return True
    except Exception as e:
        st.warning(f"NLTK data download failed: {str(e)}")
        return False

# Load spaCy model
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.warning("⚠️ spaCy English model not found. Installing...")
        try:
            import subprocess
            subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
        except Exception as e:
            st.error(f"Could not install spaCy model: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error loading spaCy model: {str(e)}")
        return None

class ResumeAnalyzer:
    def __init__(self):
        self.nlp = load_spacy_model()
        nltk_success = download_nltk_data()
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set([
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
                'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
                'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
                'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
                'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
                'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                'with', 'about', 'against', 'between', 'into', 'through', 'during',
                'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
                'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
                'should', 'now'
            ])
        # ... rest of your initialization code (roles, technical_skills, etc.)

    def extract_text_from_pdf(self, file):
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text

    def extract_text_from_docx(self, file):
        doc = docx.Document(file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    # ... the rest of your ResumeAnalyzer methods ...

def main():
    st.set_page_config(
        page_title="Advanced Resume Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎯 Advanced Resume Analyzer")
    st.markdown("Upload your resume and get comprehensive AI-powered analysis!")

    analyzer = ResumeAnalyzer()

    st.sidebar.title("🧭 Navigation")
    analysis_type = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Resume Analysis", "Job Matching", "Skill Gap Analysis", "Role Explorer", "Industry Insights"]
    )

    # Role selector in sidebar
    selected_role = None
    if analysis_type in ["Skill Gap Analysis", "Role Explorer"]:
        st.sidebar.subheader("🎯 Target Role")
        selected_role = st.sidebar.selectbox(
            "Select your target role:",
            ["Software Engineer", "Data Scientist", "DevOps Engineer", "Frontend Developer", "Backend Developer", "Product Manager", "Data Analyst", "Cloud Architect", "Mobile Developer", "QA Engineer", "UI/UX Designer", "Marketing Manager", "Financial Analyst", "Business Analyst", "Cybersecurity Analyst"],
            help="Choose the role you want to analyze against"
        )

    # Settings
    st.sidebar.subheader("⚙️ Settings")
    show_debug = st.sidebar.checkbox("Show Debug Info", value=False)
    analysis_depth = st.sidebar.slider("Analysis Depth", 1, 3, 2, help="Higher depth = more detailed analysis")

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )

    text = ""
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            text = analyzer.extract_text_from_pdf(uploaded_file)
        else:
            text = analyzer.extract_text_from_docx(uploaded_file)

        if text:
            st.success("Resume uploaded successfully!")
            # (Rest of your main analysis code follows here...)
        else:
            st.error("Could not extract text from the uploaded file. Please try another file.")

    st.markdown("---")
    st.markdown("### 💡 Tips for Better Results")
    st.markdown("""
    - Ensure your resume is in a standard format (PDF or DOCX)
    - Use clear section headings (Experience, Education, Skills)
    - Include relevant keywords for your target industry
    - Quantify your achievements with numbers and percentages
    - Keep your resume concise and well-structured
    """)

if __name__ == "__main__":
    main()
