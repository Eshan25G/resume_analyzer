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
        nltk.download('punkt_tab', quiet=True)
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
        # Set up stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

        # Available roles for analysis
        self.available_roles = {
            'Software Engineer': {
                'skills': ['python', 'java', 'javascript', 'react', 'sql', 'git', 'aws', 'docker', 'kubernetes', 'typescript'],
                'description': 'Full-stack software development role'
            },
            'Data Scientist': {
                'skills': ['python', 'r', 'sql', 'machine learning', 'pandas', 'numpy', 'tensorflow', 'scikit-learn', 'tableau', 'jupyter'],
                'description': 'Data analysis and machine learning role'
            },
            'DevOps Engineer': {
                'skills': ['docker', 'kubernetes', 'aws', 'jenkins', 'terraform', 'ansible', 'linux', 'git', 'ci/cd', 'monitoring'],
                'description': 'Infrastructure and deployment automation role'
            },
            'Frontend Developer': {
                'skills': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'typescript', 'webpack', 'sass', 'bootstrap'],
                'description': 'User interface development role'
            },
            'Backend Developer': {
                'skills': ['python', 'java', 'node.js', 'sql', 'mongodb', 'rest api', 'microservices', 'docker', 'aws', 'redis'],
                'description': 'Server-side development role'
            },
            'Product Manager': {
                'skills': ['analytics', 'project management', 'user research', 'sql', 'agile', 'scrum', 'a/b testing', 'roadmap', 'stakeholder management'],
                'description': 'Product strategy and management role'
            },
            'Data Analyst': {
                'skills': ['sql', 'excel', 'python', 'tableau', 'power bi', 'statistics', 'data visualization', 'etl', 'dashboards'],
                'description': 'Business intelligence and reporting role'
            },
            'Cloud Architect': {
                'skills': ['aws', 'azure', 'gcp', 'kubernetes', 'terraform', 'microservices', 'security', 'networking', 'serverless'],
                'description': 'Cloud infrastructure design role'
            },
            'Mobile Developer': {
                'skills': ['react native', 'flutter', 'swift', 'kotlin', 'android', 'ios', 'mobile ui/ux', 'app store', 'firebase'],
                'description': 'Mobile application development role'
            },
            'QA Engineer': {
                'skills': ['selenium', 'junit', 'pytest', 'automation testing', 'manual testing', 'api testing', 'performance testing', 'bug tracking'],
                'description': 'Quality assurance and testing role'
            },
            'UI/UX Designer': {
                'skills': ['figma', 'sketch', 'adobe xd', 'user research', 'wireframing', 'prototyping', 'user testing', 'design systems'],
                'description': 'User experience and interface design role'
            },
            'Marketing Manager': {
                'skills': ['digital marketing', 'analytics', 'seo', 'social media', 'content marketing', 'email marketing', 'ppc', 'conversion optimization'],
                'description': 'Marketing strategy and execution role'
            },
            'Financial Analyst': {
                'skills': ['excel', 'sql', 'financial modeling', 'python', 'tableau', 'accounting', 'budgeting', 'forecasting', 'risk analysis'],
                'description': 'Financial analysis and reporting role'
            },
            'Business Analyst': {
                'skills': ['requirements analysis', 'process improvement', 'stakeholder management', 'documentation', 'agile', 'sql', 'project management'],
                'description': 'Business process analysis role'
            },
            'Cybersecurity Analyst': {
                'skills': ['network security', 'penetration testing', 'incident response', 'risk assessment', 'compliance', 'security tools', 'threat analysis'],
                'description': 'Information security role'
            }
        }

        # Common technical skills database
        self.technical_skills = {
            'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'typescript'],
            'Frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails', 'bootstrap', 'jquery', 'node.js', 'next.js', 'vue.js'],
            'Databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite', 'cassandra', 'dynamodb', 'firebase'],
            'Cloud Platforms': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'cloudflare', 'netlify', 'vercel'],
            'DevOps': ['docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'ansible', 'terraform', 'vagrant', 'ci/cd'],
            'Data Science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'matplotlib', 'seaborn', 'plotly', 'tableau', 'power bi'],
            'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova'],
            'Testing': ['selenium', 'jest', 'junit', 'pytest', 'cypress', 'postman', 'jmeter'],
            'Web Technologies': ['rest api', 'graphql', 'soap', 'microservices', 'websockets', 'oauth', 'jwt'],
            'Operating Systems': ['linux', 'ubuntu', 'centos', 'windows', 'macos', 'unix']
        }

        self.ats_keywords = [
            'experience', 'skills', 'education', 'qualifications', 'achievements',
            'projects', 'certifications', 'awards', 'languages', 'interests',
            'objective', 'summary', 'profile', 'professional', 'career',
            'responsibilities', 'accomplishments', 'results', 'impact'
        ]

        self.industry_keywords = {
            'Software Development': ['agile', 'scrum', 'software development', 'coding', 'programming', 'debugging', 'testing', 'deployment'],
            'Data Science': ['machine learning', 'deep learning', 'data analysis', 'statistics', 'visualization', 'modeling', 'algorithms'],
            'Marketing': ['digital marketing', 'seo', 'sem', 'social media', 'content marketing', 'analytics', 'campaigns'],
            'Finance': ['financial analysis', 'accounting', 'budgeting', 'forecasting', 'risk management', 'compliance'],
            'Healthcare': ['patient care', 'medical', 'clinical', 'healthcare', 'diagnosis', 'treatment', 'research'],
            'Education': ['teaching', 'curriculum', 'assessment', 'learning', 'instruction', 'pedagogy', 'educational']
        }
    # ... rest of the class methods remain unchanged ...
    # (No changes needed to the rest of the class)

    # (Paste your other ResumeAnalyzer methods here)

# ... rest of your code (main, etc.) remains unchanged except for fixing duplicate Skill Gap Analysis block and variable checks ...

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
            list(analyzer.available_roles.keys()),
            help="Choose the role you want to analyze against"
        )

        if selected_role:
            role_info = analyzer.available_roles[selected_role]
            st.sidebar.info(f"**{selected_role}**\n\n{role_info['description']}")
            with st.sidebar.expander("📋 Required Skills"):
                for skill in role_info['skills']:
                    st.write(f"• {skill.title()}")

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
            # (Rest of your main analysis code follows here as in your original file...)

            # --- Remove the duplicate "Skill Gap Analysis" block ---

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
