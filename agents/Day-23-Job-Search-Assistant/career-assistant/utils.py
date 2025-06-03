"""Utility functions for the Career Application Assistant."""

import re
from typing import List, Dict, Set, Tuple
from models import (
    UserProfile, JobPosting, JobRequirement, CompanyInfo, 
    ExperienceLevel, Skill, WorkExperience
)


def extract_keywords_from_text(text: str) -> List[str]:
    """Extract important keywords from job description text."""
    # Remove common stop words and extract meaningful terms
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Extract words and phrases
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\.\-]*\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Find technology-specific patterns
    tech_patterns = [
        r'\b[a-zA-Z]+\.js\b',  # JavaScript frameworks
        r'\bC\+\+\b', r'\bC#\b',  # Programming languages
        r'\b[A-Z]{2,}\b',  # Acronyms
        r'\b\w+SQL\b',  # SQL variants
        r'\b\w+DB\b',  # Database names
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([match.lower() for match in matches])
    
    return list(set(keywords))


def parse_job_description(job_description: str) -> Dict[str, List[str]]:
    """Parse job description to extract structured information."""
    result = {
        'responsibilities': [],
        'requirements': [],
        'qualifications': [],
        'technologies': [],
        'benefits': []
    }
    
    # Split into sections based on common headers
    sections = re.split(r'\n(?=[A-Z][^a-z]*:|\n[A-Z][^a-z]*\n)', job_description)
    
    for section in sections:
        section_lower = section.lower()
        
        # Extract bullet points or numbered items
        items = re.findall(r'(?:[-•*]\s*|^\d+[\.\)]\s*)(.+)', section, re.MULTILINE)
        
        if any(keyword in section_lower for keyword in ['responsibilit', 'duties', 'role']):
            result['responsibilities'].extend(items)
        elif any(keyword in section_lower for keyword in ['requirement', 'must have', 'essential']):
            result['requirements'].extend(items)
        elif any(keyword in section_lower for keyword in ['qualification', 'education', 'experience']):
            result['qualifications'].extend(items)
        elif any(keyword in section_lower for keyword in ['benefit', 'offer', 'perks']):
            result['benefits'].extend(items)
    
    # Extract technology mentions
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'sql', 'nosql',
        'git', 'jenkins', 'ci/cd', 'agile', 'scrum', 'machine learning',
        'tensorflow', 'pytorch', 'hadoop', 'spark'
    ]
    
    text_lower = job_description.lower()
    for tech in tech_keywords:
        if tech in text_lower:
            result['technologies'].append(tech)
    
    return result


def extract_experience_level(job_description: str) -> ExperienceLevel:
    """Extract experience level from job description."""
    text_lower = job_description.lower()
    
    if any(term in text_lower for term in ['entry level', 'graduate', 'junior', '0-2 years', 'new grad']):
        return ExperienceLevel.ENTRY
    elif any(term in text_lower for term in ['junior', '1-3 years', '2-4 years']):
        return ExperienceLevel.JUNIOR
    elif any(term in text_lower for term in ['mid-level', 'intermediate', '3-5 years', '4-6 years']):
        return ExperienceLevel.MID
    elif any(term in text_lower for term in ['senior', '5+ years', '7+ years', '5-8 years']):
        return ExperienceLevel.SENIOR
    elif any(term in text_lower for term in ['lead', 'principal', 'staff', '8+ years', '10+ years']):
        return ExperienceLevel.LEAD
    elif any(term in text_lower for term in ['director', 'vp', 'head of', 'chief', 'executive']):
        return ExperienceLevel.EXECUTIVE
    
    return ExperienceLevel.MID  # Default


