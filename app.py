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
        
        # Job roles and their requirements
        self.job_roles = {
            'Software Engineer': {
                'description': 'Develop and maintain software applications',
                'key_skills': ['python', 'java', 'javascript', 'sql', 'git', 'problem-solving'],
                'responsibilities': ['Write clean, maintainable code', 'Debug and troubleshoot issues', 'Collaborate with team members', 'Participate in code reviews']
            },
            'Data Scientist': {
                'description': 'Analyze complex data to derive business insights',
                'key_skills': ['python', 'pandas', 'numpy', 'sklearn', 'matplotlib', 'sql', 'analytical'],
                'responsibilities': ['Build predictive models', 'Analyze large datasets', 'Create data visualizations', 'Present findings to stakeholders']
            },
            'Product Manager': {
                'description': 'Lead product development and strategy',
                'key_skills': ['leadership', 'analytical', 'communication', 'problem-solving', 'organized'],
                'responsibilities': ['Define product roadmap', 'Coordinate with development teams', 'Gather user requirements', 'Analyze market trends']
            },
            'Frontend Developer': {
                'description': 'Create user interfaces and web experiences',
                'key_skills': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'creative'],
                'responsibilities': ['Develop responsive web interfaces', 'Optimize user experience', 'Collaborate with designers', 'Ensure cross-browser compatibility']
            },
            'Backend Developer': {
                'description': 'Build server-side applications and APIs',
                'key_skills': ['python', 'java', 'nodejs', 'sql', 'mongodb', 'docker', 'problem-solving'],
                'responsibilities': ['Design and implement APIs', 'Optimize database performance', 'Ensure system scalability', 'Implement security measures']
            },
            'DevOps Engineer': {
                'description': 'Manage infrastructure and deployment pipelines',
                'key_skills': ['aws', 'azure', 'docker', 'kubernetes', 'terraform', 'jenkins', 'analytical'],
                'responsibilities': ['Automate deployment processes', 'Monitor system performance', 'Manage cloud infrastructure', 'Implement CI/CD pipelines']
            },
            'UX/UI Designer': {
                'description': 'Design user experiences and interfaces',
                'key_skills': ['creative', 'analytical', 'communication', 'detail-oriented', 'collaborative'],
                'responsibilities': ['Create user-centered designs', 'Conduct user research', 'Develop prototypes', 'Collaborate with developers']
            },
            'Business Analyst': {
                'description': 'Analyze business processes and requirements',
                'key_skills': ['analytical', 'communication', 'problem-solving', 'detail-oriented', 'organized'],
                'responsibilities': ['Gather business requirements', 'Analyze current processes', 'Recommend improvements', 'Create documentation']
            },
            'Marketing Manager': {
                'description': 'Develop and execute marketing strategies',
                'key_skills': ['communication', 'creative', 'analytical', 'leadership', 'organized'],
                'responsibilities': ['Develop marketing campaigns', 'Analyze market trends', 'Manage marketing budget', 'Coordinate with sales teams']
            },
            'Cybersecurity Analyst': {
                'description': 'Protect organizations from security threats',
                'key_skills': ['analytical', 'detail-oriented', 'problem-solving', 'communication', 'adaptable'],
                'responsibilities': ['Monitor security systems', 'Investigate security incidents', 'Implement security measures', 'Conduct risk assessments']
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
        """Generate a personalized cover letter"""
        if job_role not in self.job_roles:
            return "Invalid job role selected."
        
        job_info = self.job_roles[job_role]
        match_percentage, missing_skills, matched_skills = self.calculate_job_match(resume_skills, job_role)
        
        # Extract some experience/achievements from resume
        experience_keywords = ['led', 'managed', 'developed', 'implemented', 'created', 'improved', 'increased', 'achieved']
        experience_sentences = []
        sentences = re.split(r'[.!?]+', resume_text)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in experience_keywords):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 20 and len(clean_sentence) < 150:
                    experience_sentences.append(clean_sentence)
        
        # Select top 2 experience sentences
        relevant_experience = experience_sentences[:2] if experience_sentences else []
        
        # Generate cover letter
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_role} position at {company_name}. With my background in technology and proven track record of success, I am excited about the opportunity to contribute to your team.

