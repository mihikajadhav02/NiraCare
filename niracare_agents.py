"""
NiraCare Agents Module

Defines five specialized agents using Google's Generative AI SDK (Gemini):
1. IntakeAgent - Extracts structured symptoms from raw text
2. ClarifierAgent - Generates follow-up questions
3. SummaryAgent - Creates doctor-ready visit notes
4. RoutingAgent - Suggests doctor types and test categories
5. EvalAgent - Evaluates note quality (critic)

This module demonstrates:
- Multi-agent orchestration (5 agents)
- Memory/session state (NiraSession)
- Critic/Eval agent
- All using Gemini models (gemini-2.5-flash)

For Kaggle competition compliance, this uses Gemini and demonstrates
all required concepts.
"""

import json
import os
import warnings
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Fix importlib.metadata issue
try:
    import importlib.metadata
    if not hasattr(importlib.metadata, 'packages_distributions'):
        try:
            import importlib_metadata
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
        except ImportError:
            pass
except:
    pass

try:
    from dotenv import load_dotenv
except ImportError:
    pass  # python-dotenv is optional

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "Google Generative AI SDK not installed. Install with: pip install google-genai"
    )

# Load .env file if it exists (for local development)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    try:
        load_dotenv(env_path)
    except NameError:
        pass  # python-dotenv not installed, skip

# Configure Google API key from environment variable (or .env file)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found. Set it either:\n"
        "  1. As environment variable: export GOOGLE_API_KEY='your-key'\n"
        "  2. In .env file: GOOGLE_API_KEY=your-key"
    )

# Configure Gemini
genai.configure(api_key=api_key)


def _extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extracts JSON from agent response, handling common formatting issues.
    
    Args:
        response: Raw string response from agent
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]  # Remove ```json
    elif response.startswith("```"):
        response = response[3:]  # Remove ```
    
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    # Try to find JSON object boundaries
    start_idx = response.find("{")
    end_idx = response.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        response = response[start_idx:end_idx + 1]
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from agent response. "
            f"Response was: {response[:200]}... Error: {e}"
        )


# ============================================================================
# Agent 1: IntakeAgent
# ============================================================================

INTAKE_AGENT_INSTRUCTION = """You are a medical intake assistant that extracts structured symptom information from free-text descriptions.

Your task is to convert messy, emotional symptom descriptions into a clean, structured JSON format.

IMPORTANT RULES:
- Output ONLY valid JSON, no markdown, no code blocks, no explanatory text
- Do NOT provide any diagnosis, treatment suggestions, or medical advice
- Focus on extracting factual information about symptoms only

Output format (pure JSON):
{
  "symptoms": [
    {
      "name": "string (symptom name)",
      "severity": "mild|moderate|severe|unknown",
      "frequency": "string (e.g., 'daily', '3 times per week', 'occasional')",
      "since_when": "string (e.g., '2 weeks ago', 'since last month')",
      "cycle_related": "yes|no|unknown",
      "notes": "string (any additional context)"
    }
  ]
}

If no clear symptoms are mentioned, return {"symptoms": []}.
"""

# Initialize Gemini model for IntakeAgent
# Using gemini-2.5-flash (still Gemini-powered)
_intake_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=INTAKE_AGENT_INSTRUCTION
)


def run_intake_agent(raw_text: str) -> Dict[str, Any]:
    """
    Runs IntakeAgent on raw text and returns structured symptoms JSON.
    
    Args:
        raw_text: Raw free-text description from user
        
    Returns:
        Dictionary with 'symptoms' list
    """
    response = _intake_model.generate_content(raw_text)
    response_text = response.text if response.text else ""
    if not response_text:
        raise ValueError("No response received from IntakeAgent")
    return _extract_json_from_response(response_text)


# ============================================================================
# Agent 2: ClarifierAgent
# ============================================================================

CLARIFIER_AGENT_INSTRUCTION = """You are a medical clarifier assistant that generates focused follow-up questions.

Your task is to identify gaps in the symptom information and generate questions that a doctor would ask to better understand the patient's condition.

IMPORTANT RULES:
- Output ONLY valid JSON, no markdown, no code blocks, no explanatory text
- Generate 2-5 short, focused questions
- Questions should cover: duration, patterns, triggers, functional impact, timing
- Do NOT answer the questions, only ask them
- Do NOT provide diagnosis or treatment suggestions

Output format (pure JSON):
{
  "questions": [
    "Question 1?",
    "Question 2?",
    ...
  ]
}

If no clarification is needed, return {"questions": []}.
"""

_clarifier_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=CLARIFIER_AGENT_INSTRUCTION
)


