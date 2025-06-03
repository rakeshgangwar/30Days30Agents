"""AI-Powered Career Application Assistant using PydanticAI with MCP integration."""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from mcp import ClientSession, MCPServerStdio

from models import (
    UserProfile, JobPosting, WorkExperience, Skill, CompanyInfo,
    ExperienceLevel, ProfileAnalysisOutput, ResumeOptimizationOutput,
    CoverLetterOutput, InterviewPrepOutput, JobSummaryOutput
)
from utils import (
    extract_keywords_from_text, parse_job_description, 
    calculate_skill_overlap, calculate_experience_match, format_user_profile_summary,
    format_job_summary, identify_achievement_opportunities, generate_ats_keywords,
    analyze_company_culture_fit
)


@dataclass
class CareerAssistantDependencies:
    """Dependencies for the career assistant agents."""
    user_profile: Optional[UserProfile] = None
    job_posting: Optional[JobPosting] = None
    exa_server: Optional[MCPServerStdio] = None
    firecrawl_server: Optional[MCPServerStdio] = None


class ExtractedContactInfo(BaseModel):
    """Extracted contact information from resume."""
    name: Optional[str] = Field(description="Full name of the candidate")
    email: Optional[str] = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number")
    linkedin: Optional[str] = Field(description="LinkedIn profile URL")
    location: Optional[str] = Field(description="Current location/address")


class ExtractedSkills(BaseModel):
    """Extracted skills from resume."""
    technical_skills: List[str] = Field(description="Programming languages, frameworks, tools")
    soft_skills: List[str] = Field(description="Communication, leadership, problem-solving skills")
    domain_skills: List[str] = Field(description="Industry-specific skills and knowledge")


class ExtractedExperience(BaseModel):
    """Extracted work experience from resume."""
    job_title: str = Field(description="Job title or position")
    company: str = Field(description="Company name")
    duration: str = Field(description="Duration of employment")
    key_achievements: List[str] = Field(description="Major accomplishments and responsibilities")
    technologies_used: List[str] = Field(description="Technologies, tools, or methodologies used")


class JobAnalysis(BaseModel):
    """Analysis of a job posting."""
    key_requirements: List[str] = Field(description="Essential qualifications and skills")
    preferred_qualifications: List[str] = Field(description="Nice-to-have qualifications")
    responsibilities: List[str] = Field(description="Main job responsibilities")
    company_culture_indicators: List[str] = Field(description="Clues about company culture and values")
    required_experience_level: str = Field(description="Experience level required")
    technologies_mentioned: List[str] = Field(description="Technologies, tools, frameworks mentioned")


class CompanyResearch(BaseModel):
    """Research about a company."""
    company_overview: str = Field(description="Brief overview of the company")
    recent_news: List[str] = Field(description="Recent news or developments")
    culture_and_values: List[str] = Field(description="Company culture and values")
    products_services: List[str] = Field(description="Main products or services")
    competitors: List[str] = Field(description="Main competitors")
    interview_insights: List[str] = Field(description="Interview process insights and tips")


class SimpleApplicationPackage(BaseModel):
    """Simplified application package for initial implementation."""
    optimized_resume: str = Field(description="Optimized resume content")
    cover_letter: str = Field(description="Cover letter content")
    interview_preparation: Dict[str, Any] = Field(description="Interview preparation materials")
    application_strategy: str = Field(description="Application strategy")


# Profile Analysis Agent
profile_analysis_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=ProfileAnalysisOutput,
    system_prompt="""You are an expert career advisor specializing in profile analysis and job matching. 
    You help candidates understand how well they match with specific job opportunities and provide strategic career guidance.
    
    Your analysis should be:
    - Thorough and data-driven
    - Honest about strengths and gaps
    - Strategic in recommendations
    - Actionable and specific
    
    Always provide concrete suggestions for improvement and career positioning."""
)


@profile_analysis_agent.system_prompt
async def add_profile_context(ctx: RunContext[CareerAssistantDependencies]) -> str:
    """Add user profile and job context to the system prompt."""
    user_summary = format_user_profile_summary(ctx.deps.user_profile)
    
    if ctx.deps.job_posting:
        job_summary = format_job_summary(ctx.deps.job_posting)
        return f"User Profile: {user_summary}\nJob Posting: {job_summary}"
    else:
        return f"User Profile: {user_summary}"


@profile_analysis_agent.tool
async def analyze_job_match(
    ctx: RunContext[CareerAssistantDependencies],
    include_detailed_analysis: bool = True
) -> Dict[str, Any]:
    """Analyze how well the user's profile matches the job posting."""
    if not ctx.deps.job_posting:
        return {"error": "No job posting provided for analysis"}
    
    user = ctx.deps.user_profile
    job = ctx.deps.job_posting
    
    # Extract job keywords and requirements
    job_keywords = extract_keywords_from_text(job.job_description)
    
    # Calculate skill overlap
    skill_overlap, matching_skills, missing_skills = calculate_skill_overlap(
        user.skills, job_keywords
    )
    
    # Calculate experience match
    exp_match = calculate_experience_match(
        user.work_experience, job.experience_level or ExperienceLevel.MID
    )
    
    # Count requirements met
    requirements_met = 0
    total_requirements = len(job.requirements)
    user_skill_names = {skill.name.lower() for skill in user.skills}
    
    for req in job.requirements:
        req_keywords = extract_keywords_from_text(req.requirement)
        if any(keyword.lower() in user_skill_names for keyword in req_keywords):
            requirements_met += 1
    
    # Overall score calculation
    overall_score = (skill_overlap * 0.4 + exp_match * 0.3 + 
                    (requirements_met / max(total_requirements, 1)) * 0.3)
    
    # Identify strengths
    strengths = []
    for exp in user.work_experience:
        if any(keyword.lower() in exp.job_title.lower() for keyword in job_keywords[:5]):
            strengths.append(f"Relevant experience: {exp.job_title} at {exp.company}")
    
    return {
        "overall_score": round(overall_score, 2),
        "skills_match": round(skill_overlap, 2),
        "experience_match": round(exp_match, 2),
        "requirements_met": requirements_met,
        "total_requirements": total_requirements,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills[:10],  # Top 10 gaps
        "strengths": strengths,
        "job_keywords": job_keywords[:20]  # Top 20 keywords
    }


@profile_analysis_agent.tool
async def research_company_culture(
    ctx: RunContext[CareerAssistantDependencies],
    company_name: str
) -> Dict[str, Any]:
    """Research company culture and values for fit analysis."""
    # In a real implementation, this would call external APIs or web scraping
    # For now, we'll use the provided company info
    if ctx.deps.job_posting and ctx.deps.job_posting.company:
        company = ctx.deps.job_posting.company
        culture_analysis = analyze_company_culture_fit(ctx.deps.user_profile, company)
        
        return {
            "company_name": company.name,
            "industry": company.industry,
            "culture_values": company.culture_values,
            "culture_match_score": culture_analysis['culture_match_score'],
            "matching_values": culture_analysis['matching_values'],
            "questions_to_ask": culture_analysis['questions_to_ask']
        }
    
    return {"error": f"No company information available for {company_name}"}