"""
        
        # Add skills paragraph
        if matched_skills:
            skills_text = ', '.join(matched_skills[:5])  # Top 5 matched skills
            cover_letter += f"My technical expertise includes {skills_text}, which aligns well with the requirements for this role. "
        
        cover_letter += f"I am particularly drawn to this position because it allows me to {job_info['description'].lower()} and contribute to meaningful projects.\n\n"
        
        # Add experience paragraph
        if relevant_experience:
            cover_letter += "In my previous roles, I have:\n"
            for exp in relevant_experience:
                cover_letter += f"• {exp.strip()}\n"
            cover_letter += "\n"
        
        # Add responsibilities paragraph
        cover_letter += f"I am excited about the opportunity to {', '.join(job_info['responsibilities'][:3]).lower()} at {company_name}. "
        
        # Add closing
        cover_letter += f"""My passion for technology and commitment to excellence make me a strong candidate for this position.

Thank you for considering my application. I look forward to discussing how my skills and experience can contribute to {company_name}'s continued success.

Sincerely,
{name}"""
        
        return cover_letter

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
                st.header("Cover Letter Generator")
                
                # Input fields for cover letter
                col1, col2 = st.columns(2)
                
                with col1:
                    # Extract name from resume
                    extracted_name = analyzer.extract_name_from_resume(text)
                    user_name = st.text_input("Your Name", value=extracted_name)
                
                with col2:
                    company_name = st.text_input("Company Name", placeholder="e.g., Google, Microsoft")
                
                # Job role selection for cover letter
                cover_letter_job = st.selectbox(
                    "Select Job Role for Cover Letter:",
                    list(analyzer.job_roles.keys()),
                    key="cover_letter_job"
                )
                
                # Generate cover letter button
                if st.button("Generate Cover Letter", type="primary"):
                    if user_name and company_name and cover_letter_job:
                        cover_letter = analyzer.generate_cover_letter(
                            user_name, cover_letter_job, company_name, skills, text
                        )
                        
                        st.subheader("📄 Generated Cover Letter")
                        st.text_area("Cover Letter", cover_letter, height=400)
                        
                        # Download button
                        st.download_button(
                            label="Download Cover Letter",
                            data=cover_letter,
                            file_name=f"{user_name.replace(' ', '_')}_cover_letter_{cover_letter_job.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                        
                        # Match analysis for cover letter
                        match_percentage, missing_skills, matched_skills = analyzer.calculate_job_match(skills, cover_letter_job)
                        
                        st.subheader("📊 Cover Letter Analysis")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Job Match", f"{match_percentage:.1f}%")
                        
                        with col2:
                            st.metric("Skills Highlighted", len(matched_skills))
                        
                        with col3:
                            word_count = len(cover_letter.split())
                            st.metric("Word Count", word_count)
                        
                        # Recommendations for cover letter
                        st.subheader("💡 Cover Letter Tips")
                        tips = [
                            "Customize the cover letter for each application",
                            "Research the company and mention specific details",
                            "Quantify your achievements with numbers",
                            "Keep it concise (1 page maximum)",
                            "Use the same font and formatting as your resume"
                        ]
                        
                        for tip in tips:
                            st.write(f"• {tip}")
                        
                    else:
                        st.warning("Please fill in all required fields (Name, Company, Job Role)")
                
                # Sample cover letters section
                st.subheader("📝 Cover Letter Best Practices")
                
                best_practices = {
                    "Structure": [
                        "Header with your contact information",
                        "Date and employer's contact information",
                        "Professional greeting",
                        "Opening paragraph with position and interest",
                        "Body paragraphs highlighting relevant experience",
                        "Closing paragraph with call to action",
                        "Professional sign-off"
                    ],
                    "Content Tips": [
                        "Address the hiring manager by name when possible",
                        "Mention how you learned about the position",
                        "Highlight 2-3 key achievements that match the job",
                        "Show enthusiasm for the company and role",
                        "Include keywords from the job description",
                        "End with a strong call to action"
                    ],
                    "Common Mistakes": [
                        "Using a generic template for all applications",
                        "Repeating everything from your resume",
                        "Being too long or too short",
                        "Focusing on what you want vs. what you can offer",
                        "Poor grammar or spelling errors",
                        "Forgetting to customize company/position names"
                    ]
                }
                
                for category, items in best_practices.items():
                    with st.expander(f"📋 {category}"):
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
            "💼 **Job Match**: Analyzes compatibility with specific job roles",
            "✍️ **Cover Letter**: Generates personalized cover letters"
        ]
        
        for feature in features:
            st.write(feature)

if __name__ == "__main__":
    main()
