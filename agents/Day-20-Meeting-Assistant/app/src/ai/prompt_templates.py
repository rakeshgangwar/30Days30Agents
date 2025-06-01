"""
Enhanced prompt templates for meeting processing.

This module contains specialized prompts for different types of meetings
and processing tasks to improve the quality of AI-generated summaries
and action items.
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class MeetingType(Enum):
    """Types of meetings for specialized processing"""
    STANDUP = "standup"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"
    ONE_ON_ONE = "one_on_one"
    ALL_HANDS = "all_hands"
    TECHNICAL_REVIEW = "technical_review"
    CLIENT_MEETING = "client_meeting"
    GENERAL = "general"


class PromptTemplates:
    """Collection of enhanced prompt templates for meeting processing"""
    
    @staticmethod
    def get_summarization_prompt(
        transcript: str,
        meeting_title: Optional[str] = None,
        participants: Optional[List[str]] = None,
        duration_minutes: Optional[int] = None,
        summary_type: str = "detailed",
        meeting_type: MeetingType = MeetingType.GENERAL
    ) -> str:
        """
        Generate an enhanced prompt for meeting summarization.
        
        Args:
            transcript: Meeting transcript
            meeting_title: Optional meeting title
            participants: Optional list of participants
            duration_minutes: Optional meeting duration
            summary_type: Type of summary (brief, detailed, executive)
            meeting_type: Type of meeting for specialized prompts
            
        Returns:
            Formatted prompt string
        """
        # Base instructions based on summary type
        base_instructions = {
            "brief": (
                "Create a concise summary (2-3 sentences) focusing on key decisions, "
                "outcomes, and next steps. Prioritize actionable information."
            ),
            "detailed": (
                "Create a comprehensive summary covering all major discussion points, "
                "decisions made, concerns raised, and outcomes. Include context and "
                "reasoning behind decisions."
            ),
            "executive": (
                "Create an executive summary suitable for senior leadership. Focus on "
                "strategic implications, key decisions, resource requirements, risks, "
                "and business impact. Use professional, concise language."
            )
        }
        
        # Meeting-type specific additions
        meeting_specific = {
            MeetingType.STANDUP: (
                "This is a standup/scrum meeting. Focus on progress updates, "
                "blockers, and planned work. Structure the summary around: "
                "completed work, current work, blockers, and plans."
            ),
            MeetingType.PLANNING: (
                "This is a planning meeting. Emphasize project scope, timelines, "
                "resource allocation, milestones, and risk factors. Include "
                "dependencies and assumptions."
            ),
            MeetingType.RETROSPECTIVE: (
                "This is a retrospective meeting. Focus on what went well, "
                "what didn't work, lessons learned, and improvement actions. "
                "Organize by themes or categories."
            ),
            MeetingType.ONE_ON_ONE: (
                "This is a one-on-one meeting. Focus on personal development, "
                "feedback, goals, concerns, and career discussions. Maintain "
                "confidentiality and professionalism."
            ),
            MeetingType.TECHNICAL_REVIEW: (
                "This is a technical review meeting. Focus on technical decisions, "
                "architecture choices, code quality, performance considerations, "
                "and technical risks."
            ),
            MeetingType.CLIENT_MEETING: (
                "This is a client meeting. Focus on client needs, requirements, "
                "feedback, deliverables, timelines, and relationship management. "
                "Highlight commitments made."
            )
        }
        
        prompt_parts = [
            base_instructions.get(summary_type, base_instructions["detailed"])
        ]
        
        # Add meeting-specific instructions
        if meeting_type in meeting_specific:
            prompt_parts.append(meeting_specific[meeting_type])
        
        # Add context
        context_parts = []
        if meeting_title:
            context_parts.append(f"Meeting Title: {meeting_title}")
        if participants:
            context_parts.append(f"Participants: {', '.join(participants)}")
        if duration_minutes:
            context_parts.append(f"Duration: {duration_minutes} minutes")
        
        if context_parts:
            prompt_parts.append("Meeting Context:")
            prompt_parts.extend(context_parts)
        
        # Add transcript
        prompt_parts.extend([
            "",
            "Meeting Transcript:",
            transcript,
            "",
            "Summary Requirements:",
            "- Use clear, professional language",
            "- Structure with appropriate headings and bullet points",
            "- Highlight key decisions in bold",
            "- Include participant names when relevant",
            "- Focus on actionable outcomes"
        ])
        
        if summary_type == "executive":
            prompt_parts.extend([
                "- Quantify impact where possible",
                "- Identify risks and mitigation strategies",
                "- Include resource and timeline implications"
            ])
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def get_action_items_prompt(
        transcript: str,
        participants: Optional[List[str]] = None,
        context: Optional[str] = None,
        meeting_type: MeetingType = MeetingType.GENERAL
    ) -> str:
        """
        Generate an enhanced prompt for action item extraction.
        
        Args:
            transcript: Meeting transcript
            participants: Optional list of participants
            context: Optional context information
            meeting_type: Type of meeting for specialized prompts
            
        Returns:
            Formatted prompt string
        """
        base_instruction = (
            "Extract all action items from the following meeting transcript. "
            "Be thorough and identify both explicit action items (directly stated) "
            "and implicit ones (implied commitments or follow-ups)."
        )
        
        # Meeting-specific action item guidance
        meeting_guidance = {
            MeetingType.STANDUP: (
                "Focus on commitments for the next sprint/iteration, "
                "blocker resolution actions, and follow-up tasks."
            ),
            MeetingType.PLANNING: (
                "Include project setup tasks, milestone deliverables, "
                "resource procurement, and dependency management actions."
            ),
            MeetingType.RETROSPECTIVE: (
                "Focus on improvement actions, process changes, "
                "and experiment implementations."
            ),
            MeetingType.CLIENT_MEETING: (
                "Include deliverable commitments, communication actions, "
                "requirement clarifications, and follow-up meetings."
            )
        }
        
        prompt_parts = [
            base_instruction,
            "",
            meeting_guidance.get(meeting_type, ""),
            "",
            "For each action item, extract:",
            "- action: Clear, specific description of what needs to be done",
            "- assignee: Person responsible (use exact name from transcript, null if unclear)",
            "- deadline: Specific date or timeframe mentioned (null if not specified)",
            "- priority: Assess as 'high', 'medium', or 'low' based on context and urgency",
            "- category: Type of action (e.g., 'development', 'communication', 'research', 'meeting')",
            "",
            "Return ONLY a valid JSON array with this exact structure:",
            '[{"action": "description", "assignee": "name or null", "deadline": "date or null", "priority": "level", "category": "type"}]',
            ""
        ]
        
        # Add context
        if participants:
            prompt_parts.append(f"Known participants: {', '.join(participants)}")
        if context:
            prompt_parts.append(f"Meeting context: {context}")
        
        prompt_parts.extend([
            "",
            "Meeting Transcript:",
            transcript,
            "",
            "Important:",
            "- Only include genuine action items, not general discussion points",
            "- Be specific and actionable in descriptions",
            "- Use participant names exactly as they appear in the transcript",
            "- Infer priority from urgency indicators (ASAP, urgent, deadline mentions)",
            "- Return valid JSON only, no additional text or formatting"
        ])
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def get_topic_extraction_prompt(transcript: str) -> str:
        """Generate prompt for extracting key topics and themes"""
        return f"""
