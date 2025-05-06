# Day 27: Mental Health Companion (Supportive Tool Only)

**CRITICAL DISCLAIMERS & SAFETY PROTOCOLS:**
- **NOT a Replacement for Therapy:** This agent is NOT a substitute for professional mental health diagnosis, therapy, or crisis intervention. It is a supportive tool for general wellness ONLY.
- **Not for Crisis Situations:** This agent is NOT equipped to handle mental health crises (e.g., suicidal ideation, severe distress). If a user expresses thoughts of harming themselves or others, the agent MUST immediately provide crisis hotline information (e.g., National Suicide Prevention Lifeline, Crisis Text Line) and strongly advise seeking professional help. It should disengage from further conversation on the crisis topic.
- **Privacy:** User interactions should be treated with extreme sensitivity. Ideally, conversations should not be stored long-term, or if stored, should be anonymized and encrypted with explicit user consent for specific features (like mood tracking). For this project, assume minimal/no persistent storage of conversation content.
- **No Diagnosis or Treatment:** The agent MUST NOT attempt to diagnose conditions or prescribe treatments. It can only offer general information, wellness exercises, and resources.
- **Limited Scope:** The agent's capabilities should be clearly defined and limited to supportive functions like mood tracking, journaling prompts, guided exercises (breathing, mindfulness), and providing links to reputable mental health resources.

## Agent Purpose
Acts as a supportive tool for general mental wellness by offering features like mood tracking, journaling prompts, guided relaxation exercises, and providing information on general wellness topics and resources. **Strictly avoids diagnosis, therapy, and crisis management.**

## Key Features
- Mood tracking (simple check-ins, e.g., "How are you feeling today on a scale of 1-5?")
- Guided exercises (e.g., simple breathing techniques, short mindfulness prompts)
- Journaling prompts (e.g., "What's something you're grateful for today?")
- Providing links to reputable mental health resources (e.g., NAMI, NIMH, crisis hotlines)
- Offering general, evidence-based wellness tips (e.g., importance of sleep, exercise)
- **CRISIS DETECTION & REDIRECTION:** Basic keyword detection for crisis language, immediately followed by providing crisis resources and disengagement.

## Example Interactions
- User: "I'm feeling stressed today." -> Agent: "I'm sorry to hear that. Sometimes a short breathing exercise can help. Would you like to try one? Remember, I'm just a tool, and for persistent stress, talking to a professional is recommended."
- User: "Log my mood as a 3 out of 5." -> Agent: "Okay, I've noted your mood as 3 out of 5 for today. Is there anything you'd like to briefly journal about?"
- User: "Give me a journaling prompt." -> Agent: "Sure. How about this: 'Describe one small thing that brought you a moment of calm today.'"
- User: "I feel hopeless." / "I want to end it." -> Agent: **"If you're feeling hopeless or thinking about harming yourself, it's really important to talk to someone who can support you right now. You can connect with people who can support you by calling or texting 988 anytime in the US and Canada. In the UK, you can call 111. Please reach out to them. I am not equipped to handle this situation."** (Agent should then ideally stop responding further on this topic).
- User: "Tell me about anxiety." -> Agent: "Anxiety is a common feeling... [provides general NAMI/NIMH style info]. For personalized information or if anxiety is impacting your life, consulting a healthcare professional is the best step. Here are some resources..."

## Tech Stack
- **Framework**: LangChain (with strong safety guardrails)
- **Model**: Foundational LLM (GPT, Claude) with safety fine-tuning if possible.
- **Tools**: Pre-defined list of crisis hotlines/resources, potentially web search restricted to reputable mental health sites (e.g., NAMI, NIMH, NHS).
- **Storage**: Minimal. Optional: Local storage or secure database for *anonymized* mood trends *with explicit user consent*. Avoid storing free-text journal entries or detailed conversation logs.
- **UI**: Simple text interface (CLI, Streamlit) – avoid overly "human-like" avatars.

## Architecture Considerations

### Input Processing
- Parsing user input for mood logging, requests for exercises/prompts/info.
- **CRITICAL: Implementing robust keyword detection for crisis indicators.** This should be a primary filter before LLM processing where possible.
- Sanitizing input to prevent prompt injection.

### Knowledge Representation
- Pre-defined scripts for guided exercises (breathing, mindfulness).
- Curated list of journaling prompts.
- Curated list of reputable mental health resources and crisis lines (regionalized if possible).
- General wellness information snippets.
- **Strict rules/prompts defining the agent's limited role and inability to provide therapy/advice.**

### Decision Logic
- **CRISIS INTERVENTION RULE:** If crisis keywords detected -> Immediately provide crisis resources -> Disengage/redirect.
- If mood log request -> Record mood (if feature enabled with consent).
- If exercise/prompt request -> Provide pre-defined content.
- If information request -> Provide general info/links from curated list or restricted web search.
- If ambiguous -> Ask for clarification or state inability to help, reinforcing limitations.
- **LLM prompting must heavily emphasize safety, boundaries, disclaimers, and the "support tool, not therapist" role.**

### Tool Integration
- Tool for retrieving crisis hotline information.
- Tool for providing pre-defined exercises/prompts.
- Optional: Restricted web search tool for general info from approved sources.
- LLM for understanding requests and generating supportive, *non-therapeutic* responses within strict guidelines.

### Output Formatting
- Empathetic but **not overly familiar or human-like** tone.
- Clear presentation of exercises, prompts, and information.
- **Prominent and repeated disclaimers about the agent's limitations and the importance of professional help.**
- Crisis resources presented clearly and immediately when triggered.

### Memory Management
- Minimal short-term memory for conversation flow.
- Optional: Secure storage for anonymized mood data (requires consent framework).
- **Avoid storing sensitive conversation details.**

### Error Handling
- Handling unrecognized inputs gracefully, reiterating capabilities.
- Managing errors from any integrated tools (e.g., web search).
- **Prioritizing safety: If unsure how to respond safely, default to providing general resources and disclaimers.**
- Ensuring crisis detection mechanism is reliable and tested.

## Implementation Flow
1. User initiates interaction. Agent provides initial disclaimer about its role and limitations.
2. Agent receives user input.
3. **Input is scanned for crisis keywords. If detected, execute crisis intervention protocol (provide resources, disengage).**
4. If not a crisis, agent parses the request (mood log, exercise, prompt, info).
5. Agent selects appropriate action/tool based on the request.
6. Agent retrieves/generates response (mood confirmation, exercise script, prompt, info snippet, resource links) using pre-defined content or LLM under strict safety guidelines.
7. **Agent includes relevant disclaimers in the response.**
8. Agent presents the response to the user.

## Scaling Considerations
- Not applicable in the same way as other agents. Focus is on safety and responsible deployment, not massive user numbers without significant ethical review and infrastructure.
- Ensuring consistent safety behavior across all interactions.

## Limitations
- **CANNOT provide therapy or crisis support.**
- Effectiveness is limited to providing basic support and information.
- Relies heavily on pre-defined content and strict guardrails.
- Mood tracking is simplistic.
- Potential for misinterpretation of user input or providing unhelpful/generic responses.
- **Risk of users over-relying on the tool instead of seeking professional help.**
- Maintaining user privacy and data security is paramount and complex.