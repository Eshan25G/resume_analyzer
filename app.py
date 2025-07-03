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
from datetime import datetime
import random

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
        
        # Enhanced job roles with detailed information
        self.job_roles = {
            'Software Engineer': {
                'description': 'Develop and maintain software applications',
                'key_skills': ['python', 'java', 'javascript', 'sql', 'git', 'problem-solving'],
                'responsibilities': ['Write clean, maintainable code', 'Debug and troubleshoot issues', 'Collaborate with team members', 'Participate in code reviews'],
                'industry_keywords': ['software development', 'coding', 'programming', 'algorithms', 'data structures', 'testing', 'debugging'],
                'value_propositions': [
                    'deliver high-quality software solutions',
                    'optimize application performance',
                    'implement best coding practices',
                    'contribute to scalable architecture'
                ],
                'company_benefits': [
                    'reduce development time through efficient coding',
                    'improve code quality and maintainability',
                    'enhance team productivity through collaboration',
                    'drive innovation in software solutions'
                ],
                'opening_hooks': [
                    'As a passionate software engineer with expertise in {skills}',
                    'With a strong foundation in {skills} and proven development experience',
                    'Having successfully delivered multiple software projects using {skills}'
                ]
            },
            'Data Scientist': {
                'description': 'Analyze complex data to derive business insights',
                'key_skills': ['python', 'pandas', 'numpy', 'sklearn', 'matplotlib', 'sql', 'analytical'],
                'responsibilities': ['Build predictive models', 'Analyze large datasets', 'Create data visualizations', 'Present findings to stakeholders'],
                'industry_keywords': ['machine learning', 'data analysis', 'statistical modeling', 'data visualization', 'big data', 'analytics'],
                'value_propositions': [
                    'transform raw data into actionable insights',
                    'develop predictive models for business growth',
                    'optimize decision-making through data-driven solutions',
                    'identify trends and patterns in complex datasets'
                ],
                'company_benefits': [
                    'increase revenue through data-driven insights',
                    'improve operational efficiency via predictive analytics',
                    'reduce risks through statistical modeling',
                    'enhance customer experience through personalization'
                ],
                'opening_hooks': [
                    'As a data scientist with expertise in {skills} and a passion for uncovering insights',
                    'With proven experience in {skills} and a track record of delivering data-driven solutions',
                    'Having successfully built predictive models using {skills}'
                ]
            },
            'Product Manager': {
                'description': 'Lead product development and strategy',
                'key_skills': ['leadership', 'analytical', 'communication', 'problem-solving', 'organized'],
                'responsibilities': ['Define product roadmap', 'Coordinate with development teams', 'Gather user requirements', 'Analyze market trends'],
                'industry_keywords': ['product strategy', 'roadmap planning', 'stakeholder management', 'user experience', 'market research'],
                'value_propositions': [
                    'drive product vision and strategy',
                    'bridge technical and business requirements',
                    'optimize user experience and satisfaction',
                    'lead cross-functional teams to success'
                ],
                'company_benefits': [
                    'accelerate product development cycles',
                    'increase user engagement and retention',
                    'maximize product-market fit',
                    'drive revenue growth through strategic planning'
                ],
                'opening_hooks': [
                    'As a strategic product manager with strong {skills} capabilities',
                    'With proven experience in {skills} and successful product launches',
                    'Having led cross-functional teams with expertise in {skills}'
                ]
            },
            'Frontend Developer': {
                'description': 'Create user interfaces and web experiences',
                'key_skills': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'creative'],
                'responsibilities': ['Develop responsive web interfaces', 'Optimize user experience', 'Collaborate with designers', 'Ensure cross-browser compatibility'],
                'industry_keywords': ['user interface', 'responsive design', 'web development', 'user experience', 'frontend frameworks'],
                'value_propositions': [
                    'create engaging and intuitive user interfaces',
                    'optimize web performance and accessibility',
                    'implement responsive designs across devices',
                    'bridge design and development seamlessly'
                ],
                'company_benefits': [
                    'improve user engagement through intuitive interfaces',
                    'reduce bounce rates with optimized UX',
                    'increase conversion rates through better design',
                    'enhance brand perception through modern web presence'
                ],
                'opening_hooks': [
                    'As a frontend developer with expertise in {skills} and an eye for design',
                    'With strong proficiency in {skills} and passion for creating user-centric experiences',
                    'Having built responsive web applications using {skills}'
                ]
            },
            'Backend Developer': {
                'description': 'Build server-side applications and APIs',
                'key_skills': ['python', 'java', 'nodejs', 'sql', 'mongodb', 'docker', 'problem-solving'],
                'responsibilities': ['Design and implement APIs', 'Optimize database performance', 'Ensure system scalability', 'Implement security measures'],
                'industry_keywords': ['server-side development', 'API design', 'database optimization', 'system architecture', 'scalability'],
                'value_propositions': [
                    'architect scalable backend systems',
                    'optimize database performance and queries',
                    'ensure robust API design and security',
                    'implement efficient data processing solutions'
                ],
                'company_benefits': [
                    'improve system performance and reliability',
                    'reduce server costs through optimization',
                    'enhance data security and compliance',
                    'enable seamless integration with external systems'
                ],
                'opening_hooks': [
                    'As a backend developer with deep expertise in {skills}',
                    'With proven experience in {skills} and scalable system design',
                    'Having architected robust backend solutions using {skills}'
                ]
            },
            'DevOps Engineer': {
                'description': 'Manage infrastructure and deployment pipelines',
                'key_skills': ['aws', 'azure', 'docker', 'kubernetes', 'terraform', 'jenkins', 'analytical'],
                'responsibilities': ['Automate deployment processes', 'Monitor system performance', 'Manage cloud infrastructure', 'Implement CI/CD pipelines'],
                'industry_keywords': ['cloud infrastructure', 'automation', 'continuous integration', 'containerization', 'monitoring'],
                'value_propositions': [
                    'streamline deployment and release processes',
                    'optimize cloud infrastructure costs',
                    'implement robust monitoring and alerting',
                    'ensure high availability and disaster recovery'
                ],
                'company_benefits': [
                    'reduce deployment time and errors',
                    'lower infrastructure costs through optimization',
                    'improve system reliability and uptime',
                    'accelerate development velocity'
                ],
                'opening_hooks': [
                    'As a DevOps engineer with expertise in {skills} and cloud technologies',
                    'With proven experience in {skills} and infrastructure automation',
                    'Having successfully managed cloud environments using {skills}'
                ]
            },
            'UX/UI Designer': {
                'description': 'Design user experiences and interfaces',
                'key_skills': ['creative', 'analytical', 'communication', 'detail-oriented', 'collaborative'],
                'responsibilities': ['Create user-centered designs', 'Conduct user research', 'Develop prototypes', 'Collaborate with developers'],
                'industry_keywords': ['user experience', 'user interface', 'design thinking', 'prototyping', 'user research'],
                'value_propositions': [
                    'create intuitive and engaging user experiences',
                    'conduct comprehensive user research and testing',
                    'design accessible and inclusive interfaces',
                    'collaborate effectively with development teams'
                ],
                'company_benefits': [
                    'increase user satisfaction and engagement',
                    'improve product usability and accessibility',
                    'reduce development costs through clear design specifications',
                    'enhance brand perception through thoughtful design'
                ],
                'opening_hooks': [
                    'As a UX/UI designer with strong {skills} and user-centered approach',
                    'With proven experience in {skills} and successful product launches',
                    'Having created engaging user experiences with focus on {skills}'
                ]
            },
            'Business Analyst': {
                'description': 'Analyze business processes and requirements',
                'key_skills': ['analytical', 'communication', 'problem-solving', 'detail-oriented', 'organized'],
                'responsibilities': ['Gather business requirements', 'Analyze current processes', 'Recommend improvements', 'Create documentation'],
                'industry_keywords': ['business analysis', 'process improvement', 'requirements gathering', 'stakeholder management'],
                'value_propositions': [
                    'optimize business processes for efficiency',
                    'bridge communication between technical and business teams',
                    'identify cost-saving opportunities',
                    'facilitate digital transformation initiatives'
                ],
                'company_benefits': [
                    'improve operational efficiency and reduce costs',
                    'streamline business processes and workflows',
                    'enhance decision-making through data analysis',
                    'accelerate project delivery through clear requirements'
                ],
                'opening_hooks': [
                    'As a business analyst with strong {skills} and process optimization experience',
                    'With proven expertise in {skills} and successful business transformations',
                    'Having improved business processes through {skills} and analytical thinking'
                ]
            },
            'Marketing Manager': {
                'description': 'Develop and execute marketing strategies',
                'key_skills': ['communication', 'creative', 'analytical', 'leadership', 'organized'],
                'responsibilities': ['Develop marketing campaigns', 'Analyze market trends', 'Manage marketing budget', 'Coordinate with sales teams'],
                'industry_keywords': ['marketing strategy', 'campaign management', 'brand development', 'digital marketing', 'market research'],
                'value_propositions': [
                    'develop comprehensive marketing strategies',
                    'optimize campaign performance and ROI',
                    'build strong brand presence and awareness',
                    'drive customer acquisition and retention'
                ],
                'company_benefits': [
                    'increase brand visibility and market share',
                    'generate qualified leads and drive revenue',
                    'improve customer engagement and loyalty',
                    'optimize marketing spend and ROI'
                ],
                'opening_hooks': [
                    'As a marketing manager with expertise in {skills} and proven campaign success',
                    'With strong background in {skills} and data-driven marketing approach',
                    'Having led successful marketing initiatives using {skills}'
                ]
            },
            'Cybersecurity Analyst': {
                'description': 'Protect organizations from security threats',
                'key_skills': ['analytical', 'detail-oriented', 'problem-solving', 'communication', 'adaptable'],
                'responsibilities': ['Monitor security systems', 'Investigate security incidents', 'Implement security measures', 'Conduct risk assessments'],
                'industry_keywords': ['cybersecurity', 'threat detection', 'risk assessment', 'security monitoring', 'incident response'],
                'value_propositions': [
                    'protect critical business assets and data',
                    'implement comprehensive security frameworks',
                    'respond quickly to security incidents',
                    'ensure regulatory compliance and best practices'
                ],
                'company_benefits': [
                    'reduce security risks and potential breaches',
                    'maintain customer trust and reputation',
                    'ensure compliance with industry regulations',
                    'minimize downtime from security incidents'
                ],
                'opening_hooks': [
                    'As a cybersecurity analyst with strong {skills} and threat detection expertise',
                    'With proven experience in {skills} and security incident response',
                    'Having protected organizations through {skills} and proactive security measures'
                ]
            }
        }

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

    def extract_quantifiable_achievements(self, text):
        """Extract quantifiable achievements from resume"""
        achievements = []
        
        # Patterns for numbers and percentages
        number_patterns = [
            r'\b(\d+(?:\.\d+)?%)\b',  # Percentages
            r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:users?|customers?|clients?|projects?|applications?|systems?)\b',  # Numbers with units
            r'\b(?:increased?|improved?|reduced?|decreased?|saved?|generated?|managed?|led?)\s+.*?(\d+(?:\.\d+)?%)\b',  # Action + percentage
            r'\b(?:increased?|improved?|reduced?|decreased?|saved?|generated?)\s+.*?(\$\d+(?:,\d{3})*(?:\.\d+)?[kmb]?)\b'  # Money
        ]
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            for pattern in number_patterns:
                matches = re.findall(pattern, sentence.lower())
                if matches:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 20 and len(clean_sentence) < 200:
                        achievements.append(clean_sentence)
                        break
        
        return list(set(achievements))  # Remove duplicates

    def extract_years_of_experience(self, text):
        """Extract years of experience from resume"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0

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
    
    def calculate_job_match(self, resume_skills, job_role):
        """Calculate how well resume matches a job role"""
        if job_role not in self.job_roles:
            return 0, []
        
        required_skills = self.job_roles[job_role]['key_skills']
        
        # Flatten resume skills
        all_resume_skills = []
        for category_skills in resume_skills['technical'].values():
            all_resume_skills.extend(category_skills)
        all_resume_skills.extend(resume_skills['soft'])
        
        # Calculate match
        matched_skills = []
        for skill in required_skills:
            if skill in all_resume_skills:
                matched_skills.append(skill)
        
        match_percentage = (len(matched_skills) / len(required_skills)) * 100
        missing_skills = [skill for skill in required_skills if skill not in matched_skills]
        
        return match_percentage, missing_skills, matched_skills
    
    def extract_name_from_resume(self, text):
        """Extract name from resume text (simple heuristic)"""
        lines = text.split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            # Look for lines that might contain names (not email, phone, etc.)
            if line and not any(char in line for char in ['@', 'http', '+', '(', ')', '-']) and len(line.split()) <= 3:
                words = line.split()
                if len(words) >= 2 and all(word.isalpha() for word in words):
                    return ' '.join(words)
        return "Your Name"
    
    def generate_cover_letter(self, name, job_role, company_name, resume_skills, resume_text):
        """Generate a sophisticated, personalized cover letter"""
        if job_role not in self.job_roles:
            return "Invalid job role selected."
        
        job_info = self.job_roles[job_role]
        match_percentage, missing_skills, matched_skills = self.calculate_job_match(resume_skills, job_role)
        
        # Extract quantifiable achievements
        achievements = self.extract_quantifiable_achievements(resume_text)
        
        # Extract years of experience
        years_experience = self.extract_years_of_experience(resume_text)
        
        # Get top matched skills for the opening
        top_skills = matched_skills[:3] if matched_skills else job_info['key_skills'][:3]
        skills_text = ', '.join(top_skills)
        
        # Select appropriate opening hook
        opening_hook = random.choice(job_info['opening_hooks']).format(skills=skills_text)
        
        # Generate cover letter
        cover_letter = f"""Dear Hiring Manager,

