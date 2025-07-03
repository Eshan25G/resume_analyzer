import streamlit as st
import pandas as pd
import re
from collections import Counter
import PyPDF2
import docx
from io import BytesIO
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import plotly.express as px
import plotly.graph_objects as go

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Common skills and categories
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'bootstrap'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'data': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'tensorflow', 'pytorch', 'sklearn', 'tableau', 'powerbi'],
            'tools': ['git', 'jira', 'confluence', 'jenkins', 'gitlab', 'github']
        }
        
        # Common soft skills
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem-solving', 'analytical',
            'creative', 'adaptable', 'organized', 'detail-oriented', 'collaborative'
        ]
        
        # Education keywords
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'education', 'diploma', 'certification', 'course'
        ]
        
        # Experience keywords
        self.experience_keywords = [
            'experience', 'work', 'employment', 'job', 'position', 'role',
            'responsibilities', 'achievements', 'projects'
        ]

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
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
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""

    def extract_contact_info(self, text):
        """Extract contact information from text"""
        contact_info = {}
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['emails'] = emails
        
        # Phone regex
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact_info['phones'] = phones
        
        # LinkedIn regex
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        contact_info['linkedin'] = linkedin
        
        return contact_info

    def extract_skills(self, text):
        """Extract technical and soft skills from text"""
        text_lower = text.lower()
        found_skills = {'technical': {}, 'soft': []}
        
        # Technical skills
        for category, skills in self.technical_skills.items():
            found_skills['technical'][category] = []
            for skill in skills:
                if skill in text_lower:
                    found_skills['technical'][category].append(skill)
        
        # Soft skills
        for skill in self.soft_skills:
            if skill in text_lower or skill.replace('-', ' ') in text_lower:
                found_skills['soft'].append(skill)
        
        return found_skills

    def calculate_resume_score(self, text, skills):
        """Calculate a basic resume score"""
        score = 0
        max_score = 100
        
        # Contact information (20 points)
        contact_info = self.extract_contact_info(text)
        if contact_info['emails']:
            score += 10
        if contact_info['phones']:
            score += 10
        
        # Skills (40 points)
        total_technical_skills = sum(len(skills_list) for skills_list in skills['technical'].values())
        score += min(total_technical_skills * 2, 30)  # Max 30 points for technical skills
        score += min(len(skills['soft']) * 2, 10)  # Max 10 points for soft skills
        
        # Education keywords (20 points)
        education_score = sum(1 for keyword in self.education_keywords if keyword in text.lower())
        score += min(education_score * 5, 20)
        
        # Experience keywords (20 points)
        experience_score = sum(1 for keyword in self.experience_keywords if keyword in text.lower())
        score += min(experience_score * 3, 20)
        
        return min(score, max_score)

    def get_word_frequency(self, text):
        """Get word frequency analysis"""
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha() and word not in self.stop_words]
        return Counter(words)

