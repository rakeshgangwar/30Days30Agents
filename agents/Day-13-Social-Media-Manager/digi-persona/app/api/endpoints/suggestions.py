"""
Content Suggestions API Endpoints Module

This module provides API endpoints for content suggestions.
"""

from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.personas.manager import get_persona_manager
from app.core.ai.generator import get_content_generator
from app.schemas.content import (ContentSuggestionRequest, ContentSuggestionResponse,
                                 ApplySuggestionRequest, ApplySuggestionResponse, Suggestion)

router = APIRouter()


@router.post("/apply-suggestion", response_model=ApplySuggestionResponse)
async def apply_suggestion(
    request: ApplySuggestionRequest = Body(...),
    db: Session = Depends(get_db),
) -> ApplySuggestionResponse:
    """
    Apply a suggestion to content using AI.

    Args:
        request: The request containing the content and suggestion.
        db: Database session.

    Returns:
        A response containing the improved content.

    Raises:
        HTTPException: If the persona is not found or an error occurs.
    """
    try:
        # Get managers
        persona_manager = get_persona_manager(db)
        content_generator = get_content_generator()

        # Get persona if ID is provided
        persona = None
        if request.persona_id:
            persona = persona_manager.get_persona(request.persona_id)
            if not persona:
                raise HTTPException(status_code=404, detail=f"Persona with ID {request.persona_id} not found")

        # Create a prompt for the AI to apply the suggestion
        prompt = f"""
        You are an expert content writer. You need to improve the following content by applying a specific suggestion.

        ORIGINAL CONTENT:
        """

        if persona:
            prompt += f"""
            This content is written in the persona of {persona.name}, who has the following characteristics:
            - Background: {persona.background}
            - Tone: {persona.tone}
            - Purpose: {persona.purpose}
            """

        if request.content_type:
            prompt += f"\nContent type: {request.content_type}"

        # Add platform-specific instructions and character limits
        max_length = None
        if request.platform:
            prompt += f"\nPlatform: {request.platform}"

            # Set character limits based on platform
            if request.platform.lower() == "twitter":
                max_length = 280
            elif request.platform.lower() == "linkedin":
                max_length = 3000
            elif request.platform.lower() == "bluesky":
                max_length = 300

        # Default character limit if none specified
        if not max_length and request.content_type:
            if request.content_type.lower() == "post":
                max_length = 1000
            elif request.content_type.lower() == "article":
                max_length = 5000

        # Use a default if no other limits apply
        if not max_length:
            max_length = 1000

        prompt += f"""

        {request.content}

        SUGGESTION TO APPLY:
        {request.suggestion}
"""
        # Add user feedback to the prompt if provided
        if request.feedback:
            prompt += f"""

        USER FEEDBACK:
        {request.feedback}
"""
        prompt += f"""

        Please rewrite the content applying this suggestion. Maintain the same general meaning and key points,
        but improve it according to the suggestion. The content must be no longer than {max_length} characters.

        IMPORTANT: Return only the improved content, nothing else. Do NOT wrap the content in quotes.
        Write it as if it's a direct social media post ready to be published.
        """

        # Generate improved content using the AI
        improved_content = content_generator.openai_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Post-process the content to remove any quotes that might have been added
        # This ensures the content is ready for social media without quotation marks
        processed_content = improved_content.strip()

        # Remove surrounding quotes if present
        if (processed_content.startswith('"') and processed_content.endswith('"')) or \
           (processed_content.startswith('\'') and processed_content.endswith('\'')):
            processed_content = processed_content[1:-1].strip()

        return ApplySuggestionResponse(improved_content=processed_content)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error applying suggestion: {str(e)}")