# Resume Optimization Agent
resume_optimization_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=ResumeOptimizationOutput,
    system_prompt="""You are an expert resume writer and ATS optimization specialist.
    You help candidates tailor their resumes for specific job opportunities to maximize their chances of getting interviews.
    
    Your recommendations should:
    - Be specific and actionable
    - Focus on ATS optimization
    - Highlight relevant achievements with quantified impact
    - Use job-relevant keywords naturally
    - Maintain authenticity while maximizing relevance
    
    Always provide concrete examples of improved bullet points and specific implementation guidance."""
)


@resume_optimization_agent.system_prompt
async def add_resume_context(ctx: RunContext[CareerAssistantDependencies]) -> str:
    """Add resume optimization context."""
    user = ctx.deps.user_profile
    context = f"Candidate has {len(user.work_experience)} work experiences and {len(user.skills)} skills listed."
    
    if ctx.deps.job_posting:
        context += f" Optimizing for {ctx.deps.job_posting.job_title} at {ctx.deps.job_posting.company.name}."
    
    return context


@resume_optimization_agent.tool
async def generate_tailored_bullet_points(
    ctx: RunContext[CareerAssistantDependencies],
    focus_on_role: str = ""
) -> List[str]:
    """Generate tailored resume bullet points for the target job."""
    user = ctx.deps.user_profile
    job = ctx.deps.job_posting
    
    if not job:
        return ["Error: No job posting provided for tailoring"]
    
    job_keywords = extract_keywords_from_text(job.job_description)
    relevant_achievements = identify_achievement_opportunities(user.work_experience, job_keywords)
    
    tailored_bullets = []
    
    # Create enhanced bullet points
    for achievement in relevant_achievements[:8]:  # Top 8 achievements
        # Add quantification if missing
        if any(char.isdigit() for char in achievement):
            tailored_bullets.append(f"• {achievement}")
        else:
            tailored_bullets.append(f"• {achievement} (quantified impact to be added)")
    
    # Add skill-focused bullets
    for skill in user.skills[:5]:
        if skill.name.lower() in [kw.lower() for kw in job_keywords]:
            bullet = f"• Applied {skill.name} expertise in {skill.proficiency.value}-level capacity"
            if skill.years_experience:
                bullet += f" over {skill.years_experience} years"
            tailored_bullets.append(bullet)
    
    return tailored_bullets


@resume_optimization_agent.tool
async def identify_ats_keywords(
    ctx: RunContext[CareerAssistantDependencies]
) -> List[str]:
    """Identify important ATS keywords for the job."""
    if not ctx.deps.job_posting:
        return ["Error: No job posting provided"]
    
    return generate_ats_keywords(ctx.deps.job_posting.job_description)


# Cover Letter Agent
cover_letter_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=CoverLetterOutput,
    system_prompt="""You are an expert cover letter writer who creates compelling, personalized cover letters.
    You help candidates tell their story in a way that resonates with hiring managers and demonstrates clear value.
    
    Your cover letters should:
    - Tell a cohesive story connecting past experience to the target role
    - Demonstrate specific knowledge of the company and role
    - Highlight quantified achievements relevant to the position
    - Show genuine enthusiasm and cultural fit
    - Include a clear call to action
    
    Always personalize content based on the candidate's background and the specific opportunity."""
)


@cover_letter_agent.system_prompt
async def add_cover_letter_context(ctx: RunContext[CareerAssistantDependencies]) -> str:
    """Add context for cover letter generation."""
    if ctx.deps.job_posting:
        return f"Generating cover letter for {ctx.deps.job_posting.job_title} position at {ctx.deps.job_posting.company.name}"
    return "Generating general cover letter template"


@cover_letter_agent.tool
async def extract_relevant_experiences(
    ctx: RunContext[CareerAssistantDependencies],
    max_experiences: int = 3
) -> List[Dict[str, Any]]:
    """Extract the most relevant work experiences for the cover letter."""
    user = ctx.deps.user_profile
    job = ctx.deps.job_posting
    
    if not job:
        return [{"error": "No job posting provided"}]
    
    job_keywords = extract_keywords_from_text(job.job_description)
    relevant_experiences = []
    
    for exp in user.work_experience[:max_experiences]:
        relevance_score = 0
        
        # Check job title relevance
        for keyword in job_keywords:
            if keyword.lower() in exp.job_title.lower():
                relevance_score += 2
        
        # Check achievements relevance
        for achievement in exp.key_achievements:
            for keyword in job_keywords:
                if keyword.lower() in achievement.lower():
                    relevance_score += 1
        
        relevant_experiences.append({
            "experience": exp,
            "relevance_score": relevance_score,
            "duration": f"{exp.duration_years} years",
            "top_achievement": exp.key_achievements[0] if exp.key_achievements else "No specific achievement listed"
        })
    
    # Sort by relevance
    relevant_experiences.sort(key=lambda x: x["relevance_score"], reverse=True)
    return relevant_experiences


# Interview Preparation Agent
interview_prep_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=InterviewPrepOutput,
    system_prompt="""You are an expert interview coach who helps candidates prepare for job interviews.
    You provide comprehensive preparation strategies, relevant questions, and coaching on how to present experiences effectively.
    
    Your preparation should include:
    - Role-specific technical and behavioral questions
    - Company-specific questions based on their culture and industry
    - STAR method guidance for behavioral responses
    - Questions for the candidate to ask interviewers
    - Confidence-building strategies
    
    Always tailor your guidance to the specific role and company, and help candidates connect their experiences to the job requirements."""
)


@interview_prep_agent.system_prompt
async def add_interview_context(ctx: RunContext[CareerAssistantDependencies]) -> str:
    """Add interview preparation context."""
    context = f"Preparing candidate with {sum(exp.duration_years for exp in ctx.deps.user_profile.work_experience):.1f} years total experience"
    
    if ctx.deps.job_posting:
        context += f" for {ctx.deps.job_posting.job_title} interview at {ctx.deps.job_posting.company.name}"
    
    return context


@interview_prep_agent.tool
async def generate_behavioral_questions(
    ctx: RunContext[CareerAssistantDependencies],
    question_count: int = 5
) -> List[Dict[str, Any]]:
    """Generate behavioral interview questions based on the role and user's experience."""
    user = ctx.deps.user_profile
    job = ctx.deps.job_posting
    
    # Common behavioral question themes
    themes = [
        "leadership and teamwork",
        "problem-solving and critical thinking", 
        "handling challenges and setbacks",
        "communication and collaboration",
        "learning and adaptability"
    ]
    
    questions = []
    
    for theme in themes[:question_count]:
        question_data = {
            "theme": theme,
            "question": f"Tell me about a time when you demonstrated {theme}.",
            "preparation_tip": f"Use STAR method to structure your response about {theme}",
            "user_experience_hint": ""
        }
        
        # Find relevant user experience for this theme
        for exp in user.work_experience:
            for achievement in exp.key_achievements:
                if any(word in achievement.lower() for word in theme.split()):
                    question_data["user_experience_hint"] = f"Consider discussing: {achievement}"
                    break
            if question_data["user_experience_hint"]:
                break
        
        questions.append(question_data)
    
    return questions


