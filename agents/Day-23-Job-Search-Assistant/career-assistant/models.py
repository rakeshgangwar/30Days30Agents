"""Core Pydantic models for the Career Application Assistant."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    """Experience levels for roles and user background."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class SkillProficiency(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """A skill with proficiency level and years of experience."""
    name: str = Field(description="Name of the skill")
    proficiency: SkillProficiency = Field(description="Proficiency level")
    years_experience: Optional[int] = Field(None, description="Years of experience with this skill")
    certifications: List[str] = Field(default_factory=list, description="Related certifications")


class WorkExperience(BaseModel):
    """Work experience entry."""
    job_title: str = Field(description="Job title/position")
    company: str = Field(description="Company name")
    duration_years: float = Field(description="Duration in years")
    key_achievements: List[str] = Field(description="Key achievements and accomplishments")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies and tools used")
    quantified_impact: Optional[str] = Field(None, description="Quantified impact/metrics")


class Education(BaseModel):
    """Education entry."""
    degree: str = Field(description="Degree name")
    institution: str = Field(description="Institution name")
    graduation_year: Optional[int] = Field(None, description="Graduation year")
    gpa: Optional[float] = Field(None, description="GPA if relevant")
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant coursework")


class CareerGoals(BaseModel):
    """User's career goals and preferences."""
    target_roles: List[str] = Field(description="Target job titles/roles")
    preferred_industries: List[str] = Field(default_factory=list, description="Preferred industries")
    experience_level_target: ExperienceLevel = Field(description="Target experience level")
    salary_expectations: Optional[str] = Field(None, description="Salary expectations")
    work_preferences: Dict[str, Union[str, bool]] = Field(
        default_factory=dict, 
        description="Work preferences (remote, location, etc.)"
    )


class UserProfile(BaseModel):
    """Complete user profile for career assistance."""
    personal_info: Dict[str, str] = Field(description="Basic personal information")
    skills: List[Skill] = Field(description="Technical and soft skills")
    work_experience: List[WorkExperience] = Field(description="Work experience history")
    education: List[Education] = Field(description="Educational background")
    career_goals: CareerGoals = Field(description="Career goals and preferences")
    resume_text: Optional[str] = Field(None, description="Full resume text")
    created_at: datetime = Field(default_factory=datetime.now, description="Profile creation date")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update date")


class JobRequirement(BaseModel):
    """A job requirement with importance level."""
    requirement: str = Field(description="The requirement description")
    importance: str = Field(description="Importance level: required, preferred, nice-to-have")
    skill_category: Optional[str] = Field(None, description="Category of the skill/requirement")


class CompanyInfo(BaseModel):
    """Company information and culture."""
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    size: Optional[str] = Field(None, description="Company size")
    culture_values: List[str] = Field(default_factory=list, description="Company culture and values")
    benefits: List[str] = Field(default_factory=list, description="Benefits offered")


class JobPosting(BaseModel):
    """Structured job posting data."""
    job_title: str = Field(description="Job title")
    company: CompanyInfo = Field(description="Company information")
    location: Optional[str] = Field(None, description="Job location")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Required experience level")
    salary_range: Optional[str] = Field(None, description="Salary range")
    job_description: str = Field(description="Full job description")
    key_responsibilities: List[str] = Field(description="Key responsibilities")
    requirements: List[JobRequirement] = Field(description="Job requirements")
    posted_date: Optional[datetime] = Field(None, description="Job posting date")


class MatchScore(BaseModel):
    """Compatibility score between user and job."""
    overall_score: float = Field(ge=0, le=1, description="Overall match score (0-1)")
    skills_match: float = Field(ge=0, le=1, description="Skills compatibility score")
    experience_match: float = Field(ge=0, le=1, description="Experience level match")
    requirements_met: int = Field(description="Number of requirements met")
    total_requirements: int = Field(description="Total number of requirements")
    strengths: List[str] = Field(description="User's strengths for this role")
    gaps: List[str] = Field(description="Skill/experience gaps")