@router.post("/suggestions", response_model=ContentSuggestionResponse)
async def get_content_suggestions(
    request: ContentSuggestionRequest = Body(...),
    db: Session = Depends(get_db),
) -> ContentSuggestionResponse:
    """
    Get AI-powered suggestions for content improvement.

    Args:
        request: The suggestion request containing content and parameters.
        db: Database session.

    Returns:
        A response containing suggestions.

    Raises:
        HTTPException: If the persona is not found or an error occurs.
    """
    try:
        # Get managers
        persona_manager = get_persona_manager(db)
        content_generator = get_content_generator()

        # Get persona if ID is provided
        persona = None
        if request.persona_id:
            persona = persona_manager.get_persona(request.persona_id)
            if not persona:
                raise HTTPException(status_code=404, detail=f"Persona with ID {request.persona_id} not found")

        # Generate suggestions based on the type
        suggestions = []

        if request.suggestion_type == "improve":
            # Generate content improvement suggestions
            suggestions = generate_improvement_suggestions(
                content_generator,
                request.content,
                persona,
                request.content_type,
                request.platform
            )
        elif request.suggestion_type == "tone":
            # Generate tone adjustment suggestions
            suggestions = generate_tone_suggestions(
                content_generator,
                request.content,
                persona,
                request.content_type,
                request.platform
            )
        elif request.suggestion_type == "hashtags":
            # Generate hashtag suggestions
            suggestions = generate_hashtag_suggestions(
                content_generator,
                request.content,
                persona,
                request.content_type,
                request.platform
            )
        elif request.suggestion_type == "engagement":
            # Generate engagement improvement suggestions
            suggestions = generate_engagement_suggestions(
                content_generator,
                request.content,
                persona,
                request.content_type,
                request.platform
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid suggestion type: {request.suggestion_type}")

        return ContentSuggestionResponse(suggestions=suggestions)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


def generate_improvement_suggestions(
    content_generator,
    content: str,
    persona: Any,
    content_type: Optional[str],
    platform: Optional[str]
) -> List[Suggestion]:
    """Generate content improvement suggestions using AI."""
    # Create a prompt for the AI to generate improvement suggestions
    prompt = f"""
    You are an expert content strategist. Review the following content and provide 3 specific suggestions
    to improve its structure, clarity, and impact. Focus on making the content more compelling and effective.

    CONTENT TO REVIEW:
    """

    if persona:
        prompt += f"""
        This content is written in the persona of {persona.name}, who has the following characteristics:
        - Background: {persona.background}
        - Tone: {persona.tone}
        - Purpose: {persona.purpose}
        """

    if content_type:
        prompt += f"\nContent type: {content_type}"

    if platform:
        prompt += f"\nPlatform: {platform}"

    prompt += f"""

    {content}

    Provide exactly 3 specific, actionable suggestions to improve this content. Each suggestion should:
    1. Identify a specific aspect to improve
    2. Explain why it would make the content better
    3. Be concise and clear

    Format each suggestion as a JSON object with 'text' (the suggestion) and 'description' (why it helps) fields.
    Return only a JSON array of these 3 objects, nothing else.

    IMPORTANT: In the 'text' field, do NOT wrap the suggestions in quotes. Write them as direct statements.
    """

    try:
        # Generate suggestions using the AI
        response = content_generator.openai_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response as JSON
        import json
        import re

        # Extract JSON array from response if needed
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        suggestions_data = json.loads(response)

        # Process suggestions to remove any quotes
        processed_suggestions = []
        for item in suggestions_data:
            text = item.get("text", "")
            # Remove surrounding quotes if present
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith('\'') and text.endswith('\'')):
                text = text[1:-1].strip()

            processed_suggestions.append(
                Suggestion(
                    id=str(uuid4()),
                    text=text,
                    type="improve",
                    description=item.get("description", "")
                )
            )

        suggestions = processed_suggestions

        return suggestions
    except Exception as e:
        # Fall back to mock data if AI generation fails
        print(f"Error generating improvement suggestions: {str(e)}")
        return [
            Suggestion(
                id=str(uuid4()),
                text="Consider adding more specific examples to strengthen your point.",
                type="improve",
                description="Adding concrete examples makes your content more relatable and convincing."
            ),
            Suggestion(
                id=str(uuid4()),
                text="Your introduction could be more attention-grabbing. Try starting with a question or surprising fact.",
                type="improve",
                description="A strong hook increases engagement and readership."
            ),
            Suggestion(
                id=str(uuid4()),
                text="The conclusion could be stronger. Consider summarizing key points and adding a clear call-to-action.",
                type="improve",
                description="A strong conclusion helps readers remember your message."
            )
        ]