@interview_prep_agent.tool
async def generate_technical_questions(
    ctx: RunContext[CareerAssistantDependencies],
    question_count: int = 5
) -> List[Dict[str, Any]]:
    """Generate technical questions based on job requirements."""
    job = ctx.deps.job_posting
    
    if not job:
        return [{"error": "No job posting provided for technical questions"}]
    
    job_keywords = extract_keywords_from_text(job.job_description)
    tech_keywords = [kw for kw in job_keywords if kw.lower() in [
        'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 
        'kubernetes', 'machine learning', 'data analysis', 'api', 'database'
    ]]
    
    questions = []
    for tech in tech_keywords[:question_count]:
        questions.append({
            "technology": tech,
            "question": f"How would you approach [specific problem] using {tech}?",
            "preparation_tip": f"Review {tech} concepts, best practices, and common use cases",
            "depth_level": "intermediate"
        })
    
    return questions


# Job Summary Agent
job_summary_agent = Agent(
    'openai:gpt-4o', 
    deps_type=CareerAssistantDependencies,
    output_type=JobSummaryOutput,
    system_prompt="""You are an expert job market analyst who helps candidates understand job opportunities.
    You provide clear, comprehensive summaries of job postings with personalized insights based on the candidate's profile.
    
    Your summaries should:
    - Highlight key information candidates need to know
    - Break down requirements into categories (must-have vs nice-to-have)
    - Provide honest assessment of fit and competitiveness
    - Include strategic application advice
    - Identify potential red flags or concerns
    
    Always provide actionable insights that help candidates make informed decisions about applying."""
)


@job_summary_agent.tool
async def analyze_job_requirements(
    ctx: RunContext[CareerAssistantDependencies]
) -> Dict[str, List[str]]:
    """Analyze and categorize job requirements."""
    job = ctx.deps.job_posting
    
    if not job:
        return {"error": ["No job posting provided"]}
    
    parsed_desc = parse_job_description(job.job_description)
    
    # Categorize requirements by importance
    categorized = {
        "must_have": [],
        "preferred": [], 
        "nice_to_have": [],
        "technologies": parsed_desc["technologies"],
        "responsibilities": parsed_desc["responsibilities"]
    }
    
    for req in job.requirements:
        if req.importance.lower() in ["required", "must", "essential"]:
            categorized["must_have"].append(req.requirement)
        elif req.importance.lower() in ["preferred", "desired"]:
            categorized["preferred"].append(req.requirement)
        else:
            categorized["nice_to_have"].append(req.requirement)
    
    return categorized


# Main Career Assistant Agent (Router)
career_assistant_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=Union[ProfileAnalysisOutput, ResumeOptimizationOutput, CoverLetterOutput, InterviewPrepOutput, JobSummaryOutput],
    system_prompt="""You are a comprehensive Career Application Assistant that helps candidates optimize their job applications.
    You can provide:
    
    1. Profile Analysis - Match analysis between candidate and job
    2. Resume Optimization - Tailored resume improvements  
    3. Cover Letter Generation - Personalized cover letter content
    4. Interview Preparation - Comprehensive interview coaching
    5. Job Summary Analysis - Detailed job posting breakdown
    
    Based on the user's request, determine which type of assistance they need and delegate to the appropriate specialized service.
    Always provide thorough, actionable guidance tailored to their specific profile and target job."""
)


@career_assistant_agent.tool
async def analyze_profile_job_match(
    ctx: RunContext[CareerAssistantDependencies],
    detailed_analysis: bool = True
) -> ProfileAnalysisOutput:
    """Provide comprehensive profile analysis against a job posting."""
    result = await profile_analysis_agent.run(
        "Analyze how well this candidate's profile matches the job posting. Provide detailed compatibility analysis, skill gap assessment, and strategic career guidance.",
        deps=ctx.deps
    )
    return result.output


@career_assistant_agent.tool
async def optimize_resume_for_job(
    ctx: RunContext[CareerAssistantDependencies]
) -> ResumeOptimizationOutput:
    """Provide resume optimization recommendations for the target job."""
    result = await resume_optimization_agent.run(
        "Generate comprehensive resume optimization recommendations for this job application. Include tailored bullet points, ATS keywords, and strategic guidance.",
        deps=ctx.deps
    )
    return result.output


@career_assistant_agent.tool
async def generate_cover_letter(
    ctx: RunContext[CareerAssistantDependencies]
) -> CoverLetterOutput:
    """Generate personalized cover letter content."""
    result = await cover_letter_agent.run(
        "Create a compelling, personalized cover letter that connects the candidate's experience to this specific role and company.",
        deps=ctx.deps
    )
    return result.output


@career_assistant_agent.tool  
async def prepare_for_interview(
    ctx: RunContext[CareerAssistantDependencies]
) -> InterviewPrepOutput:
    """Provide comprehensive interview preparation."""
    result = await interview_prep_agent.run(
        "Create a comprehensive interview preparation package including behavioral questions, technical questions, company-specific preparation, and confidence-building strategies.",
        deps=ctx.deps
    )
    return result.output


@career_assistant_agent.tool
async def summarize_job_posting(
    ctx: RunContext[CareerAssistantDependencies]
) -> JobSummaryOutput:
    """Provide detailed analysis and summary of the job posting."""
    result = await job_summary_agent.run(
        "Analyze this job posting and provide a comprehensive summary with personalized insights for this candidate.",
        deps=ctx.deps
    )
    return result.output


# Resume Analysis Agent
resume_analysis_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=UserProfile,
    system_prompt=(
        "You are an expert resume analyzer. Your task is to extract comprehensive information "
        "from resumes and convert it into a structured UserProfile format.\n\n"
        "You have access to these tools:\n"
        "- extract_contact_info: Extract contact information from resume text\n"
        "- extract_skills: Extract and categorize skills from resume text\n"
        "- extract_work_experience: Extract work experience details\n\n"
        "Use these tools as needed to gather information, then compile everything into a "
        "complete UserProfile with contact info, skills, work experience, education, and career goals."
    )
)


@resume_analysis_agent.tool
async def extract_contact_info(ctx: RunContext[CareerAssistantDependencies], resume_text: str) -> ExtractedContactInfo:
    """Extract contact information from resume text using LLM."""
    extraction_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=ExtractedContactInfo,
        system_prompt="Extract contact information from the provided resume text. Be precise and only extract clearly visible information."
    )
    
    result = await extraction_agent.run(f"Extract contact information from this resume:\n\n{resume_text}")
    return result.output