class ResumeOptimization(BaseModel):
    """Resume optimization suggestions."""
    tailored_bullet_points: List[str] = Field(description="Tailored resume bullet points")
    keywords_to_include: List[str] = Field(description="Important keywords to include")
    sections_to_emphasize: List[str] = Field(description="Resume sections to emphasize")
    achievements_to_highlight: List[str] = Field(description="Specific achievements to highlight")
    ats_optimization_tips: List[str] = Field(description="ATS optimization suggestions")


class CoverLetterContent(BaseModel):
    """Generated cover letter content."""
    opening_paragraph: str = Field(description="Opening paragraph")
    body_paragraphs: List[str] = Field(description="Body paragraphs highlighting experience")
    closing_paragraph: str = Field(description="Closing paragraph")
    key_experiences_to_mention: List[str] = Field(description="Key experiences to mention")


class InterviewQuestion(BaseModel):
    """Interview question with context and preparation tips."""
    question: str = Field(description="Interview question")
    question_type: str = Field(description="Type: behavioral, technical, situational, etc.")
    context: str = Field(description="Why this question might be asked")
    preparation_tips: List[str] = Field(description="Tips for preparing the answer")
    example_structure: Optional[str] = Field(None, description="Suggested answer structure")


class InterviewPreparation(BaseModel):
    """Complete interview preparation package."""
    role_specific_questions: List[InterviewQuestion] = Field(description="Role-specific questions")
    behavioral_questions: List[InterviewQuestion] = Field(description="Behavioral questions")
    company_specific_questions: List[InterviewQuestion] = Field(description="Company-specific questions")
    questions_for_interviewer: List[str] = Field(description="Questions to ask the interviewer")
    preparation_strategy: str = Field(description="Overall preparation strategy")


class SkillGapAnalysis(BaseModel):
    """Analysis of skill gaps and development recommendations."""
    critical_gaps: List[str] = Field(description="Critical skills missing")
    nice_to_have_gaps: List[str] = Field(description="Nice-to-have skills missing")
    development_priorities: List[str] = Field(description="Prioritized list of skills to develop")
    learning_resources: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Learning resources for each skill"
    )
    timeline_recommendations: Dict[str, str] = Field(
        default_factory=dict, 
        description="Recommended learning timeline for each skill"
    )


class CareerGuidance(BaseModel):
    """Strategic career guidance and recommendations."""
    positioning_strategy: str = Field(description="How to position yourself for this role")
    application_approach: str = Field(description="Recommended application approach")
    networking_suggestions: List[str] = Field(description="Networking and outreach suggestions")
    alternative_paths: List[str] = Field(description="Alternative career paths to consider")
    market_insights: str = Field(description="Relevant market insights")


# Complete Document Models

class CompleteResume(BaseModel):
    """Complete optimized resume document."""
    header: Dict[str, str] = Field(description="Resume header with contact info")
    professional_summary: str = Field(description="Professional summary section")
    core_skills: List[str] = Field(description="Core skills section")
    work_experience: List[Dict[str, Union[str, List[str]]]] = Field(description="Optimized work experience")
    education: List[Dict[str, str]] = Field(description="Education section")
    additional_sections: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Additional sections like certifications, projects"
    )
    ats_keywords: List[str] = Field(description="Important ATS keywords included")
    formatting_notes: List[str] = Field(description="Formatting recommendations")


class CompleteCoverLetter(BaseModel):
    """Complete cover letter document."""
    header: Dict[str, str] = Field(description="Cover letter header")
    date: str = Field(description="Date of application")
    recipient_info: Dict[str, str] = Field(description="Hiring manager/company info")
    subject_line: Optional[str] = Field(None, description="Email subject line")
    salutation: str = Field(description="Opening salutation")
    opening_paragraph: str = Field(description="Opening paragraph")
    body_paragraphs: List[str] = Field(description="Body paragraphs")
    closing_paragraph: str = Field(description="Closing paragraph")
    sign_off: str = Field(description="Professional sign-off")
    personalization_notes: List[str] = Field(description="Notes for further personalization")