def generate_tone_suggestions(
    content_generator,
    content: str,
    persona: Any,
    content_type: Optional[str],
    platform: Optional[str]
) -> List[Suggestion]:
    """Generate tone adjustment suggestions using AI."""
    # Create a prompt for the AI to generate tone suggestions
    prompt = f"""
    You are an expert content tone analyst. Review the following content and provide 3 specific suggestions
    to improve its tone, voice, and emotional impact. Focus on making the content more engaging and appropriate for its audience.

    CONTENT TO REVIEW:
    """

    if persona:
        prompt += f"""
        This content is written in the persona of {persona.name}, who has the following characteristics:
        - Background: {persona.background}
        - Tone: {persona.tone}
        - Purpose: {persona.purpose}
        """

    if content_type:
        prompt += f"\nContent type: {content_type}"

    if platform:
        prompt += f"\nPlatform: {platform}"

    prompt += f"""

    {content}

    Provide exactly 3 specific, actionable suggestions to improve the tone of this content. Each suggestion should:
    1. Identify a specific tone aspect to improve
    2. Explain why it would make the content more engaging or effective
    3. Be concise and clear

    Format each suggestion as a JSON object with 'text' (the suggestion) and 'description' (why it helps) fields.
    Return only a JSON array of these 3 objects, nothing else.

    IMPORTANT: In the 'text' field, do NOT wrap the suggestions in quotes. Write them as direct statements.
    """

    try:
        # Generate suggestions using the AI
        response = content_generator.openai_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response as JSON
        import json
        import re

        # Extract JSON array from response if needed
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        suggestions_data = json.loads(response)

        # Process suggestions to remove any quotes
        processed_suggestions = []
        for item in suggestions_data:
            text = item.get("text", "")
            # Remove surrounding quotes if present
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith('\'') and text.endswith('\'')):
                text = text[1:-1].strip()

            processed_suggestions.append(
                Suggestion(
                    id=str(uuid4()),
                    text=text,
                    type="tone",
                    description=item.get("description", "")
                )
            )

        suggestions = processed_suggestions

        return suggestions
    except Exception as e:
        # Fall back to mock data if AI generation fails
        print(f"Error generating tone suggestions: {str(e)}")
        return [
            Suggestion(
                id=str(uuid4()),
                text="Your content could benefit from a more conversational tone to connect with readers.",
                type="tone",
                description="A conversational tone builds rapport with your audience."
            ),
            Suggestion(
                id=str(uuid4()),
                text="Consider using more authoritative language to establish expertise.",
                type="tone",
                description="Authoritative language builds credibility with your audience."
            ),
            Suggestion(
                id=str(uuid4()),
                text="Try using more enthusiastic language to convey excitement about the topic.",
                type="tone",
                description="Enthusiasm is contagious and can increase reader engagement."
            )
        ]


def generate_hashtag_suggestions(
    content_generator,
    content: str,
    persona: Any,
    content_type: Optional[str],
    platform: Optional[str]
) -> List[Suggestion]:
    """Generate hashtag suggestions using AI."""
    # Create a prompt for the AI to generate hashtag suggestions
    prompt = f"""
    You are an expert social media strategist. Review the following content and suggest 3 sets of relevant hashtags
    that would increase its visibility and engagement on social media. Each set should contain 3-5 related hashtags.

    CONTENT TO REVIEW:
    """

    if persona:
        prompt += f"""
        This content is written in the persona of {persona.name}, who has the following characteristics:
        - Background: {persona.background}
        - Interests: {', '.join(persona.interests) if persona.interests else 'None'}
        - Expertise: {', '.join(persona.expertise) if persona.expertise else 'None'}
        """

    if content_type:
        prompt += f"\nContent type: {content_type}"

    if platform:
        prompt += f"\nPlatform: {platform}"

    prompt += f"""

    {content}

    Provide exactly 3 sets of hashtags. Each set should:
    1. Be relevant to the content and audience
    2. Include a mix of popular and niche hashtags
    3. Be formatted as a single string with hashtags separated by spaces

    Format each suggestion as a JSON object with 'text' (the hashtags) and 'description' (why these hashtags are effective) fields.
    Return only a JSON array of these 3 objects, nothing else.

    IMPORTANT: In the 'text' field, provide the hashtags directly without any surrounding quotes.
    """

    try:
        # Generate suggestions using the AI
        response = content_generator.openai_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response as JSON
        import json
        import re

        # Extract JSON array from response if needed
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        suggestions_data = json.loads(response)

        # Process suggestions to remove any quotes
        processed_suggestions = []
        for item in suggestions_data:
            text = item.get("text", "")
            # Remove surrounding quotes if present
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith('\'') and text.endswith('\'')):
                text = text[1:-1].strip()

            processed_suggestions.append(
                Suggestion(
                    id=str(uuid4()),
                    text=text,
                    type="hashtags",
                    description=item.get("description", "")
                )
            )

        suggestions = processed_suggestions

        return suggestions
    except Exception as e:
        # Fall back to mock data if AI generation fails
        print(f"Error generating hashtag suggestions: {str(e)}")
        return [
            Suggestion(
                id=str(uuid4()),
                text="#AITrends #TechInnovation #FutureTech",
                type="hashtags",
                description="Popular hashtags in the tech industry"
            ),
            Suggestion(
                id=str(uuid4()),
                text="#MachineLearning #DataScience #ArtificialIntelligence",
                type="hashtags",
                description="Specific AI-related hashtags"
            ),
            Suggestion(
                id=str(uuid4()),
                text="#TechNews #Innovation #DigitalTransformation",
                type="hashtags",
                description="Trending technology hashtags"
            )
        ]


