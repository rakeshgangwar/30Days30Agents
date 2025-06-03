"""Streamlined CLI for the Career Application Assistant with new user flow."""

import asyncio
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from rich import print

from models import (
    UserProfile, JobPosting, CompanyInfo, ExperienceLevel, 
    Skill, SkillProficiency, WorkExperience, CareerGoals
)
from document_processor import DocumentProcessor
from agent import career_assistant_orchestrator, JobAnalysis, CompanyResearch, SimpleApplicationPackage

console = Console()


class StreamlinedCareerCLI:
    """Streamlined CLI for career application assistance with multi-agent system."""
    
    def __init__(self):
        self.user_profile: Optional[UserProfile] = None
        self.job_posting: Optional[JobPosting] = None
        self.job_analysis: Optional[JobAnalysis] = None
        self.company_research: Optional[CompanyResearch] = None
    
    async def start(self):
        """Start the streamlined application process."""
        console.print(Panel.fit(
            "[bold blue]🚀 Career Application Assistant[/bold blue]\n"
            "[cyan]AI-Powered Multi-Agent Application Package Generator[/cyan]\n"
            "Upload resume → Add job details → Get optimized application materials\n"
            "[dim]Powered by PydanticAI with Exa Search & Firecrawl integration[/dim]",
            style="cyan"
        ))
        
        try:
            # Initialize MCP servers
            await self.setup_mcp_integration()
            
            # Step 1: Resume Upload and Processing
            await self.upload_and_process_resume()
            
            # Step 2: Job Information Collection
            await self.collect_job_information()
            
            # Step 3: Generate Complete Application Package
            await self.generate_application_package()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Application cancelled. Goodbye![/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ An error occurred: {e}[/red]")
    
    async def setup_mcp_integration(self):
        """Set up MCP servers for enhanced capabilities."""
        console.print("\n[bold cyan]🔧 Setting up AI-powered research capabilities...[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing web search and scraping tools...", total=None)
            await career_assistant_orchestrator.setup_mcp_servers()
            progress.update(task, completed=True)
        
        console.print("[green]✅ AI research tools ready![/green]")
    
    async def upload_and_process_resume(self):
        """Step 1: Upload and process the user's resume using AI agents."""
        console.print("\n" + "="*60)
        console.print("[bold yellow]📄 Step 1: AI-Powered Resume Analysis[/bold yellow]")
        
        # Get resume file path
        while True:
            resume_path = Prompt.ask(
                "\n[cyan]Please provide the path to your resume file[/cyan]\n"
                "[dim](Supported formats: PDF, DOCX, TXT)[/dim]"
            )
            
            if not resume_path:
                console.print("[red]Please provide a resume file path.[/red]")
                continue
            
            # Expand user path
            resume_path = os.path.expanduser(resume_path)
            
            if not os.path.exists(resume_path):
                console.print(f"[red]File not found: {resume_path}[/red]")
                continue
            
            try:
                # Extract text from resume
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Extracting text from resume...", total=None)
                    resume_text = DocumentProcessor.extract_resume_text(resume_path)
                    progress.update(task, completed=True)
                
                console.print("[green]✅ Resume text extracted successfully![/green]")
                break
                
            except Exception as e:
                console.print(f"[red]Error processing resume: {e}[/red]")
                if not Confirm.ask("Would you like to try a different file?"):
                    raise
        
        # Process resume using AI agents
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 AI agents analyzing your resume...", total=None)
            
            try:
                self.user_profile = await career_assistant_orchestrator.process_resume(resume_text)
                progress.update(task, completed=True)
            except Exception as e:
                console.print(f"[red]Error during AI analysis: {e}[/red]")
                # Fallback to basic processing
                progress.update(task, description="Falling back to basic processing...")
                self.user_profile = await self.fallback_resume_processing(resume_text)
                progress.update(task, completed=True)
        
        # Display extracted information
        console.print("\n[bold green]🎯 AI-Extracted Profile Information:[/bold green]")
        
        # Contact info
        if self.user_profile.personal_info:
            info_text = "\n".join([f"{k.title()}: {v}" for k, v in self.user_profile.personal_info.items() if v])
            console.print(Panel(info_text, title="👤 Contact Information", style="blue"))
        
        # Skills
        if self.user_profile.skills:
            skills_text = ", ".join([skill.name for skill in self.user_profile.skills[:15]])
            if len(self.user_profile.skills) > 15:
                skills_text += f" ... and {len(self.user_profile.skills) - 15} more"
            console.print(Panel(skills_text, title="🛠️ Skills Identified", style="green"))
        
        # Experience
        if self.user_profile.work_experience:
            exp_table = Table(title="💼 Work Experience")
            exp_table.add_column("Position", style="bold cyan")
            exp_table.add_column("Company", style="white")
            exp_table.add_column("Key Achievements", style="dim")
            
            for exp in self.user_profile.work_experience[:3]:
                achievements = ", ".join(exp.key_achievements[:2]) if exp.key_achievements else "N/A"
                if exp.key_achievements and len(exp.key_achievements) > 2:
                    achievements += "..."
                exp_table.add_row(
                    exp.job_title,
                    exp.company,
                    achievements
                )
            
            console.print(exp_table)
        
        # Allow user to verify/modify extracted information
        if Confirm.ask("\n[yellow]Would you like to verify or modify the AI-extracted information?[/yellow]"):
            await self.verify_profile_information()
        
        console.print("[green]✅ Profile analysis complete![/green]")
    
    async def fallback_resume_processing(self, resume_text: str) -> UserProfile:
        """Fallback resume processing if AI analysis fails."""
        from document_processor import ResumeParser
        
        contact_info = ResumeParser.extract_contact_info(resume_text)
        skills = ResumeParser.extract_skills(resume_text)
        experiences = ResumeParser.extract_experience(resume_text)
        
        # Convert to UserProfile format
        skill_objects = []
        for skill_name in skills:
            skill_objects.append(Skill(
                name=skill_name,
                proficiency=SkillProficiency.INTERMEDIATE
            ))
        
        work_exp_objects = []
        for exp in experiences:
            work_exp_objects.append(WorkExperience(
                job_title=exp['job_title'],
                company=exp['company'],
                duration_years=2.0,
                key_achievements=exp['achievements']
            ))
        
        return UserProfile(
            personal_info=contact_info,
            skills=skill_objects,
            work_experience=work_exp_objects,
            education=[],
            career_goals=CareerGoals(
                target_roles=["Software Engineer", "Product Manager", "Tech Professional"],
                preferred_industries=["Technology"],
                experience_level_target=ExperienceLevel.MID,
                salary_expectations=None,
                work_preferences={"remote_friendly": True}
            ),
            resume_text=resume_text
        )
    
    async def verify_profile_information(self):
        """Allow user to verify and modify profile information."""
        console.print("\n[bold cyan]👤 Profile Verification[/bold cyan]")
        
        # Verify contact info
        if Confirm.ask("Would you like to update your contact information?"):
            for key in ['name', 'email', 'phone', 'linkedin', 'location']:
                current_value = self.user_profile.personal_info.get(key, '') if self.user_profile.personal_info else ''
                new_value = Prompt.ask(f"{key.title()}", default=current_value or "")
                if new_value:
                    if not self.user_profile.personal_info:
                        self.user_profile.personal_info = {}
                    self.user_profile.personal_info[key] = new_value
    
    async def collect_job_information(self):
        """Step 2: Collect job posting information with AI-powered analysis."""
        console.print("\n" + "="*60)
        console.print("[bold yellow]💼 Step 2: Job Intelligence Gathering[/bold yellow]")
        
        # Option 1: URL or Manual Entry
        input_method = Prompt.ask(
            "\n[cyan]How would you like to provide the job information?[/cyan]",
            choices=["url", "manual"],
            default="url"
        )
        
        if input_method == "url":
            await self.scrape_job_from_url()
        else:
            await self.manual_job_entry()
        
        # AI-powered job and company analysis
        await self.analyze_job_and_company()
        
        console.print("[green]✅ Job intelligence gathering complete![/green]")
    
    async def scrape_job_from_url(self):
        """Scrape job information from URL using Firecrawl MCP."""
        while True:
            job_url = Prompt.ask("\n[cyan]Please enter the job posting URL[/cyan]")
            
            if not job_url:
                console.print("[red]Please provide a valid URL.[/red]")
                continue
            
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("🕷️ AI scraping job posting...", total=None)
                    
                    # In a full implementation, this would use Firecrawl MCP
                    # For now, fallback to basic scraping
                    from document_processor import JobDescriptionScraper
                    scraped_data = JobDescriptionScraper.scrape_url(job_url)
                    progress.update(task, completed=True)
                
                if scraped_data and scraped_data.get('job_description'):
                    console.print("[green]✅ Job posting scraped successfully![/green]")
                    
                    # Display scraped information
                    console.print(Panel(
                        f"**Title:** {scraped_data.get('job_title', 'Not found')}\n"
                        f"**Company:** {scraped_data.get('company', 'Not found')}\n"
                        f"**Description Length:** {len(scraped_data.get('job_description', ''))} characters",
                        title="📋 Scraped Information",
                        style="green"
                    ))
                    
                    if Confirm.ask("Does this look correct?"):
                        self.job_posting = self.create_job_posting_from_scraped(scraped_data)
                        break
                    else:
                        if Confirm.ask("Would you like to try manual entry instead?"):
                            await self.manual_job_entry()
                            break
                else:
                    console.print("[red]❌ Could not scrape job posting from this URL.[/red]")
                    if Confirm.ask("Would you like to try manual entry instead?"):
                        await self.manual_job_entry()
                        break
                        
            except Exception as e:
                console.print(f"[red]Error scraping URL: {e}[/red]")
                if Confirm.ask("Would you like to try manual entry instead?"):
                    await self.manual_job_entry()
                    break
    
    async def manual_job_entry(self):
        """Manual job information entry."""
        console.print("\n[cyan]📝 Manual Job Information Entry[/cyan]")
        
        job_title = Prompt.ask("Job title")
        company_name = Prompt.ask("Company name")
        location = Prompt.ask("Location (optional)", default="")
        
        console.print("\n[yellow]📋 Please paste the job description below.[/yellow]")
        console.print("[dim]Instructions:[/dim]")
        console.print("[dim]1. Paste your job description[/dim]")
        console.print("[dim]2. Press Enter to go to a new line[/dim]")
        console.print("[dim]3. Press Ctrl+D on the empty line to finish[/dim]")
        console.print("[dim]4. If that doesn't work, type 'EOF' on a new line and press Enter[/dim]")
        console.print()
        
        job_description_lines = []
        try:
            while True:
                line = input()
                # Allow 'EOF' as an alternative way to end input
                if line.strip().upper() == 'EOF':
                    break
                job_description_lines.append(line)
        except EOFError:
            pass
        except KeyboardInterrupt:
            console.print("\n[yellow]Input cancelled. Please try again.[/yellow]")
            return
        
        job_description = "\n".join(job_description_lines)
        
        if not job_description.strip():
            console.print("[red]No job description provided.[/red]")
            return
        
        self.job_posting = JobPosting(
            job_title=job_title,
            company=CompanyInfo(name=company_name, industry="Technology"),
            location=location or None,
            job_description=job_description,
            key_responsibilities=[],
            requirements=[]
        )
    
    def create_job_posting_from_scraped(self, scraped_data):
        """Create JobPosting from scraped data."""
        return JobPosting(
            job_title=scraped_data.get('job_title', 'Unknown Position'),
            company=CompanyInfo(
                name=scraped_data.get('company', 'Unknown Company'),
                industry="Technology"  # Default
            ),
            job_description=scraped_data['job_description'],
            key_responsibilities=[],
            requirements=[]
        )
    
    async def analyze_job_and_company(self):
        """AI-powered job and company analysis."""
        if not self.job_posting:
            console.print("[red]❌ No job posting to analyze.[/red]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🧠 AI analyzing job requirements and researching company...", total=None)
            
            try:
                self.job_analysis, self.company_research = await career_assistant_orchestrator.analyze_job_and_company(
                    self.job_posting.job_description,
                    self.job_posting.company.name
                )
                progress.update(task, completed=True)
                
                # Display analysis results
                console.print("\n[bold blue]📊 AI Job Analysis Results:[/bold blue]")
                
                if self.job_analysis:
                    console.print(Panel(
                        f"**Key Requirements:** {', '.join(self.job_analysis.key_requirements[:5])}\n"
                        f"**Experience Level:** {self.job_analysis.required_experience_level}\n"
                        f"**Technologies:** {', '.join(self.job_analysis.technologies_mentioned[:5])}",
                        title="🎯 Job Requirements Analysis",
                        style="blue"
                    ))
                
                if self.company_research:
                    console.print(Panel(
                        f"**Overview:** {self.company_research.company_overview[:200]}...\n"
                        f"**Recent News:** {len(self.company_research.recent_news)} items found\n"
                        f"**Competitors:** {', '.join(self.company_research.competitors[:3])}",
                        title="🏢 Company Research",
                        style="magenta"
                    ))
                
            except Exception as e:
                console.print(f"[yellow]⚠️ AI analysis partially failed: {e}[/yellow]")
                # Continue with basic analysis
                progress.update(task, description="Using basic analysis...")
                progress.update(task, completed=True)
    
    async def generate_application_package(self):
        """Step 3: Generate complete application package using AI agents."""
        console.print("\n" + "="*60)
        console.print("[bold yellow]🎯 Step 3: AI-Generated Application Package[/bold yellow]")
        
        if not self.user_profile or not self.job_posting:
            console.print("[red]❌ Missing profile or job information.[/red]")
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("🤖 AI agents crafting your application package...", total=None)
                
                # Generate complete application package using multi-agent system
                package = await career_assistant_orchestrator.generate_application_package(
                    self.user_profile,
                    self.job_posting,
                    self.job_analysis,
                    self.company_research
                )
                
                progress.update(task, completed=True)
            
            # Display results
            await self.display_application_package(package)
            
            # Offer to save documents
            if Confirm.ask("\n[cyan]Would you like to save these documents to files?[/cyan]"):
                await self.save_documents(package)
            
        except Exception as e:
            console.print(f"[red]❌ Error generating application package: {e}[/red]")
    
    async def display_application_package(self, package: SimpleApplicationPackage):
        """Display the generated application package."""
        console.print("\n" + "="*80)
        console.print("[bold green]🎉 YOUR AI-GENERATED APPLICATION PACKAGE[/bold green]")
        
        # Resume
        console.print("\n[bold blue]📄 OPTIMIZED RESUME[/bold blue]")
        resume_preview = package.optimized_resume[:500] + "..." if len(package.optimized_resume) > 500 else package.optimized_resume
        console.print(Panel(resume_preview, title="Resume Preview", style="blue"))
        
        # Cover Letter
        console.print("\n[bold magenta]✉️ COVER LETTER[/bold magenta]")
        cover_preview = package.cover_letter[:500] + "..." if len(package.cover_letter) > 500 else package.cover_letter
        console.print(Panel(cover_preview, title="Cover Letter Preview", style="magenta"))
        
        # Interview Preparation
        console.print("\n[bold red]🎤 INTERVIEW PREPARATION[/bold red]")
        if isinstance(package.interview_preparation, dict):
            prep_text = f"📝 {len(package.interview_preparation.get('questions', []))} potential questions prepared\n"
            prep_text += f"⭐ {len(package.interview_preparation.get('star_responses', {}))} STAR responses created\n"
            prep_text += f"🏢 Company insights included\n"
            prep_text += f"💡 {len(package.interview_preparation.get('preparation_tips', []))} preparation tips"
        else:
            prep_text = str(package.interview_preparation)[:300] + "..."
        
        console.print(Panel(prep_text, title="Interview Prep Summary", style="red"))
        
        # Success tips
        console.print("\n[bold green]💡 AI SUCCESS STRATEGY[/bold green]")
        success_tips = [
            "🎯 Your application is tailored to match job requirements",
            "🔍 Company research insights are integrated throughout",
            "📊 ATS-optimized formatting ensures visibility",
            "⭐ STAR method responses showcase your achievements",
            "💪 Confident presentation based on your unique strengths"
        ]
        
        tips_text = "\n".join(success_tips)
        console.print(Panel(tips_text, title="AI-Powered Application Strategy", style="green"))
    
    async def save_documents(self, package: SimpleApplicationPackage):
        """Save generated documents to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = self.job_posting.company.name.replace(" ", "_")
        
        # Create output directory
        output_dir = Path(f"ai_application_package_{company_name}_{timestamp}")
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Save resume
            resume_file = output_dir / "ai_optimized_resume.md"
            with open(resume_file, 'w') as f:
                f.write(f"# AI-Optimized Resume for {self.job_posting.job_title}\n\n")
                f.write(f"**Company:** {self.job_posting.company.name}\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**AI System:** PydanticAI Multi-Agent Career Assistant\n\n")
                f.write(package.optimized_resume)
            
            # Save cover letter
            cover_file = output_dir / "ai_cover_letter.md"
            with open(cover_file, 'w') as f:
                f.write(f"# AI-Generated Cover Letter for {self.job_posting.job_title}\n\n")
                f.write(f"**Company:** {self.job_posting.company.name}\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**AI System:** PydanticAI Multi-Agent Career Assistant\n\n")
                f.write(package.cover_letter)
            
            # Save interview prep
            interview_file = output_dir / "ai_interview_preparation.md"
            with open(interview_file, 'w') as f:
                f.write(f"# AI-Generated Interview Preparation for {self.job_posting.job_title}\n\n")
                f.write(f"**Company:** {self.job_posting.company.name}\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**AI System:** PydanticAI Multi-Agent Career Assistant\n\n")
                
                if isinstance(package.interview_preparation, dict):
                    f.write("## Potential Interview Questions\n\n")
                    for i, question in enumerate(package.interview_preparation.get('questions', []), 1):
                        f.write(f"{i}. {question}\n")
                    
                    f.write("\n## STAR Method Responses\n\n")
                    for question, response in package.interview_preparation.get('star_responses', {}).items():
                        f.write(f"**Q: {question}**\n\n{response}\n\n")
                    
                    f.write("\n## Preparation Tips\n\n")
                    for tip in package.interview_preparation.get('preparation_tips', []):
                        f.write(f"- {tip}\n")
                else:
                    f.write(str(package.interview_preparation))
            
            # Save job analysis
            if self.job_analysis:
                analysis_file = output_dir / "job_analysis.md"
                with open(analysis_file, 'w') as f:
                    f.write(f"# AI Job Analysis\n\n")
                    f.write(f"**Requirements:** {', '.join(self.job_analysis.key_requirements)}\n\n")
                    f.write(f"**Technologies:** {', '.join(self.job_analysis.technologies_mentioned)}\n\n")
                    f.write(f"**Experience Level:** {self.job_analysis.required_experience_level}\n\n")
            
            # Save company research
            if self.company_research:
                research_file = output_dir / "company_research.md"
                with open(research_file, 'w') as f:
                    f.write(f"# AI Company Research\n\n")
                    f.write(f"**Overview:** {self.company_research.company_overview}\n\n")
                    f.write(f"**Recent News:**\n")
                    for news in self.company_research.recent_news:
                        f.write(f"- {news}\n")
                    f.write(f"\n**Competitors:** {', '.join(self.company_research.competitors)}\n\n")
            
            console.print(f"\n[green]✅ AI-generated documents saved to: {output_dir}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error saving documents: {e}[/red]")


async def main():
    """Main entry point for the streamlined CLI."""
    try:
        cli = StreamlinedCareerCLI()
        await cli.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main()) 