Analyze the following meeting transcript and extract the main topics and themes discussed.

For each topic, provide:
- topic: Brief topic name (2-4 words)
- description: One sentence description
- duration_discussed: Estimate of discussion time in minutes
- participants_involved: Names of key participants in this topic
- sentiment: Overall sentiment (positive, neutral, negative, mixed)
- importance: Assess as 'high', 'medium', or 'low'

Return as JSON array:
[{{"topic": "name", "description": "desc", "duration_discussed": minutes, "participants_involved": ["names"], "sentiment": "sentiment", "importance": "level"}}]

Meeting Transcript:
{transcript}

Return only valid JSON, no additional text.
"""
    
    @staticmethod
    def get_sentiment_analysis_prompt(transcript: str) -> str:
        """Generate prompt for meeting sentiment analysis"""
        return f"""
Analyze the sentiment and emotional tone of this meeting transcript.

Provide analysis for:
- overall_sentiment: Overall meeting sentiment (positive, negative, neutral, mixed)
- engagement_level: How engaged participants were (high, medium, low)
- conflict_indicators: Any signs of disagreement or tension (true/false)
- collaboration_quality: How well the team collaborated (excellent, good, fair, poor)
- energy_level: Meeting energy (high, medium, low)
- concerns_raised: Number of concerns or issues mentioned
- positive_moments: Number of achievements or positive outcomes mentioned

Return as JSON:
{{"overall_sentiment": "sentiment", "engagement_level": "level", "conflict_indicators": boolean, "collaboration_quality": "quality", "energy_level": "level", "concerns_raised": number, "positive_moments": number}}

Meeting Transcript:
{transcript}

Return only valid JSON, no additional text.
"""


def get_enhanced_prompt(
    prompt_type: str,
    transcript: str,
    **kwargs
) -> str:
    """
    Get an enhanced prompt for the specified type.
    
    Args:
        prompt_type: Type of prompt ('summary', 'action_items', 'topics', 'sentiment')
        transcript: Meeting transcript
        **kwargs: Additional arguments for specific prompt types
        
    Returns:
        Enhanced prompt string
    """
    if prompt_type == "summary":
        return PromptTemplates.get_summarization_prompt(transcript, **kwargs)
    elif prompt_type == "action_items":
        return PromptTemplates.get_action_items_prompt(transcript, **kwargs)
    elif prompt_type == "topics":
        return PromptTemplates.get_topic_extraction_prompt(transcript)
    elif prompt_type == "sentiment":
        return PromptTemplates.get_sentiment_analysis_prompt(transcript)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")