def generate_engagement_suggestions(
    content_generator,
    content: str,
    persona: Any,
    content_type: Optional[str],
    platform: Optional[str]
) -> List[Suggestion]:
    """Generate engagement improvement suggestions using AI."""
    # Create a prompt for the AI to generate engagement suggestions
    prompt = f"""
    You are an expert in social media engagement and audience interaction. Review the following content and provide 3 specific suggestions
    to increase audience engagement, interaction, and response rates. Focus on making the content more likely to generate comments, shares, and actions.

    CONTENT TO REVIEW:
    """

    if persona:
        prompt += f"""
        This content is written in the persona of {persona.name}, who has the following characteristics:
        - Purpose: {persona.purpose}
        - Audience: {persona.audience if hasattr(persona, 'audience') else 'General'}
        """

    if content_type:
        prompt += f"\nContent type: {content_type}"

    if platform:
        prompt += f"\nPlatform: {platform}"

    prompt += f"""

    {content}

    Provide exactly 3 specific, actionable suggestions to improve engagement with this content. Each suggestion should:
    1. Identify a specific way to increase audience interaction
    2. Explain why it would make the content more engaging
    3. Be concise and clear

    Format each suggestion as a JSON object with 'text' (the suggestion) and 'description' (why it helps) fields.
    Return only a JSON array of these 3 objects, nothing else.

    IMPORTANT: In the 'text' field, do NOT wrap the suggestions in quotes. Write them as direct statements.
    """

    try:
        # Generate suggestions using the AI
        response = content_generator.openai_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response as JSON
        import json
        import re

        # Extract JSON array from response if needed
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        suggestions_data = json.loads(response)

        # Process suggestions to remove any quotes
        processed_suggestions = []
        for item in suggestions_data:
            text = item.get("text", "")
            # Remove surrounding quotes if present
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith('\'') and text.endswith('\'')):
                text = text[1:-1].strip()

            processed_suggestions.append(
                Suggestion(
                    id=str(uuid4()),
                    text=text,
                    type="engagement",
                    description=item.get("description", "")
                )
            )

        suggestions = processed_suggestions

        return suggestions
    except Exception as e:
        # Fall back to mock data if AI generation fails
        print(f"Error generating engagement suggestions: {str(e)}")
        return [
            Suggestion(
                id=str(uuid4()),
                text="End with a question to encourage comments and discussion.",
                type="engagement",
                description="Questions prompt readers to engage with your content."
            ),
            Suggestion(
                id=str(uuid4()),
                text="Include a call-to-action to guide readers on what to do next.",
                type="engagement",
                description="Clear CTAs improve conversion rates."
            ),
            Suggestion(
                id=str(uuid4()),
                text="Add a poll or survey to encourage direct participation.",
                type="engagement",
                description="Interactive elements increase engagement significantly."
            )
        ]