@resume_analysis_agent.tool
async def extract_skills(ctx: RunContext[CareerAssistantDependencies], resume_text: str) -> ExtractedSkills:
    """Extract skills from resume text using LLM."""
    extraction_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=ExtractedSkills,
        system_prompt=(
            "Extract skills from the resume text. Categorize them into technical skills "
            "(programming languages, frameworks, tools), soft skills (communication, leadership), "
            "and domain skills (industry-specific knowledge)."
        )
    )
    
    result = await extraction_agent.run(f"Extract and categorize skills from this resume:\n\n{resume_text}")
    return result.output


@resume_analysis_agent.tool
async def extract_work_experience(ctx: RunContext[CareerAssistantDependencies], resume_text: str) -> List[ExtractedExperience]:
    """Extract work experience from resume text using LLM."""
    extraction_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=List[ExtractedExperience],
        system_prompt=(
            "Extract work experience from the resume text. For each position, identify "
            "the job title, company, duration, key achievements, and technologies used. "
            "Be thorough in extracting accomplishments and quantifiable results."
        )
    )
    
    result = await extraction_agent.run(f"Extract work experience from this resume:\n\n{resume_text}")
    return result.output


# Job Analysis Agent with Web Research
job_analysis_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    output_type=Union[JobAnalysis, CompanyResearch],
    system_prompt=(
        "You are an expert job market analyst and company researcher. You have access to:\n\n"
        "Tools available:\n"
        "- analyze_job_posting: Analyze job descriptions to extract requirements and insights\n"
        "- research_company: Research companies using web search tools when available\n\n"
        "When analyzing job postings, extract key requirements, preferred qualifications, "
        "responsibilities, company culture indicators, experience level, and technologies mentioned.\n\n"
        "When researching companies, provide comprehensive information including overview, "
        "recent news, culture and values, products/services, competitors, and interview insights. "
        "Use web search capabilities when available for the most current information."
    )
)


@job_analysis_agent.tool
async def analyze_job_posting(ctx: RunContext[CareerAssistantDependencies], job_description: str) -> JobAnalysis:
    """Analyze a job posting to extract key requirements and insights."""
    analysis_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=JobAnalysis,
        system_prompt=(
            "Analyze the job posting thoroughly. Extract key requirements, preferred qualifications, "
            "responsibilities, and any indicators about company culture. Identify the required "
            "experience level and technologies mentioned."
        )
    )
    
    result = await analysis_agent.run(f"Analyze this job posting:\n\n{job_description}")
    return result.output


@job_analysis_agent.tool
async def research_company(ctx: RunContext[CareerAssistantDependencies], company_name: str) -> CompanyResearch:
    """Research company using web search and scraping."""
    
    # Try to use MCP for company research, fallback to basic research
    research_context = f"Company name: {company_name}"
    
    if ctx.deps.exa_server:
        try:
            # Use Exa for web search about the company without starting connection
            search_results = await ctx.deps.exa_server.call_tool(
                'web_search_exa',
                {
                    'query': f"{company_name} company overview recent news culture values",
                    'numResults': 5
                }
            )
            research_context += f"\nWeb search results: {search_results}"
            
        except Exception as e:
            print(f"Web research failed, using fallback: {e}")
            # Continue with basic research context
    
    # Generate company research with available context
    company_research_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=CompanyResearch,
        system_prompt=(
            "Research the company and provide comprehensive information including overview, "
            "recent news, culture, products/services, competitors, and interview insights."
        )
    )
    
    company_research_result = await company_research_agent.run(
        f"Research this company and provide comprehensive information:\n\n{research_context}"
    )
    
    return company_research_result.output


# Application Materials Generation Agent
application_generation_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    system_prompt=(
        "You are an expert career coach and application writer. Create compelling, "
        "tailored application materials (resumes, cover letters) that highlight "
        "the candidate's relevant experience and skills for the specific role. "
        "Ensure ATS compatibility and professional presentation."
    )
)


@application_generation_agent.tool
async def generate_tailored_resume(
    ctx: RunContext[CareerAssistantDependencies], 
    job_analysis: JobAnalysis,
    focus_areas: List[str]
) -> str:
    """Generate a tailored resume based on job requirements."""
    if not ctx.deps.user_profile:
        raise ValueError("User profile not available")
    
    try:
        # Generate tailored resume
        resume_agent = Agent(
            'openai:gpt-4o',
            output_type=str,
            system_prompt=(
                "You are an expert resume writer and career coach with 15+ years of experience. "
                "Create comprehensive, ATS-optimized resumes that get candidates interviews.\n\n"
                "REQUIREMENTS:\n"
                "1. Create a full 1-2 page professional resume\n"
                "2. Use clear section headers: Contact, Professional Summary, Experience, Skills, Education\n"
                "3. Write compelling bullet points with quantified achievements\n"
                "4. Optimize for ATS with relevant keywords from the job posting\n"
                "5. Tailor content specifically to the target role\n"
                "6. Use action verbs and measurable results\n"
                "7. Professional formatting with consistent spacing\n"
                "8. Include 8-12 bullet points per job experience\n"
                "9. Add a compelling professional summary (3-4 lines)\n"
                "10. Organize skills by category (Technical, Tools, Soft Skills)\n\n"
                "Make this resume compelling enough to get the candidate an interview!"
            )
        )
        
        resume_context = f"""
Create a comprehensive, professional resume for this candidate:

**CANDIDATE PROFILE:**
Name: {ctx.deps.user_profile.personal_info.get('name', 'Professional')}
Email: {ctx.deps.user_profile.personal_info.get('email', '')}
Phone: {ctx.deps.user_profile.personal_info.get('phone', '')}
LinkedIn: {ctx.deps.user_profile.personal_info.get('linkedin', '')}
Location: {ctx.deps.user_profile.personal_info.get('location', '')}

**CANDIDATE SKILLS:**
{chr(10).join([f"• {skill.name} ({skill.proficiency.value if hasattr(skill, 'proficiency') else 'Experienced'})" for skill in ctx.deps.user_profile.skills])}

**WORK EXPERIENCE:**
{chr(10).join([f"""
{exp.job_title} at {exp.company} ({exp.duration_years} years)
Key Achievements: {chr(10).join([f"- {achievement}" for achievement in exp.key_achievements[:5]])}
""" for exp in ctx.deps.user_profile.work_experience])}

**TARGET ROLE:**
Position: {ctx.deps.job_posting.job_title}
Company: {ctx.deps.job_posting.company.name}

**JOB REQUIREMENTS TO ADDRESS:**
{chr(10).join([f"• {req}" for req in job_analysis.key_requirements[:10]] if job_analysis else ["• Product management experience", "• Technical leadership", "• Strategic thinking"])}

**KEY TECHNOLOGIES MENTIONED IN JOB:**
{', '.join(job_analysis.technologies_mentioned[:10]) if job_analysis else 'AI, Machine Learning, Product Management, Python, SQL'}

Create a compelling, detailed resume that positions this candidate as the ideal fit for this specific role.
"""
        
        result = await resume_agent.run(f"Create a tailored resume based on:\n\n{resume_context}")
        return result.output
        
    except Exception as e:
        # Fallback with minimal content
        print(f"Application generation error: {e}")
        return f"**{ctx.deps.user_profile.personal_info.get('name', 'Candidate')}**\n\nTailored resume for {ctx.deps.job_posting.job_title} at {ctx.deps.job_posting.company.name}\n\nContact: {ctx.deps.user_profile.personal_info.get('email', 'N/A')}\n\n**Skills:** {', '.join([skill.name for skill in ctx.deps.user_profile.skills[:10]])}\n\n**Experience:**\n{chr(10).join([f'• {exp.job_title} at {exp.company}' for exp in ctx.deps.user_profile.work_experience])}"