def calculate_skill_overlap(user_skills: List[Skill], job_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculate skill overlap between user skills and job requirements."""
    user_skill_names = {skill.name.lower() for skill in user_skills}
    job_keywords_set = {keyword.lower() for keyword in job_keywords}
    
    # Find matches
    matches = user_skill_names.intersection(job_keywords_set)
    missing = job_keywords_set - user_skill_names
    
    # Calculate overlap percentage
    if job_keywords_set:
        overlap_percentage = len(matches) / len(job_keywords_set)
    else:
        overlap_percentage = 0.0
    
    return overlap_percentage, list(matches), list(missing)


def calculate_experience_match(user_experience: List[WorkExperience], required_level: ExperienceLevel) -> float:
    """Calculate how well user experience matches required level."""
    # Calculate total years of experience
    total_years = sum(exp.duration_years for exp in user_experience)
    
    # Map experience levels to year ranges
    level_to_years = {
        ExperienceLevel.ENTRY: (0, 2),
        ExperienceLevel.JUNIOR: (1, 3),
        ExperienceLevel.MID: (3, 6),
        ExperienceLevel.SENIOR: (5, 10),
        ExperienceLevel.LEAD: (8, 15),
        ExperienceLevel.EXECUTIVE: (12, float('inf'))
    }
    
    required_min, required_max = level_to_years[required_level]
    
    if total_years < required_min:
        # Under-qualified
        return max(0.0, total_years / required_min)
    elif total_years <= required_max:
        # Well-matched
        return 1.0
    else:
        # Over-qualified (still good but might be overqualified)
        return 0.9
    

def extract_salary_range(text: str) -> str:
    """Extract salary range from job description."""
    # Common salary patterns
    patterns = [
        r'\$[\d,]+\s*[-–]\s*\$[\d,]+',  # $50,000 - $70,000
        r'\$[\d,]+k\s*[-–]\s*\$[\d,]+k',  # $50k - $70k
        r'[\d,]+\s*[-–]\s*[\d,]+\s*(?:USD|dollars)',  # 50,000 - 70,000 USD
        r'salary.*?\$[\d,]+',  # salary of $50,000
        r'compensation.*?\$[\d,]+',  # compensation up to $50,000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return ""


def format_user_profile_summary(profile: UserProfile) -> str:
    """Create a formatted summary of user profile for agent context."""
    summary_parts = []
    
    # Basic info
    if profile.personal_info:
        name = profile.personal_info.get('name', 'Candidate')
        summary_parts.append(f"Candidate: {name}")
    
    # Experience summary
    total_years = sum(exp.duration_years for exp in profile.work_experience)
    summary_parts.append(f"Total Experience: {total_years:.1f} years")
    
    # Key skills
    if profile.skills:
        top_skills = [skill.name for skill in profile.skills[:10]]  # Top 10 skills
        summary_parts.append(f"Key Skills: {', '.join(top_skills)}")
    
    # Career goals
    if profile.career_goals.target_roles:
        target_roles = ', '.join(profile.career_goals.target_roles[:3])
        summary_parts.append(f"Target Roles: {target_roles}")
    
    # Recent experience
    if profile.work_experience:
        latest_job = profile.work_experience[0]  # Assuming sorted by recency
        summary_parts.append(f"Current/Latest Role: {latest_job.job_title} at {latest_job.company}")
    
    return " | ".join(summary_parts)


def format_job_summary(job: JobPosting) -> str:
    """Create a formatted summary of job posting for agent context."""
    summary_parts = []
    
    summary_parts.append(f"Position: {job.job_title}")
    summary_parts.append(f"Company: {job.company.name}")
    
    if job.location:
        summary_parts.append(f"Location: {job.location}")
    
    if job.experience_level:
        summary_parts.append(f"Level: {job.experience_level.value}")
    
    if job.salary_range:
        summary_parts.append(f"Salary: {job.salary_range}")
    
    # Key requirements
    if job.requirements:
        required_skills = [req.requirement for req in job.requirements[:5]]
        summary_parts.append(f"Key Requirements: {', '.join(required_skills)}")
    
    return " | ".join(summary_parts)


def identify_achievement_opportunities(user_experience: List[WorkExperience], job_keywords: List[str]) -> List[str]:
    """Identify which user achievements are most relevant to highlight."""
    relevant_achievements = []
    
    for exp in user_experience:
        for achievement in exp.key_achievements:
            achievement_lower = achievement.lower()
            
            # Check if achievement mentions job-relevant keywords
            relevance_score = sum(1 for keyword in job_keywords 
                                 if keyword.lower() in achievement_lower)
            
            if relevance_score > 0:
                relevant_achievements.append((achievement, relevance_score))
    
    # Sort by relevance and return top achievements
    relevant_achievements.sort(key=lambda x: x[1], reverse=True)
    return [achievement for achievement, _ in relevant_achievements[:10]]


def generate_ats_keywords(job_description: str) -> List[str]:
    """Generate ATS-friendly keywords from job description."""
    keywords = extract_keywords_from_text(job_description)
    
    # Filter for important terms (longer, more specific)
    ats_keywords = [
        keyword for keyword in keywords 
        if len(keyword) > 3 and not keyword.isdigit()
    ]
    
    # Add common variations
    expanded_keywords = []
    for keyword in ats_keywords:
        expanded_keywords.append(keyword)
        
        # Add common programming language variations
        if keyword in ['js', 'javascript']:
            expanded_keywords.extend(['javascript', 'js', 'node.js', 'react'])
        elif keyword in ['python']:
            expanded_keywords.extend(['python', 'django', 'flask', 'pandas'])
        elif keyword in ['java']:
            expanded_keywords.extend(['java', 'spring', 'hibernate'])
    
    return list(set(expanded_keywords))


def analyze_company_culture_fit(user_profile: UserProfile, company_info: CompanyInfo) -> Dict[str, any]:
    """Analyze fit between user preferences and company culture."""
    fit_analysis = {
        'culture_match_score': 0.0,
        'matching_values': [],
        'potential_concerns': [],
        'questions_to_ask': []
    }
    
    # Extract user values from work preferences
    user_values = user_profile.career_goals.work_preferences
    company_values = [value.lower() for value in company_info.culture_values]
    
    # Simple keyword matching for culture fit
    value_keywords = {
        'innovation': ['innovative', 'creativity', 'cutting-edge'],
        'collaboration': ['team', 'collaborative', 'together'],
        'growth': ['learning', 'development', 'growth'],
        'flexibility': ['flexible', 'remote', 'work-life'],
        'diversity': ['diverse', 'inclusive', 'equality']
    }
    
    matches = 0
    total_values = len(company_values) if company_values else 1
    
    for value in company_values:
        for category, keywords in value_keywords.items():
            if any(keyword in value for keyword in keywords):
                fit_analysis['matching_values'].append(value)
                matches += 1
                break
    
    fit_analysis['culture_match_score'] = matches / total_values
    
    # Generate questions based on company info
    if company_info.size:
        fit_analysis['questions_to_ask'].append(f"How does the company maintain its culture at {company_info.size} size?")
    
    if 'startup' in company_info.industry.lower():
        fit_analysis['questions_to_ask'].append("What is the work-life balance like in this startup environment?")
    
    return fit_analysis 