def main():
    st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
    
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume to get detailed analysis and insights!")
    
    analyzer = ResumeAnalyzer()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a resume file", 
        type=['pdf', 'docx', 'txt'],
        help="Upload PDF, DOCX, or TXT files"
    )
    
    if uploaded_file is not None:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            text = analyzer.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = analyzer.extract_text_from_docx(uploaded_file)
        else:  # txt file
            text = str(uploaded_file.read(), "utf-8")
        
        if text:
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", "🎯 Skills Analysis", "📞 Contact Info", 
                "📈 Word Frequency", "💡 Recommendations"
            ])
            
            with tab1:
                st.header("Resume Overview")
                
                # Basic stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Word Count", len(text.split()))
                
                with col2:
                    st.metric("Character Count", len(text))
                
                with col3:
                    # Calculate resume score
                    skills = analyzer.extract_skills(text)
                    score = analyzer.calculate_resume_score(text, skills)
                    st.metric("Resume Score", f"{score}/100")
                
                with col4:
                    # Estimate reading time
                    reading_time = max(1, len(text.split()) // 200)
                    st.metric("Reading Time", f"{reading_time} min")
                
                # Score gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Resume Score"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                
                # Preview text
                st.subheader("Resume Preview")
                st.text_area("", text[:1000] + "..." if len(text) > 1000 else text, height=200)
            
            with tab2:
                st.header("Skills Analysis")
                
                skills = analyzer.extract_skills(text)
                
                # Technical skills
                st.subheader("Technical Skills")
                tech_skills_found = False
                for category, skills_list in skills['technical'].items():
                    if skills_list:
                        tech_skills_found = True
                        st.write(f"**{category.title()}:** {', '.join(skills_list)}")
                
                if not tech_skills_found:
                    st.write("No technical skills detected.")
                
                # Soft skills
                st.subheader("Soft Skills")
                if skills['soft']:
                    st.write(f"**Found:** {', '.join(skills['soft'])}")
                else:
                    st.write("No soft skills detected.")
                
                # Skills distribution chart
                if any(skills['technical'].values()):
                    skill_counts = {cat: len(skills_list) for cat, skills_list in skills['technical'].items() if skills_list}
                    if skill_counts:
                        fig = px.bar(
                            x=list(skill_counts.keys()),
                            y=list(skill_counts.values()),
                            title="Technical Skills Distribution",
                            labels={'x': 'Skill Category', 'y': 'Number of Skills'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.header("Contact Information")
                
                contact_info = analyzer.extract_contact_info(text)
                
                if contact_info['emails']:
                    st.subheader("📧 Email Addresses")
                    for email in contact_info['emails']:
                        st.write(f"• {email}")
                
                if contact_info['phones']:
                    st.subheader("📱 Phone Numbers")
                    for phone in contact_info['phones']:
                        st.write(f"• {phone}")
                
                if contact_info['linkedin']:
                    st.subheader("💼 LinkedIn Profile")
                    for linkedin in contact_info['linkedin']:
                        st.write(f"• {linkedin}")
                
                if not any(contact_info.values()):
                    st.write("No contact information detected.")
            
            with tab4:
                st.header("Word Frequency Analysis")
                
                word_freq = analyzer.get_word_frequency(text)
                
                if word_freq:
                    # Top 20 words
                    top_words = word_freq.most_common(20)
                    
                    # Create bar chart
                    words, counts = zip(*top_words)
                    fig = px.bar(
                        x=list(counts),
                        y=list(words),
                        orientation='h',
                        title="Top 20 Most Frequent Words",
                        labels={'x': 'Frequency', 'y': 'Words'}
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Word frequency table
                    st.subheader("Word Frequency Table")
                    freq_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                    st.dataframe(freq_df, use_container_width=True)
            
            with tab5:
                st.header("Recommendations")
                
                recommendations = []
                
                # Check contact info
                if not contact_info['emails']:
                    recommendations.append("✉️ Add an email address to your resume")
                if not contact_info['phones']:
                    recommendations.append("📞 Include a phone number for easy contact")
                if not contact_info['linkedin']:
                    recommendations.append("💼 Add your LinkedIn profile URL")
                
                # Check skills
                total_skills = sum(len(skills_list) for skills_list in skills['technical'].values())
                if total_skills < 5:
                    recommendations.append("🔧 Add more technical skills relevant to your field")
                
                if len(skills['soft']) < 3:
                    recommendations.append("🤝 Include more soft skills (leadership, communication, etc.)")
                
                # Check resume length
                word_count = len(text.split())
                if word_count < 200:
                    recommendations.append("📝 Your resume seems short. Consider adding more details about your experience")
                elif word_count > 800:
                    recommendations.append("✂️ Your resume might be too long. Consider condensing it")
                
                # Display recommendations
                if recommendations:
                    st.subheader("Areas for Improvement")
                    for rec in recommendations:
                        st.write(f"• {rec}")
                else:
                    st.success("🎉 Great job! Your resume looks comprehensive.")
                
                # General tips
                st.subheader("General Tips")
                tips = [
                    "Use action verbs to describe your experience",
                    "Quantify your achievements with numbers when possible",
                    "Tailor your resume to each job application",
                    "Keep formatting consistent throughout",
                    "Proofread for spelling and grammar errors",
                    "Use bullet points for easy readability"
                ]
                
                for tip in tips:
                    st.write(f"💡 {tip}")
    
    else:
        st.info("👆 Please upload a resume file to get started!")
        
        # Show sample analysis
        st.subheader("What This Analyzer Does")
        features = [
            "📊 **Overview**: Basic statistics and overall resume score",
            "🎯 **Skills Analysis**: Detects technical and soft skills",
            "📞 **Contact Info**: Extracts email, phone, and LinkedIn",
            "📈 **Word Frequency**: Shows most common words used",
            "💡 **Recommendations**: Provides improvement suggestions"
        ]
        
        for feature in features:
            st.write(feature)

if __name__ == "__main__":
    main()