@application_generation_agent.tool
async def generate_cover_letter(
    ctx: RunContext[CareerAssistantDependencies],
    job_analysis: JobAnalysis,
    company_research: CompanyResearch
) -> str:
    """Generate a personalized cover letter."""
    if not ctx.deps.user_profile or not ctx.deps.job_posting:
        raise ValueError("User profile and job posting required")
    
    cover_letter_agent = Agent(
        'openai:gpt-4o',
        output_type=str,
        system_prompt=(
            "You are an expert cover letter writer with 15+ years of recruitment experience. "
            "Write compelling, personalized cover letters that get candidates interviews.\n\n"
            "REQUIREMENTS:\n"
            "1. Write a full, professional 3-4 paragraph cover letter\n"
            "2. Opening: Hook with specific company knowledge and enthusiasm\n"
            "3. Body 1: Directly address 3-4 key job requirements with specific examples\n"
            "4. Body 2: Show company research and cultural fit\n"
            "5. Closing: Strong call to action and next steps\n"
            "6. Use specific achievements with quantified results\n"
            "7. Demonstrate genuine knowledge of the company\n"
            "8. Show clear value proposition\n"
            "9. Professional tone with personality\n"
            "10. 250-400 words total length\n\n"
            "Make this cover letter compelling enough to get the hiring manager excited to meet the candidate!"
        )
    )
    
    cover_letter_context = f"""
Write a compelling cover letter for this application:

**CANDIDATE PROFILE:**
Name: {ctx.deps.user_profile.personal_info.get('name', 'Professional')}
Skills: {', '.join([skill.name for skill in ctx.deps.user_profile.skills[:8]])}

**WORK EXPERIENCE HIGHLIGHTS:**
{chr(10).join([f"""
{exp.job_title} at {exp.company}:
{chr(10).join([f"  • {achievement}" for achievement in exp.key_achievements[:3]])}
""" for exp in ctx.deps.user_profile.work_experience[:3]])}

**TARGET ROLE:**
Position: {ctx.deps.job_posting.job_title}
Company: {ctx.deps.job_posting.company.name}

**JOB REQUIREMENTS TO ADDRESS:**
{chr(10).join([f"• {req}" for req in job_analysis.key_requirements[:5]] if job_analysis else ["• Product management", "• Technical leadership", "• AI/ML experience"])}

**COMPANY RESEARCH:**
Overview: {company_research.company_overview[:300] if company_research else f"{ctx.deps.job_posting.company.name} is a leading technology company focused on digital innovation."}

Recent News: {chr(10).join([f"• {news}" for news in company_research.recent_news[:2]]) if company_research and company_research.recent_news else "• Expanding digital services and AI capabilities"}

Culture & Values: {', '.join(company_research.culture_and_values[:3]) if company_research and company_research.culture_and_values else "Innovation, Customer Focus, Excellence"}

**INSTRUCTIONS:**
Write a personalized cover letter that:
1. Shows specific knowledge of {ctx.deps.job_posting.company.name}
2. Addresses the key job requirements with concrete examples
3. Demonstrates cultural fit and genuine interest
4. Includes a compelling value proposition
5. Ends with a strong call to action
"""
    
    result = await cover_letter_agent.run(f"Write a cover letter based on:\n\n{cover_letter_context}")
    return result.output


# Interview Preparation Agent
interview_prep_agent = Agent(
    'openai:gpt-4o',
    deps_type=CareerAssistantDependencies,
    system_prompt=(
        "You are an expert interview coach. Prepare comprehensive interview "
        "materials including likely questions, STAR method answers, company "
        "research insights, and strategic advice for interview success."
    )
)


@interview_prep_agent.tool
async def generate_interview_questions(
    ctx: RunContext[CareerAssistantDependencies],
    job_analysis: JobAnalysis,
    company_research: CompanyResearch
) -> List[str]:
    """Generate likely interview questions based on the role and company."""
    questions_agent = Agent(
        'openai:gpt-4o-mini',
        output_type=List[str],
        system_prompt=(
            "Generate comprehensive interview questions that are likely to be asked "
            "for this specific role and company. Include behavioral, technical, "
            "situational, and company-specific questions."
        )
    )
    
    context = f"""
    Job Analysis: {job_analysis}
    Company Research: {company_research}
    """
    
    result = await questions_agent.run(f"Generate interview questions based on:\n\n{context}")
    return result.output


@interview_prep_agent.tool
async def create_star_responses(
    ctx: RunContext[CareerAssistantDependencies],
    interview_questions: List[str]
) -> Dict[str, str]:
    """Create STAR method responses for behavioral questions."""
    if not ctx.deps.user_profile:
        raise ValueError("User profile required")
    
    star_agent = Agent(
        'openai:gpt-4o',
        output_type=Dict[str, str],
        system_prompt=(
            "Create STAR method responses (Situation, Task, Action, Result) for "
            "behavioral interview questions using the candidate's experience. "
            "Make responses specific, quantifiable, and compelling."
        )
    )
    
    context = f"""
    User Profile: {ctx.deps.user_profile}
    Interview Questions: {interview_questions}
    """
    
    result = await star_agent.run(f"Create STAR responses based on:\n\n{context}")
    return result.output