def run_clarifier_agent(raw_text: str, intake_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs ClarifierAgent to generate follow-up questions.
    
    Args:
        raw_text: Original user input
        intake_json: Structured symptoms from IntakeAgent
        
    Returns:
        Dictionary with 'questions' list
    """
    prompt = f"""Original user input:
{raw_text}

Structured symptoms extracted:
{json.dumps(intake_json, indent=2)}

Based on the above, what follow-up questions would help clarify the symptoms?"""
    
    response = _clarifier_model.generate_content(prompt)
    response_text = response.text if response.text else ""
    if not response_text:
        raise ValueError("No response received from ClarifierAgent")
    return _extract_json_from_response(response_text)


# ============================================================================
# Agent 3: SummaryAgent
# ============================================================================

SUMMARY_AGENT_INSTRUCTION = """You are a medical documentation assistant that creates doctor-ready visit notes.

Your task is to synthesize all available information into a clear, structured visit note that a doctor can quickly understand.

CRITICAL SAFETY RULES:
- ABSOLUTELY NO diagnosis, differential diagnosis, or disease probabilities
- ABSOLUTELY NO treatment suggestions, medications, or medical advice
- ABSOLUTELY NO speculation about what condition the patient might have
- Focus ONLY on documenting what the patient reported

Output a visit note in the following format (plain text, not JSON):

CHIEF COMPLAINT:
[One sentence summarizing the main concern]

HISTORY OF PRESENT ILLNESS:
- Onset: [when symptoms started]
- Pattern: [how symptoms present - timing, triggers, etc.]
- Severity: [mild/moderate/severe and impact]
- Associated factors: [any related factors mentioned]

IMPACT ON DAILY LIFE:
[How symptoms affect daily activities, work, sleep, etc.]

QUESTIONS PATIENT WANTS TO ASK DOCTOR:
[List any questions the patient mentioned wanting to ask]

Remember: This is a communication helper, NOT a diagnostic tool.
"""

_summary_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SUMMARY_AGENT_INSTRUCTION
)


def run_summary_agent(
    raw_text: str,
    intake_json: Dict[str, Any],
    clarifier_answers: Dict[str, str]
) -> str:
    """
    Runs SummaryAgent to create a doctor-ready visit note.
    
    Args:
        raw_text: Original user input
        intake_json: Structured symptoms from IntakeAgent
        clarifier_answers: Dictionary mapping questions to user answers
        
    Returns:
        Formatted visit note as string
    """
    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in clarifier_answers.items()])
    
    prompt = f"""Original user input:
{raw_text}

Structured symptoms:
{json.dumps(intake_json, indent=2)}

Clarifying Q&A:
{answers_text}

Create a doctor-ready visit note based on the above information."""
    
    response = _summary_model.generate_content(prompt)
    response_text = response.text if response.text else ""
    if not response_text:
        raise ValueError("No response received from SummaryAgent")
    return response_text.strip()


# ============================================================================
# Agent 4: RoutingAgent (Doctor & Test Suggestions)
# ============================================================================

ROUTING_AGENT_INSTRUCTION = """You are a medical routing assistant that suggests appropriate doctor types and possible tests based on symptoms.

Your task is to provide general guidance on:
1. What type of doctor might be appropriate to see
2. What types of tests might be considered (general categories, not specific test names)

CRITICAL SAFETY RULES:
- ABSOLUTELY NO diagnosis or disease identification
- ABSOLUTELY NO specific test names or lab values
- ABSOLUTELY NO treatment recommendations
- Provide ONLY general guidance like "consider seeing a [specialist type]" or "tests might include [general category]"
- This is routing guidance, NOT medical advice

Output format (pure JSON):
{
  "recommended_doctors": [
    {
      "type": "Primary Care Physician / General Practitioner",
      "reason": "Can perform initial evaluation and coordinate care"
    },
    {
      "type": "Gynecologist",
      "reason": "For period-related or reproductive health concerns"
    }
  ],
  "possible_test_categories": [
    {
      "category": "Blood tests",
      "purpose": "To check for hormonal imbalances or other markers"
    },
    {
      "category": "Imaging studies",
      "purpose": "To visualize internal structures if needed"
    }
  ],
  "urgency_note": "General guidance: This is not urgent unless symptoms are severe. Always consult with a healthcare provider."
}

Keep recommendations general and non-specific.
"""

_routing_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=ROUTING_AGENT_INSTRUCTION
)


def run_routing_agent(
    raw_text: str,
    intake_json: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Runs RoutingAgent to suggest doctor types and test categories.
    
    Args:
        raw_text: Original user input
        intake_json: Structured symptoms from IntakeAgent
        
    Returns:
        Dictionary with 'recommended_doctors' and 'possible_test_categories'
    """
    prompt = f"""Based on the following symptom information, suggest appropriate doctor types and general test categories.

User description:
{raw_text}

Structured symptoms:
{json.dumps(intake_json, indent=2)}

Provide routing guidance in the specified JSON format."""
    
    response = _routing_model.generate_content(prompt)
    response_text = response.text if response.text else ""
    if not response_text:
        raise ValueError("No response received from RoutingAgent")
    return _extract_json_from_response(response_text)


# ============================================================================
# Agent 5: EvalAgent (Critic)
# ============================================================================

EVAL_AGENT_INSTRUCTION = """You are an evaluation assistant that assesses the quality of medical visit notes.

Your task is to evaluate whether a visit note is complete, clear, and doctor-ready.

Evaluation criteria:
1. Does it clearly state the chief complaint?
2. Does it include duration/onset information?
3. Does it describe severity and impact?
4. Does it mention patterns, triggers, or associated factors?
5. Is it free of diagnostic speculation or treatment advice?

IMPORTANT RULES:
- Output ONLY valid JSON, no markdown, no code blocks, no explanatory text
- Score should be 0-10 (10 = excellent, 0 = poor)
- List specific missing fields if any
- Provide constructive feedback

Output format (pure JSON):
{
  "score": 8,
  "missing_fields": ["field name 1", "field name 2"],
  "suggested_improvement": "One paragraph of specific feedback on how to improve the note."
}

If the note is perfect, return empty missing_fields list and score of 10.
"""

_eval_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=EVAL_AGENT_INSTRUCTION
)


def run_eval_agent(doctor_note: str) -> Dict[str, Any]:
    """
    Runs EvalAgent to evaluate the quality of a visit note.
    
    Args:
        doctor_note: The visit note to evaluate
        
    Returns:
        Dictionary with 'score', 'missing_fields', and 'suggested_improvement'
    """
    prompt = f"""Evaluate the following visit note:

{doctor_note}

Provide your evaluation in the specified JSON format."""
    
    response = _eval_model.generate_content(prompt)
    response_text = response.text if response.text else ""
    if not response_text:
        raise ValueError("No response received from EvalAgent")
    return _extract_json_from_response(response_text)

