"""Document processing and web scraping utilities for the Career Application Assistant."""

import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# DOCX processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Web scraping
try:
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False


class DocumentProcessor:
    """Process various document formats for resume extraction."""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF processing")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is required for DOCX processing")
        
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    @classmethod
    def extract_resume_text(cls, file_path: str) -> str:
        """Extract text from resume file based on extension."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return cls.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")


class ResumeParser:
    """Parse resume text to extract structured information."""
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """Extract contact information from resume text."""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone extraction
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Name extraction (first few lines, capitalized words)
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if len(line.split()) <= 4 and any(word[0].isupper() for word in line.split() if word):
                # Check if it's likely a name (not email, phone, etc.)
                if '@' not in line and not re.search(r'\d{3}', line):
                    contact_info['name'] = line
                    break
        
        return contact_info
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract skills from resume text."""
        # Common skill keywords and patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Angular|Vue|Node\.js|TypeScript)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git)\b',
            r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(?:HTML|CSS|Bootstrap|Tailwind|SASS|LESS)\b',
            r'\b(?:Machine Learning|AI|Data Science|Analytics|Statistics)\b',
            r'\b(?:Agile|Scrum|Kanban|DevOps|CI/CD|API|REST|GraphQL)\b',
        ]
        
        skills = set()
        text_upper = text.upper()
        
        # Look for skills sections
        skills_section_pattern = r'(?:SKILLS?|TECHNICAL SKILLS?|TECHNOLOGIES?)[:\n](.*?)(?:\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text_upper, re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Extract comma/bullet separated items
            skill_items = re.split(r'[,•\n]', skills_text)
            for item in skill_items:
                item = item.strip()
                if item and len(item) < 30:  # Reasonable skill name length
                    skills.add(item)
        
        # Also search for skills using patterns
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    @staticmethod
    def extract_experience(text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text."""
        experiences = []
        
        # Look for experience section
        exp_section_pattern = r'(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT)[:\n](.*?)(?:\n\n[A-Z]|EDUCATION|SKILLS|$)'
        exp_match = re.search(exp_section_pattern, text.upper(), re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(1)
            
            # Split by common job separators
            job_blocks = re.split(r'\n(?=[A-Z].*(?:Engineer|Developer|Manager|Analyst|Specialist))', exp_text)
            
            for block in job_blocks:
                if len(block.strip()) < 50:  # Skip very short blocks
                    continue
                
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if not lines:
                    continue
                
                # Extract job title and company from first line
                first_line = lines[0]
                job_title = ""
                company = ""
                
                # Common patterns: "Job Title at Company" or "Job Title | Company"
                if ' at ' in first_line:
                    parts = first_line.split(' at ')
                    job_title = parts[0].strip()
                    company = parts[1].split(',')[0].strip()  # Remove location if present
                elif ' | ' in first_line:
                    parts = first_line.split(' | ')
                    job_title = parts[0].strip()
                    company = parts[1].split(',')[0].strip()
                else:
                    job_title = first_line
                
                # Extract achievements (bullet points)
                achievements = []
                for line in lines[1:]:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        achievements.append(line[1:].strip())
                    elif len(line) > 30 and not any(keyword in line.lower() for keyword in ['phone', 'email', 'address']):
                        achievements.append(line)
                
                if job_title:
                    experiences.append({
                        'job_title': job_title,
                        'company': company or 'Unknown Company',
                        'achievements': achievements[:5]  # Limit to top 5 achievements
                    })
        
        return experiences


class JobDescriptionScraper:
    """Scrape job descriptions from various job posting URLs."""
    
    @staticmethod
    def scrape_url(url: str) -> Optional[Dict[str, str]]:
        """Scrape job description from URL."""
        if not WEB_SCRAPING_AVAILABLE:
            raise ImportError("beautifulsoup4 is required for web scraping")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get domain to apply specific scraping logic
            domain = urlparse(url).netloc.lower()
            
            if 'linkedin.com' in domain:
                return JobDescriptionScraper._scrape_linkedin(soup)
            elif 'indeed.com' in domain:
                return JobDescriptionScraper._scrape_indeed(soup)
            elif 'glassdoor.com' in domain:
                return JobDescriptionScraper._scrape_glassdoor(soup)
            else:
                return JobDescriptionScraper._scrape_generic(soup)
                
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None
    
    @staticmethod
    def _scrape_linkedin(soup: BeautifulSoup) -> Dict[str, str]:
        """Scrape LinkedIn job posting."""
        result = {}
        
        # Job title
        title_elem = soup.find('h1') or soup.find(['h1', 'h2'], class_=re.compile('job.*title', re.I))
        if title_elem:
            result['job_title'] = title_elem.get_text().strip()
        
        # Company name
        company_elem = soup.find(['span', 'a'], class_=re.compile('company.*name', re.I))
        if company_elem:
            result['company'] = company_elem.get_text().strip()
        
        # Job description
        desc_elem = soup.find(['div', 'section'], class_=re.compile('description', re.I))
        if desc_elem:
            result['job_description'] = desc_elem.get_text().strip()
        
        return result
    
    @staticmethod
    def _scrape_indeed(soup: BeautifulSoup) -> Dict[str, str]:
        """Scrape Indeed job posting."""
        result = {}
        
        # Job title
        title_elem = soup.find('h1', {'data-testid': 'jobsearch-JobInfoHeader-title'})
        if title_elem:
            result['job_title'] = title_elem.get_text().strip()
        
        # Company name
        company_elem = soup.find(['span', 'a'], {'data-testid': re.compile('.*company.*')})
        if company_elem:
            result['company'] = company_elem.get_text().strip()
        
        # Job description
        desc_elem = soup.find('div', id='jobDescriptionText')
        if desc_elem:
            result['job_description'] = desc_elem.get_text().strip()
        
        return result
    
    @staticmethod
    def _scrape_glassdoor(soup: BeautifulSoup) -> Dict[str, str]:
        """Scrape Glassdoor job posting."""
        result = {}
        
        # Job title
        title_elem = soup.find('h1', class_=re.compile('job.*title', re.I))
        if title_elem:
            result['job_title'] = title_elem.get_text().strip()
        
        # Company name
        company_elem = soup.find(['span', 'div'], class_=re.compile('employer.*name', re.I))
        if company_elem:
            result['company'] = company_elem.get_text().strip()
        
        # Job description
        desc_elem = soup.find('div', class_=re.compile('job.*description', re.I))
        if desc_elem:
            result['job_description'] = desc_elem.get_text().strip()
        
        return result
    
    @staticmethod
    def _scrape_generic(soup: BeautifulSoup) -> Dict[str, str]:
        """Generic scraping for unknown job sites."""
        result = {}
        
        # Try to find job title
        title_selectors = ['h1', '[class*="title"]', '[class*="job"]']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and len(title_elem.get_text().strip()) < 100:
                result['job_title'] = title_elem.get_text().strip()
                break
        
        # Try to find company name
        company_selectors = ['[class*="company"]', '[class*="employer"]', '[class*="organization"]']
        for selector in company_selectors:
            company_elem = soup.select_one(selector)
            if company_elem and len(company_elem.get_text().strip()) < 50:
                result['company'] = company_elem.get_text().strip()
                break
        
        # Get all text as job description
        text = soup.get_text()
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        result['job_description'] = '\n'.join(lines)
        
        return result


class WebResearcher:
    """Research interview questions and strategies from the web."""
    
    @staticmethod
    def search_interview_questions(job_title: str, company_name: str = "") -> List[Dict[str, str]]:
        """Search for interview questions related to the job title and company."""
        questions = []
        
        # Common interview questions for different roles
        common_questions = {
            'software engineer': [
                "Tell me about yourself and your background in software development.",
                "Describe a challenging technical problem you solved recently.",
                "How do you approach debugging and troubleshooting code?",
                "What's your experience with version control and collaboration?",
                "How do you stay updated with new technologies and frameworks?"
            ],
            'data scientist': [
                "Walk me through your approach to a data science project.",
                "How do you handle missing or dirty data?",
                "Explain a machine learning model you've implemented.",
                "How do you validate the performance of your models?",
                "What tools and programming languages do you prefer for data analysis?"
            ],
            'product manager': [
                "How do you prioritize features in a product roadmap?",
                "Describe a time you had to make a difficult product decision.",
                "How do you gather and incorporate user feedback?",
                "What metrics do you use to measure product success?",
                "How do you work with engineering and design teams?"
            ],
            'marketing manager': [
                "How do you develop and execute a marketing strategy?",
                "Describe a successful marketing campaign you led.",
                "How do you measure the ROI of marketing activities?",
                "What's your approach to understanding target audiences?",
                "How do you stay current with marketing trends and tools?"
            ]
        }
        
        # Find relevant questions based on job title
        job_title_lower = job_title.lower()
        for role, role_questions in common_questions.items():
            if role in job_title_lower:
                for question in role_questions:
                    questions.append({
                        'question': question,
                        'type': 'behavioral',
                        'source': 'common_questions'
                    })
                break
        
        # Add general questions
        general_questions = [
            "Why are you interested in this role and company?",
            "What are your strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Why are you looking to leave your current position?",
            "Do you have any questions for us?"
        ]
        
        for question in general_questions:
            questions.append({
                'question': question,
                'type': 'general',
                'source': 'common_questions'
            })
        
        return questions
    
    @staticmethod
    def get_interview_tips(job_title: str) -> List[str]:
        """Get interview tips for specific job roles."""
        general_tips = [
            "Research the company thoroughly - mission, values, recent news",
            "Prepare specific examples using the STAR method (Situation, Task, Action, Result)",
            "Practice coding problems if it's a technical role",
            "Prepare thoughtful questions to ask the interviewer",
            "Dress appropriately for the company culture",
            "Arrive 10-15 minutes early",
            "Bring multiple copies of your resume",
            "Follow up with a thank-you email within 24 hours"
        ]
        
        role_specific_tips = {
            'engineer': [
                "Be ready to code on a whiteboard or computer",
                "Review computer science fundamentals (algorithms, data structures)",
                "Practice explaining your thought process out loud",
                "Be prepared to discuss system design for senior roles"
            ],
            'data': [
                "Review statistics and machine learning concepts",
                "Be ready to discuss specific projects and methodologies",
                "Practice explaining technical concepts to non-technical audiences",
                "Prepare to walk through your data analysis process"
            ],
            'manager': [
                "Prepare examples of leadership and team management",
                "Be ready to discuss conflict resolution scenarios",
                "Think about how you measure and improve team performance",
                "Prepare strategic thinking examples"
            ]
        }
        
        tips = general_tips.copy()
        job_title_lower = job_title.lower()
        
        for role_key, role_tips in role_specific_tips.items():
            if role_key in job_title_lower:
                tips.extend(role_tips)
                break
        
        return tips 