# Main Multi-Agent Orchestrator
class CareerAssistantOrchestrator:
    """Orchestrates multiple agents for comprehensive career assistance."""
    
    def __init__(self):
        self.exa_server = None
        self.firecrawl_server = None
    
    async def setup_mcp_servers(self):
        """Set up MCP servers for web search and scraping."""
        exa_api_key = os.getenv('EXA_API_KEY')
        firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        
        if not exa_api_key:
            print("Warning: EXA_API_KEY not found. Web search capabilities will be limited.")
        else:
            try:
                self.exa_server = MCPServerStdio(
                    'npx',
                    args=['-y', 'exa-mcp-server'],
                    env={'EXA_API_KEY': exa_api_key}
                )
                print("✓ Exa MCP server initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize Exa MCP server: {e}")
                self.exa_server = None
        
        if not firecrawl_api_key:
            print("Warning: FIRECRAWL_API_KEY not found. Web scraping capabilities will be limited.")
        else:
            try:
                self.firecrawl_server = MCPServerStdio(
                    'npx',
                    args=['-y', 'firecrawl-mcp'],
                    env={'FIRECRAWL_API_KEY': firecrawl_api_key}
                )
                print("✓ Firecrawl MCP server initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize Firecrawl MCP server: {e}")
                self.firecrawl_server = None
    
    async def process_resume(self, resume_text: str) -> UserProfile:
        """Process resume using multi-agent system."""
        deps = CareerAssistantDependencies()
        
        # Create a dedicated extraction agent that outputs UserProfile directly
        extraction_agent = Agent(
            'openai:gpt-4o',
            output_type=UserProfile,
            system_prompt=(
                "You are an expert resume analyzer. Extract structured information from resumes "
                "and return a complete UserProfile. \n\n"
                "IMPORTANT: You must provide valid data for ALL required fields:\n"
                "- personal_info: Dict with keys like 'name', 'email', 'phone', 'linkedin', 'location'\n"
                "- skills: List of Skill objects with name and proficiency\n"
                "- work_experience: List of WorkExperience objects\n"
                "- education: List of Education objects (can be empty if not found)\n"
                "- career_goals: CareerGoals object with target_roles, preferred_industries, experience_level_target\n\n"
                "For career_goals, if not explicitly mentioned, infer reasonable defaults based on the resume content.\n"
                "For skills proficiency, use: 'beginner', 'intermediate', 'advanced', or 'expert'\n"
                "For experience_level_target, use: 'entry', 'junior', 'mid', 'senior', 'lead', or 'executive'"
            )
        )
        
        result = await extraction_agent.run(
            f"""Extract all information from this resume into a UserProfile. 

Example structure needed:
{{
  "personal_info": {{"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"}},
  "skills": [{{"name": "Python", "proficiency": "advanced"}}, {{"name": "Leadership", "proficiency": "intermediate"}}],
  "work_experience": [{{"job_title": "Software Engineer", "company": "Tech Corp", "duration_years": 3.0, "key_achievements": ["Built scalable systems"]}}],
  "education": [],
  "career_goals": {{
    "target_roles": ["Senior Software Engineer", "Tech Lead"],
    "preferred_industries": ["Technology"],
    "experience_level_target": "senior"
  }}
}}

Resume text:
{resume_text}"""
        )
        
        return result.output
    
    async def analyze_job_and_company(self, job_description: str, company_name: str) -> tuple[JobAnalysis, CompanyResearch]:
        """Analyze job posting and research company."""
        deps = CareerAssistantDependencies(
            exa_server=self.exa_server,
            firecrawl_server=self.firecrawl_server
        )
        
        # Let the job analysis agent analyze the job posting
        job_result = await job_analysis_agent.run(
            f"Please analyze this job posting and extract key requirements, responsibilities, and other important details:\n\n{job_description}",
            deps=deps
        )
        
        # Let the job analysis agent research the company 
        company_result = await job_analysis_agent.run(
            f"Please research the company '{company_name}' and provide comprehensive information including overview, recent news, culture, competitors, and interview insights. Use available web search tools if possible.",
            deps=deps
        )
        
        return job_result.output, company_result.output
    
    async def generate_application_package(
        self,
        user_profile: UserProfile,
        job_posting: JobPosting,
        job_analysis: JobAnalysis,
        company_research: CompanyResearch
    ) -> SimpleApplicationPackage:
        """Generate simple application package using multi-agent system."""
        deps = CareerAssistantDependencies(
            user_profile=user_profile,
            job_posting=job_posting
        )
        
        try:
            # Generate tailored resume
            resume_agent = Agent(
                'openai:gpt-4o',
                output_type=str,
                system_prompt=(
                    "You are an expert resume writer and career coach with 15+ years of experience. "
                    "Create comprehensive, ATS-optimized resumes that get candidates interviews.\n\n"
                    "REQUIREMENTS:\n"
                    "1. Create a full 1-2 page professional resume\n"
                    "2. Use clear section headers: Contact, Professional Summary, Experience, Skills, Education\n"
                    "3. Write compelling bullet points with quantified achievements\n"
                    "4. Optimize for ATS with relevant keywords from the job posting\n"
                    "5. Tailor content specifically to the target role\n"
                    "6. Use action verbs and measurable results\n"
                    "7. Professional formatting with consistent spacing\n"
                    "8. Include 8-12 bullet points per job experience\n"
                    "9. Add a compelling professional summary (3-4 lines)\n"
                    "10. Organize skills by category (Technical, Tools, Soft Skills)\n\n"
                    "Make this resume compelling enough to get the candidate an interview!"
                )
            )
            
            resume_context = f"""
Create a comprehensive, professional resume for this candidate:

**CANDIDATE PROFILE:**
Name: {user_profile.personal_info.get('name', 'Professional')}
Email: {user_profile.personal_info.get('email', '')}
Phone: {user_profile.personal_info.get('phone', '')}
LinkedIn: {user_profile.personal_info.get('linkedin', '')}
Location: {user_profile.personal_info.get('location', '')}

**CANDIDATE SKILLS:**
{chr(10).join([f"• {skill.name} ({skill.proficiency.value if hasattr(skill, 'proficiency') else 'Experienced'})" for skill in user_profile.skills])}

**WORK EXPERIENCE:**
{chr(10).join([f"""
{exp.job_title} at {exp.company} ({exp.duration_years} years)
Key Achievements: {chr(10).join([f"- {achievement}" for achievement in exp.key_achievements[:5]])}
""" for exp in user_profile.work_experience])}

**TARGET ROLE:**
Position: {job_posting.job_title}
Company: {job_posting.company.name}

**JOB REQUIREMENTS TO ADDRESS:**
{chr(10).join([f"• {req}" for req in job_analysis.key_requirements[:10]] if job_analysis else ["• Product management experience", "• Technical leadership", "• Strategic thinking"])}

**KEY TECHNOLOGIES MENTIONED IN JOB:**
{', '.join(job_analysis.technologies_mentioned[:10]) if job_analysis else 'AI, Machine Learning, Product Management, Python, SQL'}

Create a compelling, detailed resume that positions this candidate as the ideal fit for this specific role.
"""
            
            result = await resume_agent.run(f"Create a tailored resume based on:\n\n{resume_context}")
            
            # Generate cover letter
            cover_letter_agent = Agent(
                'openai:gpt-4o',
                output_type=str,
                system_prompt=(
                    "You are an expert cover letter writer with 15+ years of recruitment experience. "
                    "Write compelling, personalized cover letters that get candidates interviews.\n\n"
                    "REQUIREMENTS:\n"
                    "1. Write a full, professional 3-4 paragraph cover letter\n"
                    "2. Opening: Hook with specific company knowledge and enthusiasm\n"
                    "3. Body 1: Directly address 3-4 key job requirements with specific examples\n"
                    "4. Body 2: Show company research and cultural fit\n"
                    "5. Closing: Strong call to action and next steps\n"
                    "6. Use specific achievements with quantified results\n"
                    "7. Demonstrate genuine knowledge of the company\n"
                    "8. Show clear value proposition\n"
                    "9. Professional tone with personality\n"
                    "10. 250-400 words total length\n\n"
                    "Make this cover letter compelling enough to get the hiring manager excited to meet the candidate!"
                )
            )
            
            cover_letter_context = f"""
Write a compelling cover letter for this application:

**CANDIDATE PROFILE:**
Name: {user_profile.personal_info.get('name', 'Professional')}
Skills: {', '.join([skill.name for skill in user_profile.skills[:8]])}

**WORK EXPERIENCE HIGHLIGHTS:**
{chr(10).join([f"""
{exp.job_title} at {exp.company}:
{chr(10).join([f"  • {achievement}" for achievement in exp.key_achievements[:3]])}
""" for exp in user_profile.work_experience[:3]])}

**TARGET ROLE:**
Position: {job_posting.job_title}
Company: {job_posting.company.name}

**JOB REQUIREMENTS TO ADDRESS:**
{chr(10).join([f"• {req}" for req in job_analysis.key_requirements[:5]] if job_analysis else ["• Product management", "• Technical leadership", "• AI/ML experience"])}

**COMPANY RESEARCH:**
Overview: {company_research.company_overview[:300] if company_research else f"{job_posting.company.name} is a leading technology company focused on digital innovation."}

Recent News: {chr(10).join([f"• {news}" for news in company_research.recent_news[:2]]) if company_research and company_research.recent_news else "• Expanding digital services and AI capabilities"}

Culture & Values: {', '.join(company_research.culture_and_values[:3]) if company_research and company_research.culture_and_values else "Innovation, Customer Focus, Excellence"}

**INSTRUCTIONS:**
Write a personalized cover letter that:
1. Shows specific knowledge of {job_posting.company.name}
2. Addresses the key job requirements with concrete examples
3. Demonstrates cultural fit and genuine interest
4. Includes a compelling value proposition
5. Ends with a strong call to action
"""
            
            cover_letter_result = await cover_letter_agent.run(f"Write a cover letter based on:\n\n{cover_letter_context}")
            
            # Generate interview questions and responses
            interview_agent = Agent(
                'openai:gpt-4o',
                output_type=Dict[str, Any],
                system_prompt=(
                    "You are an expert interview coach with 20+ years of experience helping candidates "
                    "succeed in technical and executive interviews.\n\n"
                    "Create comprehensive interview preparation that includes:\n"
                    "1. 15-20 likely interview questions (behavioral, technical, company-specific)\n"
                    "2. 8-10 detailed STAR method responses with specific examples\n"
                    "3. 10+ preparation tips tailored to the role and company\n"
                    "4. Company insights and conversation starters\n"
                    "5. Questions for the candidate to ask interviewers\n"
                    "6. Salary negotiation guidance\n"
                    "7. Follow-up strategies\n\n"
                    "Return a detailed dictionary with these sections. Make the preparation "
                    "comprehensive enough to build genuine confidence."
                )
            )
            
            interview_context = f"""
Create comprehensive interview preparation for this candidate:

**CANDIDATE PROFILE:**
Name: {user_profile.personal_info.get('name', 'Professional')}

**WORK EXPERIENCE:**
{chr(10).join([f"""
{exp.job_title} at {exp.company} ({exp.duration_years} years):
{chr(10).join([f"  • {achievement}" for achievement in exp.key_achievements])}
""" for exp in user_profile.work_experience])}

**SKILLS:**
Technical: {', '.join([skill.name for skill in user_profile.skills if skill.name.lower() in ['python', 'sql', 'ai', 'machine learning', 'product management', 'analytics', 'data', 'engineering']])}
Other: {', '.join([skill.name for skill in user_profile.skills if skill.name.lower() not in ['python', 'sql', 'ai', 'machine learning', 'product management', 'analytics', 'data', 'engineering']][:5])}

**TARGET ROLE:**
Position: {job_posting.job_title}
Company: {job_posting.company.name}

**JOB REQUIREMENTS:**
{chr(10).join([f"• {req}" for req in job_analysis.key_requirements] if job_analysis else ["• Product management experience", "• Technical leadership", "• Strategic thinking"])}

**COMPANY INSIGHTS:**
Overview: {company_research.company_overview if company_research else f"{job_posting.company.name} is a leading technology company."}
Culture: {', '.join(company_research.culture_and_values) if company_research and company_research.culture_and_values else "Innovation-focused, collaborative culture"}
Recent News: {chr(10).join(company_research.recent_news) if company_research and company_research.recent_news else "Expanding digital capabilities and AI initiatives"}

**INSTRUCTIONS:**
Create a comprehensive interview preparation package that includes:
1. questions: List of 15-20 potential interview questions
2. star_responses: Dictionary with 8-10 detailed STAR responses
3. preparation_tips: List of 10+ actionable preparation tips
4. company_insights: Key talking points about the company
5. questions_to_ask: 8-10 thoughtful questions for the interviewer
6. salary_guidance: Negotiation tips and market insights
7. follow_up_strategy: Post-interview action plan

Make this thorough enough to give the candidate genuine confidence and competitive advantage.
"""
            
            interview_result = await interview_agent.run(f"Create interview preparation based on:\n\n{interview_context}")
            
            return SimpleApplicationPackage(
                optimized_resume=result.output,
                cover_letter=cover_letter_result.output,
                interview_preparation=interview_result.output,
                application_strategy="Focus on relevant experience and cultural fit with emphasis on AI/ML expertise"
            )
            
        except Exception as e:
            # Fallback with minimal content
            print(f"Application generation error: {e}")
            return SimpleApplicationPackage(
                optimized_resume=self._generate_detailed_fallback_resume(user_profile, job_posting, job_analysis),
                cover_letter=self._generate_detailed_fallback_cover_letter(user_profile, job_posting, company_research),
                interview_preparation=self._generate_detailed_fallback_interview_prep(user_profile, job_posting, job_analysis),
                application_strategy="Focus on relevant experience and cultural fit with emphasis on technical expertise and leadership potential"
            )
    
    def _generate_detailed_fallback_resume(self, user_profile: UserProfile, job_posting: JobPosting, job_analysis: JobAnalysis) -> str:
        """Generate a detailed fallback resume."""
        name = user_profile.personal_info.get('name', 'Professional Candidate')
        email = user_profile.personal_info.get('email', '')
        phone = user_profile.personal_info.get('phone', '')
        linkedin = user_profile.personal_info.get('linkedin', '')
        location = user_profile.personal_info.get('location', '')
        
        # Contact section
        contact_section = f"""# {name}
**Email:** {email} | **Phone:** {phone}
**LinkedIn:** {linkedin} | **Location:** {location}

---

## Professional Summary

Results-driven {job_posting.job_title} with {sum(exp.duration_years for exp in user_profile.work_experience):.0f}+ years of experience in {', '.join([skill.name for skill in user_profile.skills[:3]])}. Proven track record of leading cross-functional teams, driving product strategy, and delivering innovative solutions that drive business growth. Expertise in {', '.join([skill.name for skill in user_profile.skills[3:8]])} with a passion for leveraging technology to solve complex business challenges.

---

## Professional Experience
"""
        
        # Experience section
        for exp in user_profile.work_experience:
            contact_section += f"""
### {exp.job_title}
**{exp.company}** | {exp.duration_years} years

"""
            if exp.key_achievements:
                for achievement in exp.key_achievements:
                    contact_section += f"• {achievement}\n"
            else:
                contact_section += f"• Led strategic initiatives and cross-functional projects\n"
                contact_section += f"• Drove product development and feature enhancement\n"
                contact_section += f"• Collaborated with engineering and design teams\n"
        
        # Skills section
        technical_skills = [skill.name for skill in user_profile.skills if skill.name.lower() in ['python', 'sql', 'ai', 'machine learning', 'product management', 'analytics', 'data', 'engineering', 'aws', 'cloud']]
        other_skills = [skill.name for skill in user_profile.skills if skill.name not in technical_skills]
        
        contact_section += f"""
---

## Core Competencies

**Technical Skills:** {', '.join(technical_skills[:10])}

**Leadership & Strategy:** {', '.join(other_skills[:8])}

**Industry Knowledge:** Product Management, Strategic Planning, Cross-functional Leadership, Data-Driven Decision Making

---

## Education

"""
        if user_profile.education:
            for edu in user_profile.education:
                contact_section += f"**{edu.degree}** | {edu.institution} | {edu.graduation_year}\n"
        else:
            contact_section += "**Bachelor's Degree** | Computer Science/Engineering/Business\n"
        
        return contact_section
    
    def _generate_detailed_fallback_cover_letter(self, user_profile: UserProfile, job_posting: JobPosting, company_research: CompanyResearch) -> str:
        """Generate a detailed fallback cover letter."""
        name = user_profile.personal_info.get('name', 'Professional Candidate')
        
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_posting.job_title} position at {job_posting.company.name}. With my extensive background in {', '.join([skill.name for skill in user_profile.skills[:3]])}, I am excited about the opportunity to contribute to your team's continued success and innovation.

