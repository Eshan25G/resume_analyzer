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
        
        if text:
            st.success("✅ Resume uploaded successfully!")
            
            # Debug info
            if show_debug:
                st.sidebar.subheader("🔍 Debug Info")
                st.sidebar.write(f"Text length: {len(text)} characters")
                st.sidebar.write(f"Word count: {len(text.split())}")
                st.sidebar.write(f"Analysis depth: {analysis_depth}")
                
                with st.sidebar.expander("Raw Text Preview"):
                    st.text(text[:500] + "..." if len(text) > 500 else text) nltk_success:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'])
        else:
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'])
        
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
        
        # ATS-friendly keywords
        self.ats_keywords = [
            'experience', 'skills', 'education', 'qualifications', 'achievements',
            'projects', 'certifications', 'awards', 'languages', 'interests',
            'objective', 'summary', 'profile', 'professional', 'career',
            'responsibilities', 'accomplishments', 'results', 'impact'
        ]
        
        # Industry-specific keywords
        self.industry_keywords = {
            'Software Development': ['agile', 'scrum', 'software development', 'coding', 'programming', 'debugging', 'testing', 'deployment'],
            'Data Science': ['machine learning', 'deep learning', 'data analysis', 'statistics', 'visualization', 'modeling', 'algorithms'],
            'Marketing': ['digital marketing', 'seo', 'sem', 'social media', 'content marketing', 'analytics', 'campaigns'],
            'Finance': ['financial analysis', 'accounting', 'budgeting', 'forecasting', 'risk management', 'compliance'],
            'Healthcare': ['patient care', 'medical', 'clinical', 'healthcare', 'diagnosis', 'treatment', 'research'],
            'Education': ['teaching', 'curriculum', 'assessment', 'learning', 'instruction', 'pedagogy', 'educational']
        }

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""

    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""

    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from resume text."""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['emails'] = emails
        
        # Phone number extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact_info['phones'] = [''.join(phone) for phone in phones]
        
        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        contact_info['linkedin'] = linkedin
        
        # GitHub extraction
        github_pattern = r'github\.com/[A-Za-z0-9-]+'
        github = re.findall(github_pattern, text.lower())
        contact_info['github'] = github
        
        return contact_info

    def extract_skills(self, text: str) -> Dict:
        """Extract technical skills from resume text."""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.technical_skills.items():
            category_skills = []
            for skill in skills:
                if skill.lower() in text_lower:
                    category_skills.append(skill)
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills

    def calculate_ats_score(self, text: str) -> Dict:
        """Calculate ATS compatibility score."""
        text_lower = text.lower()
        
        # Check for ATS-friendly formatting
        ats_checks = {
            'has_contact_info': bool(re.search(r'@', text) and re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text)),
            'has_standard_sections': any(keyword in text_lower for keyword in self.ats_keywords),
            'no_tables': '|' not in text and '┌' not in text and '┐' not in text,
            'no_images': True,  # Assuming uploaded file has been processed
            'readable_fonts': True,  # Assuming standard fonts
            'proper_headings': len(re.findall(r'\n[A-Z][A-Z\s]+\n', text)) > 2,
            'bullet_points': '•' in text or '*' in text or '-' in text,
            'keywords_present': sum(1 for keyword in self.ats_keywords if keyword in text_lower) > 5
        }
        
        score = (sum(ats_checks.values()) / len(ats_checks)) * 100
        
        return {
            'score': round(score, 2),
            'checks': ats_checks,
            'recommendations': self.get_ats_recommendations(ats_checks)
        }

    def get_ats_recommendations(self, checks: Dict) -> List[str]:
        """Get ATS improvement recommendations."""
        recommendations = []
        
        if not checks['has_contact_info']:
            recommendations.append("Add clear contact information (email and phone)")
        if not checks['has_standard_sections']:
            recommendations.append("Include standard sections (Experience, Education, Skills)")
        if not checks['no_tables']:
            recommendations.append("Avoid complex tables and layouts")
        if not checks['proper_headings']:
            recommendations.append("Use clear section headings")
        if not checks['bullet_points']:
            recommendations.append("Use bullet points for better readability")
        if not checks['keywords_present']:
            recommendations.append("Include more relevant keywords")
        
        return recommendations

    def analyze_readability(self, text: str) -> Dict:
        """Analyze text readability."""
        try:
            flesch_score = flesch_reading_ease(text)
            fk_grade = flesch_kincaid_grade(text)
            
            # Readability interpretation
            if flesch_score >= 90:
                level = "Very Easy"
            elif flesch_score >= 80:
                level = "Easy"
            elif flesch_score >= 70:
                level = "Fairly Easy"
            elif flesch_score >= 60:
                level = "Standard"
            elif flesch_score >= 50:
                level = "Fairly Difficult"
            elif flesch_score >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"
            
            return {
                'flesch_score': round(flesch_score, 2),
                'fk_grade': round(fk_grade, 2),
                'level': level
            }
        except:
            return {
                'flesch_score': 0,
                'fk_grade': 0,
                'level': "Unable to calculate"
            }

    def generate_word_cloud(self, text: str) -> WordCloud:
        """Generate word cloud from resume text."""
        try:
            # Try to use NLTK tokenizer first
            if download_nltk_data():
                try:
                    words = word_tokenize(text.lower())
                except:
                    # Fallback to simple split if NLTK fails
                    words = text.lower().split()
            else:
                # Simple split fallback
                words = text.lower().split()
            
            # Clean words
            words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
            
            if not words:
                return None
            
            text_for_cloud = ' '.join(words)
            
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10
            ).generate(text_for_cloud)
            return wordcloud
            
        except Exception as e:
            st.error(f"Error generating word cloud: {str(e)}")
            return None

    def match_job_description(self, resume_text: str, job_description: str) -> Dict:
        """Match resume with job description."""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        try:
            # Try to use NLTK tokenizer
            if download_nltk_data():
                try:
                    job_words = set(word_tokenize(job_lower))
                    resume_words = set(word_tokenize(resume_lower))
                except:
                    # Fallback to simple split
                    job_words = set(job_lower.split())
                    resume_words = set(resume_lower.split())
            else:
                # Simple split fallback
                job_words = set(job_lower.split())
                resume_words = set(resume_lower.split())
            
            # Clean words
            job_words = {word for word in job_words if word.isalnum() and word not in self.stop_words and len(word) > 2}
            resume_words = {word for word in resume_words if word.isalnum() and word not in self.stop_words and len(word) > 2}
            
            # Calculate match percentage
            common_words = job_words.intersection(resume_words)
            match_percentage = (len(common_words) / len(job_words)) * 100 if job_words else 0
            
            # Missing keywords
            missing_keywords = job_words - resume_words
            
            return {
                'match_percentage': round(match_percentage, 2),
                'common_keywords': list(common_words),
                'missing_keywords': list(missing_keywords)[:20],  # Top 20 missing
                'total_job_keywords': len(job_words),
                'matched_keywords': len(common_words)
            }
            
        except Exception as e:
            st.error(f"Error in job matching: {str(e)}")
            return {
                'match_percentage': 0,
                'common_keywords': [],
                'missing_keywords': [],
                'total_job_keywords': 0,
                'matched_keywords': 0
            }

    def detect_industry(self, text: str) -> str:
        """Detect likely industry based on resume content."""
        text_lower = text.lower()
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return "General"

    def analyze_experience_level(self, text: str) -> Dict:
        """Analyze experience level based on resume content."""
        text_lower = text.lower()
        
        # Look for experience indicators
        experience_indicators = {
            'entry_level': ['intern', 'entry level', 'graduate', 'junior', 'trainee', 'fresher'],
            'mid_level': ['2 years', '3 years', '4 years', '5 years', 'experienced', 'professional'],
            'senior_level': ['senior', 'lead', 'manager', 'director', '7+ years', '8+ years', '10+ years'],
            'executive': ['executive', 'ceo', 'cto', 'vp', 'vice president', 'head of']
        }
        
        level_scores = {}
        for level, indicators in experience_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            level_scores[level] = score
        
        # Determine experience level
        if level_scores:
            predicted_level = max(level_scores, key=level_scores.get)
            confidence = level_scores[predicted_level]
        else:
            predicted_level = "unknown"
            confidence = 0
        
        return {
            'level': predicted_level,
            'confidence': confidence,
            'scores': level_scores
        }

def main():
    st.set_page_config(
        page_title="Advanced Resume Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎯 Advanced Resume Analyzer")
    st.markdown("Upload your resume and get comprehensive AI-powered analysis!")
    
    # Initialize analyzer
    analyzer = ResumeAnalyzer()
    
    # Sidebar
    st.sidebar.title("🧭 Navigation")
    analysis_type = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Resume Analysis", "Job Matching", "Skill Gap Analysis", "Role Explorer", "Industry Insights"]
    )
    
    # Role selector in sidebar
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
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file is not None:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            text = analyzer.extract_text_from_pdf(uploaded_file)
        else:
            text = analyzer.extract_text_from_docx(uploaded_file)
        
        if text:
            st.success("Resume uploaded successfully!")
            
            # Main analysis based on selected type
            if analysis_type == "Resume Analysis":
                st.header("📊 Resume Analysis")
                
                # Create tabs for different analyses
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Overview", "ATS Score", "Skills", "Readability", "Contact Info"
                ])
                
                with tab1:
                    st.subheader("Resume Overview")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        word_count = len(text.split())
                        st.metric("Word Count", word_count)
                    
                    with col2:
                        char_count = len(text)
                        st.metric("Character Count", char_count)
                    
                    with col3:
                        industry = analyzer.detect_industry(text)
                        st.metric("Detected Industry", industry)
                    
                    # Experience Level Analysis
                    exp_analysis = analyzer.analyze_experience_level(text)
                    st.subheader("Experience Level Analysis")
                    st.info(f"Predicted Level: **{exp_analysis['level'].title()}** (Confidence: {exp_analysis['confidence']})")
                    
                    # Word Cloud
                    st.subheader("☁️ Word Cloud")
                    wordcloud = analyzer.generate_word_cloud(text)
                    if wordcloud:
                        try:
                            import matplotlib.pyplot as plt
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                            plt.close(fig)
                        except Exception as e:
                            st.error(f"Error displaying word cloud: {str(e)}")
                    else:
                        st.info("Unable to generate word cloud - this may be due to insufficient text content")
                
                with tab2:
                    st.subheader("ATS Compatibility Score")
                    
                    ats_result = analyzer.calculate_ats_score(text)
                    
                    # Score display
                    score_color = "green" if ats_result['score'] >= 70 else "orange" if ats_result['score'] >= 50 else "red"
                    st.markdown(f"### ATS Score: <span style='color: {score_color}'>{ats_result['score']}%</span>", unsafe_allow_html=True)
                    
                    # Progress bar
                    st.progress(ats_result['score'] / 100)
                    
                    # Detailed checks
                    st.subheader("Detailed Checks")
                    for check, passed in ats_result['checks'].items():
                        icon = "✅" if passed else "❌"
                        st.write(f"{icon} {check.replace('_', ' ').title()}")
                    
                    # Recommendations
                    if ats_result['recommendations']:
                        st.subheader("Recommendations")
                        for rec in ats_result['recommendations']:
                            st.write(f"• {rec}")
                
                with tab3:
                    st.subheader("Skills Analysis")
                    
                    skills = analyzer.extract_skills(text)
                    
                    if skills:
                        for category, skill_list in skills.items():
                            st.write(f"**{category}:**")
                            st.write(", ".join(skill_list))
                            st.write("")
                        
                        # Skills chart
                        skills_data = pd.DataFrame([
                            {"Category": category, "Count": len(skill_list)}
                            for category, skill_list in skills.items()
                        ])
                        
                        fig = px.bar(
                            skills_data, 
                            x="Category", 
                            y="Count",
                            title="Skills by Category",
                            color="Count",
                            color_continuous_scale="viridis"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No technical skills detected. Consider adding more specific technical skills.")
                
                with tab4:
                    st.subheader("Readability Analysis")
                    
                    readability = analyzer.analyze_readability(text)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Flesch Reading Ease", readability['flesch_score'])
                        st.metric("Flesch-Kincaid Grade", readability['fk_grade'])
                    
                    with col2:
                        st.metric("Readability Level", readability['level'])
                    
                    # Readability recommendations
                    st.subheader("Readability Tips")
                    if readability['flesch_score'] < 60:
                        st.warning("Consider simplifying your language for better readability.")
                    else:
                        st.success("Your resume has good readability!")
                
                with tab5:
                    st.subheader("Contact Information")
                    
                    contact_info = analyzer.extract_contact_info(text)
                    
                    if contact_info['emails']:
                        st.write("📧 **Emails:**", ", ".join(contact_info['emails']))
                    
                    if contact_info['phones']:
                        st.write("📱 **Phones:**", ", ".join(contact_info['phones']))
                    
                    if contact_info['linkedin']:
                        st.write("🔗 **LinkedIn:**", ", ".join(contact_info['linkedin']))
                    
                    if contact_info['github']:
                        st.write("💻 **GitHub:**", ", ".join(contact_info['github']))
                    
                    # Check for missing contact info
                    missing_contact = []
                    if not contact_info['emails']:
                        missing_contact.append("Email")
                    if not contact_info['phones']:
                        missing_contact.append("Phone")
                    if not contact_info['linkedin']:
                        missing_contact.append("LinkedIn")
                    
                    if missing_contact:
                        st.warning(f"Missing contact information: {', '.join(missing_contact)}")
            
            elif analysis_type == "Job Matching":
                st.header("🎯 Job Matching Analysis")
                
                job_description = st.text_area(
                    "Paste the job description here:",
                    height=200,
                    placeholder="Paste the job description you want to match against..."
                )
                
                if job_description:
                    match_result = analyzer.match_job_description(text, job_description)
                    
                    # Match score
                    score_color = "green" if match_result['match_percentage'] >= 70 else "orange" if match_result['match_percentage'] >= 50 else "red"
                    st.markdown(f"### Match Score: <span style='color: {score_color}'>{match_result['match_percentage']}%</span>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Job Keywords", match_result['total_job_keywords'])
                        st.metric("Matched Keywords", match_result['matched_keywords'])
                    
                    with col2:
                        st.subheader("Common Keywords")
                        if match_result['common_keywords']:
                            st.write(", ".join(match_result['common_keywords'][:20]))
                        else:
                            st.info("No common keywords found")
                    
                    # Missing keywords
                    st.subheader("Missing Keywords (Top 20)")
                    if match_result['missing_keywords']:
                        missing_df = pd.DataFrame(match_result['missing_keywords'], columns=['Keywords'])
                        st.dataframe(missing_df, use_container_width=True)
                    else:
                        st.success("No missing keywords!")
            
            elif analysis_type == "Skill Gap Analysis":
                st.header("📈 Skill Gap Analysis")
                
                if 'selected_role' in locals():
                    role_info = analyzer.available_roles[selected_role]
                    required_skills = role_info['skills']
                    
                    current_skills = analyzer.extract_skills(text)
                    
                    # Flatten current skills
                    all_current_skills = []
                    for skill_list in current_skills.values():
                        all_current_skills.extend([skill.lower() for skill in skill_list])
                    
                    # Calculate gaps
                    missing_skills = [skill for skill in required_skills if skill not in all_current_skills]
                    matching_skills = [skill for skill in required_skills if skill in all_current_skills]
                    
                    # Skill completion percentage
                    completion_percentage = (len(matching_skills) / len(required_skills)) * 100
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Skills Matched", len(matching_skills))
                    with col2:
                        st.metric("Skills Missing", len(missing_skills))
                    with col3:
                        st.metric("Completion Rate", f"{completion_percentage:.1f}%")
                    
                    # Progress bar
                    st.progress(completion_percentage / 100)
                    
                    # Skills breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Skills You Have")
                        if matching_skills:
                            for skill in matching_skills:
                                st.success(f"• {skill.title()}")
                        else:
                            st.info("No matching skills found")
                    
                    with col2:
                        st.subheader("❌ Skills to Develop")
                        if missing_skills:
                            for skill in missing_skills:
                                st.error(f"• {skill.title()}")
                        else:
                            st.success("All skills covered!")
                    
                    # Recommendations
                    st.subheader("🎯 Learning Recommendations")
                    if missing_skills:
                        priority_skills = missing_skills[:5]  # Top 5 priority skills
                        st.write("**Priority Skills to Learn:**")
                        for i, skill in enumerate(priority_skills, 1):
                            st.write(f"{i}. **{skill.title()}** - High demand for {selected_role}")
                    
                    # Skill progress chart
                    if matching_skills or missing_skills:
                        skill_data = pd.DataFrame({
                            'Skill': [skill.title() for skill in required_skills],
                            'Status': ['Have' if skill in all_current_skills else 'Need' for skill in required_skills]
                        })
                        
                        fig = px.histogram(
                            skill_data, 
                            x='Status', 
                            title=f"Skill Status for {selected_role}",
                            color='Status',
                            color_discrete_map={'Have': 'green', 'Need': 'red'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select a target role from the sidebar")
            
            elif analysis_type == "Role Explorer":
                st.header("🔍 Role Explorer")
                
                if 'selected_role' in locals():
                    role_info = analyzer.available_roles[selected_role]
                    
                    st.subheader(f"🎯 {selected_role}")
                    st.write(role_info['description'])
                    
                    # Role requirements
                    st.subheader("📋 Required Skills")
                    skills_df = pd.DataFrame(role_info['skills'], columns=['Skill'])
                    skills_df['Skill'] = skills_df['Skill'].str.title()
                    st.dataframe(skills_df, use_container_width=True, hide_index=True)
                    
                    # Compare with your resume
                    if text:
                        st.subheader("📊 Your Match Analysis")
                        current_skills = analyzer.extract_skills(text)
                        
                        # Flatten current skills
                        all_current_skills = []
                        for skill_list in current_skills.values():
                            all_current_skills.extend([skill.lower() for skill in skill_list])
                        
                        # Calculate match
                        matching_skills = [skill for skill in role_info['skills'] if skill in all_current_skills]
                        match_percentage = (len(matching_skills) / len(role_info['skills'])) * 100
                        
                        # Match visualization
                        match_color = "green" if match_percentage >= 70 else "orange" if match_percentage >= 50 else "red"
                        st.markdown(f"### Match Score: <span style='color: {match_color}'>{match_percentage:.1f}%</span>", unsafe_allow_html=True)
                        
                        # Detailed breakdown
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**✅ Skills You Have:**")
                            for skill in matching_skills:
                                st.write(f"• {skill.title()}")
                        
                        with col2:
                            missing_skills = [skill for skill in role_info['skills'] if skill not in all_current_skills]
                            st.write("**❌ Skills to Develop:**")
                            for skill in missing_skills:
                                st.write(f"• {skill.title()}")
                    
                    # Role comparison
                    st.subheader("🔄 Compare with Other Roles")
                    
                    # Show similar roles
                    if text:
                        role_matches = {}
                        for role, info in analyzer.available_roles.items():
                            if role != selected_role:
                                matching = [skill for skill in info['skills'] if skill in all_current_skills]
                                match_pct = (len(matching) / len(info['skills'])) * 100
                                role_matches[role] = match_pct
                        
                        # Sort by match percentage
                        sorted_roles = sorted(role_matches.items(), key=lambda x: x[1], reverse=True)[:5]
                        
                        st.write("**Top 5 Alternative Roles Based on Your Skills:**")
                        for role, match_pct in sorted_roles:
                            st.write(f"• **{role}**: {match_pct:.1f}% match")
                
                else:
                    st.info("Please select a role from the sidebar to explore")
            
            elif analysis_type == "Skill Gap Analysis":
                st.header("📈 Skill Gap Analysis")
                
                target_role = st.selectbox(
                    "Select target role:",
                    list(analyzer.available_roles.keys()),
                    help="Choose the role you want to analyze against"
                )
                
                if target_role:
                    role_info = analyzer.available_roles[target_role]
                    required_skills = role_info['skills']
                    
                    current_skills = analyzer.extract_skills(text)
                    
                    # Flatten current skills
                    all_current_skills = []
                    for skill_list in current_skills.values():
                        all_current_skills.extend([skill.lower() for skill in skill_list])
                    
                    # Calculate gaps
                    missing_skills = [skill for skill in required_skills if skill not in all_current_skills]
                    matching_skills = [skill for skill in required_skills if skill in all_current_skills]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Skills You Have")
                        for skill in matching_skills:
                            st.write(f"• {skill.title()}")
                    
                    with col2:
                        st.subheader("❌ Skills to Develop")
                        for skill in missing_skills:
                            st.write(f"• {skill.title()}")
                    
                    # Skill completion percentage
                    completion_percentage = (len(matching_skills) / len(required_skills)) * 100
                    st.metric("Skill Completion", f"{completion_percentage:.1f}%")
                    st.progress(completion_percentage / 100)
            
            elif analysis_type == "Industry Insights":
                st.header("🏢 Industry Insights")
                
                detected_industry = analyzer.detect_industry(text)
                st.subheader(f"Detected Industry: {detected_industry}")
                
                # Industry-specific recommendations
                st.subheader("Industry-Specific Recommendations")
                
                recommendations = {
                    "Software Development": [
                        "Include GitHub profile with active repositories",
                        "Mention specific programming languages and frameworks",
                        "Highlight any open-source contributions",
                        "Include technical project details"
                    ],
                    "Data Science": [
                        "Include links to data science portfolios",
                        "Mention specific ML/AI frameworks",
                        "Highlight statistical analysis experience",
                        "Include quantifiable results from data projects"
                    ],
                    "Marketing": [
                        "Include campaign performance metrics",
                        "Mention digital marketing certifications",
                        "Highlight multi-channel campaign experience",
                        "Include social media management experience"
                    ],
                    "Finance": [
                        "Include relevant financial certifications",
                        "Mention specific financial software experience",
                        "Highlight quantitative analysis skills",
                        "Include regulatory compliance experience"
                    ]
                }
                
                if detected_industry in recommendations:
                    for rec in recommendations[detected_industry]:
                        st.write(f"• {rec}")
                else:
                    st.info("General recommendations: Focus on quantifiable achievements and relevant keywords.")
        
        else:
            st.error("Could not extract text from the uploaded file. Please try another file.")
    
    # Footer
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