class CompleteInterviewPrep(BaseModel):
    """Complete interview preparation document."""
    overview: str = Field(description="Overview of the interview preparation strategy")
    company_research: Dict[str, str] = Field(description="Company research summary")
    role_analysis: Dict[str, str] = Field(description="Role requirements analysis")
    
    # Question sections
    behavioral_questions: List[Dict[str, Union[str, List[str]]]] = Field(
        description="Behavioral questions with STAR method answers"
    )
    technical_questions: List[Dict[str, Union[str, List[str]]]] = Field(
        description="Technical questions and preparation tips"
    )
    company_specific_questions: List[Dict[str, Union[str, List[str]]]] = Field(
        description="Company-specific questions"
    )
    
    # Your questions to ask
    questions_to_ask: List[Dict[str, str]] = Field(
        description="Questions to ask the interviewer with reasoning"
    )
    
    # Preparation sections
    key_talking_points: List[str] = Field(description="Key points to emphasize about yourself")
    success_stories: List[Dict[str, str]] = Field(description="STAR method success stories")
    potential_concerns: List[Dict[str, str]] = Field(description="Potential concerns and how to address them")
    
    # Final preparation
    day_of_interview: List[str] = Field(description="Day of interview checklist")
    follow_up_strategy: str = Field(description="Post-interview follow-up strategy")


# Main Agent Output Models

class ProfileAnalysisOutput(BaseModel):
    """Output for user profile analysis against a job."""
    match_score: MatchScore = Field(description="Compatibility analysis")
    skill_gap_analysis: SkillGapAnalysis = Field(description="Skill gap analysis")
    career_guidance: CareerGuidance = Field(description="Strategic career guidance")
    summary: str = Field(description="Executive summary of the analysis")


class ResumeOptimizationOutput(BaseModel):
    """Output for resume optimization requests."""
    resume_optimization: ResumeOptimization = Field(description="Resume optimization suggestions")
    match_improvement: str = Field(description="How these changes improve job match")
    implementation_priority: List[str] = Field(description="Priority order for implementing changes")
    summary: str = Field(description="Summary of optimization strategy")


class CoverLetterOutput(BaseModel):
    """Output for cover letter generation."""
    cover_letter: CoverLetterContent = Field(description="Generated cover letter content")
    personalization_notes: List[str] = Field(description="Notes on personalizing the content")
    tone_recommendations: str = Field(description="Recommended tone and style")
    summary: str = Field(description="Summary of the cover letter approach")


class InterviewPrepOutput(BaseModel):
    """Output for interview preparation."""
    interview_preparation: InterviewPreparation = Field(description="Complete interview prep package")
    focus_areas: List[str] = Field(description="Key areas to focus preparation on")
    confidence_building_tips: List[str] = Field(description="Tips for building confidence")
    summary: str = Field(description="Interview preparation summary")


class JobSummaryOutput(BaseModel):
    """Output for job description analysis and summary."""
    job_summary: str = Field(description="Concise job summary")
    key_highlights: List[str] = Field(description="Key highlights relevant to user")
    requirements_breakdown: Dict[str, List[str]] = Field(
        description="Requirements categorized by type"
    )
    company_analysis: str = Field(description="Company culture and fit analysis")
    recommendation: str = Field(description="Recommendation on whether to apply")


# New Complete Document Output Models

class CompleteApplicationPackage(BaseModel):
    """Complete application package with optimized resume, cover letter, and interview prep."""
    optimized_resume: CompleteResume = Field(description="Complete optimized resume")
    cover_letter: CompleteCoverLetter = Field(description="Complete cover letter")
    interview_preparation: CompleteInterviewPrep = Field(description="Complete interview preparation guide")
    application_strategy: str = Field(description="Overall application strategy and timeline")
    success_probability: float = Field(ge=0, le=1, description="Estimated success probability") 