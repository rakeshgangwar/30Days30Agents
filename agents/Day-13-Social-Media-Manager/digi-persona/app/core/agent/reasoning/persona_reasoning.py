"""
Persona Reasoning

This module provides reasoning capabilities for persona agents.
"""
from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate


class PersonaReasoning:
    """
    Reasoning capabilities for persona agents.
    
    This class provides methods for persona-specific reasoning tasks such as
    content planning, tone analysis, and decision making.
    """
    
    def __init__(self, llm: BaseLLM, persona_data: Dict[str, Any]):
        """
        Initialize the reasoning module.
        
        Args:
            llm: The language model to use for reasoning
            persona_data: Dictionary containing persona information
        """
        self.llm = llm
        self.persona_data = persona_data
        self.persona_name = persona_data.get('name', 'Unknown')
        
        # Initialize reasoning chains
        self._init_reasoning_chains()
    
    def _init_reasoning_chains(self):
        """Initialize the reasoning chains."""
        # Content planning chain
        content_planning_template = """
        As {persona_name}, you need to plan content about {topic} for {platform}.
        
        Your persona characteristics:
        - Description: {persona_description}
        - Tone: {persona_tone}
        - Style: {persona_style}
        - Interests: {persona_interests}
        
        Create a brief content plan that includes:
        1. Main points to cover
        2. Tone and style considerations
        3. Any specific elements to include (hashtags, mentions, etc.)
        
        Content Plan:
        """
        
        self.content_planning_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["persona_name", "persona_description", "persona_tone", 
                                "persona_style", "persona_interests", "topic", "platform"],
                template=content_planning_template
            )
        )
        
        # Tone analysis chain
        tone_analysis_template = """
        As {persona_name}, analyze the following content for tone and style:
        
        CONTENT:
        {content}
        
        Your persona characteristics:
        - Tone: {persona_tone}
        - Style: {persona_style}
        
        Analyze whether this content matches your persona's tone and style.
        If not, suggest specific changes to make it more authentic to your persona.
        
        Analysis:
        """
        
        self.tone_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["persona_name", "persona_tone", "persona_style", "content"],
                template=tone_analysis_template
            )
        )
    
    def plan_content(self, topic: str, platform: str) -> str:
        """
        Plan content for a specific topic and platform.
        
        Args:
            topic: The topic to plan content for
            platform: The platform the content is intended for
            
        Returns:
            A content plan
        """
        return self.content_planning_chain.run({
            "persona_name": self.persona_data.get('name', 'Unknown'),
            "persona_description": self.persona_data.get('description', 'No description available'),
            "persona_tone": self.persona_data.get('tone', 'Neutral'),
            "persona_style": self.persona_data.get('style', 'Standard'),
            "persona_interests": ', '.join(self.persona_data.get('interests', ['General topics'])),
            "topic": topic,
            "platform": platform
        })
    
    def analyze_tone(self, content: str) -> str:
        """
        Analyze the tone and style of content.
        
        Args:
            content: The content to analyze
            
        Returns:
            Analysis of the content's tone and style
        """
        return self.tone_analysis_chain.run({
            "persona_name": self.persona_data.get('name', 'Unknown'),
            "persona_tone": self.persona_data.get('tone', 'Neutral'),
            "persona_style": self.persona_data.get('style', 'Standard'),
            "content": content
        })
    
    def make_decision(self, question: str, options: List[str], context: Optional[str] = None) -> str:
        """
        Make a decision based on the persona's characteristics.
        
        Args:
            question: The decision question
            options: List of possible options
            context: Optional additional context
            
        Returns:
            The decision and reasoning
        """
        decision_template = """
        As {persona_name}, you need to make a decision.
        
        Your persona characteristics:
        - Description: {persona_description}
        - Tone: {persona_tone}
        - Style: {persona_style}
        - Interests: {persona_interests}
        
        Question: {question}
        
        Options:
        {options_text}
        
        {context_text}
        
        Based on your persona's characteristics, which option would you choose and why?
        
        Decision:
        """
        
        options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
        context_text = f"Additional context: {context}" if context else ""
        
        decision_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["persona_name", "persona_description", "persona_tone", 
                                "persona_style", "persona_interests", "question", 
                                "options_text", "context_text"],
                template=decision_template
            )
        )
        
        return decision_chain.run({
            "persona_name": self.persona_data.get('name', 'Unknown'),
            "persona_description": self.persona_data.get('description', 'No description available'),
            "persona_tone": self.persona_data.get('tone', 'Neutral'),
            "persona_style": self.persona_data.get('style', 'Standard'),
            "persona_interests": ', '.join(self.persona_data.get('interests', ['General topics'])),
            "question": question,
            "options_text": options_text,
            "context_text": context_text
        })