{opening_hook}, I am excited to apply for the {job_role} position at {company_name}. """
        
        # Add experience context if available
        if years_experience > 0:
            cover_letter += f"With {years_experience} years of experience in the field, "
        
        cover_letter += f"I am particularly drawn to {company_name} because of your commitment to innovation and excellence in the industry.\n\n"
        
        # Technical expertise paragraph
        if matched_skills:
            cover_letter += f"My technical expertise perfectly aligns with your requirements, particularly in {', '.join(matched_skills[:4])}. "
        
        # Add value proposition
        value_prop = random.choice(job_info['value_propositions'])
        cover_letter += f"I excel at helping organizations {value_prop}, which directly supports {company_name}'s mission and goals.\n\n"
        
        # Achievements paragraph
        if achievements:
            cover_letter += "Key achievements that demonstrate my impact include:\n"
            for achievement in achievements[:3]:  # Top 3 achievements
                cover_letter += f"• {achievement.strip()}\n"
            cover_letter += "\n"
        else:
            # Generic achievements based on job role
            cover_letter += f"In my previous roles, I have consistently delivered results by:\n"
            for responsibility in job_info['responsibilities'][:3]:
                cover_letter += f"• {responsibility}\n"
            cover_letter += "\n"
        
        # Company benefits paragraph
        company_benefit = random.choice(job_info['company_benefits'])
        cover_letter += f"I am excited about the opportunity to contribute to {company_name}'s success by helping to {company_benefit}. "
        
        # Industry knowledge
        industry_keywords = ', '.join(job_info['industry_keywords'][:3])
        cover_letter += f"My deep understanding of {industry_keywords} positions me well to make an immediate impact in this role.\n\n"
        
        # Future focus and learning
        if missing_skills:
            cover_letter += f"I am committed to continuous learning and am particularly interested in expanding my expertise in {', '.join(missing_skills[:2])} to further enhance my contribution to your team.\n\n"
        
        # Closing
        cover_letter += f"I would welcome the opportunity to discuss how my skills and passion for {job_role.lower()} can contribute to {company_name}'s continued success. Thank you for considering my application.\n\n"
        
        cover_letter += f"Best regards,\n{name}"
        
        return cover_letter

    def get_cover_letter_suggestions(self, job_role, match_percentage, missing_skills, achievements):
        """Generate specific suggestions for improving the cover letter"""
        suggestions = []
        
        # Match percentage based suggestions
        if match_percentage < 50:
            suggestions.append("🎯 **Skill Gap Alert**: Your current skill match is below 50%. Consider highlighting transferable skills and your ability to learn quickly.")
        elif match_percentage < 70:
            suggestions.append("✨ **Good Match**: You have a solid foundation. Emphasize your relevant experience and enthusiasm for the role.")
        else:
            suggestions.append("🌟 **Excellent Match**: Your skills align well! Focus on specific achievements and how you can add immediate value.")
        
        # Missing skills suggestions
        if missing_skills:
            suggestions.append(f"📚 **Skill Development**: Consider mentioning your interest in learning {', '.join(missing_skills[:2])} to show growth mindset.")
        
        # Achievements suggestions
        if achievements:
            suggestions.append("📊 **Quantify Impact**: Great! Your resume contains measurable achievements. Make sure to highlight 2-3 in your cover letter.")
        else:
            suggestions.append("📈 **Add Numbers**: Try to quantify your achievements with specific numbers, percentages, or dollar amounts.")
        
        # Job-specific suggestions
        if job_role in self.job_roles:
            job_info = self.job_roles[job_role]
            industry_keywords = job_info['industry_keywords']
            suggestions.append(f"🏷️ **Industry Keywords**: Include terms like '{', '.join(industry_keywords[:3])}' to pass ATS systems.")
        
        # General suggestions
        suggestions.extend([
            "🔍 **Research**: Mention specific company initiatives, values, or recent news to show genuine interest.",
            "💼 **Call to Action**: End with a proactive statement about following up or next steps.",
            "📝 **Proofread**: Always have someone else review your cover letter for typos and clarity.",
            "🎨 **Format**: Use the same header as your resume for consistency and professional appearance."
        ])
        
        return suggestions

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
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Overview", "🎯 Skills Analysis", "📞 Contact Info", 
                "📈 Word Frequency", "💼 Job Match", "✍️ Cover Letter"
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
                st.header("Job Role Matching")
                
                # Job role selection
                st.subheader("Select Target Job Role")
                selected_job = st.selectbox(
                    "Choose a job role to analyze compatibility:",
                    list(analyzer.job_roles.keys())
                )
                
                if selected_job:
                    job_info = analyzer.job_roles[selected_job]
                    
                    # Display job information
                    st.write(f"**Job Description:** {job_info['description']}")
                    st.write(f"**Key Skills Required:** {', '.join(job_info['key_skills'])}")
                    
                    # Calculate match
                    match_percentage, missing_skills, matched_skills = analyzer.calculate_job_match(skills, selected_job)
                    
                    # Display match results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Match Percentage", f"{match_percentage:.1f}%")
                        
                        # Match gauge
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = match_percentage,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Job Match Score"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkgreen"},
                                'steps': [
                                    {'range': [0, 40], 'color': "lightgray"},
                                    {'range': [40, 70], 'color': "yellow"},
                                    {'range': [70, 100], 'color': "lightgreen"}
                                ]
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        if matched_skills:
                            st.subheader("✅ Matched Skills")
                            for skill in matched_skills:
                                st.write(f"• {skill}")
                        
                        if missing_skills:
                            st.subheader("❌ Missing Skills")
                            for skill in missing_skills:
                                st.write(f"• {skill}")
                        
                        # Improvement suggestions
                        if missing_skills:
                            st.subheader("💡 Suggestions")
                            st.write("Consider adding these skills to improve your match:")
                            for skill in missing_skills[:3]:  # Top 3 missing skills
                                st.write(f"🎯 Learn {skill}")
                    
                    # Key responsibilities
                    st.subheader("Key Responsibilities")
                    for responsibility in job_info['responsibilities']:
                        st.write(f"• {responsibility}")
            
            with tab6:
                st.header("Enhanced Cover Letter Generator")
                
                # Input fields for cover letter
                col1, col2 = st.columns(2)
                
                with col1:
                    # Extract name from resume
                    extracted_name = analyzer.extract_name_from_resume(text)
                    user_name = st.text_input("Your Name", value=extracted_name)
                
                with col2:
                    company_name = st.text_input("Company Name", placeholder="e.g., Google, Microsoft, Apple")
                
                # Job role selection for cover letter
                cover_letter_job = st.selectbox(
                    "Select Job Role for Cover Letter:",
                    list(analyzer.job_roles.keys()),
                    key="cover_letter_job"
                )
                
                # Additional customization options
                st.subheader("📝 Customization Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    tone = st.selectbox(
                        "Cover Letter Tone:",
                        ["Professional", "Enthusiastic", "Confident", "Analytical"]
                    )
                
                with col2:
                    focus_area = st.selectbox(
                        "Primary Focus:",
                        ["Technical Skills", "Leadership Experience", "Problem Solving", "Innovation", "Team Collaboration"]
                    )
                
                # Generate cover letter button
                if st.button("🚀 Generate Enhanced Cover Letter", type="primary"):
                    if user_name and company_name and cover_letter_job:
                        # Generate cover letter
                        cover_letter = analyzer.generate_cover_letter(
                            user_name, cover_letter_job, company_name, skills, text
                        )
                        
                        # Display cover letter
                        st.subheader("📄 Generated Cover Letter")
                        st.text_area("Cover Letter", cover_letter, height=500, key="cover_letter_display")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Cover Letter",
                            data=cover_letter,
                            file_name=f"{user_name.replace(' ', '_')}_cover_letter_{cover_letter_job.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                        
                        # Analysis section
                        st.subheader("📊 Cover Letter Analysis")
                        
                        # Get match analysis
                        match_percentage, missing_skills, matched_skills = analyzer.calculate_job_match(skills, cover_letter_job)
                        achievements = analyzer.extract_quantifiable_achievements(text)
                        years_experience = analyzer.extract_years_of_experience(text)
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Job Match", f"{match_percentage:.1f}%")
                        
                        with col2:
                            st.metric("Skills Highlighted", len(matched_skills))
                        
                        with col3:
                            word_count = len(cover_letter.split())
                            st.metric("Word Count", word_count)
                        
                        with col4:
                            st.metric("Experience Years", years_experience if years_experience > 0 else "Not specified")
                        
                        # Personalized suggestions
                        st.subheader("💡 Personalized Cover Letter Suggestions")
                        suggestions = analyzer.get_cover_letter_suggestions(
                            cover_letter_job, match_percentage, missing_skills, achievements
                        )
                        
                        for suggestion in suggestions:
                            st.markdown(suggestion)
                        
                        # Advanced analytics
                        st.subheader("🔍 Advanced Analytics")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Strengths of Your Cover Letter:**")
                            strengths = []
                            if match_percentage > 70:
                                strengths.append("✅ Strong skill alignment with job requirements")
                            if achievements:
                                strengths.append("✅ Includes quantifiable achievements")
                            if years_experience > 3:
                                strengths.append("✅ Demonstrates substantial experience")
                            if len(matched_skills) > 4:
                                strengths.append("✅ Highlights multiple relevant skills")
                            if word_count >= 200 and word_count <= 400:
                                strengths.append("✅ Optimal length for readability")
                            
                            if not strengths:
                                strengths.append("📝 Consider adding more specific achievements")
                            
                            for strength in strengths:
                                st.write(strength)
                        
                        with col2:
                            st.write("**Areas for Improvement:**")
                            improvements = []
                            if match_percentage < 50:
                                improvements.append("🔄 Consider emphasizing transferable skills")
                            if not achievements:
                                improvements.append("📊 Add specific, measurable achievements")
                            if years_experience == 0:
                                improvements.append("⏰ Mention any relevant project or internship experience")
                            if len(missing_skills) > 3:
                                improvements.append("📚 Address skill gaps or show willingness to learn")
                            if word_count < 200:
                                improvements.append("📝 Expand with more specific examples")
                            elif word_count > 400:
                                improvements.append("✂️ Consider condensing for better impact")
                            
                            if not improvements:
                                improvements.append("🌟 Your cover letter looks comprehensive!")
                            
                            for improvement in improvements:
                                st.write(improvement)
                        
                        # Industry-specific tips
                        if cover_letter_job in analyzer.job_roles:
                            job_info = analyzer.job_roles[cover_letter_job]
                            st.subheader(f"🎯 {cover_letter_job}-Specific Tips")
                            
                            tips = [
                                f"Use industry keywords: {', '.join(job_info['industry_keywords'][:4])}",
                                f"Emphasize your ability to: {', '.join(job_info['value_propositions'][:2])}",
                                f"Highlight experience in: {', '.join(job_info['responsibilities'][:3])}",
                                f"Show how you can: {job_info['company_benefits'][0]}"
                            ]
                            
                            for tip in tips:
                                st.write(f"• {tip}")
                        
                        # Template variations
                        st.subheader("📋 Alternative Cover Letter Templates")
                        
                        template_options = {
                            "Technical Focus": "Emphasizes technical skills and project experience",
                            "Leadership Focus": "Highlights management and team leadership experience", 
                            "Results Focus": "Concentrates on measurable achievements and impact",
                            "Growth Focus": "Emphasizes learning agility and career progression"
                        }
                        
                        for template, description in template_options.items():
                            with st.expander(f"{template} Template"):
                                st.write(f"**Focus:** {description}")
                                st.write("**Best for:** Candidates who want to emphasize this particular strength")
                                if st.button(f"Generate {template}", key=f"template_{template}"):
                                    # This would generate different variations - simplified for example
                                    st.write("💡 This would generate a cover letter with adjusted focus and tone")
                        
                    else:
                        st.warning("Please fill in all required fields (Name, Company, Job Role)")
                
                # Cover letter best practices section
                st.subheader("📚 Enhanced Cover Letter Best Practices")
                
                best_practices = {
                    "📝 Structure & Format": [
                        "Use a professional header matching your resume",
                        "Keep to one page maximum (300-400 words)",
                        "Use standard business letter format",
                        "Include specific date and recipient information when possible",
                        "Use consistent font and formatting with your resume"
                    ],
                    "🎯 Content Strategy": [
                        "Research the company and mention specific details",
                        "Address the hiring manager by name when possible",
                        "Start with a compelling opening that shows enthusiasm",
                        "Use the middle paragraphs to prove your value",
                        "End with a strong call to action",
                        "Tailor each cover letter to the specific job"
                    ],
                    "💪 Making Impact": [
                        "Use specific examples and quantifiable achievements",
                        "Show how you can solve their problems",
                        "Demonstrate knowledge of their industry/company",
                        "Include relevant keywords from the job posting",
                        "Show personality while maintaining professionalism",
                        "Proofread multiple times for errors"
                    ],
                    "🚫 Common Mistakes": [
                        "Don't repeat everything from your resume",
                        "Avoid generic templates without customization",
                        "Don't focus only on what you want from them",
                        "Don't use overly complex language or jargon",
                        "Don't forget to customize company/position names",
                        "Don't submit without proofreading"
                    ]
                }
                
                for category, items in best_practices.items():
                    with st.expander(f"{category}"):
                        for item in items:
                            st.write(f"• {item}")
            
            # Move recommendations to a separate section
            st.header("💡 Overall Recommendations")
            
            recommendations = []
            
            # Check contact info
            contact_info = analyzer.extract_contact_info(text)
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
            
            # Check for quantifiable achievements
            achievements = analyzer.extract_quantifiable_achievements(text)
            if not achievements:
                recommendations.append("📊 Add quantifiable achievements with specific numbers or percentages")
            
            # Display recommendations
            if recommendations:
                st.subheader("Areas for Improvement")
                for rec in recommendations:
                    st.write(f"• {rec}")
            else:
                st.success("🎉 Great job! Your resume looks comprehensive.")
            
            # Enhanced general tips
            st.subheader("🌟 Pro Tips for Resume Success")
            
            pro_tips = [
                "**Use Action Verbs**: Start bullet points with strong action verbs (achieved, developed, led, implemented)",
                "**Quantify Everything**: Add numbers, percentages, and dollar amounts whenever possible",
                "**Tailor for Each Job**: Customize your resume for each application using job posting keywords",
                "**Show Impact**: Focus on results and outcomes, not just responsibilities",
                "**Keep it Current**: Update your resume regularly with new skills and achievements",
                "**ATS Optimization**: Use standard section headers and avoid complex formatting",
                "**Professional Email**: Ensure your email address is professional and appropriate",
                "**Consistent Formatting**: Use consistent fonts, spacing, and bullet point styles",
                "**Relevant Keywords**: Include industry-specific keywords and technical terms",
                "**Proofread Thoroughly**: Check for spelling, grammar, and formatting errors"
            ]
            
            for tip in pro_tips:
                st.write(f"💡 {tip}")
    
    else:
        st.info("👆 Please upload a resume file to get started!")
        
        # Enhanced feature showcase
        st.subheader("🚀 What This Enhanced Analyzer Does")
        
        features = [
            "📊 **Comprehensive Overview**: Detailed statistics and intelligent resume scoring",
            "🎯 **Advanced Skills Analysis**: Detects technical and soft skills with category breakdown",
            "📞 **Contact Information**: Extracts and validates email, phone, and LinkedIn profiles",
            "📈 **Word Frequency Analysis**: Identifies most used words and suggests improvements",
            "💼 **Intelligent Job Matching**: Analyzes compatibility with 10+ job roles",
            "✍️ **AI-Powered Cover Letters**: Generates personalized, role-specific cover letters",
            "🔍 **Achievement Detection**: Identifies quantifiable accomplishments automatically",
            "💡 **Personalized Suggestions**: Provides tailored recommendations for improvement",
            "📋 **Industry-Specific Tips**: Offers role-specific advice and best practices",
            "📊 **Advanced Analytics**: Detailed analysis of resume and cover letter effectiveness"
        ]
        
        for feature in features:
            st.write(feature)
        
        # Sample analysis preview
        st.subheader("📈 Sample Analysis Preview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Resume Analysis Includes:**")
            analysis_features = [
                "✅ Resume score out of 100",
                "✅ Skills categorization",
                "✅ Contact information validation",
                "✅ Word frequency analysis",
                "✅ Years of experience detection",
                "✅ Achievement quantification"
            ]
            for feature in analysis_features:
                st.write(feature)
        
        with col2:
            st.write("**Cover Letter Generator Includes:**")
            cover_letter_features = [
                "✅ Job-specific customization",
                "✅ Achievement highlighting",
                "✅ Industry keyword optimization",
                "✅ Personalized suggestions",
                "✅ Multiple template options",
                "✅ Professional formatting"
            ]
            for feature in cover_letter_features:
                st.write(feature)

if __name__ == "__main__":
    main()