In my {sum(exp.duration_years for exp in user_profile.work_experience):.0f} years of professional experience, I have consistently delivered impactful results across {len(user_profile.work_experience)} different roles. At {user_profile.work_experience[0].company if user_profile.work_experience else 'Previous Company'}, I {user_profile.work_experience[0].key_achievements[0] if user_profile.work_experience and user_profile.work_experience[0].key_achievements else 'led strategic initiatives that drove significant business growth'}. This experience has prepared me well for the challenges and opportunities inherent in the {job_posting.job_title} role.

What particularly attracts me to {job_posting.company.name} is {company_research.company_overview[:100] if company_research else 'your commitment to innovation and excellence in the technology sector'}. Your focus on {', '.join(company_research.culture_and_values[:2]) if company_research and company_research.culture_and_values else 'customer-centric solutions and technological advancement'} aligns perfectly with my professional values and career aspirations.

I am particularly excited about the opportunity to leverage my expertise in {', '.join([skill.name for skill in user_profile.skills[:5]])} to help drive {job_posting.company.name}'s strategic objectives. My proven ability to work effectively with cross-functional teams, combined with my analytical mindset and passion for innovation, positions me well to make an immediate impact in this role.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's success. Thank you for considering my application, and I look forward to hearing from you soon.

Sincerely,
{name}"""
    
    def _generate_detailed_fallback_interview_prep(self, user_profile: UserProfile, job_posting: JobPosting, job_analysis: JobAnalysis) -> Dict[str, Any]:
        """Generate detailed fallback interview preparation."""
        return {
            "questions": [
                f"Why are you interested in the {job_posting.job_title} role at {job_posting.company.name}?",
                "Tell me about yourself and your background.",
                "What's your greatest professional achievement?",
                "How do you handle challenging situations or setbacks?",
                "Describe a time when you had to lead a cross-functional team.",
                "What's your approach to product strategy and prioritization?",
                "How do you stay current with industry trends and technologies?",
                "Tell me about a time you had to make a difficult decision with limited information.",
                "How do you measure success in your current role?",
                "What attracts you to our company specifically?",
                "Where do you see yourself in 5 years?",
                "How do you handle competing priorities and tight deadlines?",
                "Describe your experience with data-driven decision making.",
                "What's your approach to stakeholder management?",
                "Tell me about a time you had to influence without authority."
            ],
            "star_responses": {
                "Leadership Example": f"SITUATION: At {user_profile.work_experience[0].company if user_profile.work_experience else 'Previous Company'}, we faced a critical project deadline with multiple stakeholders. TASK: I needed to coordinate a cross-functional team of 8 people across engineering, design, and business teams. ACTION: I implemented daily standups, created clear communication channels, and established milestone tracking. RESULT: We delivered the project 2 weeks ahead of schedule and improved team collaboration processes.",
                "Problem Solving": "SITUATION: Encountered a significant technical challenge that was blocking product development. TASK: Find a solution that wouldn't delay our release timeline. ACTION: Researched alternative approaches, consulted with technical experts, and proposed a phased implementation plan. RESULT: Successfully resolved the issue and maintained our launch schedule while improving system performance.",
                "Innovation": f"SITUATION: Identified an opportunity to improve our product using {user_profile.skills[0].name if user_profile.skills else 'emerging technology'}. TASK: Develop and implement a solution that would differentiate us from competitors. ACTION: Led research, built a prototype, and presented the business case to leadership. RESULT: Secured funding and increased user engagement by 25%.",
                "Stakeholder Management": "SITUATION: Multiple stakeholders had conflicting priorities for our product roadmap. TASK: Align everyone on a unified strategy while maintaining key relationships. ACTION: Facilitated workshops, gathered data on user impact, and created a prioritization framework. RESULT: Achieved consensus and improved stakeholder satisfaction scores."
            },
            "preparation_tips": [
                f"Research {job_posting.company.name}'s recent news, products, and company culture",
                "Prepare specific examples that demonstrate your impact using the STAR method",
                "Practice explaining technical concepts in business terms",
                "Review the job description and prepare examples for each requirement",
                "Prepare thoughtful questions about the role, team, and company strategy",
                "Research the interviewer's background on LinkedIn if possible",
                "Practice your elevator pitch and be ready to summarize your experience",
                "Prepare to discuss your career goals and how they align with the role",
                "Be ready to explain why you're leaving your current position",
                "Prepare examples of how you've handled failure or setbacks",
                "Practice discussing salary expectations and compensation",
                "Prepare examples of successful cross-functional collaboration"
            ],
            "questions_to_ask": [
                "What are the biggest challenges facing the team right now?",
                "How do you measure success in this role?",
                "What's the team structure and who would I work with most closely?",
                "What's the company's product roadmap for the next year?",
                "How does this role contribute to the company's strategic objectives?",
                "What opportunities exist for professional development and growth?",
                "What's the company culture like day-to-day?",
                "What are the next steps in the interview process?"
            ],
            "company_insights": f"Focus on {job_posting.company.name}'s mission, recent developments, and how your skills align with their strategic direction.",
            "follow_up_strategy": "Send thank-you emails within 24 hours, reiterating your interest and highlighting key discussion points from the interview."
        }


# Create global orchestrator instance
career_assistant_orchestrator = CareerAssistantOrchestrator() 